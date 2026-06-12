# DiscordVoiceVox

Discord のボイスチャンネルでテキストメッセージを VOICEVOX / COEIROINK / SHAREVOX / A.I.VOICE / Aivis Speech / AquesTalk で読み上げる Bot。

---

## 目次

1. [技術仕様](#技術仕様)
2. [セットアップ](#セットアップ)
3. [環境変数リファレンス](#環境変数リファレンス)
4. [スラッシュコマンド一覧](#スラッシュコマンド一覧)
5. [ディレクトリ構成](#ディレクトリ構成)

---

## 技術仕様

### アーキテクチャ概要

```
Discord API (py-cord)
       │
  FastShardedBot        ← 自動シャーディング対応 Bot クラス
       │
  main.py               ← イベント処理・TTS ロジック・スラッシュコマンド
       │
  LavalinkClient.py     ← Lavalink 音声ストリーミングアダプター
       │
  commands/
  └─ SetAlarmCommand.py ← アラーム機能（Cog として分離）
```

### インフラ構成（Docker Compose）

```
voicevox-net (bridge network)
├── dvvox-postgres       ← PostgreSQL 16
├── dvvox-engine         ← VOICEVOX Engine（GPU 対応）
├── dvvox-lavalink       ← Lavalink 4
└── voicevox-main / voicevox-c / ...  ← Bot インスタンス（複数）
```

すべてのサービスが Docker Compose の内部ネットワーク（`voicevox-net`）で通信します。

### 外部サービス依存

| サービス | デフォルトポート | 役割 |
|---|---|---|
| VOICEVOX Engine | 50021 | TTS 音声生成（メイン） |
| COEIROINK | 50032 | 追加 TTS エンジン |
| SHAREVOX | 50025 | 追加 TTS エンジン |
| A.I.VOICE | 8001 | 追加 TTS エンジン |
| Aivis Speech | 8001 | 追加 TTS エンジン |
| AquesTalk | 8001 | 追加 TTS エンジン |
| Lavalink | 2333 | 音声ストリーミングサーバー |
| PostgreSQL | 5432 | ユーザー・ギルド設定の永続化 |

### ボイス ID 体系

| 範囲 | エンジン |
|---|---|
| 0 〜 999 | VOICEVOX |
| 1000 〜 1999 | COEIROINK |
| 2000 〜 2999 | SHAREVOX |
| 3000 〜 3999 | A.I.VOICE（録音・配信不可） |
| 4000 〜 4999 | AquesTalk（商用利用は別途ライセンス必要） |
| 5000 〜 | Aivis Speech |

### データ永続化

| ストレージ | 用途 |
|---|---|
| PostgreSQL `voice` テーブル | ユーザーごとの音声ID・速度・ピッチ設定 |
| PostgreSQL `guild` テーブル | ギルドごとの各種 on/off 設定 |
| `guild_setting/*.json` | 自動接続チャンネル・アラームなど追加設定 |
| `cache/voice_cache.json` | 生成済み音声のキャッシュ（24時間ごとにリセット） |
| `user_dict/` | カスタム読み上げ辞書・音声ファイル |
| `logs/` | ログファイル（起動日時付きファイル名） |

### メッセージ読み上げフロー

```
on_message イベント
    │
    ├─ ミュートリスト・コマンド判定（除外）
    │
    ├─ 名前読み上げ / 連投スキップ判定
    │
    ├─ テキスト前処理（URL・絵文字・メンション・スポイラー除去）
    │
    ├─ カスタム辞書変換（グローバル辞書・ギルド辞書）
    │
    ├─ インラインコマンド解析（.vN ボイス / .pN ピッチ / .sN 速度）
    │
    ├─ 翻訳（is_translate=on 時）
    │
    ├─ text2wav → VOICEVOX 系 API で音声生成
    │
    └─ Lavalink 経由でボイスチャンネルに送出
```

### Lavalink フェイルオーバー

ノード切断時に接続中プレイヤーを別ノードへ自動マイグレーション。再生位置を保持して再開（250ms 前から再生して切れ目を補完）。

### キュースピードアップ

キューが 5 件以上蓄積した場合、自動的に読み上げ速度を最大 300 まで引き上げ（`queue_speedup=on` 時、デフォルト on）。

### GPU サポート

`IS_GPU=True` + `GPU_HOST` 設定で、指定時間帯（`START_TIME`〜`END_TIME`）に GPU エンジンへリクエストを切り替え。Docker Compose では VOICEVOX Engine コンテナが NVIDIA GPU を使用します（`nvidia-ubuntu22.04` イメージ）。

### 主要ライブラリ

| ライブラリ | 役割 |
|---|---|
| py-cord[speed] | Discord API ラッパー |
| asyncpg | 非同期 PostgreSQL クライアント |
| lavalink | Lavalink クライアント |
| aiohttp[speedups] | 非同期 HTTP クライアント |
| aiodns | 非同期 DNS リゾルバー |
| ko2kana | 韓国語→カナ変換 |
| romajitable | ローマ字→カナ変換 |
| translators | 自動翻訳 |
| emoji | 絵文字テキスト変換 |
| google-re2 | 高速正規表現 |
| watchfiles | ファイル変更監視 |
| websockets | 緊急地震速報 WebSocket 受信 |
| msgspec | 高速シリアライゼーション |
| cachetools | キャッシュユーティリティ |

---

## セットアップ

### Docker Compose でのセットアップ（推奨）

VOICEVOX Engine・Lavalink・PostgreSQL はすべて Docker Compose に統合されています。別途インストール・起動は不要です。

#### 前提条件

- Docker & Docker Compose v2
- NVIDIA GPU を使用する場合: NVIDIA Container Toolkit（`nvidia-docker2`）

#### 手順

```bash
# 1. リポジトリを clone
git clone <repo_url>
cd DiscordVoiceVox

# 2. Lavalink 設定ファイルを作成
mkdir -p lavalink
cat > lavalink/application.yml << 'EOF'
server:
  port: 2333
  address: 0.0.0.0
lavalink:
  server:
    password: "change_me_lavalink_password"
    sources:
      http: true
EOF

# 3. Docker Compose 用の環境変数ファイルを作成
#    （POSTGRES_PASSWORD と LAVALINK_PASSWORD を設定）
cat > .env << 'EOF'
POSTGRES_PASSWORD=your_db_password
LAVALINK_PASSWORD=change_me_lavalink_password
EOF

# 4. Bot インスタンスの環境変数ファイルを作成
cp env/bot.env.example env/bot-main.env

# 複数インスタンス起動する場合は追加で作成
# cp env/bot.env.example env/bot-c.env

# 5. 必須項目を編集
nano env/bot-main.env
#   BOT_TOKEN=your_discord_bot_token_here
#   BOT_NICKNAME=ずんだもんβ
#   DB_PASS=your_db_password          ← POSTGRES_PASSWORD と同じ値
#   LAVALINK_PASSWORD=change_me_...   ← LAVALINK_PASSWORD と同じ値

# 6. ビルド & 起動
docker compose up --build -d

# 7. ログ確認
docker compose logs -f voicevox-main
```

> **注意:** VOICEVOX Engine の起動には最大 90 秒かかります（`start_period: 90s`）。Bot は Engine が healthy になるまで自動待機します。

#### 再デプロイ

```bash
docker compose up --build -d
```

`master` ブランチへの push で GitHub Actions が自動的に `git pull` + 上記コマンドを実行します（`.github/workflows/main.yml` で設定済み）。

#### GPU なしで動かす場合

`docker-compose.yml` の `voicevox-engine` サービスの `image` を CPU 版に変更してください。

```yaml
voicevox-engine:
  image: voicevox/voicevox_engine:cpu-ubuntu22.04-latest
```

また `deploy.resources` ブロックも削除してください。

---

### 直接実行（非 Docker）

```bash
# 1. 依存パッケージインストール
pip install -r requirements.txt

# 2. 環境変数ファイルを作成
cp env/bot.env.example .env

# 3. .env を編集（最低限 BOT_TOKEN・DB_PASS を設定）
#    DB_HOST / VOICEVOX_HOST / LAVALINK_HOST を 127.0.0.1:xxxx に変更する
nano .env

# 4. 起動
python main.py
```

非 Docker 環境では VOICEVOX Engine・Lavalink・PostgreSQL を別途ホスト上で起動してください。

---

## 環境変数リファレンス

### Bot インスタンス設定（`env/bot-main.env` など）

`env/bot.env.example` をコピーして編集してください。

#### 必須

| 変数 | 説明 |
|---|---|
| `BOT_TOKEN` | Discord Bot トークン |
| `BOT_NICKNAME` | Bot の表示名 |
| `DB_PASS` | PostgreSQL パスワード（`POSTGRES_PASSWORD` と同じ値） |

#### データベース

| 変数 | デフォルト（Docker） | 説明 |
|---|---|---|
| `DB_HOST` | `postgres` | PostgreSQL ホスト（Docker では Compose サービス名） |
| `DB_PORT` | `5432` | PostgreSQL ポート |
| `DB_NAME` | `postgres` | データベース名 |
| `DB_USER` | `postgres` | データベースユーザー |

#### TTS エンジン

| 変数 | デフォルト（Docker） | 説明 |
|---|---|---|
| `VOICEVOX_HOST` | `voicevox-engine:50021` | VOICEVOX エンジンアドレス |
| `VOICEVOX_HOSTS` | `voicevox-engine:50021` | 複数ホストをカンマ区切りで指定可 |
| `VOICEVOX_QUERY_HOST` | `voicevox-engine:50021` | クエリ専用エンジンアドレス |
| `COEIROINK_HOST` | `127.0.0.1:50032` | COEIROINK アドレス |
| `SHAREVOX_HOST` | `127.0.0.1:50025` | SHAREVOX アドレス |
| `AIVOICE_HOST` | `127.0.0.1:8001` | A.I.VOICE アドレス |
| `AIVIS_HOST` | `127.0.0.1:8001` | Aivis Speech アドレス |
| `AQUES_HOST` | `127.0.0.1:8001` | AquesTalk アドレス |

#### Lavalink

| 変数 | デフォルト（Docker） | 説明 |
|---|---|---|
| `LAVALINK_HOST` | `lavalink:2333` | `host:port` 形式。`http://` は**不要** |
| `LAVALINK_PASSWORD` | `youshallnotpass` | Lavalink 接続パスワード |
| `LAVALINK_UPLOADER` | （空） | Lavalink アップロードノード（オプション） |
| `USE_LAVALINK_UPLOAD` | `True` | Lavalink アップロード機能を使用するか |

> **正:** `LAVALINK_HOST=lavalink:2333`
> **誤:** `LAVALINK_HOST=http://lavalink:2333`

#### オプション

| 変数 | デフォルト | 説明 |
|---|---|---|
| `IS_GPU` | `False` | GPU による音声生成を有効化 |
| `GPU_HOST` | （空） | GPU エンジンのアドレス |
| `START_TIME` | `21:00` | GPU 使用開始時刻（JST） |
| `END_TIME` | `02:00` | GPU 使用終了時刻（JST） |
| `EEW_WEBHOOK_URL` | （空） | 緊急地震速報受信用 WebSocket URL |
| `GLOBAL_DICT_CHECK` | `True` | グローバル辞書チェックの有効化 |
| `USAGE_LIMIT_PRICE` | `0` | 利用制限プラン価格（0 = 制限なし） |
| `SENTRY_DSN` | （空） | Sentry エラートラッキング DSN |

### Docker Compose 共通設定（`.env`）

プロジェクトルートの `.env` に設定します（`docker-compose.yml` が参照）。

| 変数 | 説明 |
|---|---|
| `POSTGRES_PASSWORD` | PostgreSQL の root パスワード |
| `LAVALINK_PASSWORD` | Lavalink サーバーのパスワード（デフォルト: `youshallnotpass`） |

---

## スラッシュコマンド一覧

### ユーザーコマンド

| コマンド | 説明 |
|---|---|
| `/vc` | VC 読み上げ開始・終了 |
| `/skip` | 現在の読み上げをスキップ |
| `/setvc [voiceid] [speed] [pitch]` | 自分の音声・速度・ピッチを設定。引数なしで一覧表示 |
| `/setvc [voiceid] [speed] [pitch] target_user:@ユーザー` | 指定メンバーのサーバー内音声を上書き設定（manage_messages 権限必要） |
| `/set voice [id]` | ボイスを変更（引数なしで一覧表示） |
| `/set speed [値]` | 読み上げ速度を変更（50以上） |
| `/set pitch [値]` | 読み上げピッチを変更（-100〜100） |

### サーバー管理者コマンド（manage_guild 権限必要）

| コマンド | 説明 |
|---|---|
| `/server-set autojoin [on/off]` | 自動接続チャンネルを設定 |
| `/server-set reademoji [on/off]` | 絵文字の読み上げ |
| `/server-set readname [on/off]` | 発言者名の読み上げ |
| `/server-set skip_repeat_name [on/off]` | 連投時の名前読み上げスキップ |
| `/server-set queue_speedup [on/off]` | キュー蓄積時の自動速度アップ |
| `/server-set readurl [on/off]` | URL の読み上げ |
| `/server-set readjoinleave [on/off]` | 入退室の読み上げ |
| `/server-set readmention [on/off]` | メンションの読み上げ |
| `/server-set readsan [on/off]` | 名前へのさん付け |
| `/server-set translate [on/off]` | 自動翻訳（ja→en など） |
| `/server-set eew [on/off]` | 緊急地震速報通知 |
| `/server-set lang [ja/ko]` | 読み上げ言語 |
| `/server-set joinnotice [on/off]` | 接続・切断の埋め込み表示 |
| `/server-set mute-voice [id/show/off]` | 特定ボイスIDを使用禁止に設定 |
| `/server-set text_limit [文字数]` | 読み上げ文字数の上限設定 |
| `/server-set show-info` | サーバー設定情報の表示 |
| `/setalarm add/del/list` | アラームの追加・削除・一覧表示 |

### インラインコマンド（メッセージ中で使用）

メッセージに以下を含めると、その発言のみボイスや速度を一時変更できます。

| 書式 | 説明 | 例 |
|---|---|---|
| `.v[ID]` | ボイスを一時変更 | `こんにちは .v1` |
| `.p[値]` | ピッチを一時変更（-100〜100） | `こんにちは .p50` |
| `.s[値]` | 速度を一時変更（50以上） | `こんにちは .s150` |

---

## ディレクトリ構成

```
DiscordVoiceVox/
├── main.py                 # Bot 本体（イベント処理・コマンド・TTS ロジック）
├── fast_sharded_bot.py     # 自動シャーディング対応 Bot クラス
├── LavalinkClient.py       # Lavalink アダプター
├── requirements.txt        # Python 依存パッケージ
├── Dockerfile
├── docker-compose.yml      # 全サービス統合（Bot・VOICEVOX・Lavalink・PostgreSQL）
├── .env                    # Docker Compose 共通設定（POSTGRES_PASSWORD 等）
├── commands/
│   └── SetAlarmCommand.py  # アラームコマンド（Cog）
├── env/
│   ├── bot.env.example     # 環境変数テンプレート
│   ├── bot-main.env        # メインインスタンス設定（gitignore 対象）
│   └── bot-c.env ...       # 追加インスタンス設定（gitignore 対象）
├── lavalink/
│   └── application.yml     # Lavalink サーバー設定
├── guild_setting/          # ギルドごとの追加設定 JSON
├── user_dict/              # カスタム読み上げ辞書・音声ファイル
├── logs/                   # ログファイル
└── cache/
    └── voice_cache.json    # 音声キャッシュ（24時間ごとにリセット）
```
