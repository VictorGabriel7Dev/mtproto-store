# Changelog

All notable changes to mtproto-store are documented here.

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
