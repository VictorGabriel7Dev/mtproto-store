[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | **Bahasa Indonesia** | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Gunakan Telegram sebagai penyimpanan objek tanpa batas berbasis potongan - melalui protokol MTProto native, sebagai satu biner CLI mandiri.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Tanpa Python, tanpa API bot, tanpa runtime eksternal. Satu biner Go statis yang masuk ke akun pengguna Telegram melalui MTProto dan menyimpan berkas sembarang sebagai unggahan berpotongan di kanal privat.

## Apa fungsinya

- Masuk ke **akun pengguna** Telegram (nomor telepon -> kode login -> kata sandi 2FA opsional), meniru klien resmi Telegram Desktop, yang menjaga sesi tetap stabil dan menghindari konflik logout dengan klien lain.
- Menyimpan berkas sembarang sebagai **unggahan berpotongan** di kanal privat, melewati batas ukuran bot (hingga 2 GB per berkas, atau 4 GB dengan Telegram Premium).
- Membuat atau menggunakan kembali **kanal penyimpanan** privatnya sendiri, ditandai dengan sufiks yang dapat dikonfigurasi sehingga hanya menyentuh kanalnya sendiri.
- Mengalirkan kembali unduhan, menampilkan daftar item tersimpan, dan mencetak JSON yang dapat dibaca mesin ke stdout untuk memudahkan skrip.

Dibangun di atas [`gotd/td`](https://github.com/gotd/td) (MTProto murni Go).

## Membangun

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` menghapus simbol debug dan tabel DWARF (sekitar 23 MB -> 16 MB). Ini melakukan kompilasi silang secara statis untuk target apa pun (tanpa CGO), dan biner Linux statis yang sama berjalan di Android (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Ukuran biner

| Build | Ukuran (satu arsitektur) |
|---|---|
| bawaan (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| di atas, lalu `upx --best --lzma` | ~5-6 MB |

Stack MTProto (`gotd/td` ditambah resolver kamuflase TLS yang meniru Telegram Desktop) adalah bagian terbesar dari ukurannya. CI menerbitkan biner rilis **terkompresi UPX** untuk setiap target; UPX mengekstrak dirinya sendiri saat startup dengan overhead yang dapat diabaikan. Jika Anda lebih suka tidak mendistribusikan biner yang dikemas, build `-s -w` tanpa kompresi adalah cadangannya.

## Penggunaan

Setiap perintah mencetak satu objek JSON ke stdout (`"ok": true | false`).

| Perintah | Tujuan |
|---|---|
| `send-code --phone <number>` | Mulai login; Telegram mengirim kode login |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Selesaikan login |
| `bot-login --token <token>` | Masuk sebagai bot (terbatas) |
| `check-auth` (alias `status`) | Laporkan status autentikasi |
| `init-storage [--title <title>] [--channel-id <id>]` | Buat atau gunakan kembali kanal penyimpanan privat |
| `upload --dir <path> [flags]` | Mengunggah berkas dalam direktori sebagai potongan |
| `download [flags]` | Unduh arsip tersimpan |
| `delete --ref <id>[,<id>...]` | Menghapus satu atau beberapa item tersimpan |
| `list-remote` (alias `list-backups`) | Tampilkan daftar item tersimpan |
| `logout` | Lepaskan sesi lokal |

## Konfigurasi (lingkungan)

| Variabel | Bawaan | Arti |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Direktori status (sesi, konfigurasi tujuan, log) |
| `MTPROTO_STORE_TAG` | `MTPS` | Sufiks yang menandai kanal penyimpanan alat ini |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | `api_id` Anda sendiri dari my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | `api_hash` Anda sendiri |

**Catatan Ketentuan Layanan:** nilai bawaan yang tertanam meniru klien resmi Telegram Desktop. Untuk penerapan Anda sendiri, dapatkan dan atur `api_id` / `api_hash` Anda sendiri di <https://my.telegram.org> dan tinjau Ketentuan Layanan Telegram. Anda bertanggung jawab atas cara Anda menggunakan akun Anda.

### Sesi dan status

Direktori status menyimpan semua yang disimpan alat ini di antara proses, di bawah `$MTPROTO_STORE_STATE`:

| Jalur | Isi |
|---|---|
| `creds/telegram.session` | **sesi** yang terautentikasi |
| `dests/telegram.json` | referensi kanal penyimpanan yang telah diselesaikan |
| `staging/tg_auth.json` | status login berumur pendek (antara `send-code` dan `sign-in`) |
| `logs/progress-*.json` | kemajuan per operasi |

**Sesi adalah kredensial sensitif**: siapa pun yang dapat membacanya mengendalikan akun, tanpa prompt kata sandi atau 2FA. Alat ini membuat direktori `0700` dan menulis sesi `0600`, tetapi perlindungan yang sebenarnya adalah *di mana* Anda mengarahkan `MTPROTO_STORE_STATE`. Simpan di penyimpanan privat. Khususnya di Android, utamakan penyimpanan **Credential-Encrypted** (mis. di bawah `/data/misc_ce/<user>`), yang hanya terbuka setelah pengguna melakukan autentikasi, daripada penyimpanan **Device-Encrypted** (mis. `/data/adb`, yang dapat dibaca sebelum pembukaan kunci pertama).

## Kredit

Inti dari alat ini awalnya ditulis oleh **Ash ([@ash-iir](https://github.com/ash-iir))**, yang merancang klien penyimpanan MTProto terkompilasi yang menjadi dasarnya. Seluruh penghargaan atas karya asli diberikan kepada penulisnya. Repositori ini mengekstrak, menghapus merek, dan menggeneralisasi karya tersebut menjadi alat mandiri yang dapat digunakan kembali.

## Lihat juga

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - arsip data `build.prop` Pixel asli yang dapat dijelajahi dan diperbarui otomatis.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - bot moderasi antispam untuk grup Telegram.

## Lisensi

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) dan kontributor. Lihat [LICENSE](LICENSE). Menjalankan versi yang dimodifikasi sebagai layanan jaringan mewajibkan Anda menawarkan sumbernya.

## Kontak

- https://victorgabriel.dev
- *GitHub:* @VictorGabriel7Dev https://github.com/VictorGabriel7Dev
- *Telegram:* @VictorGabriel_Dev https://t.me/VictorGabriel_Dev
- *Discord:* @VictorGabriel.dev https://discord.com/users/1481407654458036265
- *LinkedIn:* in/victorgabriel-dev https://www.linkedin.com/in/victorgabriel-dev
- *Instagram:* @VictorGabriel_Dev https://www.instagram.com/VictorGabriel_Dev
- *WhatsApp:* @VictorGabriel_Dev https://wa.me/@VictorGabriel_Dev
- *E-mail:* contato@victorgabriel.dev

---

`telegram` `mtproto` `gotd` `cloud-storage` `object-storage` `unlimited-storage` `cli` `golang` `static-binary` `cross-platform` `self-hosted` `file-storage` `chunked-upload` `mtproto-store`
