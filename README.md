**English** | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Use Telegram as unlimited, chunked object storage - over the native MTProto protocol, as a single self-contained CLI binary.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

No Python, no bot API, no external runtime. A single static Go binary that logs into a Telegram user account over MTProto and stores arbitrary files as chunked uploads in a private channel.

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
| `upload --dir <path> [flags]` | Upload a file as chunks |
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

### Sessions and state

The state directory holds everything the tool keeps between runs, under `$MTPROTO_STORE_STATE`:

| Path | Contents |
|---|---|
| `creds/telegram.session` | the authenticated **session** |
| `dests/telegram.json` | the resolved storage-channel reference |
| `staging/tg_auth.json` | short-lived login state (between `send-code` and `sign-in`) |
| `logs/progress-*.json` | per-operation progress |

The **session is a sensitive credential**: anyone who can read it controls the account, with no password or 2FA prompt. The tool creates the directory `0700` and writes the session `0600`, but the real protection is *where* you point `MTPROTO_STORE_STATE`. Keep it on private storage. On Android specifically, prefer **Credential-Encrypted** storage (e.g. under `/data/misc_ce/<user>`), which is unlocked only after the user authenticates, over **Device-Encrypted** storage (e.g. `/data/adb`, readable before first unlock).

## Credits

The core of this tool was originally authored by **Ash ([@ash-iir](https://github.com/ash-iir))**, who designed the compiled-MTProto storage client it is built on. Full credit for the original work goes to its author. This repository extracts, de-brands and generalizes that work into a standalone, reusable tool.

## See also

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - a browsable, auto-updated archive of real Pixel `build.prop` data.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - anti-spam moderation bot for Telegram groups.

## License

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) and contributors. See [LICENSE](LICENSE). Running a modified version as a network service obliges you to offer its source.

## Contact

- https://victorgabriel.dev
- **GitHub:** @VictorGabriel7Dev https://github.com/VictorGabriel7Dev
- **Telegram:** @VictorGabriel_Dev https://t.me/VictorGabriel_Dev
- **Discord:** @VictorGabriel.dev https://discord.com/users/1481407654458036265
- **LinkedIn:** in/victorgabriel-dev https://www.linkedin.com/in/victorgabriel-dev
- **Instagram:** @VictorGabriel_Dev https://www.instagram.com/VictorGabriel_Dev
- **WhatsApp:** @VictorGabriel_Dev https://wa.me/@VictorGabriel_Dev
- **E-mail:** contato@victorgabriel.dev

---

`telegram` `mtproto` `gotd` `cloud-storage` `object-storage` `unlimited-storage` `cli` `golang` `static-binary` `cross-platform` `self-hosted` `file-storage` `chunked-upload` `mtproto-store`
