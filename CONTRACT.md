# Integration contract

`mtproto-store` is built to be driven by other programs and agents. This document is the stable machine contract: every command, its flags, the JSON it prints, and the error codes. English only (it describes literal identifiers).

## General shape

- One subcommand per invocation: `mtproto-store <command> [flags]`.
- Every command prints **exactly one JSON object** to **stdout**, always with a boolean `ok`.
- On failure the object is `{ "ok": false, "code": "ERR_...", "message": "<human text>" }`. On success `ok` is `true` and the command-specific fields below are present.
- Logs and diagnostics, if any, go to **stderr**; stdout is reserved for the single JSON result, so a caller can parse stdout directly.
- Flags accept both `--flag value` and `--flag=value` (and the single-dash `-flag` forms). `--dest` defaults to `telegram`.
- State (session, destination config, staging, progress) lives under `$MTPROTO_STORE_STATE` (see README).

## Commands

### `send-code --phone <number>`
Begins login; Telegram sends the login code to the account. Writes short-lived staging state.
- **Success:** `{ "ok": true, "phone": "<normalized>", "phone_code_hash": "<hash>" }`
- **Already logged in:** `{ "ok": true, "phone": "<normalized>", "already_authorized": true }` (the session is already authenticated; no code is sent, and `sign-in` can be skipped)
- **Errors:** `ERR_INVALID_ARGS`, `ERR_INVALID_PHONE`, `ERR_SEND_CODE`, `ERR_CLIENT`

### `sign-in --phone <number> --code <code> [--password <2fa>]`
Completes login with the received code (and 2FA password if the account has one).
- **Success:** `{ "ok": true, "user": {…}, "channel": {…}|null }`
- **Errors:** `ERR_INVALID_ARGS`, `2FA_REQUIRED` (the account has 2FA; re-run with `--password`), `ERR_SIGN_IN`, `ERR_CLIENT`

### `bot-login --token <bot_token>`
Authenticates as a **bot** instead of a user account. **Limited mode:** a bot cannot create or discover channels and cannot read history, so bot mode only works against a channel that a user account already set up (saved in the destination config) and to which the bot has been added as an admin. `upload`, `download` and `delete` then work; `list-remote` and channel creation do not, and file-size limits are stricter than a user account.
- **Success:** `{ "ok": true, "is_auth": true, "bot": true, "user": { "id": <int>, "first_name": "…", "username": "…" } }`
- **Errors:** `ERR_INVALID_ARGS`, `ERR_SIGN_IN`, `ERR_CLIENT`

### `check-auth` (alias `status`)
Reports whether a usable, authenticated session exists. **The authentication gate is the `is_auth` boolean, not the presence of `user`.**
- **Not authenticated:** `{ "ok": true, "is_auth": false }` (no `user` / `channel` fields)
- **Authenticated:** `{ "ok": true, "is_auth": true, "user": { "id": <int>, "first_name": "…", "username": "…", "phone": "…" }, "channel": { "id": "-100…", "title": "…" } | null }`
- **Errors:** `ERR_CLIENT`

> The `user` object is `{ id, first_name, username, phone }` wherever it appears (here and in `sign-in`). Only `check-auth` carries `is_auth`; a successful `sign-in` implies authentication.

### `init-storage [--title <title>] [--channel-id <id>]`
Resolves the private storage channel, in this order: (1) `--channel-id` pins a specific channel by its id; (2) the saved destination config is reused if its channel still exists (robust to the channel being **renamed**, which a title scan would miss); (3) a channel whose title ends in the storage tag is reused; (4) otherwise a new channel is created (randomized name, or `--title`). Idempotent and safe to call on every startup.
- **Success (reused):** `{ "ok": true, "channel": { "id": "-100…", "title": "…" }, "reused": true }`
- **Success (created):** `{ "ok": true, "channel": { "id": "-100…", "title": "…" }, "created": true }`
- **Errors:** `ERR_INVALID_ARGS`, `ERR_NOT_AUTH`, `ERR_INIT_STORAGE`, `ERR_CLIENT`

