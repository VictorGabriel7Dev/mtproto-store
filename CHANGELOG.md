# Changelog

All notable changes to mtproto-store are documented here.

## v1.1.0

- **New `delete` verb:** `delete --ref <message_id>[,<id>...]` removes one or more stored items (comma-separated for a batch), completing the CRUD cycle. JSON: `{ok, deleted:[...]}`.
- **`init-storage` continuity:** it now reuses the saved destination channel by id before falling back to a title scan, so renaming the storage channel in Telegram no longer splits backups into a new channel. New `--channel-id <id>` flag pins a specific channel.
- **Bot authentication:** new `bot-login --token <token>` authenticates as a bot. Limited mode (works against a pre-configured channel where the bot is an admin; no channel creation or listing) - see CONTRACT.md.

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
