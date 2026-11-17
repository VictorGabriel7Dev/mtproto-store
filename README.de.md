[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | **Deutsch** | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Nutzen Sie Telegram als unbegrenzten, fragmentierten Objektspeicher - über das native MTProto-Protokoll, als einzelne eigenständige CLI-Binärdatei.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Kein Python, keine Bot-API, keine externe Laufzeitumgebung. Eine einzelne statische Go-Binärdatei, die sich über MTProto bei einem Telegram-Benutzerkonto anmeldet und beliebige Dateien als fragmentierte Uploads in einem privaten Kanal speichert.

## Was es tut

- Meldet sich bei einem Telegram-**Benutzerkonto** an (Telefonnummer -> Anmeldecode -> optionales 2FA-Passwort) und emuliert dabei den offiziellen Telegram-Desktop-Client, wodurch Sitzungen stabil bleiben und Abmeldekonflikte mit anderen Clients vermieden werden.
- Speichert beliebige Dateien als **fragmentierte Uploads** in einem privaten Kanal und umgeht so die Größenbeschränkungen von Bots (bis zu 2 GB pro Datei oder 4 GB mit Telegram Premium).
- Erstellt oder verwendet einen eigenen privaten **Speicherkanal** erneut, der mit einem konfigurierbaren Suffix gekennzeichnet ist, sodass er ausschließlich seine eigenen Kanäle berührt.
- Streamt Downloads zurück, listet gespeicherte Elemente auf und gibt maschinenlesbares JSON auf stdout aus, um das Skripten zu erleichtern.

Basiert auf [`gotd/td`](https://github.com/gotd/td) (reines Go-MTProto).

## Erstellung

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` entfernt die Debug-Symbole und DWARF-Tabellen (etwa 23 MB -> 16 MB). Es kompiliert per Cross-Compilation statisch für jedes Ziel (ohne CGO), und dieselben statischen Linux-Binärdateien laufen unter Android (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Binärgröße

| Erstellung | Größe (eine Architektur) |
|---|---|
| Standard (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| das Obige, dann `upx --best --lzma` | ~5-6 MB |

Der MTProto-Stack (`gotd/td` plus ein TLS-Tarnungs-Resolver, der Telegram Desktop nachahmt) macht den Großteil der Größe aus. Die CI veröffentlicht für jedes Ziel **UPX-komprimierte** Release-Binärdateien; UPX entpackt sich beim Start selbst mit vernachlässigbarem Mehraufwand. Wenn Sie keine gepackten Binärdateien ausliefern möchten, ist der unkomprimierte `-s -w`-Build die Ausweichlösung.

## Verwendung

Jeder Befehl gibt ein einzelnes JSON-Objekt auf stdout aus (`"ok": true | false`).

| Befehl | Zweck |
|---|---|
| `send-code --phone <number>` | Startet die Anmeldung; Telegram sendet den Anmeldecode |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Schließt die Anmeldung ab |
| `bot-login --token <token>` | Als Bot anmelden (eingeschränkt) |
| `check-auth` (alias `status`) | Meldet den Authentifizierungsstatus |
| `init-storage [--title <title>] [--channel-id <id>]` | Erstellt oder verwendet den privaten Speicherkanal erneut |
| `upload --dir <path> [flags]` | Lädt die Dateien eines Verzeichnisses in Blöcken hoch |
| `download [flags]` | Lädt ein gespeichertes Archiv herunter |
| `delete --ref <id>[,<id>...]` | Löscht ein oder mehrere gespeicherte Elemente |
| `list-remote` (alias `list-backups`) | Listet gespeicherte Elemente auf |
| `logout` | Verwirft die lokale Sitzung |

## Konfiguration (Umgebung)

| Variable | Standard | Bedeutung |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Statusverzeichnis (Sitzung, Zielkonfiguration, Protokolle) |
| `MTPROTO_STORE_TAG` | `MTPS` | Suffix, das die Speicherkanäle dieses Tools kennzeichnet |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Ihre eigene `api_id` von my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Ihr eigener `api_hash` |

**Hinweis zu den Nutzungsbedingungen:** Die integrierten Standardwerte emulieren den offiziellen Telegram-Desktop-Client. Besorgen und setzen Sie für Ihre eigenen Bereitstellungen Ihre eigene `api_id` / `api_hash` unter <https://my.telegram.org> und lesen Sie die Nutzungsbedingungen von Telegram. Sie sind für die Nutzung Ihres Kontos verantwortlich.

### Sitzungen und Status

Das Statusverzeichnis enthält alles, was das Tool zwischen den Ausführungen aufbewahrt, unter `$MTPROTO_STORE_STATE`:

| Pfad | Inhalt |
|---|---|
| `creds/telegram.session` | die authentifizierte **Sitzung** |
| `dests/telegram.json` | die aufgelöste Referenz des Speicherkanals |
| `staging/tg_auth.json` | kurzlebiger Anmeldestatus (zwischen `send-code` und `sign-in`) |
| `logs/progress-*.json` | Fortschritt pro Vorgang |

Die **Sitzung ist eine sensible Anmeldeinformation**: Wer sie lesen kann, kontrolliert das Konto, ohne Abfrage von Passwort oder 2FA. Das Tool erstellt das Verzeichnis mit `0700` und schreibt die Sitzung mit `0600`, doch der eigentliche Schutz liegt darin, *wohin* Sie `MTPROTO_STORE_STATE` verweisen lassen. Bewahren Sie sie auf privatem Speicher auf. Speziell unter Android sollten Sie **Credential-Encrypted**-Speicher (z. B. unter `/data/misc_ce/<user>`), der erst nach der Authentifizierung des Benutzers entsperrt wird, dem **Device-Encrypted**-Speicher (z. B. `/data/adb`, vor dem ersten Entsperren lesbar) vorziehen.

## Danksagungen

Der Kern dieses Tools wurde ursprünglich von **Ash ([@ash-iir](https://github.com/ash-iir))** geschrieben, der den kompilierten MTProto-Speicherclient entworfen hat, auf dem es aufbaut. Die gesamte Anerkennung für die ursprüngliche Arbeit gebührt ihrem Autor. Dieses Repository extrahiert, entfernt die Marke und verallgemeinert diese Arbeit zu einem eigenständigen, wiederverwendbaren Tool.

## Siehe auch

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - ein durchsuchbares, automatisch aktualisiertes Archiv echter `build.prop`-Daten von Pixel-Geräten.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - Anti-Spam-Moderationsbot für Telegram-Gruppen.

## Lizenz

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) und Mitwirkende. Siehe [LICENSE](LICENSE). Der Betrieb einer modifizierten Version als Netzwerkdienst verpflichtet Sie, deren Quellcode anzubieten.

## Kontakt

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
