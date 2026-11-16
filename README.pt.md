[English](README.md) | **Português** | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Use o Telegram como armazenamento de objetos ilimitado e fragmentado - sobre o protocolo nativo MTProto, em um único binário de linha de comando autossuficiente.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Sem Python, sem API de bot, sem runtime externo. Um único binário estático em Go que faz login em uma conta de usuário do Telegram por MTProto e armazena arquivos arbitrários como uploads fragmentados em um canal privado.

## O que faz

- Faz login em uma **conta de usuário** do Telegram (número de telefone -> código de login -> senha 2FA opcional), emulando o cliente oficial Telegram Desktop, o que mantém as sessões estáveis e evita conflitos de logout com outros clientes.
- Armazena arquivos arbitrários como **uploads fragmentados** em um canal privado, contornando os limites de tamanho dos bots (até 2 GB por arquivo, ou 4 GB com o Telegram Premium).
- Cria ou reutiliza seu próprio **canal de armazenamento** privado, marcado com um sufixo configurável para tocar apenas em seus próprios canais.
- Transmite os downloads de volta, lista os itens armazenados e imprime JSON legível por máquina no stdout para facilitar a automação.

Construído sobre [`gotd/td`](https://github.com/gotd/td) (MTProto puro em Go).

## Compilação

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` remove os símbolos de depuração e as tabelas DWARF (cerca de 23 MB -> 16 MB). Ele faz compilação cruzada estática para qualquer alvo (sem CGO), e os mesmos binários Linux estáticos rodam no Android (arm64-v8a, armeabi-v7a, x86_64, x86):

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Tamanho do binário

| Compilação | Tamanho (uma arquitetura) |
|---|---|
| padrão (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| o anterior, depois `upx --best --lzma` | ~5-6 MB |

A pilha MTProto (`gotd/td` mais um resolvedor de camuflagem TLS que imita o Telegram Desktop) é a maior parte do tamanho. A CI publica binários de release **comprimidos com UPX** para cada alvo; o UPX se autodescompacta na inicialização com sobrecarga desprezível. Se você preferir não distribuir binários empacotados, a compilação `-s -w` sem compressão é a alternativa.

## Uso

Todo comando imprime um único objeto JSON no stdout (`"ok": true | false`).

| Comando | Finalidade |
|---|---|
| `send-code --phone <number>` | Inicia o login; o Telegram envia o código de login |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Conclui o login |
| `check-auth` (alias `status`) | Informa o estado de autenticação |
| `init-storage [--title <title>]` | Cria ou reutiliza o canal de armazenamento privado |
| `upload --file <path> [flags]` | Envia um arquivo em fragmentos |
| `download [flags]` | Baixa um arquivo armazenado |
| `list-remote` (alias `list-backups`) | Lista os itens armazenados |
| `logout` | Descarta a sessão local |

## Configuração (ambiente)

| Variável | Padrão | Significado |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Diretório de estado (sessão, configuração de destino, logs) |
| `MTPROTO_STORE_TAG` | `MTPS` | Sufixo que marca os canais de armazenamento desta ferramenta |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Seu próprio `api_id` de my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Seu próprio `api_hash` |

**Nota sobre os Termos de Serviço:** os padrões internos emulam o cliente oficial Telegram Desktop. Para suas próprias implantações, obtenha e defina seu próprio `api_id` / `api_hash` em <https://my.telegram.org> e revise os Termos de Serviço do Telegram. Você é responsável pelo uso que faz da sua conta.

### Sessões e estado

O diretório de estado guarda tudo o que a ferramenta mantém entre execuções, em `$MTPROTO_STORE_STATE`:

| Caminho | Conteúdo |
|---|---|
| `creds/telegram.session` | a **sessão** autenticada |
| `dests/telegram.json` | a referência resolvida do canal de armazenamento |
| `staging/tg_auth.json` | estado de login de curta duração (entre `send-code` e `sign-in`) |
| `logs/progress-*.json` | progresso por operação |

A **sessão é uma credencial sensível**: qualquer pessoa que consiga lê-la controla a conta, sem solicitação de senha ou 2FA. A ferramenta cria o diretório como `0700` e grava a sessão como `0600`, mas a proteção real está em *onde* você aponta `MTPROTO_STORE_STATE`. Mantenha-a em armazenamento privado. No Android especificamente, prefira o armazenamento **Credential-Encrypted** (por exemplo, em `/data/misc_ce/<user>`), que só é desbloqueado depois que o usuário se autentica, ao armazenamento **Device-Encrypted** (por exemplo, `/data/adb`, legível antes do primeiro desbloqueio).

## Créditos

O núcleo desta ferramenta foi originalmente escrito por **Ash ([@ash-iir](https://github.com/ash-iir))**, que projetou o cliente de armazenamento MTProto compilado sobre o qual ela é construída. Todo o crédito pelo trabalho original é do seu autor. Este repositório extrai, remove a marca e generaliza esse trabalho em uma ferramenta autônoma e reutilizável.

## Veja também

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - um acervo navegável e atualizado automaticamente de dados reais de `build.prop` de Pixel.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - bot de moderação anti-spam para grupos do Telegram.

## Licença

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) e contribuidores. Veja [LICENSE](LICENSE). Executar uma versão modificada como serviço de rede obriga você a oferecer o código-fonte dela.

## Contato

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
