[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | **ไทย** | [Українська](README.uk.md)

# mtproto-store

*ใช้ Telegram เป็นที่เก็บออบเจกต์แบบไม่จำกัดและแบ่งเป็นชิ้น - ผ่านโปรโตคอล MTProto ดั้งเดิม ในรูปแบบไฟล์ไบนารี CLI เดี่ยวที่สมบูรณ์ในตัว*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

ไม่ต้องใช้ Python ไม่ต้องใช้ bot API ไม่ต้องมีรันไทม์ภายนอก เป็นไฟล์ไบนารี Go แบบสแตติกไฟล์เดียวที่เข้าสู่ระบบบัญชีผู้ใช้ Telegram ผ่าน MTProto และจัดเก็บไฟล์ใดก็ได้เป็นการอัปโหลดแบบแบ่งชิ้นในแชนเนลส่วนตัว

## ทำอะไรได้บ้าง

- เข้าสู่ระบบ**บัญชีผู้ใช้** Telegram (หมายเลขโทรศัพท์ -> รหัสเข้าสู่ระบบ -> รหัสผ่าน 2FA ที่เป็นตัวเลือก) โดยจำลองไคลเอนต์ Telegram Desktop อย่างเป็นทางการ ซึ่งช่วยให้เซสชันเสถียรและหลีกเลี่ยงความขัดแย้งเรื่องการออกจากระบบกับไคลเอนต์อื่น
- จัดเก็บไฟล์ใดก็ได้เป็น**การอัปโหลดแบบแบ่งชิ้น**ในแชนเนลส่วนตัว โดยข้ามขีดจำกัดขนาดของบอต (สูงสุด 2 GB ต่อไฟล์ หรือ 4 GB เมื่อใช้ Telegram Premium)
- สร้างหรือใช้ซ้ำ**แชนเนลจัดเก็บ**ส่วนตัวของตัวเอง ซึ่งกำกับด้วยคำต่อท้ายที่กำหนดค่าได้ เพื่อให้แตะต้องเฉพาะแชนเนลของตัวเองเท่านั้น
- สตรีมการดาวน์โหลดกลับมา แสดงรายการที่จัดเก็บไว้ และพิมพ์ JSON ที่เครื่องอ่านได้ออกทาง stdout เพื่อให้เขียนสคริปต์ได้ง่าย

สร้างขึ้นบน [`gotd/td`](https://github.com/gotd/td) (MTProto แบบ Go ล้วน)

## การสร้าง

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` จะลบสัญลักษณ์ดีบักและตาราง DWARF ออก (ประมาณ 23 MB -> 16 MB) โดยสามารถคอมไพล์ข้ามแพลตฟอร์มแบบสแตติกสำหรับเป้าหมายใดก็ได้ (ไม่ใช้ CGO) และไฟล์ไบนารี Linux แบบสแตติกชุดเดียวกันก็ทำงานบน Android ได้ (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### ขนาดไฟล์ไบนารี

| การสร้าง | ขนาด (หนึ่งสถาปัตยกรรม) |
|---|---|
| ค่าเริ่มต้น (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| แบบข้างต้น แล้วตามด้วย `upx --best --lzma` | ~5-6 MB |

สแตก MTProto (`gotd/td` บวกกับตัวแก้ไข (resolver) พรางตัว TLS ที่เลียนแบบ Telegram Desktop) เป็นส่วนที่กินขนาดมากที่สุด CI เผยแพร่ไฟล์ไบนารีรีลีสที่**บีบอัดด้วย UPX** สำหรับทุกเป้าหมาย UPX จะคลายตัวเองเมื่อเริ่มทำงานโดยมีโอเวอร์เฮดที่แทบไม่สำคัญ หากคุณไม่ต้องการแจกจ่ายไฟล์ไบนารีที่แพ็กไว้ บิลด์ `-s -w` แบบไม่บีบอัดคือทางเลือกสำรอง

## การใช้งาน

ทุกคำสั่งจะพิมพ์ออบเจกต์ JSON เดียวออกทาง stdout (`"ok": true | false`)

| คำสั่ง | วัตถุประสงค์ |
|---|---|
| `send-code --phone <number>` | เริ่มการเข้าสู่ระบบ; Telegram จะส่งรหัสเข้าสู่ระบบ |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | ทำการเข้าสู่ระบบให้เสร็จสมบูรณ์ |
| `check-auth` (alias `status`) | รายงานสถานะการยืนยันตัวตน |
| `init-storage [--title <title>]` | สร้างหรือใช้ซ้ำแชนเนลจัดเก็บส่วนตัว |
| `upload --file <path> [flags]` | อัปโหลดไฟล์เป็นชิ้น ๆ |
| `download [flags]` | ดาวน์โหลดอาร์ไคฟ์ที่จัดเก็บไว้ |
| `list-remote` (alias `list-backups`) | แสดงรายการที่จัดเก็บไว้ |
| `logout` | ยกเลิกเซสชันในเครื่อง |

## การกำหนดค่า (สภาพแวดล้อม)

| ตัวแปร | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | ไดเรกทอรีสถานะ (เซสชัน, การกำหนดค่าปลายทาง, บันทึก) |
| `MTPROTO_STORE_TAG` | `MTPS` | คำต่อท้ายที่ทำเครื่องหมายแชนเนลจัดเก็บของเครื่องมือนี้ |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | `api_id` ของคุณเองจาก my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | `api_hash` ของคุณเอง |

**หมายเหตุเกี่ยวกับข้อกำหนดในการให้บริการ:** ค่าเริ่มต้นที่มีมาในตัวจะจำลองไคลเอนต์ Telegram Desktop อย่างเป็นทางการ สำหรับการใช้งานของคุณเอง โปรดขอและตั้งค่า `api_id` / `api_hash` ของคุณเองที่ <https://my.telegram.org> และทบทวนข้อกำหนดในการให้บริการของ Telegram คุณเป็นผู้รับผิดชอบต่อวิธีที่คุณใช้บัญชีของคุณ

### เซสชันและสถานะ

ไดเรกทอรีสถานะเก็บทุกอย่างที่เครื่องมือเก็บไว้ระหว่างการรันแต่ละครั้ง ภายใต้ `$MTPROTO_STORE_STATE`:

| เส้นทาง | เนื้อหา |
|---|---|
| `creds/telegram.session` | **เซสชัน**ที่ยืนยันตัวตนแล้ว |
| `dests/telegram.json` | การอ้างอิงแชนเนลจัดเก็บที่แปลงค่าแล้ว |
| `staging/tg_auth.json` | สถานะการเข้าสู่ระบบที่มีอายุสั้น (ระหว่าง `send-code` และ `sign-in`) |
| `logs/progress-*.json` | ความคืบหน้าต่อการดำเนินการ |

**เซสชันเป็นข้อมูลรับรองที่ละเอียดอ่อน**: ใครก็ตามที่อ่านมันได้จะควบคุมบัญชีได้ โดยไม่มีการถามรหัสผ่านหรือ 2FA เครื่องมือจะสร้างไดเรกทอรีเป็น `0700` และเขียนเซสชันเป็น `0600` แต่การป้องกันที่แท้จริงคือ*ตำแหน่ง*ที่คุณชี้ `MTPROTO_STORE_STATE` ไป เก็บไว้ในที่จัดเก็บส่วนตัว โดยเฉพาะบน Android ให้เลือกใช้ที่จัดเก็บแบบ **Credential-Encrypted** (เช่น ภายใต้ `/data/misc_ce/<user>`) ซึ่งจะปลดล็อกหลังจากผู้ใช้ยืนยันตัวตนแล้วเท่านั้น มากกว่าที่จัดเก็บแบบ **Device-Encrypted** (เช่น `/data/adb` ที่อ่านได้ก่อนการปลดล็อกครั้งแรก)

## เครดิต

แกนหลักของเครื่องมือนี้เดิมเขียนโดย **Ash ([@ash-iir](https://github.com/ash-iir))** ผู้ออกแบบไคลเอนต์จัดเก็บ MTProto แบบคอมไพล์ที่เครื่องมือนี้สร้างขึ้นบนฐานนั้น เครดิตทั้งหมดของผลงานต้นฉบับเป็นของผู้สร้าง ที่เก็บนี้ดึงเอา ลบแบรนด์ และทำให้ผลงานนั้นเป็นรูปแบบทั่วไป กลายเป็นเครื่องมือแบบสแตนด์อโลนที่นำกลับมาใช้ซ้ำได้

## ดูเพิ่มเติม

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - คลังข้อมูล `build.prop` ของ Pixel จริง ที่เรียกดูได้และอัปเดตอัตโนมัติ
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - บอตดูแลและป้องกันสแปมสำหรับกลุ่ม Telegram

## สัญญาอนุญาต

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) และผู้มีส่วนร่วม ดู [LICENSE](LICENSE) การรันเวอร์ชันที่แก้ไขแล้วเป็นบริการเครือข่ายทำให้คุณมีหน้าที่ต้องเสนอซอร์สโค้ดของมัน

## ติดต่อ

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
