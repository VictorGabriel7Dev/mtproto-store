[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | **한국어** | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Telegram 을 무제한의 청크 분할 오브젝트 스토리지로 활용 - 네이티브 MTProto 프로토콜을 통해, 단일의 자기 완결형 CLI 바이너리로.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Python 도, bot API 도, 외부 런타임도 필요 없습니다. MTProto 를 통해 Telegram 사용자 계정에 로그인하고, 임의의 파일을 비공개 채널에 청크 분할 업로드로 저장하는 단일 정적 Go 바이너리입니다.

## 기능

- Telegram **사용자 계정**에 로그인합니다(전화번호 -> 로그인 코드 -> 선택적 2FA 비밀번호). 공식 Telegram Desktop 클라이언트를 에뮬레이트하므로 세션이 안정적으로 유지되고 다른 클라이언트와의 로그아웃 충돌을 피할 수 있습니다.
- 임의의 파일을 비공개 채널에 **청크 분할 업로드**로 저장하여 bot 의 크기 제한을 우회합니다(파일당 최대 2 GB, Telegram Premium 사용 시 최대 4 GB).
- 설정 가능한 접미사로 태그가 붙은 자체 비공개 **스토리지 채널**을 생성하거나 재사용하므로, 항상 자신의 채널만 다룹니다.
- 다운로드를 스트리밍으로 되돌려 받고, 저장된 항목을 나열하며, 스크립트 작성이 쉽도록 기계가 읽을 수 있는 JSON 을 stdout 에 출력합니다.

[`gotd/td`](https://github.com/gotd/td)(순수 Go 로 구현된 MTProto)를 기반으로 합니다.

## 빌드

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` 은 디버그 심볼과 DWARF 테이블을 제거합니다(약 23 MB -> 16 MB). CGO 없이 모든 타깃에 대해 정적으로 크로스 컴파일되며, 동일한 정적 Linux 바이너리가 Android 에서도 실행됩니다(arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### 바이너리 크기

| 빌드 | 크기(단일 아키텍처) |
|---|---|
| 기본값(`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| 위 빌드에 이어 `upx --best --lzma` | ~5-6 MB |

MTProto 스택(`gotd/td` 에 Telegram Desktop 을 흉내 내는 TLS 위장 리졸버를 더한 것)이 용량의 대부분을 차지합니다. CI 는 모든 타깃에 대해 **UPX 로 압축된** 릴리스 바이너리를 게시합니다. UPX 는 시작 시 자체 압축 해제되며 오버헤드는 거의 없습니다. 패킹된 바이너리를 배포하고 싶지 않다면, 압축되지 않은 `-s -w` 빌드가 대안입니다.

## 사용법

모든 명령은 단일 JSON 오브젝트를 stdout 에 출력합니다(`"ok": true | false`).

| 명령 | 용도 |
|---|---|
| `send-code --phone <number>` | 로그인을 시작한다. Telegram 이 로그인 코드를 보낸다 |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | 로그인을 완료한다 |
| `check-auth`(별칭 `status`) | 인증 상태를 보고한다 |
| `init-storage [--title <title>]` | 비공개 스토리지 채널을 생성하거나 재사용한다 |
| `upload --file <path> [flags]` | 파일을 청크로 업로드한다 |
| `download [flags]` | 저장된 아카이브를 다운로드한다 |
| `list-remote`(별칭 `list-backups`) | 저장된 항목을 나열한다 |
| `logout` | 로컬 세션을 폐기한다 |

## 구성(환경 변수)

| 변수 | 기본값 | 의미 |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | 상태 디렉터리(세션, 대상 설정, 로그) |
| `MTPROTO_STORE_TAG` | `MTPS` | 이 도구의 스토리지 채널을 표시하는 접미사 |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | my.telegram.org 에서 받은 자신만의 `api_id` |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | 자신만의 `api_hash` |

**서비스 약관 참고:** 내장 기본값은 공식 Telegram Desktop 클라이언트를 에뮬레이트합니다. 자신의 배포에서는 <https://my.telegram.org> 에서 자신만의 `api_id` / `api_hash` 를 발급받아 설정하고 Telegram 의 서비스 약관을 확인하세요. 계정을 어떻게 사용하는지는 전적으로 사용자의 책임입니다.

### 세션과 상태

상태 디렉터리는 도구가 실행과 실행 사이에 보관하는 모든 것을 `$MTPROTO_STORE_STATE` 아래에 저장합니다:

| 경로 | 내용 |
|---|---|
| `creds/telegram.session` | 인증된 **세션** |
| `dests/telegram.json` | 해석된 스토리지 채널 참조 |
| `staging/tg_auth.json` | 수명이 짧은 로그인 상태(`send-code` 와 `sign-in` 사이) |
| `logs/progress-*.json` | 작업별 진행 상황 |

**세션은 민감한 자격 증명입니다**: 이를 읽을 수 있는 사람은 누구나 비밀번호나 2FA 입력 없이 계정을 제어할 수 있습니다. 도구는 디렉터리를 `0700` 으로 생성하고 세션을 `0600` 으로 기록하지만, 진짜 보호는 `MTPROTO_STORE_STATE` 를 *어디로* 향하게 하느냐에 달려 있습니다. 비공개 스토리지에 보관하세요. 특히 Android 에서는, (첫 잠금 해제 전에도 읽을 수 있는 `/data/adb` 같은) **기기 암호화(Device-Encrypted)** 스토리지보다, 사용자가 인증한 후에만 잠금이 해제되는 (`/data/misc_ce/<user>` 아래 같은) **자격 증명 암호화(Credential-Encrypted)** 스토리지를 우선하세요.

## 크레딧

이 도구의 핵심은 원래 **Ash ([@ash-iir](https://github.com/ash-iir))** 가 작성했으며, 그는 이 도구의 기반이 되는 컴파일형 MTProto 스토리지 클라이언트를 설계했습니다. 원본 작업에 대한 모든 공로는 그 작성자에게 돌아갑니다. 이 저장소는 그 작업을 추출하고 브랜드 요소를 제거하여 독립적이고 재사용 가능한 도구로 일반화한 것입니다.

## 함께 보기

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - 실제 Pixel 의 `build.prop` 데이터를 탐색할 수 있고 자동으로 업데이트되는 아카이브.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - Telegram 그룹용 스팸 방지 모더레이션 bot.

## 라이선스

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) 및 기여자들. [LICENSE](LICENSE) 를 참조하세요. 수정된 버전을 네트워크 서비스로 운영하면 그 소스를 제공할 의무가 발생합니다.

## 연락처

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
