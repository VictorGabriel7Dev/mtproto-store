[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | **Nederlands** | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Gebruik Telegram als onbeperkte, in stukken verdeelde objectopslag - via het native MTProto-protocol, als een enkele zelfstandige CLI-binary.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Geen Python, geen bot-API, geen externe runtime. Een enkele statische Go-binary die zich aanmeldt bij een Telegram-gebruikersaccount via MTProto en willekeurige bestanden als in stukken verdeelde uploads opslaat in een privékanaal.

## Wat het doet

- Meldt zich aan bij een Telegram-**gebruikersaccount** (telefoonnummer -> inlogcode -> optioneel 2FA-wachtwoord) en emuleert daarbij de officiële Telegram Desktop-client, wat sessies stabiel houdt en uitlogconflicten met andere clients voorkomt.
- Slaat willekeurige bestanden op als **in stukken verdeelde uploads** in een privékanaal en omzeilt zo de groottelimieten voor bots (tot 2 GB per bestand, of 4 GB met Telegram Premium).
- Maakt of hergebruikt zijn eigen privé-**opslagkanaal**, gemarkeerd met een configureerbaar achtervoegsel, zodat het altijd alleen zijn eigen kanalen aanraakt.
- Streamt downloads terug, toont een lijst van opgeslagen items en drukt machineleesbare JSON af op stdout voor eenvoudig scripten.

Gebouwd op [`gotd/td`](https://github.com/gotd/td) (pure-Go MTProto).

## Bouwen

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` verwijdert de debugsymbolen en DWARF-tabellen (van ongeveer 23 MB naar 16 MB). Het cross-compileert statisch voor elk doel (zonder CGO), en dezelfde statische Linux-binaries draaien op Android (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Grootte van de binary

| Bouw | Grootte (één architectuur) |
|---|---|
| standaard (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| het bovenstaande, daarna `upx --best --lzma` | ~5-6 MB |

De MTProto-stack (`gotd/td` plus een TLS-camouflageresolver die Telegram Desktop nabootst) vormt het grootste deel van de grootte. CI publiceert **UPX-gecomprimeerde** release-binaries voor elk doel; UPX pakt zichzelf bij het opstarten uit met verwaarloosbare overhead. Als je liever geen ingepakte binaries levert, is de ongecomprimeerde `-s -w`-build de terugvaloptie.

## Gebruik

Elk commando drukt één JSON-object af op stdout (`"ok": true | false`).

| Commando | Doel |
|---|---|
| `send-code --phone <number>` | Start het inloggen; Telegram stuurt de inlogcode |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Voltooi het inloggen |
| `bot-login --token <token>` | Inloggen als bot (beperkt) |
| `check-auth` (alias `status`) | Rapporteer de authenticatiestatus |
| `init-storage [--title <title>] [--channel-id <id>]` | Maak of hergebruik het privé-opslagkanaal |
| `upload --dir <path> [flags]` | Uploadt de bestanden in een map in delen |
| `download [flags]` | Download een opgeslagen archief |
| `delete --ref <id>[,<id>...]` | Verwijdert een of meer opgeslagen items |
| `list-remote` (alias `list-backups`) | Toon een lijst van opgeslagen items |
| `logout` | Verwijder de lokale sessie |

## Configuratie (omgeving)

| Variabele | Standaard | Betekenis |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Toestandsmap (sessie, bestemmingsconfiguratie, logs) |
| `MTPROTO_STORE_TAG` | `MTPS` | Achtervoegsel dat de opslagkanalen van dit hulpmiddel markeert |
| `MTPROTO_STORE_LABEL` | - | Optionele naam die als `label` wordt opgeslagen in de metadata van elk geüpload item (teruggegeven door `list-remote`) |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Je eigen `api_id` van my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Je eigen `api_hash` |

**Opmerking over de servicevoorwaarden:** de ingebouwde standaardwaarden emuleren de officiële Telegram Desktop-client. Verkrijg en stel voor je eigen implementaties je eigen `api_id` / `api_hash` in op <https://my.telegram.org> en bekijk de servicevoorwaarden van Telegram. Je bent zelf verantwoordelijk voor hoe je je account gebruikt.

### Sessies en toestand

De toestandsmap bevat alles wat het hulpmiddel tussen uitvoeringen bewaart, onder `$MTPROTO_STORE_STATE`:

| Pad | Inhoud |
|---|---|
| `creds/telegram.session` | de geauthenticeerde **sessie** |
| `dests/telegram.json` | de opgeloste verwijzing naar het opslagkanaal |
| `staging/tg_auth.json` | kortstondige inlogtoestand (tussen `send-code` en `sign-in`) |
| `logs/progress-*.json` | voortgang per bewerking |

De **sessie is een gevoelige credential**: iedereen die haar kan lezen, beheert het account, zonder vraag om wachtwoord of 2FA. Het hulpmiddel maakt de map aan met `0700` en schrijft de sessie weg met `0600`, maar de echte bescherming is *waar* je `MTPROTO_STORE_STATE` naar laat wijzen. Houd die op privéopslag. Geef specifiek op Android de voorkeur aan **Credential-Encrypted**-opslag (bijv. onder `/data/misc_ce/<user>`), die pas wordt ontgrendeld nadat de gebruiker zich heeft geauthenticeerd, boven **Device-Encrypted**-opslag (bijv. `/data/adb`, die leesbaar is vóór de eerste ontgrendeling).

## Dankbetuigingen

De kern van dit hulpmiddel is oorspronkelijk geschreven door **Ash ([@ash-iir](https://github.com/ash-iir))**, die de op gecompileerde MTProto gebaseerde opslagclient ontwierp waarop het is gebouwd. Alle eer voor het oorspronkelijke werk gaat naar de auteur ervan. Deze repository extraheert, de-brandt en generaliseert dat werk tot een zelfstandig, herbruikbaar hulpmiddel.

## Zie ook

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - een doorzoekbaar, automatisch bijgewerkt archief van echte Pixel-`build.prop`-gegevens.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - antispam-moderatiebot voor Telegram-groepen.

## Licentie

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) en bijdragers. Zie [LICENSE](LICENSE). Het draaien van een gewijzigde versie als netwerkdienst verplicht je de broncode ervan aan te bieden.

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