### `upload --dir <path> [--dest telegram] [--opid <id>]`
Uploads every file in the directory `<path>` as chunked documents into the storage channel. `--opid`, if given, makes the command write progress to `logs/progress-<opid>.json` (percent/phase), so a host can poll a long transfer.
If `MTPROTO_STORE_LABEL` is set, its value is stored as `label` in each uploaded item's caption metadata (the `meta` that `list-remote` returns), so a host can attach a human-readable name without putting it in the file name. Unset: no `label` key, exactly as before.
- **Success:** `{ "ok": true, "uploaded": [ { "name": "<file>", "size": <bytes>, "sha256": "<hex>", "message_id": <int> }, … ] }` (empty `[]` if the directory held no regular files)
- **Errors:** `ERR_INVALID_ARGS`, `ERR_NO_FILES`, `ERR_NOT_AUTH`, `ERR_UPLOAD`, `ERR_CLIENT`

### `download --ref <message_id> --out <path> [--dest telegram] [--opid <id>]`
Downloads a stored document (identified by its `message_id`, as returned by `list-remote`/`upload`) to `--out`.
- **Success:** `{ "ok": true, "file": "<out path>", "size": <bytes> }`
- **Errors:** `ERR_INVALID_ARGS`, `ERR_INVALID_REF`, `ERR_NOT_AUTH`, `ERR_DOWNLOAD`, `ERR_CLIENT`

### `delete --ref <message_id>[,<id>...] [--dest telegram]`
Deletes one or more stored items by `message_id` (comma-separated for a batch, e.g. `--ref 2,5,7`).
- **Success:** `{ "ok": true, "deleted": [ <int>, … ] }`
- **Errors:** `ERR_INVALID_ARGS`, `ERR_INVALID_REF`, `ERR_NOT_AUTH`, `ERR_DELETE`, `ERR_CLIENT`

### `list-remote` (alias `list-backups`) `[--dest telegram]`
Lists the documents stored in the channel.
- **Success:** `{ "ok": true, "backups": [ { "message_id": <int>, "name": "<file>", "size": <bytes>, "date": <unix>, "meta": {…} }, … ] }`
- **Errors:** `ERR_INVALID_ARGS`, `ERR_NOT_AUTH`, `ERR_LIST`, `ERR_CLIENT`

### `logout`
Drops the local session.
- **Success:** `{ "ok": true }`

## Error codes

| Code | Meaning |
|---|---|
| `ERR_NO_COMMAND` | No subcommand given |
| `ERR_UNKNOWN_VERB` | Unknown subcommand |
| `ERR_INVALID_ARGS` | Missing or malformed flags |
| `ERR_INVALID_PHONE` | Phone number could not be parsed |
| `ERR_INVALID_REF` | Download reference (`--ref`) is missing or invalid |
| `ERR_NO_FILES` | Upload found nothing to send |
| `ERR_NOT_AUTH` | No authenticated session (run `send-code` + `sign-in`) |
| `ERR_SEND_CODE` | Telegram rejected the login-code request |
| `ERR_SIGN_IN` | Sign-in failed (wrong or expired code) |
| `2FA_REQUIRED` | The account has two-factor auth; re-run `sign-in` with `--password` |
| `ERR_INIT_STORAGE` | Could not create or resolve the storage channel |
| `ERR_UPLOAD` | Upload failed mid-transfer |
| `ERR_DOWNLOAD` | Download failed |
| `ERR_LIST` | Listing the channel failed |
| `ERR_DELETE` | Deleting one or more messages failed |
| `ERR_CLIENT` | MTProto client could not be created or connected |

## Notes for integrators

- Treat `message_id` as the opaque handle for a stored item; pass it back as `--ref` to download.
- `init-storage` is idempotent: it reuses an existing tagged channel, so it is safe to call on every startup.
- Progress files (`--opid`) are best-effort and may lag; the authoritative result is the final JSON on stdout.
- The process is cancellable by the host (SIGTERM/SIGKILL); a partial upload leaves no success JSON.
