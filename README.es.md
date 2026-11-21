[English](README.md) | [Português](README.pt.md) | **Español** | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Usa Telegram como almacenamiento de objetos ilimitado y fragmentado - sobre el protocolo nativo MTProto, como un único binario de línea de comandos autónomo.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Sin Python, sin API de bot, sin entorno de ejecución externo. Un único binario estático en Go que inicia sesión en una cuenta de usuario de Telegram por MTProto y almacena archivos arbitrarios como subidas fragmentadas en un canal privado.

## Qué hace

- Inicia sesión en una **cuenta de usuario** de Telegram (número de teléfono -> código de inicio de sesión -> contraseña 2FA opcional), emulando el cliente oficial Telegram Desktop, lo que mantiene las sesiones estables y evita conflictos de cierre de sesión con otros clientes.
- Almacena archivos arbitrarios como **subidas fragmentadas** en un canal privado, sorteando los límites de tamaño de los bots (hasta 2 GB por archivo, o 4 GB con Telegram Premium).
- Crea o reutiliza su propio **canal de almacenamiento** privado, marcado con un sufijo configurable para tocar únicamente sus propios canales.
- Transmite las descargas de vuelta, lista los elementos almacenados e imprime JSON legible por máquina en stdout para facilitar la automatización.

Construido sobre [`gotd/td`](https://github.com/gotd/td) (MTProto puro en Go).

## Compilación

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` elimina los símbolos de depuración y las tablas DWARF (unos 23 MB -> 16 MB). Compila de forma cruzada y estática para cualquier destino (sin CGO), y los mismos binarios estáticos de Linux se ejecutan en Android (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Tamaño del binario

| Compilación | Tamaño (una arquitectura) |
|---|---|
| predeterminada (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| lo anterior, luego `upx --best --lzma` | ~5-6 MB |

La pila MTProto (`gotd/td` más un resolvedor de camuflaje TLS que imita a Telegram Desktop) es la mayor parte del tamaño. La CI publica binarios de lanzamiento **comprimidos con UPX** para cada destino; UPX se autoextrae al inicio con una sobrecarga insignificante. Si prefieres no distribuir binarios empaquetados, la compilación `-s -w` sin comprimir es la alternativa.

## Uso

Cada comando imprime un único objeto JSON en stdout (`"ok": true | false`).

| Comando | Propósito |
|---|---|
| `send-code --phone <number>` | Inicia el inicio de sesión; Telegram envía el código de inicio de sesión |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Completa el inicio de sesión |
| `bot-login --token <token>` | Inicia sesión como bot (limitado) |
| `check-auth` (alias `status`) | Informa el estado de autenticación |
| `init-storage [--title <title>] [--channel-id <id>]` | Crea o reutiliza el canal de almacenamiento privado |
| `upload --dir <path> [flags]` | Sube los archivos de un directorio en fragmentos |
| `download --ref <id> --out <path> [flags]` | Descarga un archivo almacenado |
| `delete --ref <id>[,<id>...]` | Elimina uno o más elementos almacenados |
| `list-remote` (alias `list-backups`) | Lista los elementos almacenados |
| `logout` | Descarta la sesión local |

## Configuración (entorno)

| Variable | Predeterminado | Significado |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Directorio de estado (sesión, configuración de destino, registros) |
| `MTPROTO_STORE_TAG` | `MTPS` | Sufijo que marca los canales de almacenamiento de esta herramienta |
| `MTPROTO_STORE_LABEL` | - | Nombre opcional guardado como `label` en los metadatos de cada elemento subido (lo devuelve `list-remote`) |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Tu propio `api_id` de my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Tu propio `api_hash` |

**Nota sobre los Términos de Servicio:** los valores predeterminados integrados emulan el cliente oficial Telegram Desktop. Para tus propios despliegues, obtén y define tu propio `api_id` / `api_hash` en <https://my.telegram.org> y revisa los Términos de Servicio de Telegram. Eres responsable del uso que hagas de tu cuenta.

### Sesiones y estado

El directorio de estado contiene todo lo que la herramienta conserva entre ejecuciones, en `$MTPROTO_STORE_STATE`:

| Ruta | Contenido |
|---|---|
| `creds/telegram.session` | la **sesión** autenticada |
| `dests/telegram.json` | la referencia resuelta del canal de almacenamiento |
| `staging/tg_auth.json` | estado de inicio de sesión de corta duración (entre `send-code` y `sign-in`) |
| `logs/progress-*.json` | progreso por operación |

La **sesión es una credencial sensible**: cualquiera que pueda leerla controla la cuenta, sin solicitud de contraseña ni 2FA. La herramienta crea el directorio como `0700` y escribe la sesión como `0600`, pero la protección real está en *dónde* apuntas `MTPROTO_STORE_STATE`. Mantenla en almacenamiento privado. En Android en particular, prefiere el almacenamiento **Credential-Encrypted** (por ejemplo, en `/data/misc_ce/<user>`), que solo se desbloquea después de que el usuario se autentica, frente al almacenamiento **Device-Encrypted** (por ejemplo, `/data/adb`, legible antes del primer desbloqueo).

## Créditos

El núcleo de esta herramienta fue escrito originalmente por **Ash ([@ash-iir](https://github.com/ash-iir))**, quien diseñó el cliente de almacenamiento MTProto compilado sobre el que se construye. Todo el crédito por el trabajo original es de su autor. Este repositorio extrae, elimina la marca y generaliza ese trabajo en una herramienta autónoma y reutilizable.

## Véase también

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - un archivo navegable y actualizado automáticamente de datos reales de `build.prop` de Pixel.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - bot de moderación anti-spam para grupos de Telegram.

## Contacto

- https://victorgabriel.dev
- **GitHub:** @VictorGabriel7Dev https://github.com/VictorGabriel7Dev
- **Telegram:** @VictorGabriel_Dev https://t.me/VictorGabriel_Dev
- **Discord:** @VictorGabriel.dev https://discord.com/users/1481407654458036265
- **LinkedIn:** in/victorgabriel-dev https://www.linkedin.com/in/victorgabriel-dev
- **Instagram:** @VictorGabriel_Dev https://www.instagram.com/VictorGabriel_Dev
- **WhatsApp:** @VictorGabriel_Dev https://wa.me/@VictorGabriel_Dev
- **E-mail:** contato@victorgabriel.dev

## Licencia

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) y colaboradores. Consulta [LICENSE](LICENSE). Ejecutar una versión modificada como servicio de red te obliga a ofrecer su código fuente.

---

`telegram` `mtproto` `gotd` `cloud-storage` `object-storage` `unlimited-storage` `cli` `golang` `static-binary` `cross-platform` `self-hosted` `file-storage` `chunked-upload` `mtproto-store`
