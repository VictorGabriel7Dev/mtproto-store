[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | **Čeština** | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Používejte Telegram jako neomezené objektové úložiště s rozdělením na části - přes nativní protokol MTProto, jako jediný samostatný binární soubor CLI.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Žádný Python, žádné bot API, žádné externí běhové prostředí. Jediný statický binární soubor Go, který se přihlásí k uživatelskému účtu Telegramu přes MTProto a ukládá libovolné soubory jako nahrávání rozdělená na části v soukromém kanálu.

## Co to dělá

- Přihlásí se k **uživatelskému účtu** Telegramu (telefonní číslo -> přihlašovací kód -> volitelné heslo 2FA), přičemž emuluje oficiálního klienta Telegram Desktop, což udržuje relace stabilní a zabraňuje konfliktům odhlášení s jinými klienty.
- Ukládá libovolné soubory jako **nahrávání rozdělená na části** v soukromém kanálu a obchází tak limity velikosti pro boty (až 2 GB na soubor nebo 4 GB s Telegram Premium).
- Vytváří nebo znovu používá vlastní soukromý **kanál úložiště**, označený konfigurovatelnou příponou, takže pracuje vždy jen s vlastními kanály.
- Streamuje stahování zpět, vypisuje uložené položky a tiskne strojově čitelný JSON na stdout pro snadné skriptování.

Postaveno na [`gotd/td`](https://github.com/gotd/td) (čistý Go MTProto).

## Sestavení

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` odstraní ladicí symboly a tabulky DWARF (z přibližně 23 MB na 16 MB). Staticky se křížově kompiluje pro libovolný cíl (bez CGO) a stejné statické binární soubory pro Linux běží na Androidu (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Velikost binárního souboru

| Sestavení | Velikost (jedna architektura) |
|---|---|
| výchozí (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| výše uvedené, poté `upx --best --lzma` | ~5-6 MB |

Zásobník MTProto (`gotd/td` plus resolver s TLS kamufláží napodobující Telegram Desktop) tvoří většinu velikosti. CI publikuje **UPX komprimované** binární soubory vydání pro každý cíl; UPX se při startu sám rozbalí se zanedbatelnou režií. Pokud raději nechcete dodávat zabalené binární soubory, záložní možností je nekomprimované sestavení `-s -w`.

## Použití

Každý příkaz vytiskne jediný objekt JSON na stdout (`"ok": true | false`).

| Příkaz | Účel |
|---|---|
| `send-code --phone <number>` | Zahájit přihlášení; Telegram odešle přihlašovací kód |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Dokončit přihlášení |
| `bot-login --token <token>` | Přihlásit jako bot (omezené) |
| `check-auth` (alias `status`) | Nahlásit stav ověření |
| `init-storage [--title <title>] [--channel-id <id>]` | Vytvořit nebo znovu použít soukromý kanál úložiště |
| `upload --dir <path> [flags]` | Nahraje soubory z adresáře po částech |
| `download [flags]` | Stáhnout uložený archiv |
| `delete --ref <id>[,<id>...]` | Smaže jednu nebo více uložených položek |
| `list-remote` (alias `list-backups`) | Vypsat uložené položky |
| `logout` | Zrušit místní relaci |

## Konfigurace (prostředí)

| Proměnná | Výchozí | Význam |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Adresář stavu (relace, konfigurace cíle, logy) |
| `MTPROTO_STORE_TAG` | `MTPS` | Přípona, která označuje kanály úložiště tohoto nástroje |
| `MTPROTO_STORE_LABEL` | - | Volitelný název uložený jako `label` v metadatech každé nahrané položky (vrací ho `list-remote`) |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Váš vlastní `api_id` z my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Váš vlastní `api_hash` |

**Poznámka k podmínkám služby:** vestavěné výchozí hodnoty emulují oficiálního klienta Telegram Desktop. Pro vlastní nasazení získejte a nastavte vlastní `api_id` / `api_hash` na <https://my.telegram.org> a prostudujte si podmínky služby Telegramu. Nesete odpovědnost za to, jak svůj účet používáte.

### Relace a stav

Adresář stavu obsahuje vše, co si nástroj uchovává mezi spuštěními, v `$MTPROTO_STORE_STATE`:

| Cesta | Obsah |
|---|---|
| `creds/telegram.session` | ověřená **relace** |
| `dests/telegram.json` | vyřešený odkaz na kanál úložiště |
| `staging/tg_auth.json` | krátkodobý stav přihlášení (mezi `send-code` a `sign-in`) |
| `logs/progress-*.json` | průběh pro každou operaci |

**Relace je citlivý přihlašovací údaj**: kdokoli, kdo ji dokáže přečíst, ovládá účet, bez výzvy k zadání hesla nebo 2FA. Nástroj vytvoří adresář s právy `0700` a zapíše relaci s právy `0600`, ale skutečnou ochranou je to, *kam* nasměrujete `MTPROTO_STORE_STATE`. Uchovávejte ji v soukromém úložišti. Konkrétně na Androidu preferujte úložiště **Credential-Encrypted** (např. pod `/data/misc_ce/<user>`), které se odemkne až po ověření uživatele, před úložištěm **Device-Encrypted** (např. `/data/adb`, čitelným před prvním odemčením).

## Poděkování

Jádro tohoto nástroje původně napsal **Ash ([@ash-iir](https://github.com/ash-iir))**, který navrhl klienta úložiště na zkompilovaném MTProto, na němž je postaven. Veškeré uznání za původní práci patří jejímu autorovi. Tento repozitář extrahuje, odstraňuje branding a zobecňuje tuto práci do samostatného, znovupoužitelného nástroje.

## Viz také

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - procházitelný, automaticky aktualizovaný archiv skutečných dat `build.prop` z Pixelů.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - moderační bot proti spamu pro skupiny Telegramu.

## Licence

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) a přispěvatelé. Viz [LICENSE](LICENSE). Provozování upravené verze jako síťové služby vás zavazuje nabídnout její zdrojový kód.

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
