[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | **हिन्दी** | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Telegram को असीमित, खंडित (chunked) ऑब्जेक्ट स्टोरेज के रूप में उपयोग करें - मूल MTProto प्रोटोकॉल के माध्यम से, एक अकेली स्व-निहित CLI बाइनरी के रूप में।*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

न Python, न bot API, न कोई बाहरी रनटाइम। एक अकेली स्थिर (static) Go बाइनरी जो MTProto के माध्यम से एक Telegram उपयोगकर्ता खाते में लॉग इन करती है और मनमानी फ़ाइलों को एक निजी चैनल में खंडित अपलोड के रूप में संग्रहीत करती है।

## यह क्या करता है

- एक Telegram **उपयोगकर्ता खाते** में लॉग इन करता है (फ़ोन नंबर -> लॉगिन कोड -> वैकल्पिक 2FA पासवर्ड), जो आधिकारिक Telegram Desktop क्लाइंट का अनुकरण करता है, जिससे सत्र स्थिर रहते हैं और अन्य क्लाइंट के साथ लॉगआउट का टकराव नहीं होता।
- मनमानी फ़ाइलों को एक निजी चैनल में **खंडित अपलोड** के रूप में संग्रहीत करता है, जिससे bot की आकार सीमाएँ पार हो जाती हैं (प्रति फ़ाइल 2 GB तक, या Telegram Premium के साथ 4 GB तक)।
- अपना स्वयं का निजी **स्टोरेज चैनल** बनाता या पुनः उपयोग करता है, जिसे एक विन्यास-योग्य प्रत्यय से टैग किया जाता है, ताकि यह हमेशा केवल अपने ही चैनलों को छुए।
- डाउनलोड को स्ट्रीम करके वापस लाता है, संग्रहीत वस्तुओं की सूची बनाता है, और स्क्रिप्टिंग को आसान बनाने के लिए मशीन-पठनीय JSON को stdout पर प्रिंट करता है।

[`gotd/td`](https://github.com/gotd/td) (शुद्ध-Go MTProto) पर आधारित।

## बिल्ड

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` डिबग प्रतीकों और DWARF तालिकाओं को हटा देता है (लगभग 23 MB -> 16 MB)। यह किसी भी लक्ष्य के लिए स्थिर रूप से क्रॉस-कंपाइल होता है (बिना CGO के), और वही स्थिर Linux बाइनरियाँ Android पर भी चलती हैं (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### बाइनरी का आकार

| बिल्ड | आकार (एक आर्किटेक्चर) |
|---|---|
| डिफ़ॉल्ट (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| उपर्युक्त, फिर `upx --best --lzma` | ~5-6 MB |

MTProto स्टैक (`gotd/td` के साथ एक TLS-छद्मावरण रिज़ॉल्वर जो Telegram Desktop की नकल करता है) ही आकार का अधिकांश भाग है। CI हर लक्ष्य के लिए **UPX-संपीड़ित** रिलीज़ बाइनरियाँ प्रकाशित करता है; UPX प्रारंभ के समय नगण्य ओवरहेड के साथ स्वयं को विघटित कर लेता है। यदि आप पैक की गई बाइनरियाँ वितरित नहीं करना चाहते, तो असंपीड़ित `-s -w` बिल्ड एक विकल्प है।

## उपयोग

प्रत्येक कमांड stdout पर एक अकेला JSON ऑब्जेक्ट प्रिंट करता है (`"ok": true | false`)।

| कमांड | उद्देश्य |
|---|---|
| `send-code --phone <number>` | लॉगिन शुरू करें; Telegram लॉगिन कोड भेजता है |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | लॉगिन पूरा करें |
| `check-auth` (उपनाम `status`) | प्रमाणीकरण स्थिति की रिपोर्ट करें |
| `init-storage [--title <title>]` | निजी स्टोरेज चैनल बनाएँ या पुनः उपयोग करें |
| `upload --dir <path> [flags]` | किसी फ़ाइल को खंडों के रूप में अपलोड करें |
| `download [flags]` | संग्रहीत आर्काइव डाउनलोड करें |
| `list-remote` (उपनाम `list-backups`) | संग्रहीत वस्तुओं की सूची बनाएँ |
| `logout` | स्थानीय सत्र को हटाएँ |

## विन्यास (एनवायरनमेंट)

| वेरिएबल | डिफ़ॉल्ट | अर्थ |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | स्थिति निर्देशिका (सत्र, गंतव्य विन्यास, लॉग) |
| `MTPROTO_STORE_TAG` | `MTPS` | प्रत्यय जो इस उपकरण के स्टोरेज चैनलों को चिह्नित करता है |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | my.telegram.org से प्राप्त आपका अपना `api_id` |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | आपका अपना `api_hash` |

**सेवा की शर्तों से संबंधित टिप्पणी:** अंतर्निहित डिफ़ॉल्ट मान आधिकारिक Telegram Desktop क्लाइंट का अनुकरण करते हैं। अपनी स्वयं की तैनाती के लिए, <https://my.telegram.org> पर अपना स्वयं का `api_id` / `api_hash` प्राप्त करके सेट करें और Telegram की सेवा की शर्तों की समीक्षा करें। आप अपने खाते का उपयोग कैसे करते हैं, इसके लिए आप स्वयं उत्तरदायी हैं।

### सत्र और स्थिति

स्थिति निर्देशिका वह सब कुछ रखती है जिसे उपकरण रन के बीच `$MTPROTO_STORE_STATE` के अंतर्गत संजोकर रखता है:

| पथ | सामग्री |
|---|---|
| `creds/telegram.session` | प्रमाणित **सत्र** |
| `dests/telegram.json` | समाधानित स्टोरेज-चैनल संदर्भ |
| `staging/tg_auth.json` | अल्पकालिक लॉगिन स्थिति (`send-code` और `sign-in` के बीच) |
| `logs/progress-*.json` | प्रति-संक्रिया प्रगति |

**सत्र एक संवेदनशील प्रमाण-पत्र है**: जो कोई भी इसे पढ़ सकता है, वह बिना किसी पासवर्ड या 2FA संकेत के खाते को नियंत्रित कर लेता है। उपकरण निर्देशिका को `0700` पर बनाता है और सत्र को `0600` पर लिखता है, परंतु असली सुरक्षा इस बात में है कि आप `MTPROTO_STORE_STATE` को *कहाँ* इंगित करते हैं। इसे निजी स्टोरेज पर रखें। विशेष रूप से Android पर, **डिवाइस-एन्क्रिप्टेड (Device-Encrypted)** स्टोरेज (उदाहरण के लिए `/data/adb`, जो पहली बार अनलॉक होने से पहले भी पठनीय है) की तुलना में **क्रेडेंशियल-एन्क्रिप्टेड (Credential-Encrypted)** स्टोरेज (उदाहरण के लिए `/data/misc_ce/<user>` के अंतर्गत) को प्राथमिकता दें, जो केवल उपयोगकर्ता के प्रमाणीकरण के बाद ही अनलॉक होती है।

## श्रेय

इस उपकरण का मूल भाग मूल रूप से **Ash ([@ash-iir](https://github.com/ash-iir))** द्वारा लिखा गया था, जिन्होंने उस संकलित-MTProto स्टोरेज क्लाइंट को डिज़ाइन किया जिस पर यह आधारित है। मूल कार्य का पूरा श्रेय उसके लेखक को जाता है। यह रिपॉज़िटरी उस कार्य को निकालकर, उसकी ब्रांडिंग हटाकर और उसे एक स्वतंत्र, पुनः उपयोग-योग्य उपकरण के रूप में सामान्यीकृत करती है।

## यह भी देखें

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - वास्तविक Pixel `build.prop` डेटा का एक ब्राउज़-योग्य, स्वतः-अद्यतन संग्रह।
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - Telegram समूहों के लिए एक एंटी-स्पैम मॉडरेशन bot।

## लाइसेंस

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) और योगदानकर्ता। [LICENSE](LICENSE) देखें। किसी संशोधित संस्करण को एक नेटवर्क सेवा के रूप में चलाने पर आप उसका स्रोत प्रस्तुत करने के लिए बाध्य होते हैं।

## संपर्क

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
