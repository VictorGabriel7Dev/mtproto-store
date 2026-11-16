[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | **Türkçe** | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Telegram'ı sınırsız, parçalı nesne depolaması olarak kullanın - yerel MTProto protokolü üzerinden, tek ve kendi kendine yeten bir CLI ikili dosyası olarak.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Python yok, bot API yok, harici çalışma zamanı yok. MTProto üzerinden bir Telegram kullanıcı hesabına giriş yapan ve rastgele dosyaları özel bir kanalda parçalı yüklemeler olarak depolayan tek bir statik Go ikili dosyası.

## Ne yapar

- Bir Telegram **kullanıcı hesabına** giriş yapar (telefon numarası -> giriş kodu -> isteğe bağlı 2FA parolası) ve resmi Telegram Desktop istemcisini taklit eder; bu, oturumları kararlı tutar ve diğer istemcilerle oturum kapatma çakışmalarını önler.
- Rastgele dosyaları özel bir kanalda **parçalı yüklemeler** olarak depolar ve bot boyut sınırlarını aşar (dosya başına 2 GB'a kadar veya Telegram Premium ile 4 GB'a kadar).
- Kendi özel **depolama kanalını** oluşturur veya yeniden kullanır; yalnızca kendi kanallarına dokunacak şekilde yapılandırılabilir bir sonekle etiketlenir.
- İndirmeleri geri akışla aktarır, depolanan öğeleri listeler ve kolay betik yazımı için stdout'a makine tarafından okunabilir JSON yazar.

[`gotd/td`](https://github.com/gotd/td) (saf Go MTProto) üzerine kurulmuştur.

## Derleme

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath`, hata ayıklama sembollerini ve DWARF tablolarını kaldırır (yaklaşık 23 MB -> 16 MB). Herhangi bir hedef için statik olarak çapraz derlenir (CGO yok) ve aynı statik Linux ikili dosyaları Android'de çalışır (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### İkili dosya boyutu

| Derleme | Boyut (tek mimari) |
|---|---|
| varsayılan (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| yukarıdaki, ardından `upx --best --lzma` | ~5-6 MB |

MTProto yığını (`gotd/td` artı Telegram Desktop'u taklit eden bir TLS kamuflaj çözücüsü) boyutun büyük bölümünü oluşturur. CI, her hedef için **UPX ile sıkıştırılmış** sürüm ikili dosyaları yayımlar; UPX, ihmal edilebilir bir ek yükle başlangıçta kendini açar. Paketlenmiş ikili dosyalar dağıtmamayı tercih ederseniz, sıkıştırılmamış `-s -w` derlemesi yedek seçenektir.

## Kullanım

Her komut, stdout'a tek bir JSON nesnesi yazar (`"ok": true | false`).

| Komut | Amaç |
|---|---|
| `send-code --phone <number>` | Girişi başlat; Telegram giriş kodunu gönderir |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Girişi tamamla |
| `check-auth` (alias `status`) | Kimlik doğrulama durumunu bildir |
| `init-storage [--title <title>]` | Özel depolama kanalını oluştur veya yeniden kullan |
| `upload --file <path> [flags]` | Bir dosyayı parçalar hâlinde yükle |
| `download [flags]` | Depolanan bir arşivi indir |
| `list-remote` (alias `list-backups`) | Depolanan öğeleri listele |
| `logout` | Yerel oturumu bırak |

## Yapılandırma (ortam)

| Değişken | Varsayılan | Anlamı |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Durum dizini (oturum, hedef yapılandırması, günlükler) |
| `MTPROTO_STORE_TAG` | `MTPS` | Bu aracın depolama kanallarını işaretleyen sonek |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | my.telegram.org adresinden kendi `api_id` değeriniz |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Kendi `api_hash` değeriniz |

**Hizmet Şartları notu:** yerleşik varsayılanlar resmi Telegram Desktop istemcisini taklit eder. Kendi dağıtımlarınız için <https://my.telegram.org> adresinden kendi `api_id` / `api_hash` değerinizi edinip ayarlayın ve Telegram'ın Hizmet Şartları'nı inceleyin. Hesabınızı nasıl kullandığınızdan siz sorumlusunuz.

### Oturumlar ve durum

Durum dizini, aracın çalıştırmalar arasında sakladığı her şeyi `$MTPROTO_STORE_STATE` altında tutar:

| Yol | İçerik |
|---|---|
| `creds/telegram.session` | kimliği doğrulanmış **oturum** |
| `dests/telegram.json` | çözümlenmiş depolama kanalı referansı |
| `staging/tg_auth.json` | kısa ömürlü giriş durumu (`send-code` ile `sign-in` arasında) |
| `logs/progress-*.json` | işlem başına ilerleme |

**Oturum hassas bir kimlik bilgisidir**: onu okuyabilen herkes, parola veya 2FA istemi olmadan hesabı denetler. Araç dizini `0700` olarak oluşturur ve oturumu `0600` olarak yazar, ancak gerçek koruma `MTPROTO_STORE_STATE` değerini *nereye* yönlendirdiğinizdir. Onu özel depolamada tutun. Özellikle Android'de, kullanıcı kimlik doğrulaması yaptıktan sonra kilidi açılan **Credential-Encrypted** depolamayı (örn. `/data/misc_ce/<user>` altında), ilk kilit açılmadan önce okunabilen **Device-Encrypted** depolamaya (örn. `/data/adb`) tercih edin.

## Teşekkür

Bu aracın çekirdeği başlangıçta **Ash ([@ash-iir](https://github.com/ash-iir))** tarafından yazılmıştır; üzerine inşa edildiği derlenmiş MTProto depolama istemcisini o tasarlamıştır. Orijinal çalışmanın tüm kredisi yazarına aittir. Bu depo, o çalışmayı çıkararak, markasını kaldırarak ve genelleştirerek bağımsız, yeniden kullanılabilir bir araca dönüştürür.

## Ayrıca bakınız

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - gerçek Pixel `build.prop` verilerinin göz atılabilir, otomatik güncellenen bir arşivi.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - Telegram grupları için antispam moderasyon botu.

## Lisans

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) ve katkıda bulunanlar. [LICENSE](LICENSE) dosyasına bakın. Değiştirilmiş bir sürümü ağ hizmeti olarak çalıştırmak, sizi kaynağını sunmaya mecbur eder.

## İletişim

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
