[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | **日本語** | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Telegram を無制限かつチャンク分割されたオブジェクトストレージとして利用 - ネイティブの MTProto プロトコル経由で、単一の自己完結型 CLI バイナリとして。*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Python も bot API も外部ランタイムも不要。MTProto 経由で Telegram ユーザーアカウントにログインし、任意のファイルをプライベートチャンネルへチャンク分割アップロードとして保存する、単一の静的 Go バイナリです。

## 機能

- Telegram の**ユーザーアカウント**にログインします（電話番号 -> ログインコード -> 任意の 2FA パスワード）。公式の Telegram Desktop クライアントをエミュレートするため、セッションが安定し、他のクライアントとのログアウト競合を回避できます。
- 任意のファイルをプライベートチャンネルに**チャンク分割アップロード**として保存し、bot のサイズ制限を回避します（1 ファイルあたり最大 2 GB、Telegram Premium なら最大 4 GB）。
- 設定可能なサフィックスでタグ付けされた、自分専用のプライベート**ストレージチャンネル**を作成または再利用するため、常に自分のチャンネルだけを操作します。
- ダウンロードをストリーミングで取り戻し、保存済みの項目を一覧表示し、スクリプト処理を容易にするために機械可読な JSON を stdout に出力します。

[`gotd/td`](https://github.com/gotd/td)（純粋な Go による MTProto）を基盤としています。

## ビルド

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` はデバッグシンボルと DWARF テーブルを取り除きます（約 23 MB -> 16 MB）。CGO なしで任意のターゲット向けに静的クロスコンパイルでき、同じ静的 Linux バイナリが Android でも動作します（arm64-v8a、armeabi-v7a、x86_64、x86）：

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### バイナリサイズ

| ビルド | サイズ（1 アーキテクチャ） |
|---|---|
| デフォルト（`go build`） | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| 上記のうえに `upx --best --lzma` | ~5-6 MB |

MTProto スタック（`gotd/td` に、Telegram Desktop を模倣する TLS カモフラージュ用リゾルバを加えたもの）がサイズの大半を占めます。CI はすべてのターゲット向けに **UPX で圧縮された**リリースバイナリを公開します。UPX は起動時に自己展開し、オーバーヘッドはごくわずかです。パックされたバイナリを配布したくない場合は、非圧縮の `-s -w` ビルドが代替となります。

## 使い方

すべてのコマンドは、単一の JSON オブジェクトを stdout に出力します（`"ok": true | false`）。

| コマンド | 目的 |
|---|---|
| `send-code --phone <number>` | ログインを開始する。Telegram がログインコードを送信する |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | ログインを完了する |
| `bot-login --token <token>` | ボットとしてログイン（制限あり） |
| `check-auth`（エイリアス `status`） | 認証状態を報告する |
| `init-storage [--title <title>] [--channel-id <id>]` | プライベートストレージチャンネルを作成または再利用する |
| `upload --dir <path> [flags]` | ディレクトリ内のファイルをチャンクに分けてアップロード |
| `download [flags]` | 保存済みのアーカイブをダウンロードする |
| `delete --ref <id>[,<id>...]` | 保存された項目を1つ以上削除 |
| `list-remote`（エイリアス `list-backups`） | 保存済みの項目を一覧表示する |
| `logout` | ローカルセッションを破棄する |

## 設定（環境変数）

| 変数 | デフォルト | 意味 |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | 状態ディレクトリ（セッション、宛先設定、ログ） |
| `MTPROTO_STORE_TAG` | `MTPS` | このツールのストレージチャンネルを示すサフィックス |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | my.telegram.org で取得した自分専用の `api_id` |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | 自分専用の `api_hash` |

**利用規約に関する注意：** 組み込みのデフォルト値は公式の Telegram Desktop クライアントをエミュレートします。自分自身のデプロイでは、<https://my.telegram.org> で自分専用の `api_id` / `api_hash` を取得して設定し、Telegram の利用規約を確認してください。アカウントをどう利用するかは、あなた自身の責任です。

### セッションと状態

状態ディレクトリは、ツールが実行の合間に保持するすべてを `$MTPROTO_STORE_STATE` の下に保存します：

| パス | 内容 |
|---|---|
| `creds/telegram.session` | 認証済みの**セッション** |
| `dests/telegram.json` | 解決済みのストレージチャンネル参照 |
| `staging/tg_auth.json` | 短命のログイン状態（`send-code` と `sign-in` の間） |
| `logs/progress-*.json` | 操作ごとの進捗 |

**セッションは機微な資格情報です**：これを読める者は誰でも、パスワードや 2FA の入力なしにアカウントを制御できます。ツールはディレクトリを `0700` で作成し、セッションを `0600` で書き込みますが、本当の保護は `MTPROTO_STORE_STATE` を*どこに*向けるかにかかっています。プライベートなストレージに保管してください。特に Android では、（最初のロック解除前でも読み取れる `/data/adb` などの）**デバイス暗号化（Device-Encrypted）**ストレージよりも、ユーザーの認証後にのみロック解除される（`/data/misc_ce/<user>` 配下などの）**資格情報暗号化（Credential-Encrypted）**ストレージを優先してください。

## クレジット

このツールの中核は、もともと **Ash ([@ash-iir](https://github.com/ash-iir))** によって書かれました。本ツールの基盤となっている、コンパイル済み MTProto ストレージクライアントを設計したのは彼です。オリジナルの成果に対するすべての功績は、その作者に帰します。本リポジトリは、その成果を抽出し、ブランド要素を取り除き、スタンドアロンで再利用可能なツールへと一般化したものです。

## 関連情報

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - 実際の Pixel の `build.prop` データを閲覧でき、自動更新されるアーカイブ。
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - Telegram グループ向けのスパム対策モデレーション bot。

## ライセンス

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) およびコントリビューター。[LICENSE](LICENSE) を参照してください。改変版をネットワークサービスとして運用する場合、そのソースを提供する義務が生じます。

## 連絡先

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
