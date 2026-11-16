[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | **العربية** | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*استخدم Telegram بوصفه مساحة تخزين كائنات غير محدودة ومجزأة (chunked) - عبر بروتوكول MTProto الأصلي، كملف تنفيذي واحد ومكتفٍ ذاتيًا لواجهة سطر الأوامر (CLI).*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

لا Python، ولا bot API، ولا أي بيئة تشغيل خارجية. ملف تنفيذي ثابت (static) واحد مكتوب بلغة Go يسجّل الدخول إلى حساب مستخدم على Telegram عبر MTProto ويخزّن ملفات اعتباطية على هيئة رفعات مجزأة في قناة خاصة.

## ماذا يفعل

- يسجّل الدخول إلى **حساب مستخدم** على Telegram (رقم الهاتف -> رمز الدخول -> كلمة مرور اختيارية للمصادقة الثنائية 2FA)، مع محاكاة عميل Telegram Desktop الرسمي، مما يبقي الجلسات مستقرة ويتجنّب تعارضات تسجيل الخروج مع العملاء الآخرين.
- يخزّن ملفات اعتباطية على هيئة **رفعات مجزأة** في قناة خاصة، متجاوزًا حدود الحجم الخاصة بالـ bot (حتى 2 غيغابايت لكل ملف، أو 4 غيغابايت مع Telegram Premium).
- ينشئ أو يعيد استخدام **قناة تخزين** خاصة به، موسومة بلاحقة قابلة للتهيئة، بحيث لا يتعامل أبدًا إلا مع قنواته الخاصة.
- يعيد تدفق التنزيلات، ويسرد العناصر المخزَّنة، ويطبع JSON قابلًا للقراءة آليًا على stdout لتسهيل كتابة السكربتات.

مبني على [`gotd/td`](https://github.com/gotd/td) (تنفيذ MTProto بلغة Go خالصة).

## البناء (Build)

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

يقوم `-ldflags="-s -w" -trimpath` بإزالة رموز التنقيح وجداول DWARF (نحو 23 ميغابايت -> 16 ميغابايت). وهو يُترجم تقاطعيًا بشكل ثابت لأي هدف (بدون CGO)، وتعمل الملفات التنفيذية الثابتة نفسها الخاصة بـ Linux على Android (arm64-v8a، armeabi-v7a، x86_64، x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### حجم الملف التنفيذي

| البناء | الحجم (معمارية واحدة) |
|---|---|
| الافتراضي (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| ما سبق، ثم `upx --best --lzma` | ~5-6 MB |

تشكّل حزمة MTProto (أي `gotd/td` إضافةً إلى محلّل تمويه TLS يحاكي Telegram Desktop) الجزء الأكبر من الحجم. يَنشر نظام التكامل المستمر (CI) ملفات إصدار تنفيذية **مضغوطة بـ UPX** لكل هدف؛ ويفكّ UPX ضغط نفسه ذاتيًا عند بدء التشغيل بعبء لا يُذكر. وإذا كنت تفضّل عدم توزيع ملفات تنفيذية مضغوطة، فإن بناء `-s -w` غير المضغوط هو البديل.

## الاستخدام

يطبع كل أمر كائن JSON واحدًا على stdout (`"ok": true | false`).

| الأمر | الغرض |
|---|---|
| `send-code --phone <number>` | بدء تسجيل الدخول؛ يرسل Telegram رمز الدخول |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | إكمال تسجيل الدخول |
| `check-auth` (الاسم البديل `status`) | الإبلاغ عن حالة المصادقة |
| `init-storage [--title <title>]` | إنشاء قناة التخزين الخاصة أو إعادة استخدامها |
| `upload --file <path> [flags]` | رفع ملف على هيئة أجزاء |
| `download [flags]` | تنزيل أرشيف مخزَّن |
| `list-remote` (الاسم البديل `list-backups`) | سرد العناصر المخزَّنة |
| `logout` | إسقاط الجلسة المحلية |

## التهيئة (متغيرات البيئة)

| المتغير | الافتراضي | المعنى |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | دليل الحالة (الجلسة، تهيئة الوجهة، السجلات) |
| `MTPROTO_STORE_TAG` | `MTPS` | اللاحقة التي تَسِم قنوات التخزين الخاصة بهذه الأداة |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | `api_id` الخاص بك من my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | `api_hash` الخاص بك |

**ملاحظة بخصوص شروط الخدمة:** تحاكي القيم الافتراضية المدمجة عميل Telegram Desktop الرسمي. ولعمليات النشر الخاصة بك، احصل على `api_id` / `api_hash` الخاص بك واضبطه على <https://my.telegram.org> وراجع شروط خدمة Telegram. أنت المسؤول عن كيفية استخدامك لحسابك.

### الجلسات والحالة

يحتفظ دليل الحالة بكل ما تبقيه الأداة بين عمليات التشغيل، تحت `$MTPROTO_STORE_STATE`:

| المسار | المحتوى |
|---|---|
| `creds/telegram.session` | **الجلسة** المصادَق عليها |
| `dests/telegram.json` | مرجع قناة التخزين الذي تم حلّه |
| `staging/tg_auth.json` | حالة دخول قصيرة العمر (بين `send-code` و `sign-in`) |
| `logs/progress-*.json` | تقدّم كل عملية على حدة |

**الجلسة بيانات اعتماد حساسة**: فأي شخص يستطيع قراءتها يتحكم في الحساب، دون أي مطالبة بكلمة مرور أو مصادقة ثنائية. تنشئ الأداة الدليل بالصلاحية `0700` وتكتب الجلسة بالصلاحية `0600`، لكن الحماية الحقيقية تكمن في *أين* توجّه `MTPROTO_STORE_STATE`. احتفظ بها على مساحة تخزين خاصة. وعلى Android تحديدًا، فضّل التخزين **المشفَّر ببيانات الاعتماد (Credential-Encrypted)** (مثلًا تحت `/data/misc_ce/<user>`)، الذي لا يُفتَح إلا بعد مصادقة المستخدم، على التخزين **المشفَّر بالجهاز (Device-Encrypted)** (مثل `/data/adb`، القابل للقراءة قبل أول فتح للقفل).

## شكر وتقدير

كُتب جوهر هذه الأداة في الأصل على يد **Ash ([@ash-iir](https://github.com/ash-iir))**، الذي صمّم عميل تخزين MTProto المُترجَم الذي بُنيت عليه. والفضل الكامل في العمل الأصلي يعود إلى مؤلفه. ويستخرج هذا المستودع ذلك العمل ويجرّده من العلامة التجارية ويعمّمه ليصبح أداة مستقلة وقابلة لإعادة الاستخدام.

## انظر أيضًا

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - أرشيف قابل للتصفح ومُحدَّث تلقائيًا لبيانات `build.prop` حقيقية من أجهزة Pixel.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - bot لإشراف مكافحة البريد المزعج لمجموعات Telegram.

## الترخيص

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) والمساهمون. انظر [LICENSE](LICENSE). إن تشغيل نسخة معدَّلة كخدمة شبكية يُلزمك بتقديم شِفرتها المصدرية.

## التواصل

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
