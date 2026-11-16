# mtproto-store

Use Telegram as unlimited, chunked object storage - over the native **MTProto** protocol, as a single self-contained CLI binary. No Python, no bot API, no external runtime.

> **Credit:** the core was originally authored by **Ash ([@ash-iir](https://github.com/ash-iir))**. This repository extracts and generalizes that work into a standalone, reusable tool.

## What it does

- Logs into a Telegram **user account** (phone number -> login code -> optional 2FA password), emulating the official Telegram Desktop client, which keeps sessions stable and avoids logout conflicts with other clients.
- Stores arbitrary files as **chunked uploads** in a private channel, bypassing bot size limits (up to 2 GB per file, or 4 GB with Telegram Premium).
- Creates or reuses its own private **storage channel**, tagged with a configurable suffix so it only ever touches its own channels.
- Streams downloads back, lists stored items, and prints machine-readable JSON on stdout for easy scripting.

Built on [`gotd/td`](https://github.com/gotd/td) (pure-Go MTProto).

## Build

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` strips the debug symbols and DWARF tables (about 23 MB -> 16 MB). It cross-compiles statically for any target (no CGO), and the same static Linux binaries run on Android (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Binary size

| Build | Size (one arch) |
|---|---|
| default (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| the above, then `upx --best --lzma` | ~5-6 MB |

The MTProto stack (`gotd/td` plus a TLS-camouflage resolver that mimics Telegram Desktop) is the bulk of the size. CI publishes **UPX-compressed** release binaries for every target; UPX self-extracts at startup with negligible overhead. If you prefer not to ship packed binaries, the uncompressed `-s -w` build is the fallback.

## Usage

Every command prints a single JSON object to stdout (`"ok": true | false`).

| Command | Purpose |
|---|---|
| `send-code --phone <number>` | Begin login; Telegram sends the login code |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Complete login |
| `check-auth` (alias `status`) | Report authentication state |
| `init-storage [--title <title>]` | Create or reuse the private storage channel |
| `upload --file <path> [flags]` | Upload a file as chunks |
| `download [flags]` | Download a stored archive |
| `list-remote` (alias `list-backups`) | List stored items |
| `logout` | Drop the local session |

## Configuration (environment)

| Variable | Default | Meaning |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | State directory (session, destination config, logs) |
| `MTPROTO_STORE_TAG` | `MTPS` | Suffix that marks this tool's storage channels |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Your own `api_id` from my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Your own `api_hash` |

**Terms of Service note:** the built-in defaults emulate the official Telegram Desktop client. For your own deployments, obtain and set your own `api_id` / `api_hash` at <https://my.telegram.org> and review Telegram's Terms of Service. You are responsible for how you use your account.

## License

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) and contributors. See [LICENSE](LICENSE). Running a modified version as a network service obliges you to offer its source.
