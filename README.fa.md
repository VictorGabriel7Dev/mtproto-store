[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | **فارسی** | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*از Telegram به عنوان یک فضای ذخیره‌سازی شیءگرای نامحدود و تکه‌تکه (chunked) استفاده کنید - از طریق پروتکل بومی MTProto، به صورت یک باینری CLI مستقل و خودبسنده.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

نه Python، نه bot API و نه هیچ محیط اجرای خارجی. یک باینری ایستای Go واحد که از طریق MTProto به یک حساب کاربری Telegram وارد می‌شود و فایل‌های دلخواه را به صورت آپلودهای تکه‌تکه در یک کانال خصوصی ذخیره می‌کند.

## چه کاری انجام می‌دهد

- به یک **حساب کاربری** Telegram وارد می‌شود (شماره تلفن -> کد ورود -> رمز اختیاری ۲ مرحله‌ای)، و کلاینت رسمی Telegram Desktop را شبیه‌سازی می‌کند که نشست‌ها را پایدار نگه می‌دارد و از تداخل خروج با سایر کلاینت‌ها جلوگیری می‌کند.
- فایل‌های دلخواه را به صورت **آپلودهای تکه‌تکه** در یک کانال خصوصی ذخیره می‌کند و محدودیت‌های حجمی bot را دور می‌زند (تا ۲ گیگابایت برای هر فایل، یا ۴ گیگابایت با Telegram Premium).
- **کانال ذخیره‌سازی** خصوصی خودش را می‌سازد یا دوباره استفاده می‌کند، که با یک پسوند قابل‌پیکربندی برچسب‌گذاری شده است، بنابراین همیشه تنها با کانال‌های خودش سروکار دارد.
- دانلودها را به صورت جریانی بازمی‌گرداند، موارد ذخیره‌شده را فهرست می‌کند و برای سهولت اسکریپت‌نویسی، JSON قابل‌خواندن توسط ماشین را روی stdout چاپ می‌کند.

ساخته‌شده بر پایهٔ [`gotd/td`](https://github.com/gotd/td) (پیاده‌سازی MTProto به صورت کاملاً Go).

## ساخت (Build)

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` نمادهای اشکال‌زدایی و جداول DWARF را حذف می‌کند (حدود ۲۳ مگابایت -> ۱۶ مگابایت). این دستور به صورت ایستا برای هر هدفی کراس‌کامپایل می‌شود (بدون CGO)، و همان باینری‌های ایستای Linux روی Android هم اجرا می‌شوند (arm64-v8a، armeabi-v7a، x86_64، x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### اندازهٔ باینری

| ساخت | اندازه (یک معماری) |
|---|---|
| پیش‌فرض (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| مورد بالا، سپس `upx --best --lzma` | ~5-6 MB |

پشتهٔ MTProto (یعنی `gotd/td` به علاوهٔ یک تحلیل‌گر استتار TLS که Telegram Desktop را تقلید می‌کند) بخش عمدهٔ حجم را تشکیل می‌دهد. CI برای هر هدف باینری‌های انتشار **فشرده‌شده با UPX** را منتشر می‌کند؛ UPX هنگام راه‌اندازی خودش را با سرباری ناچیز باز می‌کند. اگر ترجیح می‌دهید باینری‌های بسته‌بندی‌شده را توزیع نکنید، ساخت فشرده‌نشدهٔ `-s -w` گزینهٔ جایگزین است.

## استفاده

هر فرمان یک شیء JSON واحد را روی stdout چاپ می‌کند (`"ok": true | false`).

| فرمان | هدف |
|---|---|
| `send-code --phone <number>` | آغاز ورود؛ Telegram کد ورود را می‌فرستد |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | تکمیل ورود |
| `check-auth` (نام مستعار `status`) | گزارش وضعیت احراز هویت |
| `init-storage [--title <title>]` | ساخت یا استفادهٔ دوباره از کانال ذخیره‌سازی خصوصی |
| `upload --file <path> [flags]` | آپلود یک فایل به صورت تکه‌تکه |
| `download [flags]` | دانلود یک آرشیو ذخیره‌شده |
| `list-remote` (نام مستعار `list-backups`) | فهرست‌کردن موارد ذخیره‌شده |
| `logout` | کنارگذاشتن نشست محلی |

## پیکربندی (متغیرهای محیطی)

| متغیر | پیش‌فرض | معنی |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | پوشهٔ وضعیت (نشست، پیکربندی مقصد، لاگ‌ها) |
| `MTPROTO_STORE_TAG` | `MTPS` | پسوندی که کانال‌های ذخیره‌سازی این ابزار را نشانه‌گذاری می‌کند |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | `api_id` شخصی شما از my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | `api_hash` شخصی شما |

**نکتهٔ مربوط به شرایط خدمات:** مقادیر پیش‌فرض داخلی، کلاینت رسمی Telegram Desktop را شبیه‌سازی می‌کنند. برای استقرارهای خودتان، `api_id` / `api_hash` شخصی خود را در <https://my.telegram.org> دریافت و تنظیم کنید و شرایط خدمات Telegram را مرور کنید. شما مسئول نحوهٔ استفاده از حساب خود هستید.

### نشست‌ها و وضعیت

پوشهٔ وضعیت هر چیزی را که ابزار بین اجراها نگه می‌دارد، در زیر `$MTPROTO_STORE_STATE` ذخیره می‌کند:

| مسیر | محتوا |
|---|---|
| `creds/telegram.session` | **نشست** احراز هویت‌شده |
| `dests/telegram.json` | ارجاع تفکیک‌شدهٔ کانال ذخیره‌سازی |
| `staging/tg_auth.json` | وضعیت کوتاه‌عمر ورود (بین `send-code` و `sign-in`) |
| `logs/progress-*.json` | پیشرفت به ازای هر عملیات |

**نشست یک اعتبارنامهٔ حساس است**: هر کسی که بتواند آن را بخواند، بدون هیچ درخواست رمز یا ۲ مرحله‌ای، حساب را در کنترل می‌گیرد. ابزار پوشه را با `0700` می‌سازد و نشست را با `0600` می‌نویسد، اما محافظت واقعی به این بستگی دارد که `MTPROTO_STORE_STATE` را به *کجا* اشاره می‌دهید. آن را روی فضای ذخیره‌سازی خصوصی نگه دارید. به‌طور خاص در Android، فضای ذخیره‌سازی **رمزنگاری‌شده با اعتبارنامه (Credential-Encrypted)** را (برای نمونه زیر `/data/misc_ce/<user>`) که تنها پس از احراز هویت کاربر باز می‌شود، به فضای ذخیره‌سازی **رمزنگاری‌شده با دستگاه (Device-Encrypted)** (برای نمونه `/data/adb` که پیش از نخستین باز شدن قفل هم قابل‌خواندن است) ترجیح دهید.

## سپاسگزاری

هستهٔ این ابزار در اصل توسط **Ash ([@ash-iir](https://github.com/ash-iir))** نوشته شده است، کسی که کلاینت ذخیره‌سازی کامپایل‌شدهٔ MTProto را که این ابزار بر پایهٔ آن ساخته شده طراحی کرد. تمام اعتبارِ کار اصلی به نویسندهٔ آن تعلق دارد. این مخزن آن کار را استخراج، از نشان تجاری پاک و به یک ابزار مستقل و قابل‌استفادهٔ دوباره تعمیم می‌دهد.

## همچنین ببینید

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - یک آرشیو قابل‌مرور و به‌طور خودکار به‌روزرسانی‌شده از دادهٔ واقعی `build.prop` دستگاه‌های Pixel.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - یک bot مدیریتی ضد هرزنامه برای گروه‌های Telegram.

## مجوز

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) و مشارکت‌کنندگان. به [LICENSE](LICENSE) مراجعه کنید. اجرای یک نسخهٔ تغییریافته به عنوان یک سرویس شبکه‌ای، شما را موظف می‌کند که کد منبع آن را ارائه دهید.

## تماس

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
