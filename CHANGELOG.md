# Changelog

All notable changes to mtproto-store are documented here.

## v1.2.0

New: an optional upload label, plus correctness and robustness fixes.

- **`MTPROTO_STORE_LABEL` (optional).** When set, its value is stored as `label` in each uploaded item's caption metadata and returned by `list-remote` in `meta`, so a host can attach a human-readable name without encoding it into the file name. An environment variable (not a flag), so an older binary ignores it; capped at 128 characters. Contributed by Ash ([@ash-iir](https://github.com/ash-iir)).
- **Bad flags return JSON, not a silent exit.** `send-code`, `sign-in`, `init-storage` and `bot-login` parsed flags in a mode that exited the process (code 2, empty stdout) on an unknown or malformed flag. They now emit `{ok:false, code:"ERR_INVALID_ARGS"}` like every other command.
- **`upload` requires `--dir`.** A missing `--dir` previously globbed the current working directory and could upload its contents; it now returns `ERR_INVALID_ARGS` before touching the filesystem.
- **Correct `ERR_NOT_AUTH`.** `upload`, `download` and `list-remote` now verify the session first and return `ERR_NOT_AUTH` when unauthenticated, instead of a misleading `ERR_UPLOAD` / `ERR_DOWNLOAD` / `ERR_LIST`.
- **`check-auth` hardened.** It no longer dereferences a nil user on an authorized-but-userless session, and reports `ERR_CLIENT` (not `is_auth:false`) when it cannot connect, so a transient network error is not mistaken for a logged-out account.
- **`upload` fails loudly** instead of returning a `message_id:0` handle it could not resolve (now tolerant of both `Updates` and `UpdatesCombined`), and emits `uploaded: []` rather than `null` for an empty set.
- **Stricter references.** `download --ref` rejects non-positive ids as `ERR_INVALID_REF`; `delete` rejects an invalid id inside a batch (e.g. `2,abc,5`) instead of silently dropping it.
- **Unknown flags are rejected** across `upload` / `download` / `list-remote` / `delete` instead of being swallowed as positional arguments.
- **Connection failures report `ERR_CLIENT`.** Every command now separates a transport/connect failure (reported as `ERR_CLIENT`, as the contract states) from a command-level error, instead of labelling a dropped connection with the command's own code.
- **`send-code` on an already-authenticated session** returns `{ok:true, already_authorized:true}` instead of an empty `phone_code_hash`, so a host can skip `sign-in`.
- CONTRACT documents the `sha256` field in `upload` results, the `already_authorized` response, and the per-command `ERR_INVALID_ARGS` code.

## v1.1.1

Maintenance release. No functional change to the CLI; the binary is unchanged from v1.1.0.

- **CI conformance guard:** a new `check` job (`gofmt` + `go vet` + `scripts/check-sync.py`) runs on every push and pull request. The guard fails the build if the documented commands or error codes drift from the binary, if upstream branding leaks into a tracked file, or if a translated README drops a command row - a durable fix for documentation drifting out of sync with the code.

## v1.1.0

- **New `delete` verb:** `delete --ref <message_id>[,<id>...]` removes one or more stored items (comma-separated for a batch), completing the CRUD cycle. JSON: `{ok, deleted:[...]}`.
- **`init-storage` continuity:** it now reuses the saved destination channel by id before falling back to a title scan, so renaming the storage channel in Telegram no longer splits backups into a new channel. New `--channel-id <id>` flag pins a specific channel.
- **Bot authentication:** new `bot-login --token <token>` authenticates as a bot. Limited mode (works against a pre-configured channel where the bot is an admin; no channel creation or listing) - see CONTRACT.md.
- `list-remote` now returns an empty array (`[]`) instead of `null` for an empty channel.

## v1.0.0

First stable release. The full flow is validated end-to-end against live Telegram: login (phone, code, 2FA password), storage-channel creation, chunked upload, listing, and download, with a byte-exact round-trip and the Telegram Desktop emulation confirmed. Documentation corrected (`upload` takes `--dir`; `2FA_REQUIRED` is documented). No breaking changes from v0.1.0.

## v0.1.0

Initial release.

- Telegram as unlimited, chunked object storage over native MTProto, as a single self-contained Go binary - no Python, no bot API, no external runtime. Built on gotd/td.
- Commands: `send-code`, `sign-in`, `check-auth` / `status`, `init-storage`, `upload`, `download`, `list-remote` / `list-backups`, `logout`. Each prints a single JSON object to stdout (see CONTRACT.md).
- Official Telegram Desktop emulation for stable sessions and no logout conflicts; `api_id` / `api_hash` overridable via `MTPROTO_STORE_API_ID` / `MTPROTO_STORE_API_HASH`.
- Configurable storage-channel tag, state directory and credentials via environment (`MTPROTO_STORE_TAG`, `MTPROTO_STORE_STATE`, ...).
- Chunked uploads/downloads bypassing bot size limits (up to 2 GB per file, or 4 GB with Telegram Premium); automatic private storage-channel discovery and reuse.
- Cross-compiled static binaries for the Android ABIs (arm64-v8a, armeabi-v7a, x86_64, x86) and desktop (Linux, macOS, Windows); UPX-compressed release builds.
- README available in 22 languages.

Originally authored by Ash (@ash-iir); extracted into a standalone, de-branded, reusable tool.
