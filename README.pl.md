[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | **Polski** | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Używaj Telegrama jako nieograniczonego, dzielonego na części magazynu obiektów - przez natywny protokół MTProto, jako pojedynczy samodzielny plik binarny CLI.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Bez Pythona, bez bot API, bez zewnętrznego środowiska uruchomieniowego. Pojedynczy statyczny plik binarny Go, który loguje się do konta użytkownika Telegrama przez MTProto i przechowuje dowolne pliki jako przesłania dzielone na części w prywatnym kanale.

## Co robi

- Loguje się do **konta użytkownika** Telegrama (numer telefonu -> kod logowania -> opcjonalne hasło 2FA), emulując oficjalnego klienta Telegram Desktop, co utrzymuje stabilność sesji i zapobiega konfliktom wylogowania z innymi klientami.
- Przechowuje dowolne pliki jako **przesłania dzielone na części** w prywatnym kanale, omijając limity rozmiaru dla botów (do 2 GB na plik lub 4 GB z Telegram Premium).
- Tworzy lub ponownie wykorzystuje własny prywatny **kanał magazynu**, oznaczony konfigurowalnym sufiksem, tak że zawsze działa tylko na własnych kanałach.
- Odsyła pobrania strumieniowo, wyświetla listę przechowywanych elementów i wypisuje czytelny maszynowo JSON na stdout, co ułatwia tworzenie skryptów.

Zbudowany na [`gotd/td`](https://github.com/gotd/td) (czysty Go MTProto).

## Budowanie

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` usuwa symbole debugowania i tablice DWARF (z około 23 MB do 16 MB). Kompiluje się statycznie i skrośnie dla dowolnego celu (bez CGO), a te same statyczne pliki binarne Linuksa działają na Androidzie (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Rozmiar pliku binarnego

| Budowanie | Rozmiar (jedna architektura) |
|---|---|
| domyślnie (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| powyższe, następnie `upx --best --lzma` | ~5-6 MB |

Stos MTProto (`gotd/td` plus resolver z kamuflażem TLS naśladujący Telegram Desktop) stanowi większość rozmiaru. CI publikuje **skompresowane UPX** pliki binarne wydań dla każdego celu; UPX samorozpakowuje się przy starcie z pomijalnym narzutem. Jeśli wolisz nie dostarczać spakowanych plików binarnych, rozwiązaniem awaryjnym jest nieskompresowana kompilacja `-s -w`.

## Użycie

Każde polecenie wypisuje pojedynczy obiekt JSON na stdout (`"ok": true | false`).

| Polecenie | Przeznaczenie |
|---|---|
| `send-code --phone <number>` | Rozpocznij logowanie; Telegram wysyła kod logowania |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Dokończ logowanie |
| `check-auth` (alias `status`) | Zgłoś stan uwierzytelnienia |
| `init-storage [--title <title>]` | Utwórz lub ponownie wykorzystaj prywatny kanał magazynu |
| `upload --dir <path> [flags]` | Prześlij plik w częściach |
| `download [flags]` | Pobierz przechowywane archiwum |
| `list-remote` (alias `list-backups`) | Wyświetl listę przechowywanych elementów |
| `logout` | Usuń lokalną sesję |

## Konfiguracja (środowisko)

| Zmienna | Domyślnie | Znaczenie |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Katalog stanu (sesja, konfiguracja celu, logi) |
| `MTPROTO_STORE_TAG` | `MTPS` | Sufiks oznaczający kanały magazynu tego narzędzia |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Twój własny `api_id` z my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Twój własny `api_hash` |

**Uwaga o Warunkach korzystania z usługi:** wbudowane wartości domyślne emulują oficjalnego klienta Telegram Desktop. W przypadku własnych wdrożeń uzyskaj i ustaw własne `api_id` / `api_hash` pod adresem <https://my.telegram.org> oraz zapoznaj się z Warunkami korzystania z usługi Telegrama. Odpowiadasz za to, jak używasz swojego konta.

### Sesje i stan

Katalog stanu przechowuje wszystko, co narzędzie zachowuje między uruchomieniami, w `$MTPROTO_STORE_STATE`:

| Ścieżka | Zawartość |
|---|---|
| `creds/telegram.session` | uwierzytelniona **sesja** |
| `dests/telegram.json` | rozwiązane odniesienie do kanału magazynu |
| `staging/tg_auth.json` | krótkotrwały stan logowania (między `send-code` a `sign-in`) |
| `logs/progress-*.json` | postęp dla każdej operacji |

**Sesja to poufne poświadczenie**: każdy, kto może ją odczytać, kontroluje konto, bez pytania o hasło ani 2FA. Narzędzie tworzy katalog z uprawnieniami `0700` i zapisuje sesję z uprawnieniami `0600`, ale prawdziwą ochroną jest to, *gdzie* kierujesz `MTPROTO_STORE_STATE`. Trzymaj go w prywatnym magazynie. W szczególności na Androidzie preferuj magazyn **Credential-Encrypted** (np. pod `/data/misc_ce/<user>`), który jest odblokowywany dopiero po uwierzytelnieniu użytkownika, zamiast magazynu **Device-Encrypted** (np. `/data/adb`, odczytywalnego przed pierwszym odblokowaniem).

## Podziękowania

Rdzeń tego narzędzia został pierwotnie napisany przez **Ash ([@ash-iir](https://github.com/ash-iir))**, który zaprojektował oparty na skompilowanym MTProto klient magazynu, na którym jest ono zbudowane. Pełne uznanie za oryginalną pracę należy do jej autora. To repozytorium wyodrębnia, usuwa branding i uogólnia tę pracę w samodzielne, nadające się do ponownego użycia narzędzie.

## Zobacz także

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - przeglądalne, automatycznie aktualizowane archiwum prawdziwych danych `build.prop` z Pixeli.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - bot moderujący przeciw spamowi dla grup Telegrama.

## Licencja

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) i współtwórcy. Zobacz [LICENSE](LICENSE). Uruchamianie zmodyfikowanej wersji jako usługi sieciowej zobowiązuje cię do udostępnienia jej kodu źródłowego.

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
