[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Deutsch](README.de.md) | **Français** | [Русский](README.ru.md) | [Bahasa Indonesia](README.id.md) | [Türkçe](README.tr.md) | [Polski](README.pl.md) | [Nederlands](README.nl.md) | [Svenska](README.sv.md) | [Čeština](README.cs.md) | [Tiếng Việt](README.vi.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [فارسی](README.fa.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [ไทย](README.th.md) | [Українська](README.uk.md)

# mtproto-store

*Utilisez Telegram comme stockage d'objets illimité et fragmenté - via le protocole natif MTProto, sous la forme d'un unique binaire en ligne de commande autonome.*

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/VictorGabriel7Dev/mtproto-store)](https://github.com/VictorGabriel7Dev/mtproto-store/releases)
[![Languages](https://img.shields.io/badge/languages-22-orange.svg)](README.md)

Pas de Python, pas d'API de bot, aucun runtime externe. Un unique binaire statique en Go qui se connecte à un compte utilisateur Telegram via MTProto et stocke des fichiers arbitraires sous forme de téléversements fragmentés dans un canal privé.

## Ce qu'il fait

- Se connecte à un **compte utilisateur** Telegram (numéro de téléphone -> code de connexion -> mot de passe 2FA facultatif), en émulant le client officiel Telegram Desktop, ce qui maintient les sessions stables et évite les conflits de déconnexion avec d'autres clients.
- Stocke des fichiers arbitraires sous forme de **téléversements fragmentés** dans un canal privé, en contournant les limites de taille des bots (jusqu'à 2 GB par fichier, ou 4 GB avec Telegram Premium).
- Crée ou réutilise son propre **canal de stockage** privé, marqué d'un suffixe configurable afin de ne jamais toucher qu'à ses propres canaux.
- Renvoie les téléchargements en flux, liste les éléments stockés et affiche du JSON lisible par machine sur stdout pour faciliter l'automatisation.

Basé sur [`gotd/td`](https://github.com/gotd/td) (MTProto en Go pur).

## Compilation

```sh
CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

`-ldflags="-s -w" -trimpath` supprime les symboles de débogage et les tables DWARF (environ 23 MB -> 16 MB). Il effectue une compilation croisée statique pour n'importe quelle cible (sans CGO), et les mêmes binaires Linux statiques fonctionnent sur Android (arm64-v8a, armeabi-v7a, x86_64, x86) :

```sh
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o mtproto-store .
```

### Taille du binaire

| Compilation | Taille (une architecture) |
|---|---|
| par défaut (`go build`) | ~23 MB |
| `-s -w -trimpath` | ~16 MB |
| ci-dessus, puis `upx --best --lzma` | ~5-6 MB |

La pile MTProto (`gotd/td` plus un résolveur de camouflage TLS qui imite Telegram Desktop) représente l'essentiel de la taille. La CI publie des binaires de version **compressés avec UPX** pour chaque cible ; UPX se décompresse automatiquement au démarrage avec une surcharge négligeable. Si vous préférez ne pas distribuer de binaires compactés, la compilation `-s -w` non compressée constitue la solution de repli.

## Utilisation

Chaque commande affiche un seul objet JSON sur stdout (`"ok": true | false`).

| Commande | Rôle |
|---|---|
| `send-code --phone <number>` | Démarre la connexion ; Telegram envoie le code de connexion |
| `sign-in --phone <number> --code <code> [--password <2fa>]` | Termine la connexion |
| `bot-login --token <token>` | Se connecter en tant que bot (limité) |
| `check-auth` (alias `status`) | Indique l'état d'authentification |
| `init-storage [--title <title>] [--channel-id <id>]` | Crée ou réutilise le canal de stockage privé |
| `upload --dir <path> [flags]` | Téléverse les fichiers d'un répertoire en fragments |
| `download --ref <id> --out <path> [flags]` | Télécharge une archive stockée |
| `delete --ref <id>[,<id>...]` | Supprime un ou plusieurs éléments stockés |
| `list-remote` (alias `list-backups`) | Liste les éléments stockés |
| `logout` | Supprime la session locale |

## Configuration (environnement)

| Variable | Valeur par défaut | Signification |
|---|---|---|
| `MTPROTO_STORE_STATE` | `$HOME/.mtproto-store` | Répertoire d'état (session, configuration de destination, journaux) |
| `MTPROTO_STORE_TAG` | `MTPS` | Suffixe qui marque les canaux de stockage de cet outil |
| `MTPROTO_STORE_LABEL` | - | Nom facultatif enregistré comme `label` dans les métadonnées de chaque élément envoyé (renvoyé par `list-remote`) |
| `MTPROTO_STORE_API_ID` | Telegram Desktop | Votre propre `api_id` depuis my.telegram.org |
| `MTPROTO_STORE_API_HASH` | Telegram Desktop | Votre propre `api_hash` |

**Note sur les conditions d'utilisation :** les valeurs par défaut intégrées émulent le client officiel Telegram Desktop. Pour vos propres déploiements, obtenez et définissez votre propre `api_id` / `api_hash` sur <https://my.telegram.org> et consultez les conditions d'utilisation de Telegram. Vous êtes responsable de l'usage que vous faites de votre compte.

### Sessions et état

Le répertoire d'état contient tout ce que l'outil conserve entre les exécutions, sous `$MTPROTO_STORE_STATE` :

| Chemin | Contenu |
|---|---|
| `creds/telegram.session` | la **session** authentifiée |
| `dests/telegram.json` | la référence résolue du canal de stockage |
| `staging/tg_auth.json` | état de connexion de courte durée (entre `send-code` et `sign-in`) |
| `logs/progress-*.json` | progression par opération |

La **session est un identifiant sensible** : quiconque peut la lire contrôle le compte, sans invite de mot de passe ni de 2FA. L'outil crée le répertoire en `0700` et écrit la session en `0600`, mais la véritable protection réside dans *l'endroit* où vous pointez `MTPROTO_STORE_STATE`. Conservez-la sur un stockage privé. Sur Android en particulier, préférez le stockage **Credential-Encrypted** (par exemple sous `/data/misc_ce/<user>`), qui n'est déverrouillé qu'après l'authentification de l'utilisateur, au stockage **Device-Encrypted** (par exemple `/data/adb`, lisible avant le premier déverrouillage).

## Remerciements

Le cœur de cet outil a été initialement écrit par **Ash ([@ash-iir](https://github.com/ash-iir))**, qui a conçu le client de stockage MTProto compilé sur lequel il repose. Tout le mérite du travail original revient à son auteur. Ce dépôt extrait, démarque et généralise ce travail pour en faire un outil autonome et réutilisable.

## Voir aussi

- [**build.prop**](https://github.com/VictorGabriel7Dev/build.prop) - une archive consultable et mise à jour automatiquement de données `build.prop` réelles de Pixel.
- [**telegram-antispam-bot**](https://github.com/VictorGabriel7Dev/telegram-antispam-bot) - bot de modération anti-spam pour les groupes Telegram.

## Contact

- https://victorgabriel.dev
- **GitHub:** @VictorGabriel7Dev https://github.com/VictorGabriel7Dev
- **Telegram:** @VictorGabriel_Dev https://t.me/VictorGabriel_Dev
- **Discord:** @VictorGabriel.dev https://discord.com/users/1481407654458036265
- **LinkedIn:** in/victorgabriel-dev https://www.linkedin.com/in/victorgabriel-dev
- **Instagram:** @VictorGabriel_Dev https://www.instagram.com/VictorGabriel_Dev
- **WhatsApp:** @VictorGabriel_Dev https://wa.me/@VictorGabriel_Dev
- **E-mail:** contato@victorgabriel.dev

## Licence

**AGPL-3.0-or-later** - (C) Ash ([@ash-iir](https://github.com/ash-iir)) et contributeurs. Voir [LICENSE](LICENSE). Exécuter une version modifiée en tant que service réseau vous oblige à en proposer le code source.

---

`telegram` `mtproto` `gotd` `cloud-storage` `object-storage` `unlimited-storage` `cli` `golang` `static-binary` `cross-platform` `self-hosted` `file-storage` `chunked-upload` `mtproto-store`
