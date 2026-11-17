[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | **Українська**

# mtproto-store

*Використовуйте Telegram як безлімітне об'єктне сховище з розбиттям на частини - через нативний протокол MTProto, у вигляді єдиного самодостатнього CLI-бінарника.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Без Python, без bot API, без зовнішнього середовища виконання. Єдиний статичний Go-бінарник, який входить до користувацького акаунта Telegram через MTProto і зберігає довільні файли в приватному каналі у вигляді завантажень, розбитих на частини.

## Що він робить

- Входить до **користувацького акаунта** Telegram (номер телефону -> код входу -> необов'язковий пароль 2FA), емулюючи офіційний клієнт Telegram Desktop, що зберігає стабільність сесій і запобігає конфліктам виходу з іншими клієнтами.
- Зберігає довільні файли у вигляді **завантажень, розбитих на частини**, у приватному каналі, обходячи обмеження на розмір для ботів (до 2 ГБ на файл, або 4 ГБ з Telegram Premium).
- Створює або повторно використовує власний приватний **канал сховища**, позначений налаштовуваним суфіксом, тож він працює лише зі своїми каналами.
- Віддає завантаження потоком назад, виводить список збережених елементів і друкує машиночитаний JSON у stdout для зручного написання скриптів.

Побудований на [`gotd/td`](https://github.com/gotd/td) (чистий Go MTProto).

## Збірка

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` видаляє налагоджувальні символи і таблиці DWARF (приблизно з 23 МБ до 16 МБ). Він статично крос-компілюється під будь-яку ціль (без CGO), і ті самі статичні Linux-бінарники працюють на Android (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Розмір бінарника

| Збірка | Розмір (одна архітектура) |
|---|---|
| за замовчуванням (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| те саме, потім `upx --best --lzma` | ~5-6 MB |

Стек MTProto (`gotd/td` плюс резолвер з TLS-камуфляжем, що імітує Telegram Desktop) становить основну частину розміру. CI публікує **стиснуті UPX** релізні бінарники для кожної цілі; UPX самостійно розпаковується під час запуску з незначними накладними витратами. Якщо ви волієте не постачати запаковані бінарники, запасним варіантом є нестиснена збірка `-s -w`.

## Використання

Кожна команда друкує один об'єкт JSON у stdout (`"ok": true | false`).

| Команда | Призначення |
|---|---|
| `send-code --phone <number>` | Розпочати вхід; Telegram надсилає код входу |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Завершити вхід |
| `check-auth` (alias `status`) | Повідомити стан автентифікації |
| `init-storage [--title <title>]` | Створити або повторно використати приватний канал сховища |
| `upload --dir <path> [flags]` | Вивантажити файл частинами |
| `download [flags]` | Завантажити збережений архів |
| `list-remote` (alias `list-backups`) | Вивести список збережених елементів |
| `logout` | Видалити локальну сесію |

## Конфігурація (середовище)

| Змінна | За замовчуванням | Значення |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Каталог стану (сесія, конфігурація призначення, логи) |
| `MTPROTO_STORE_TAG` | `MTPS` | Суфікс, що позначає канали сховища цього інструмента |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Ваш власний `api_id` з my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Ваш власний `api_hash` |

**Примітка щодо Умов надання послуг:** вбудовані значення за замовчуванням емулюють офіційний клієнт Telegram Desktop. Для власних розгортань отримайте і задайте власні `api_id` / `api_hash` на <https://my.telegram.org> та ознайомтеся з Умовами надання послуг Telegram. Ви несете відповідальність за те, як використовуєте свій акаунт.

### Сесії та стан

Каталог стану містить усе, що інструмент зберігає між запусками, у `$MTPROTO_STORE_STATE`:

| Шлях | Вміст |
|---|---|
| `creds/telegram.session` | автентифікована **сесія** |
| `dests/telegram.json` | розв'язане посилання на канал сховища |
| `staging/tg_auth.json` | короткочасний стан входу (між `send-code` та `sign-in`) |
| `logs/progress-*.json` | прогрес за кожною операцією |

**Сесія - це конфіденційні облікові дані**: будь-хто, хто може її прочитати, керує акаунтом, без запиту пароля чи 2FA. Інструмент створює каталог з правами `0700` і записує сесію з правами `0600`, але справжній захист - у тому, *куди* ви спрямовуєте `MTPROTO_STORE_STATE`. Тримайте його у приватному сховищі. Зокрема, на Android віддавайте перевагу сховищу **Credential-Encrypted** (наприклад, під `/data/misc_ce/<user>`), яке розблоковується лише після автентифікації користувача, а не сховищу **Device-Encrypted** (наприклад, `/data/adb`, яке читається до першого розблокування).

## Подяки

Основу цього інструмента спочатку створив **Ash ([@ash-iir](https://github.com/ash-iir))**, який спроектував клієнт сховища на скомпільованому MTProto, що лежить у його основі. Уся заслуга за оригінальну роботу належить її авторові. Цей репозиторій видобуває, прибирає брендинг і узагальнює цю роботу в самостійний, придатний для повторного використання інструмент.

## Дивіться також

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - переглядуваний, автоматично оновлюваний архів справжніх даних `build.prop` для Pixel.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - бот-модератор проти спаму для груп Telegram.

## Ліцензія

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) та учасники. Див. [LICENSE](LICENSE). Запуск зміненої версії як мережевого сервісу зобов'язує вас надати її вихідний код.

## Контакти

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
