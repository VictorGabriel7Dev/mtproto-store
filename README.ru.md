[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | **Русский** | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Используйте Telegram как безлимитное объектное хранилище с разбиением на части - через нативный протокол MTProto, в виде единого самодостаточного CLI-бинарника.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Без Python, без bot API, без внешней среды выполнения. Единый статический Go-бинарник, который входит в пользовательский аккаунт Telegram по MTProto и хранит произвольные файлы в приватном канале в виде загрузок, разбитых на части.

## Что он делает

- Входит в **пользовательский аккаунт** Telegram (номер телефона -> код входа -> необязательный пароль 2FA), эмулируя официальный клиент Telegram Desktop, что сохраняет стабильность сессий и предотвращает конфликты выхода с другими клиентами.
- Хранит произвольные файлы в виде **загрузок, разбитых на части**, в приватном канале, обходя ограничения на размер для ботов (до 2 ГБ на файл, или 4 ГБ с Telegram Premium).
- Создаёт или повторно использует собственный приватный **канал хранилища**, помеченный настраиваемым суффиксом, так что он работает только со своими каналами.
- Отдаёт загрузки потоком обратно, выводит список сохранённых элементов и печатает машиночитаемый JSON в stdout для удобного написания скриптов.

Построен на [`gotd/td`](https://github.com/gotd/td) (чистый Go MTProto).

## Сборка

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` удаляет отладочные символы и таблицы DWARF (примерно с 23 МБ до 16 МБ). Он статически кросс-компилируется под любую цель (без CGO), и те же статические Linux-бинарники работают на Android (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Размер бинарника

| Сборка | Размер (одна архитектура) |
|---|---|
| по умолчанию (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| то же, затем `upx --best --lzma` | ~5-6 MB |

Стек MTProto (`gotd/td` плюс резолвер с TLS-камуфляжем, имитирующий Telegram Desktop) составляет основную часть размера. CI публикует **сжатые UPX** релизные бинарники для каждой цели; UPX самораспаковывается при запуске с пренебрежимо малыми накладными расходами. Если вы предпочитаете не поставлять упакованные бинарники, запасным вариантом служит несжатая сборка `-s -w`.

## Использование

Каждая команда печатает один JSON-объект в stdout (`"ok": true | false`).

| Команда | Назначение |
|---|---|
| `send-code --phone <number>` | Начать вход; Telegram отправляет код входа |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Завершить вход |
| `bot-login --token <token>` | Вход как бот (ограниченно) |
| `check-auth` (alias `status`) | Сообщить состояние аутентификации |
| `init-storage [--title <title>] [--channel-id <id>]` | Создать или повторно использовать приватный канал хранилища |
| `upload --dir <path> [flags]` | Загружает файлы из каталога по частям |
| `download [flags]` | Скачать сохранённый архив |
| `delete --ref <id>[,<id>...]` | Удаляет один или несколько сохранённых элементов |
| `list-remote` (alias `list-backups`) | Вывести список сохранённых элементов |
| `logout` | Удалить локальную сессию |

## Конфигурация (окружение)

| Переменная | По умолчанию | Значение |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Каталог состояния (сессия, конфигурация назначения, логи) |
| `MTPROTO_STORE_TAG` | `MTPS` | Суффикс, помечающий каналы хранилища этого инструмента |
| `MTPROTO_STORE_LABEL` | - | Необязательное имя, сохраняемое как `label` в метаданных каждого загруженного элемента (возвращается в `list-remote`) |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Ваш собственный `api_id` с my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Ваш собственный `api_hash` |

**Примечание об Условиях обслуживания:** встроенные значения по умолчанию эмулируют официальный клиент Telegram Desktop. Для собственных развёртываний получите и задайте свои `api_id` / `api_hash` на <https://my.telegram.org> и ознакомьтесь с Условиями обслуживания Telegram. Вы несёте ответственность за то, как используете свой аккаунт.

### Сессии и состояние

Каталог состояния содержит всё, что инструмент сохраняет между запусками, в `$MTPROTO_STORE_STATE`:

| Путь | Содержимое |
|---|---|
| `creds/telegram.session` | аутентифицированная **сессия** |
| `dests/telegram.json` | разрешённая ссылка на канал хранилища |
| `staging/tg_auth.json` | кратковременное состояние входа (между `send-code` и `sign-in`) |
| `logs/progress-*.json` | прогресс по каждой операции |

**Сессия - это конфиденциальные учётные данные**: любой, кто может её прочитать, управляет аккаунтом, без запроса пароля или 2FA. Инструмент создаёт каталог с правами `0700` и записывает сессию с правами `0600`, но реальная защита - в том, *куда* вы направляете `MTPROTO_STORE_STATE`. Храните его в приватном хранилище. В частности, на Android предпочитайте хранилище **Credential-Encrypted** (например, под `/data/misc_ce/<user>`), которое разблокируется только после аутентификации пользователя, вместо хранилища **Device-Encrypted** (например, `/data/adb`, читаемого до первой разблокировки).

## Благодарности

Основа этого инструмента изначально создана **Ash ([@ash-iir](https://github.com/ash-iir))**, который спроектировал клиент хранилища на скомпилированном MTProto, лежащий в его основе. Все заслуги за оригинальную работу принадлежат её автору. Этот репозиторий извлекает, устраняет брендинг и обобщает эту работу в самостоятельный, переиспользуемый инструмент.

## Смотрите также

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - просматриваемый, автоматически обновляемый архив настоящих данных `build.prop` для Pixel.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - бот-модератор против спама для групп Telegram.

## Лицензия

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) и участники. См. [LICENSE](LICENSE). Запуск изменённой версии в качестве сетевого сервиса обязывает вас предоставить её исходный код.

## Контакты

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
