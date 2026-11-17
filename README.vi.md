[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | **Tiếng Việt** | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Sử dụng Telegram làm kho lưu trữ đối tượng không giới hạn, chia theo khối - qua giao thức MTProto gốc, dưới dạng một tệp nhị phân CLI độc lập duy nhất.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Không Python, không bot API, không môi trường chạy bên ngoài. Một tệp nhị phân Go tĩnh duy nhất đăng nhập vào tài khoản người dùng Telegram qua MTProto và lưu trữ các tệp tùy ý dưới dạng tải lên theo khối trong một kênh riêng tư.

## Chức năng

- Đăng nhập vào **tài khoản người dùng** Telegram (số điện thoại -> mã đăng nhập -> mật khẩu 2FA tùy chọn), mô phỏng ứng dụng khách Telegram Desktop chính thức, giúp giữ phiên ổn định và tránh xung đột đăng xuất với các ứng dụng khách khác.
- Lưu trữ các tệp tùy ý dưới dạng **tải lên theo khối** trong một kênh riêng tư, vượt qua giới hạn kích thước của bot (tối đa 2 GB mỗi tệp, hoặc 4 GB với Telegram Premium).
- Tạo hoặc tái sử dụng **kênh lưu trữ** riêng của chính nó, được gắn thẻ bằng một hậu tố có thể cấu hình để chỉ chạm vào các kênh của riêng nó.
- Truyền tải lại các bản tải xuống, liệt kê các mục đã lưu, và in JSON máy đọc được ra stdout để dễ dàng viết kịch bản.

Được xây dựng trên [`gotd/td`](https://github.com/gotd/td) (MTProto thuần Go).

## Biên dịch

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` loại bỏ các ký hiệu gỡ lỗi và bảng DWARF (khoảng 23 MB -> 16 MB). Nó biên dịch chéo tĩnh cho bất kỳ nền tảng đích nào (không CGO), và cùng các tệp nhị phân Linux tĩnh đó chạy trên Android (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Kích thước tệp nhị phân

| Bản dựng | Kích thước (một kiến trúc) |
|---|---|
| mặc định (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| như trên, rồi `upx --best --lzma` | ~5-6 MB |

Ngăn xếp MTProto (`gotd/td` cộng với một bộ phân giải ngụy trang TLS mô phỏng Telegram Desktop) chiếm phần lớn kích thước. CI phát hành các tệp nhị phân bản phát hành **được nén UPX** cho mọi nền tảng đích; UPX tự giải nén khi khởi động với chi phí không đáng kể. Nếu bạn không muốn phân phối các tệp nhị phân đã đóng gói, bản dựng `-s -w` không nén là phương án dự phòng.

## Sử dụng

Mỗi lệnh in ra một đối tượng JSON duy nhất ra stdout (`"ok": true | false`).

| Lệnh | Mục đích |
|---|---|
| `send-code --phone <number>` | Bắt đầu đăng nhập; Telegram gửi mã đăng nhập |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Hoàn tất đăng nhập |
| `check-auth` (alias `status`) | Báo cáo trạng thái xác thực |
| `init-storage [--title <title>]` | Tạo hoặc tái sử dụng kênh lưu trữ riêng tư |
| `upload --dir <path> [flags]` | Tải lên các tệp trong một thư mục theo từng phần |
| `download [flags]` | Tải xuống một kho lưu trữ đã lưu |
| `list-remote` (alias `list-backups`) | Liệt kê các mục đã lưu |
| `logout` | Hủy phiên cục bộ |

## Cấu hình (môi trường)

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Thư mục trạng thái (phiên, cấu hình đích, nhật ký) |
| `MTPROTO_STORE_TAG` | `MTPS` | Hậu tố đánh dấu các kênh lưu trữ của công cụ này |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | `api_id` của riêng bạn từ my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | `api_hash` của riêng bạn |

**Lưu ý về Điều khoản Dịch vụ:** các giá trị mặc định tích hợp mô phỏng ứng dụng khách Telegram Desktop chính thức. Đối với các triển khai của riêng bạn, hãy lấy và đặt `api_id` / `api_hash` của riêng bạn tại <https://my.telegram.org> và xem lại Điều khoản Dịch vụ của Telegram. Bạn chịu trách nhiệm về cách bạn sử dụng tài khoản của mình.

### Phiên và trạng thái

Thư mục trạng thái lưu giữ mọi thứ mà công cụ giữ lại giữa các lần chạy, trong `$MTPROTO_STORE_STATE`:

| Đường dẫn | Nội dung |
|---|---|
| `creds/telegram.session` | **phiên** đã được xác thực |
| `dests/telegram.json` | tham chiếu kênh lưu trữ đã được phân giải |
| `staging/tg_auth.json` | trạng thái đăng nhập ngắn hạn (giữa `send-code` và `sign-in`) |
| `logs/progress-*.json` | tiến trình theo từng thao tác |

**Phiên là một thông tin xác thực nhạy cảm**: bất kỳ ai có thể đọc được nó đều kiểm soát tài khoản, mà không cần mật khẩu hay lời nhắc 2FA. Công cụ tạo thư mục `0700` và ghi phiên `0600`, nhưng sự bảo vệ thực sự nằm ở *nơi* bạn trỏ `MTPROTO_STORE_STATE` tới. Hãy giữ nó trên bộ lưu trữ riêng tư. Cụ thể trên Android, hãy ưu tiên bộ lưu trữ **Credential-Encrypted** (ví dụ dưới `/data/misc_ce/<user>`), vốn chỉ được mở khóa sau khi người dùng xác thực, hơn là bộ lưu trữ **Device-Encrypted** (ví dụ `/data/adb`, có thể đọc được trước lần mở khóa đầu tiên).

## Ghi công

Phần lõi của công cụ này ban đầu được viết bởi **Ash ([@ash-iir](https://github.com/ash-iir))**, người đã thiết kế ứng dụng khách lưu trữ MTProto được biên dịch mà nó dựa trên. Toàn bộ công lao cho tác phẩm gốc thuộc về tác giả của nó. Kho lưu trữ này trích xuất, gỡ bỏ thương hiệu và tổng quát hóa công việc đó thành một công cụ độc lập, có thể tái sử dụng.

## Xem thêm

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - một kho lưu trữ dữ liệu `build.prop` Pixel thật, có thể duyệt và tự động cập nhật.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - bot kiểm duyệt chống spam cho các nhóm Telegram.

## Giấy phép

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) và những người đóng góp. Xem [LICENSE](LICENSE). Việc chạy một phiên bản đã sửa đổi như một dịch vụ mạng buộc bạn phải cung cấp mã nguồn của nó.

## Liên hệ

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
