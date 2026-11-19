[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | **Svenska** | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Använd Telegram som obegränsad objektlagring i delar - via det inbyggda MTProto-protokollet, som en enda fristående CLI-binär.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Inget Python, inget bot-API, ingen extern körmiljö. En enda statisk Go-binär som loggar in på ett Telegram-användarkonto över MTProto och lagrar godtyckliga filer som uppdelade uppladdningar i en privat kanal.

## Vad det gör

- Loggar in på ett Telegram-**användarkonto** (telefonnummer -> inloggningskod -> valfritt 2FA-lösenord) och emulerar den officiella Telegram Desktop-klienten, vilket håller sessionerna stabila och undviker utloggningskonflikter med andra klienter.
- Lagrar godtyckliga filer som **uppdelade uppladdningar** i en privat kanal och kringgår botens storleksgränser (upp till 2 GB per fil, eller 4 GB med Telegram Premium).
- Skapar eller återanvänder sin egen privata **lagringskanal**, märkt med ett konfigurerbart suffix så att den bara rör sina egna kanaler.
- Strömmar tillbaka nedladdningar, listar lagrade objekt och skriver ut maskinläsbar JSON på stdout för enkel skriptning.

Byggd på [`gotd/td`](https://github.com/gotd/td) (ren Go-MTProto).

## Bygga

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` tar bort felsökningssymbolerna och DWARF-tabellerna (cirka 23 MB -> 16 MB). Den korskompilerar statiskt för valfri målplattform (ingen CGO), och samma statiska Linux-binärer körs på Android (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Binärstorlek

| Bygge | Storlek (en arkitektur) |
|---|---|
| standard (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| samma som ovan, sedan `upx --best --lzma` | ~5-6 MB |

MTProto-stacken (`gotd/td` plus en TLS-kamouflageresolver som efterliknar Telegram Desktop) står för merparten av storleken. CI publicerar **UPX-komprimerade** release-binärer för varje målplattform; UPX packar upp sig själv vid start med försumbar overhead. Om du föredrar att inte distribuera packade binärer är den okomprimerade `-s -w`-byggningen reservalternativet.

## Användning

Varje kommando skriver ut ett enda JSON-objekt till stdout (`"ok": true | false`).

| Kommando | Syfte |
|---|---|
| `send-code --phone <number>` | Starta inloggning; Telegram skickar inloggningskoden |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Slutför inloggning |
| `bot-login --token <token>` | Logga in som bot (begränsat) |
| `check-auth` (alias `status`) | Rapportera autentiseringstillstånd |
| `init-storage [--title <title>] [--channel-id <id>]` | Skapa eller återanvänd den privata lagringskanalen |
| `upload --dir <path> [flags]` | Laddar upp filerna i en katalog i delar |
| `download [flags]` | Ladda ner ett lagrat arkiv |
| `delete --ref <id>[,<id>...]` | Tar bort ett eller flera lagrade objekt |
| `list-remote` (alias `list-backups`) | Lista lagrade objekt |
| `logout` | Släpp den lokala sessionen |

## Konfiguration (miljö)

| Variabel | Standard | Betydelse |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Tillståndskatalog (session, destinationskonfiguration, loggar) |
| `MTPROTO_STORE_TAG` | `MTPS` | Suffix som markerar det här verktygets lagringskanaler |
| `MTPROTO_STORE_LABEL` | - | Valfritt namn som sparas som `label` i metadata för varje uppladdat objekt (returneras av `list-remote`) |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Ditt eget `api_id` från my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Ditt eget `api_hash` |

**Villkor för tjänsten (not):** de inbyggda standardvärdena emulerar den officiella Telegram Desktop-klienten. För dina egna driftsättningar, skaffa och ange ditt eget `api_id` / `api_hash` på <https://my.telegram.org> och läs igenom Telegrams användarvillkor. Du är ansvarig för hur du använder ditt konto.

### Sessioner och tillstånd

Tillståndskatalogen innehåller allt som verktyget behåller mellan körningar, under `$MTPROTO_STORE_STATE`:

| Sökväg | Innehåll |
|---|---|
| `creds/telegram.session` | den autentiserade **sessionen** |
| `dests/telegram.json` | den upplösta referensen till lagringskanalen |
| `staging/tg_auth.json` | kortlivat inloggningstillstånd (mellan `send-code` och `sign-in`) |
| `logs/progress-*.json` | förlopp per operation |

**Sessionen är en känslig autentiseringsuppgift**: vem som helst som kan läsa den kontrollerar kontot, utan lösenord eller 2FA-fråga. Verktyget skapar katalogen `0700` och skriver sessionen `0600`, men det verkliga skyddet är *var* du pekar `MTPROTO_STORE_STATE`. Håll den på privat lagring. Specifikt på Android, föredra **Credential-Encrypted**-lagring (t.ex. under `/data/misc_ce/<user>`), som låses upp först efter att användaren autentiserat sig, framför **Device-Encrypted**-lagring (t.ex. `/data/adb`, läsbar före första upplåsningen).

## Erkännanden

Kärnan i det här verktyget skrevs ursprungligen av **Ash ([@ash-iir](https://github.com/ash-iir))**, som designade den kompilerade MTProto-lagringsklient som det bygger på. All heder för det ursprungliga arbetet går till dess upphovsperson. Det här arkivet extraherar det arbetet, tar bort varumärkningen och generaliserar det till ett fristående, återanvändbart verktyg.

## Se även

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - ett bläddringsbart, automatiskt uppdaterat arkiv med riktiga Pixel-`build.prop`-data.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - antispam-modereringsbot för Telegram-grupper.

## Licens

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) och bidragsgivare. Se [LICENSE](LICENSE). Att köra en modifierad version som en nätverkstjänst förpliktar dig att erbjuda dess källkod.

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
