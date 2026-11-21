[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | **中文** | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*把 Telegram 当作无限、分块的对象存储 - 通过原生 MTProto 协议，以单个自包含的 CLI 二进制文件实现。*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

无需 Python，无需 bot API，无需外部运行时。单个静态 Go 二进制文件，通过 MTProto 登录 Telegram 用户账户，并以分块上传的方式将任意文件存储在私有频道中。

## 功能

- 登录 Telegram **用户账户**（手机号 -> 登录验证码 -> 可选的两步验证密码），模拟官方 Telegram Desktop 客户端，从而保持会话稳定，并避免与其他客户端发生登出冲突。
- 以**分块上传**的方式将任意文件存储在私有频道中，绕过 bot 的大小限制（每个文件最多 2 GB，使用 Telegram Premium 时最多 4 GB）。
- 创建或复用自己的私有**存储频道**，并用可配置的后缀标记，因此它只会操作自己的频道。
- 流式下载数据，列出已存储的项目，并在 stdout 上打印机器可读的 JSON，便于脚本处理。

基于 [`gotd/td`](https://github.com/gotd/td)（纯 Go 实现的 MTProto）构建。

## 构建

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` 会剥离调试符号和 DWARF 表（约 23 MB -> 16 MB）。它可以为任意目标进行静态交叉编译（无需 CGO），并且同一个静态 Linux 二进制文件可在 Android 上运行（arm64-v8a、armeabi-v7a、x86_64、x86）：

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### 二进制文件大小

| 构建 | 大小（单一架构） |
|---|---|
| 默认（`go build`） | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| 上述构建，再经 `upx --best --lzma` | ~5-6 MB |

MTProto 栈（`gotd/td` 加上一个模拟 Telegram Desktop 的 TLS 伪装解析器）占了体积的大部分。CI 会为每个目标发布**经 UPX 压缩**的发行版二进制文件；UPX 在启动时自解压，开销可忽略。如果你不愿分发打包过的二进制文件，未压缩的 `-s -w` 构建是备选方案。

## 用法

每条命令都会向 stdout 打印一个 JSON 对象（`"ok": true | false`）。

| 命令 | 用途 |
|---|---|
| `send-code --phone <number>` | 开始登录；Telegram 发送登录验证码 |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | 完成登录 |
| `bot-login --token <token>` | 以机器人身份登录（受限） |
| `check-auth`（别名 `status`） | 报告认证状态 |
| `init-storage [--title <title>] [--channel-id <id>]` | 创建或复用私有存储频道 |
| `upload --dir <path> [flags]` | 将目录中的文件分块上传 |
| `download --ref <id> --out <path> [flags]` | 下载已存储的归档 |
| `delete --ref <id>[,<id>...]` | 删除一个或多个已存储的项目 |
| `list-remote`（别名 `list-backups`） | 列出已存储的项目 |
| `logout` | 丢弃本地会话 |

## 配置（环境变量）

| 变量 | 默认值 | 含义 |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | 状态目录（会话、目标配置、日志） |
| `MTPROTO_STORE_TAG` | `MTPS` | 标记本工具存储频道的后缀 |
| `MTPROTO_STORE_LABEL` | - | 可选名称,以 `label` 保存在每个上传项目的元数据中(由 `list-remote` 返回) |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | 你自己的 `api_id`，来自 my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | 你自己的 `api_hash` |

**服务条款说明：** 内置默认值模拟官方 Telegram Desktop 客户端。对于你自己的部署，请在 <https://my.telegram.org> 获取并设置你自己的 `api_id` / `api_hash`，并查阅 Telegram 的服务条款。你需要为如何使用自己的账户负责。

### 会话与状态

状态目录保存了本工具在多次运行之间保留的一切内容，位于 `$MTPROTO_STORE_STATE` 下：

| 路径 | 内容 |
|---|---|
| `creds/telegram.session` | 已认证的**会话** |
| `dests/telegram.json` | 解析后的存储频道引用 |
| `staging/tg_auth.json` | 短暂的登录状态（介于 `send-code` 与 `sign-in` 之间） |
| `logs/progress-*.json` | 每次操作的进度 |

**会话是一项敏感凭据**：任何能读取它的人都能控制该账户，无需密码或两步验证提示。本工具以 `0700` 创建目录，以 `0600` 写入会话，但真正的保护在于你把 `MTPROTO_STORE_STATE` *指向哪里*。请将其保存在私有存储上。特别是在 Android 上，相比**设备加密（Device-Encrypted）**存储（例如 `/data/adb`，在首次解锁前即可读取），应优先选择**凭据加密（Credential-Encrypted）**存储（例如 `/data/misc_ce/<user>` 下），后者只有在用户认证之后才会解锁。

## 鸣谢

本工具的核心最初由 **Ash ([@ash-iir](https://github.com/ash-iir))** 编写，他设计了它所基于的编译型 MTProto 存储客户端。原始作品的全部功劳归于其作者。本仓库将该作品提取、去品牌化并泛化为一个独立、可复用的工具。

## 另见

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - 一个可浏览、自动更新的真实 Pixel `build.prop` 数据存档。
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - 用于 Telegram 群组的反垃圾信息审核机器人。

## 联系

- https://victorgabriel.dev
- **GitHub:** @VictorGabriel7Dev https://github.com/VictorGabriel7Dev
- **Telegram:** @VictorGabriel_Dev https://t.me/VictorGabriel_Dev
- **Discord:** @VictorGabriel.dev https://discord.com/users/1481407654458036265
- **LinkedIn:** in/victorgabriel-dev https://www.linkedin.com/in/victorgabriel-dev
- **Instagram:** @VictorGabriel_Dev https://www.instagram.com/VictorGabriel_Dev
- **WhatsApp:** @VictorGabriel_Dev https://wa.me/@VictorGabriel_Dev
- **E-mail:** contato@victorgabriel.dev

## 许可证

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) 及贡献者。参见 [LICENSE](LICENSE)。以网络服务方式运行修改后的版本，会使你有义务提供其源代码。

---

`telegram` `mtproto` `gotd` `cloud-storage` `object-storage` `unlimited-storage` `cli` `golang` `static-binary` `cross-platform` `self-hosted` `file-storage` `chunked-upload` `mtproto-store`
