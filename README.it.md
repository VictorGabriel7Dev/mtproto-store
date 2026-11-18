[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | **Italiano** | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Usa Telegram come archiviazione di oggetti illimitata e frammentata - tramite il protocollo nativo MTProto, come un unico binario a riga di comando autonomo.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Niente Python, niente API per bot, nessun runtime esterno. Un unico binario statico in Go che accede a un account utente Telegram tramite MTProto e archivia file arbitrari come caricamenti frammentati in un canale privato.

## Cosa fa

- Accede a un **account utente** Telegram (numero di telefono -> codice di accesso -> password 2FA opzionale), emulando il client ufficiale Telegram Desktop, il che mantiene le sessioni stabili ed evita conflitti di disconnessione con altri client.
- Archivia file arbitrari come **caricamenti frammentati** in un canale privato, aggirando i limiti di dimensione dei bot (fino a 2 GB per file, o 4 GB con Telegram Premium).
- Crea o riutilizza il proprio **canale di archiviazione** privato, contrassegnato con un suffisso configurabile in modo da operare solo sui propri canali.
- Restituisce i download in streaming, elenca gli elementi archiviati e stampa JSON leggibile dalle macchine su stdout per semplificare l'automazione.

Basato su [`gotd/td`](https://github.com/gotd/td) (MTProto puro in Go).

## Compilazione

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` rimuove i simboli di debug e le tabelle DWARF (circa 23 MB -> 16 MB). Esegue la compilazione incrociata in modo statico per qualsiasi destinazione (senza CGO), e gli stessi binari Linux statici funzionano su Android (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Dimensione del binario

| Compilazione | Dimensione (una architettura) |
|---|---|
| predefinita (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| quanto sopra, poi `upx --best --lzma` | ~5-6 MB |

Lo stack MTProto (`gotd/td` più un resolver di camuffamento TLS che imita Telegram Desktop) costituisce la maggior parte della dimensione. La CI pubblica binari di rilascio **compressi con UPX** per ogni destinazione; UPX si autoestrae all'avvio con un overhead trascurabile. Se preferisci non distribuire binari compressi, la compilazione `-s -w` non compressa è l'alternativa.

## Utilizzo

Ogni comando stampa un singolo oggetto JSON su stdout (`"ok": true | false`).

| Comando | Scopo |
|---|---|
| `send-code --phone <number>` | Avvia l'accesso; Telegram invia il codice di accesso |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Completa l'accesso |
| `bot-login --token <token>` | Accedi come bot (limitato) |
| `check-auth` (alias `status`) | Riporta lo stato di autenticazione |
| `init-storage [--title <title>] [--channel-id <id>]` | Crea o riutilizza il canale di archiviazione privato |
| `upload --dir <path> [flags]` | Carica i file di una directory a blocchi |
| `download [flags]` | Scarica un archivio memorizzato |
| `delete --ref <id>[,<id>...]` | Elimina uno o più elementi archiviati |
| `list-remote` (alias `list-backups`) | Elenca gli elementi archiviati |
| `logout` | Elimina la sessione locale |

## Configurazione (ambiente)

| Variabile | Predefinito | Significato |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Directory di stato (sessione, configurazione della destinazione, log) |
| `MTPROTO_STORE_TAG` | `MTPS` | Suffisso che contrassegna i canali di archiviazione di questo strumento |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Il tuo `api_id` da my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Il tuo `api_hash` |

**Nota sui Termini di Servizio:** i valori predefiniti integrati emulano il client ufficiale Telegram Desktop. Per le tue implementazioni, ottieni e imposta il tuo `api_id` / `api_hash` su <https://my.telegram.org> e consulta i Termini di Servizio di Telegram. Sei responsabile dell'uso che fai del tuo account.

### Sessioni e stato

La directory di stato contiene tutto ciò che lo strumento conserva tra un'esecuzione e l'altra, in `$MTPROTO_STORE_STATE`:

| Percorso | Contenuto |
|---|---|
| `creds/telegram.session` | la **sessione** autenticata |
| `dests/telegram.json` | il riferimento risolto del canale di archiviazione |
| `staging/tg_auth.json` | stato di accesso di breve durata (tra `send-code` e `sign-in`) |
| `logs/progress-*.json` | avanzamento per operazione |

La **sessione è una credenziale sensibile**: chiunque possa leggerla controlla l'account, senza richiesta di password o 2FA. Lo strumento crea la directory come `0700` e scrive la sessione come `0600`, ma la vera protezione sta in *dove* punti `MTPROTO_STORE_STATE`. Conservala in un'archiviazione privata. Su Android in particolare, preferisci l'archiviazione **Credential-Encrypted** (ad esempio in `/data/misc_ce/<user>`), che viene sbloccata solo dopo l'autenticazione dell'utente, rispetto all'archiviazione **Device-Encrypted** (ad esempio `/data/adb`, leggibile prima del primo sblocco).

## Riconoscimenti

Il nucleo di questo strumento è stato originariamente scritto da **Ash ([@ash-iir](https://github.com/ash-iir))**, che ha progettato il client di archiviazione MTProto compilato su cui si basa. Tutto il merito del lavoro originale va al suo autore. Questo repository estrae, rimuove il marchio e generalizza quel lavoro in uno strumento autonomo e riutilizzabile.

## Vedi anche

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - un archivio consultabile e aggiornato automaticamente di dati reali `build.prop` dei Pixel.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - bot di moderazione anti-spam per gruppi Telegram.

## Licenza

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) e collaboratori. Vedi [LICENSE](LICENSE). Eseguire una versione modificata come servizio di rete ti obbliga a offrirne il codice sorgente.

## Contatti

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
