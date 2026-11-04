<p align="center">
  <img src="docs/banner.png" alt="Slack Log Bot" width="100%">
</p>

# Slack Log Bot

Slack無料プランではメッセージ履歴が一定期間で消えてしまいます。
このbotは、Slackの投稿・スレッド返信・添付ファイルを自動で **Google スプレッドシート** と **Google Drive** に保存します。

## 特徴

- **リアルタイム収集** — Socket Modeで常駐し、投稿を即時記録。ファイルアップロードはバックグラウンド処理のためメッセージ順序が崩れない
- **週次定期収集** — 毎週自動で過去1週間のメッセージを収集
- **過去履歴の一括取り込み** — Slackコマンドまたはスクリプトで既存メッセージをバックフィル
- **Slackコマンド** — botにメンションしてURL表示・バックフィルを実行
- **スレッド対応** — 親メッセージとスレッド返信を隣接して記録。返信は背景色で区別し、**折りたたんで隠せる**。親メッセージには返信数を表示
- **発言者の識別** — 表示名のセルを人ごとに色分けし、投稿者が変わる行に区切り線を表示
- **添付ファイル保存** — PDF・画像等をSlackからダウンロードしてGoogle Driveに自動アップロード。チャンネル別フォルダで整理、Drive URLをスプレッドシートに記録
- **重複防止** — メッセージの一意ID（TS）で自動判定。何度実行しても同じメッセージは追加されない
- **変更への追従** — Slack側で表示名を変えたりメッセージを編集すると、記録済みの行にも反映される
- **削除への追従** — Slackでメッセージを削除すると、その行も消える。添付ファイルはDriveのゴミ箱へ
- **リネーム追従** — スプレッドシートはチャンネルIDで紐づくため、チャンネル名を変えてもログが分断されない
- **アクセス制御** — public channel は共有スプレッドシート、private channel は専用フォルダと専用スプレッドシートに分け、private channel のメンバーだけに共有。参加・退出に応じて自動で追従
- **保存先を選べる** — botアカウントのマイドライブ、または**共有ドライブ**。共有ドライブならファイルの所有者が組織になり、botのアカウントを失ってもログが残る
- **複数botの並行運用** — 1つのチェックアウトから、公開チャンネル用・非公開チャンネル用のように保存先ごと分けた複数のbotを動かせる
- **見やすいスプレッドシート** — グリーンヘッダー・色分け・メッセージ列11ptフォント・列幅調整・オートフィルターを自動適用

## 動作イメージ

> スクリーンショットは旧バージョンのものです（列構成・書式が現在と異なります）。


<table>
  <tr>
    <td width="50%"><strong>Slack</strong></td>
    <td width="50%"><strong>Google Sheets</strong></td>
  </tr>
  <tr>
    <td><img src="docs/screenshot_slack.png" alt="Slack側の動作イメージ"></td>
    <td><img src="docs/screenshot_sheets.png" alt="スプレッドシート側の動作イメージ"></td>
  </tr>
</table>

## プロジェクト構成

```
slack_log_bot/
├── main.py              # リアルタイム収集 (Socket Mode) + Slackコマンド
├── collect_weekly.py     # 週次定期収集 (cron/systemd timer)
├── backfill.py           # 過去履歴の一括取り込み
├── google_sheets.py      # スプレッドシート操作・書式設定
├── google_drive.py       # Drive添付ファイルアップロード
├── collector.py          # チャンネル履歴の収集（3つの入口で共用）
├── slack_utils.py        # Slackユーザー・チャンネル情報の解決
├── google_auth.py        # Google OAuth2認証（Sheets/Drive共通）
├── sheet_guide.py        # 説明タブ・チャンネル一覧タブの生成
├── migrate_to_per_channel.py     # 旧構成からの移行（共有シート→チャンネル別）
├── migrate_columns.py            # 旧構成からの移行（9列→7列）
├── cleanup_duplicate_files.py    # 重複した添付ファイルの掃除
├── relink_attachments.py         # 既存の添付セルをファイル名リンクに変換
├── config.py             # 環境変数の読み込み
├── setup.py              # セットアップウィザード（対話式）
├── slack-app-manifest.yml # Slack Appマニフェスト（貼るだけでApp設定完了）
├── requirements.txt      # Python依存パッケージ
├── .env.example          # 環境変数テンプレート
├── deploy/
│   ├── systemd/          # 複数bot用のテンプレートユニット（slack-log-bot@<名前>）
│   └── raspi/            # Raspberry Pi の cloud-init 一式
├── profiles/             # 複数bot運用時の設定（bot ごとに .env とトークン／git管理外）
└── .gitignore
```

## Slackコマンド

チャンネル内でbotにメンションすると、以下のコマンドが使えます：

| コマンド | 説明 |
|----------|------|
| `@slack-log-bot-private help` | コマンド一覧とスプレッドシートURLを表示 |
| `@slack-log-bot-private url` | そのチャンネルのスプレッドシートURLを表示 |
| `@slack-log-bot-private backfill` | そのチャンネルの過去90日分のログを即座に収集 |
| `@slack-log-bot-private backfill 30` | 過去N日分を収集（日数指定） |

## スプレッドシートの構成

public channel のログは、ルートフォルダ内の `public` フォルダに自動検出・作成される
索引スプレッドシートに、チャンネルごとのタブとして追加されます。public channel のログは、
そのスプレッドシートの共有設定に従います。

private channel は、チャンネルごとに専用の Drive フォルダとスプレッドシートを作成し、
Slack チャンネルのメンバーの Google アカウントにのみ共有されます。

```
📊 Slack ログ                      ← 索引 + public channel のログタブ
 ├── 📖 このシートについて
 ├── 📇 チャンネル一覧
 ├── #general                       ← public channel のログタブ
 └── #random                        ← public channel のログタブ

📁 Slack ログ (ルートフォルダ)
 ├── 📁 public
 │    └── 📊 Slack ログ              ← public channel のログタブ
 └── 📁 private
   └── 📁 #secret-project         ← private channel 専用フォルダ
     ├── 📊 Slack Log - #secret-project
     └── 添付ファイル
```

> public channel は同じスプレッドシートのタブなので、そのスプレッドシートを共有された人は
> public channel の各タブを閲覧できます。private channel のログを分ける必要があるため、
> private channel はチャンネルごとに別スプレッドシートにしています。

索引スプレッドシートにはログ本体は入っておらず、
`📖 このシートについて` と `📇 チャンネル一覧` に加えて、public channel のログタブを持ちます。
チャンネル一覧には public channel とそのログタブへの URL が並びます。private channel は
アクセス制御のため一覧には表示されず、専用フォルダ内のスプレッドシートを使用します。

> **メンバーのメールアドレスが必要です。** Slack プロフィールのメールアドレスを
> Google アカウントとして共有先に指定するため、`users:read.email` スコープが要ります。
> メールが取得できないメンバー（botなど）はスキップされます。

### 共有の自動同期

チャンネルのメンバー構成が変わると、共有設定も自動で追従します。

| きっかけ | 動作 |
|---------|------|
| private メンバーが**参加** | そのチャンネルのスプレッドシートと専用フォルダを自動で共有 |
| private メンバーが**退出** | そのメンバーのスプレッドシートと専用フォルダの共有を自動で解除 |
| チャンネルが**リネーム** | private のスプレッドシートとDriveフォルダの名前を追従（ログは分断されません） |
| メンバーが**表示名を変更** | 記録済みの行の表示名も書き換え、色もそのまま引き継ぐ |
| メッセージが**編集** | その行の本文を更新（行の高さも再計算） |
| メッセージが**削除** | その行を削除。添付ファイルは Drive のゴミ箱へ |
| 週次収集の実行時 | 全チャンネルで未共有のメンバーを補完（botの停止中に起きた参加を回収） |

private channel に共有する権限は**編集者**です。Google スプレッドシートのアウトライン（スレッドの
折りたたみ `+` / `−`）は閲覧権限では操作できないためです。private channel のフォルダは
添付ファイルと専用スプレッドシートをまとめて保護します。編集者による再共有は禁止し、
メンバーの1人がログを他所へ渡せないようにしています。付与したい権限より弱い権限しか
持っていない人は自動で昇格します。オーナーや、手でより強い権限を付けた人は下げません。

> メールアドレスが1件も解決できなかった場合、既存の共有は**解除されません**。
> 一時的な取得失敗でチャンネル全員がアクセスを失うのを避けるためです。

#### 共有ドライブに保存する場合

保存先フォルダが**共有ドライブ**の中にある場合も、private channel ごとのフォルダを
限定公開にした `private` 親フォルダの下に作成し、Slack メンバーだけをそのフォルダへ共有します。public channel は
共有ドライブの通常のメンバー権限に従います。

| | マイドライブ | 共有ドライブ |
|---|---|---|
| ファイルの所有者 | bot の Google アカウント | **共有ドライブ（組織）** |
| bot のアカウントを失ったら | ログも失う | ログは残る |
| チャンネルごとのアクセス制御 | 効く | `private` 親フォルダの限定公開で効く |
| 退出時の権限剥奪 | 効く | private フォルダで効く |

共有ドライブを使う場合は、bot の起動前に `private` 親フォルダを Google Drive の
「限定公開」に設定してください。channel ごとのフォルダ、専用スプレッドシート、
添付ファイルはその権限を継承します。Google Workspace 管理者の設定で限定公開を
使えない場合は、共有ドライブの管理者に設定を依頼してください。

共有ドライブのメンバーは、限定アクセスを設定していない public channel のログを閲覧できます。
private channel のログを見せる相手は Slack channel のメンバーとして管理してください。

保存先の決め方と権限の設定は、[Step 4](#step-4-保存先を決めてセットアップ) を参照してください。

### カラム

| 日時 | 表示名 | メッセージ | 添付ファイル | メッセージTS | スレッドTS |
|------|--------|-----------|-------------|-------------|-----------|

| カラム | 説明 |
|--------|------|
| 表示名 | Slackプロフィールの表示名。人ごとに背景色が付く |
| メッセージ | 投稿本文。`<@U012ABC>` のようなメンションは `@name` に、`<#C012ABC>` は `#channel` に展開される。返信がある投稿には末尾に `💬3` のように返信数が付く |
| 添付ファイル | ファイル名がGoogle Driveへのリンクになっている（複数ある場合は改行区切り） |
| メッセージTS | Slack固有のタイムスタンプID（重複判定に使用） |
| スレッドTS | スレッド親メッセージのID。返信でなければ空 |

> 外した列と理由:
> **チャンネル名** — 1チャンネル=1スプレッドシートなので全行に同じ値が並ぶだけ。
> **@ユーザー名** — 表示名と同じ人を指す二重表記。
> **パーマリンク** — 無料プランでは90日を過ぎたメッセージがSlack上で開けなくなり、
> アーカイブとして価値が出る頃にはリンクが死んでいるため
> （必要なら `https://<workspace>.slack.com/archives/<チャンネルID>/p<TSからドットを除去>` で復元できます）。

### スプレッドシートの書式

| 要素 | 書式 |
|------|------|
| ヘッダー行 | グリーン背景 + 白太字 + 固定（スクロールで隠れない） + オートフィルター |
| 表示名 | 人ごとの背景色。名前のハッシュで決まるため、**同じ人はどのチャンネルでも同じ色**（設定不要） |
| 投稿者の切り替わり | 上罫線で区切り、同じ人の連投が1つの塊に見える |
| スレッド返信 | 薄いグリーン背景。**アウトライン（行グループ）で折りたたみ可能** |
| 親メッセージ | 返信がある場合、本文末尾に `💬3` のように返信数を表示 |
| メッセージ列 | 11ptフォント + テキスト折り返し有効 |
| 行の高さ | メッセージの長さに応じて 37px（1行）〜117px（6行）で自動調整 |
| 列幅 | 合計 1030px（ノートPCの画面幅に収まる想定） |

> **スレッドの折りたたみ**: 行番号の左に出る `−` / `+` で開閉できます。左上の `1` `2` で全スレッドを一括開閉。
> 折りたたんでも Sheets は件数を表示しないため、**親メッセージ側に `💬n` を出しています**。

> 行の高さは、メッセージを列幅で折り返したときの行数から計算しています。
> 短い投稿は1行分のまま詰まり、長い投稿だけが広がります。
> ただし **6行分（117px）が上限**で、それを超える長文は表示が途中で切れます。
> **データは全文保持されており**、セルを選べば数式バーに全文が出ます。
> 上限を変えるには `google_sheets.py` の `MAX_MESSAGE_LINES` を調整してください。

### Google Drive の構成

botが作るものは、すべて1つのフォルダにまとまります。

```
📁 Slack ログ (ルートフォルダ)
 │
 ├── 📁 public
 │    ├── 📊 Slack ログ                    ← public channel のログタブ
 │         ├── 📁 #general
 │         └── 📁 #random
 │
 └── 📁 private
   ├── 📁 #hoge-private                 ← チャンネルメンバーのみ
   │    ├── 📊 Slack Log - #hoge-private
   │    └── 会議資料.pdf
   └── 📁 #fuga-private                 ← チャンネルメンバーのみ
     ├── 📊 Slack Log - #fuga-private
     └── 人事異動案.pdf
```

> `python setup.py` は再実行するたびに、索引スプレッドシートをルートフォルダへ配置します。
> private channel のフォルダとスプレッドシート、public channel の添付ファイル用フォルダは、
> それぞれの保存場所を維持します。**IDとURLは変わらない**ため、記録済みのリンクはそのまま使えます。

---

## 導入手順

### 前提条件

- Python 3.10以上（macOS標準の3.9では動きません）
- Slackワークスペースの管理者権限（アプリ作成に必要）
- Googleアカウント

---

### Step 1: Slack Appの作成

このリポジトリの [`slack-app-manifest.yml`](slack-app-manifest.yml) を貼り付けるだけで、
スコープ・イベント・Socket Mode がすべて設定済みのアプリが作られます。

#### 1-1. マニフェストからアプリを作成

1. [Slack API](https://api.slack.com/apps) にアクセス
2. **「Create New App」** → **「From an app manifest」** を選択
3. 対象のワークスペースを選んで **「Next」**
4. **YAML** タブを開き、[`slack-app-manifest.yml`](slack-app-manifest.yml) の中身をまるごと貼り付けて **「Next」**
5. 権限の確認画面が出るので **「Create」**

> アプリ名を変えたい場合は、貼り付ける前に YAML 内の `display_information.name` と
> `features.bot_user.display_name` の両方を書き換えてください。

#### 1-2. App-Level Token の生成

App-Level Token だけはマニフェストで作れないため、手動で生成します。

1. 左メニュー **「Basic Information」** → **「App-Level Tokens」** → **「Generate Token and Scopes」**
2. Token名: `socket-token`、Scope: **`connections:write`** を追加して **「Generate」**
3. 生成された `xapp-...` トークンを控えておく（この画面を閉じると再表示できません）

#### 1-3. アプリのインストール

1. 左メニュー **「Install App」** → **「Install to Workspace」**
2. 権限を確認して **「許可する」**
3. 表示される **Bot User OAuth Token**（`xoxb-...`）を控えておく
4. 記録したいチャンネルにbotを招待: `/invite @slack-log-bot-private`
   > プライベートチャンネルにも忘れずに招待してください

<details>
<summary><b>マニフェストを使わず手動で設定する場合（既存アプリに追加するときなど）</b></summary>

**OAuth & Permissions** → **Bot Token Scopes** に以下を追加:

| Scope | 用途 |
|-------|------|
| `app_mentions:read` | botへのメンションイベント受信（`app_mention` イベントに必須） |
| `channels:history` | パブリックチャンネルのメッセージ履歴読み取り |
| `channels:read` | チャンネル情報（名前等）の取得 |
| `groups:history` | プライベートチャンネルのメッセージ履歴読み取り |
| `groups:read` | プライベートチャンネル情報の取得 |
| `users:read` | 表示名の取得 |
| `users:read.email` | ユーザーのメールアドレス取得（プライベートチャンネルの共有制御に必要） |
| `files:read` | 添付ファイルのダウンロード |
| `chat:write` | botのメッセージ送信（コマンド応答に必要） |

**Event Subscriptions** → **Enable Events** をON → **Subscribe to bot events** に以下を追加:

- `message.channels` — パブリックチャンネルのメッセージ
- `message.groups` — プライベートチャンネルのメッセージ
- `app_mention` — botへのメンション（コマンド応答に必要）
- `member_joined_channel` — メンバー参加時に共有を自動追加
- `member_left_channel` — メンバー退出時に共有を自動解除
- `channel_rename` / `group_rename` — チャンネル名変更に追従
- `user_change` — 表示名の変更に追従

**Socket Mode** → **Enable Socket Mode** をON。

その後、上記 1-2（App-Level Token 生成）と 1-3（インストール）を実施してください。

> 既存アプリのマニフェストを差し替える方法もあります:
> **「App Manifest」** 画面で YAML を貼り替えて **「Save Changes」** → その後アプリの再インストールが必要です。

</details>

---

### Step 2: Google Cloudの設定

必要なのは **OAuth クライアントID を1つ作るだけ**です。
スプレッドシートと Drive フォルダは Step 4 の `setup.py` が自動で作成するため、
手で作ってIDをコピーする作業はありません。

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを新規作成（既存でも可）
2. 以下の2つのAPIを有効化:
   - **Google Sheets API** — [有効化リンク](https://console.cloud.google.com/apis/library/sheets.googleapis.com)
   - **Google Drive API** — [有効化リンク](https://console.cloud.google.com/apis/library/drive.googleapis.com)
3. **OAuth同意画面**（[Google Auth Platform](https://console.cloud.google.com/auth/overview)）を設定
  - 左メニューの **「ブランディング」** を開く
  - **アプリ名**に `Slackログ保存bot_privch対応版` を入力
  - **ユーザーサポートメール**は自分の Google アカウントを選択
  - 下部の **デベロッパーの連絡先情報**に自分のメールアドレスを入力
  - ホームページとプライバシーポリシーは、後述の GitHub Pages URL を入力
  - ロゴと利用規約 URL は個人利用なら空欄のままでよい
  - 画面下部の **「保存」** を押す
4. **[対象](https://console.cloud.google.com/auth/audience)** を開く
  - **ユーザーの種類**は **外部** を選択
  - **テストユーザー**に、Drive と Sheets を操作する自分の Google アカウントを追加
5. 必要に応じて **[データアクセス](https://console.cloud.google.com/auth/scopes)** を開き、次のスコープを追加
  - `https://www.googleapis.com/auth/spreadsheets`
  - `https://www.googleapis.com/auth/drive`
6. **[認証情報](https://console.cloud.google.com/apis/credentials) →「認証情報を作成」→「OAuth クライアント ID」**
   - アプリケーションの種類: **デスクトップアプリ**
   - 作成後、JSONをダウンロードして `client_secret.json` としてプロジェクトに配置

> ブランディング画面のアプリ名が `temp-...` のままでも動作しますが、OAuth の確認画面に表示される名前なので、
> この bot 用の名前に変更してください。**確認ステータス**の警告は、個人利用の初回設定では無視して構いません。
>
> Google Auth Platform の画面に **「外部」** が表示されない場合は、ブランディングを保存してから
> 左メニューの **「対象」** を開いてください。そこで「内部」または「外部」を選択します。
> 「内部」しか選べない場合は、Google Workspace 組織に属するプロジェクトで、管理者が外部アプリを
> 禁止している可能性があります。その場合は管理者に外部アプリの許可を依頼するか、個人利用できる
> Google Cloud プロジェクトを選択してください。

GitHub Pages の設定、公開 URL、Google OAuth への入力値は
[`docs/github-pages.md`](docs/github-pages.md) を参照してください。t

> [!IMPORTANT]
> 個人利用や動作確認だけなら、アプリを審査へ送信する必要はありません。
> **対象**の画面で自分の Google アカウントをテストユーザーに追加してください。
> 認証時に「このアプリは Google で確認されていません」と警告が出た場合は、
> **「詳細」→「（アプリ名）に移動」** で進めます。
>
> テスト中の OAuth トークンは、Google の仕様でリフレッシュトークンが7日で失効する場合があります。
> 長期間、複数ユーザーで運用する場合だけ、必要な情報を揃えて **アプリの検証**へ送信し、
> 本番環境へ切り替えてください。

---

### Raspberry Pi / ヘッドレス機で動かす場合

常時稼働させるなら Raspberry Pi 4 で十分動きます。Socket Mode なので**受信ポートを開ける必要はありません**。

**64bit版の Raspberry Pi OS（Bookworm 以降）を使ってください。**

- Bookworm は Python 3.11 なのでそのまま使えます（**Bullseye は 3.9 なので動きません**）
- 32bit版（armhf）は `cryptography` のビルド済みホイールが無く、Rust でのソースビルドになります

依存パッケージのうちネイティブ拡張を持つのは `cryptography` / `cffi` / `protobuf` /
`charset_normalizer` の4つだけで、arm64 ならすべてホイールが入ります。

`deploy/raspi/` に cloud-init 一式があります。SDカードを焼いて `user-data` と
`network-config` をブートパーティションに置けば、起動時に clone から
仮想環境の構築、systemd への登録までが済みます。ホスト名・ユーザー名・
IPアドレスは書き換えてください（`user-data` の先頭に一覧があります）。

> **認証情報はブートパーティションに置かないでください。** FAT32 は
> パーミッションを持てないので、カードを差した人なら誰でも読めます。
> `.env` と `*.json` は起動後に scp で送ります。

#### Google 認証をヘッドレスで通す

`setup.py` の Google 認証はブラウザを開いて `localhost` で受け取るため、SSH 越しだとそのままでは完了できません。方法は2つあります。

**A. SSHポートフォワード**（Pi 上で完結させたい場合）

手元の端末から:

```bash
ssh -L 8080:localhost:8080 pi@raspberrypi.local
```

Pi 側で:

```bash
python setup.py --auth-port 8080
```

表示されたURLを**手元のブラウザ**で開けば、リダイレクトがフォワード経由でPiに届きます。

**B. 認証だけ手元のPCで済ませる**（簡単）

手元のPCで `python setup.py` を通したあと、生成された `client_secret.json` と
`drive_token.json` を Pi にコピーします。`setup.py` は既存の認証を再利用するので、
Pi 側ではブラウザが不要になります。

```bash
scp client_secret.json drive_token.json pi@raspberrypi.local:~/slack-log-bot/
```

常駐は後述の [systemd の手順](#systemd-で常駐化-linux)がそのまま使えます。

---

### 複数の bot を動かす場合

1チャンネル群につき1体、という分け方ができます。たとえば公開チャンネル用と
プライベートチャンネル用で、保存先の Google アカウントごと分ける場合です。

**プロファイル**を使うと、1つのチェックアウトから複数の bot を動かせます。
コードは共有され、Slack アプリ・Google アカウント・保存先だけが分かれます。
`git pull` 1回で全部の bot が更新されます。

bot 同士は一切通信しないので、**別々のマシンで動かしても構いません**。
1台に同居させるときだけプロファイルが要ります。

```
slack-log-bot/
├── client_secret.json          ← 共通で使う場合はここ（プロファイル側にもあればそちら優先）
└── profiles/
    ├── public/
    │   ├── .env                ← Slack トークン・保存先ID
    │   └── drive_token.json    ← Google アカウントA
    └── leaders/
        ├── .env
        └── drive_token.json    ← Google アカウントB
```

セットアップは `--profile` を付けて、bot の数だけ繰り返します。

```bash
.venv/bin/python setup.py --profile public
.venv/bin/python setup.py --profile leaders
```

保存先を分けるので、[Step 4](#step-4-保存先を決めてセットアップ) の判断も bot ごとに行います。
共有ドライブに置くなら `--parent` を添えます。

```bash
.venv/bin/python setup.py --profile leaders --parent 'https://drive.google.com/drive/folders/xxxxx'
```

> **1つのチャンネルに2体 invite しないでください。** 同じ発言が両方のシートに
> 記録されます。**同じ bot を2箇所で同時に動かさないでください。** 同じアプリ
> トークンで Socket Mode 接続が二重になります。

実行時は `SLACK_LOG_PROFILE` で切り替えます。

```bash
SLACK_LOG_PROFILE=leaders .venv/bin/python main.py
SLACK_LOG_PROFILE=leaders .venv/bin/python backfill.py --days 90
```

常駐化には `deploy/systemd/` のテンプレートユニットを使います。`@` の後ろが
プロファイル名です。

```bash
sudo cp deploy/systemd/slack-log-*@.* /etc/systemd/system/
sudo systemctl enable --now slack-log-bot@public
sudo systemctl enable --now slack-log-bot@leaders
sudo systemctl enable --now slack-log-collect@public.timer
```

> `--profile` を付けずに実行すると、これまで通りチェックアウト直下の `.env` を
> 読みます。1体だけ動かしている既存の環境はそのまま動きます。

**Slack App は bot ごとに作成が必要です**（Step 1 を bot の数だけ実施）。
`features.bot_user.display_name` を `slack-log-bot-private` のように変えてください。
ASCII のみです。

**1つのチャンネルに2体 invite しないでください。** 同じ発言が両方のシートに
記録されます。

#### 別々のワークスペースで使う場合

`setup.py` が作る Drive フォルダと索引スプレッドシートには**ワークスペース名が入る**ため、
同じ Google アカウントでも混ざりません。

```
📁 Slack ログ - 研究室        ← ワークスペースA
📁 Slack ログ - サークル      ← ワークスペースB
```

> 名前を分けていないと、2つ目のワークスペースが1つ目のフォルダを名前で見つけて再利用し、
> 同名チャンネル（`#general` など）のログが同じスプレッドシートに混ざります。

Google の認証情報は使い回せます。同じ Google アカウントに保存するなら、
`client_secret.json` をチェックアウト直下に置けば全プロファイルが共有します。

---
### Step 3: botのインストール

```bash
git clone https://github.com/nnnnnnnnnke/slack-log-bot.git
cd slack-log-bot

uv venv --python 3.13 .venv
uv sync
```

> [!IMPORTANT]
> **Python 3.10 以上が必要です。**
> macOS に最初から入っている `/usr/bin/python3` は 3.9 なので、
> `python3 -m venv` だとそれを拾って `TypeError: unsupported operand type(s) for |`
> で起動に失敗します。[uv](https://docs.astral.sh/uv/) を使うか、
> 3.10以上の Python を明示してください。

<details>
<summary>uv を使わない場合</summary>

```bash
python3.13 -m venv .venv     # バージョンを明示する
.venv/bin/pip install -r requirements.txt
```

</details>

以降は `uv run` 経由で実行できます。

```bash
uv run setup.py
uv run main.py
uv run backfill.py --days 7
```

---

### Step 4: 保存先を決めてセットアップ

#### 4-1. 保存先を決める

ログの置き場所は2通りあります。**あとから移すのは面倒なので、先に決めてください。**

| | bot アカウントのマイドライブ | チームの共有ドライブ |
|---|---|---|
| 用意するもの | なし（既定） | Google Workspace の共有ドライブ |
| ファイルの所有者 | bot の Google アカウント | **組織** |
| bot のアカウントを失ったら | **ログも失う** | ログは残る |
| チャンネルごとのアクセス制御 | **効く** | 効かない（ドライブのメンバー全員が全部読める） |
| 退出時の権限剥奪 | **効く** | 効かない |

判断の目安です。

- **チャンネルごとに見せる相手を変えたい** → マイドライブ
- **bot 用アカウントに依存したくない・組織の資産にしたい** → 共有ドライブ
- **その置き場のログを全員が見てよい** → 共有ドライブでも困りません

共有ドライブを使う場合は、bot の Google アカウントを**「コンテンツ管理者」以上**
として追加してください。「投稿者」だとファイルをゴミ箱に移せず、添付の整理と、
削除されたメッセージの後片付けが動きません。

> 組織外のアカウントを共有ドライブのメンバーにできない設定になっていることが
> あります。その場合は、そのドメインのアカウントを1つ用意してください。

#### 4-2. 共有ドライブなら、先に権限を確かめる

bot がそこでやることを実際に全部試して、最後に全部消します。何も書き換えません。

```bash
uv run setup.py --check-drive 'https://drive.google.com/drive/folders/xxxxx'
```

共有ドライブを指定した場合は、private channel 用の限定アクセス設定も実際の Drive API で
確認し、テスト用に作成したフォルダ・ファイルは最後に削除します。

```
保存先の事前チェック
  ✓ フォルダを開けました: チーム共有（共有ドライブ内）
  ✓ フォルダの作成
  ✓ スプレッドシートの作成
  ✓ ファイルのアップロード（添付ファイル用）
  ✓ ゴミ箱への移動（削除されたメッセージの添付を片付ける）
  ✓ 作ったものを検索で見つけられるか
```

失敗したら、どの操作がどう失敗したかと、原因の候補を表示します。共有ドライブが
bot を拒む理由は「メンバーでない」「権限が弱い」「組織外を追加できない設定」と
複数あり、それぞれ導入手順の別々の場所で違う顔をして現れます。先にまとめて
潰せます。

#### 4-3. セットアップウィザード

```bash
python setup.py
```

保存先を共有ドライブにするなら、そのフォルダを指定します。省略すると対話で
聞かれ、そこでも空 Enter ならマイドライブに作成します。

```bash
python setup.py --parent 'https://drive.google.com/drive/folders/xxxxx'
```

> `.env` に `GOOGLE_DRIVE_FOLDER_ID` が既にある場合、保存先はその値が優先され、
> `--parent` は無視されます。移したいときは、その行を消してから実行してください。
> **既に書き込まれたファイルは移動しません**（新旧が分断されます）。

対話形式で以下をすべて実行します:

| | 内容 |
|---|---|
| 1/4 | Slackトークンの入力と接続確認 — **必要なスコープが揃っているか事前に検証**し、足りなければ名前を挙げて中断 |
| 2/4 | Googleの認証（ブラウザが開きます）→ `drive_token.json` を生成 |
| 3/4 | **スプレッドシートとDriveフォルダを自動作成**し、IDを `.env` に書き込み |
| 4/4 | 実際に開けるかを確認する書き込みテスト |

何度でも再実行できます。設定済みかつ正常な項目はスキップされるので、
途中で失敗しても最初からやり直す必要はありません。

```bash
python setup.py --reauth   # Googleの認証だけやり直す
```

<details>
<summary><b>手動で .env を設定する場合</b></summary>

既存の保存先フォルダを使いたいときは、`.env` に親フォルダ ID を直接指定します。
public/private フォルダと public スプレッドシートは、その親フォルダから自動検出されます。

```bash
cp .env.example .env
```

```ini
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
SLACK_APP_TOKEN=xapp-x-xxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxx

# Google DriveフォルダURLの /folders/ の後ろ
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here

TIMEZONE=Asia/Tokyo
```

その後 `python setup.py` を実行すれば、認証と疎通確認だけが行われます。

</details>

---

### Step 5: 動作確認

```bash
# まず過去メッセージの取り込みテスト（特定チャンネル・過去7日）
python backfill.py --channel general --days 7
```

成功すると以下のようなログが出力されます:

```
2026-03-31 09:00:01 [INFO] Backfilling #general [public]...
2026-03-31 09:00:03 [INFO] Wrote 15 messages (grouped) to #general
2026-03-31 09:00:03 [INFO]   #general: 15 new, 0 duplicates skipped
2026-03-31 09:00:03 [INFO] Backfill complete. New: 15, Skipped (duplicate): 0
```

Google スプレッドシートを開いて、メッセージが記録されていることを確認してください。

---

## 運用方法

### A. リアルタイム収集

Socket Modeで常駐させて、投稿をリアルタイムに記録します。

```bash
source .venv/bin/activate
python main.py
```

#### systemd で常駐化 (Linux)

```bash
sudo tee /etc/systemd/system/slack-log-bot.service << 'EOF'
[Unit]
Description=Slack Log Bot - Realtime (Socket Mode)
After=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/slack_log_bot
ExecStart=/home/ubuntu/slack_log_bot/.venv/bin/python main.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/log/slack-log-bot.log
StandardError=append:/var/log/slack-log-bot.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now slack-log-bot.service
```

### B. 週次定期収集

毎週自動でメッセージを収集します。重複チェック付きなので何度実行しても安全です。
リアルタイム収集との併用可能（二重記録は発生しません）。

```bash
# 過去8日分を収集（7日 + 1日の重複マージン）
python collect_weekly.py

# botが参加しているpublic channel全件
python collect_weekly.py --public

# 特定チャンネルのみ
python collect_weekly.py --channel general

# 日数を指定
python collect_weekly.py --days 14
```

#### systemd timer で自動化 (Linux)

```bash
# サービスファイル
sudo tee /etc/systemd/system/slack-log-bot-weekly.service << 'EOF'
[Unit]
Description=Slack Log Bot - Weekly Collection
After=network-online.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/slack_log_bot
ExecStart=/home/ubuntu/slack_log_bot/.venv/bin/python collect_weekly.py
StandardOutput=append:/var/log/slack-log-bot-weekly.log
StandardError=append:/var/log/slack-log-bot-weekly.log
EOF

# タイマーファイル（毎週月曜 9:00）
sudo tee /etc/systemd/system/slack-log-bot-weekly.timer << 'EOF'
[Unit]
Description=Run Slack Log Bot weekly

[Timer]
OnCalendar=Mon *-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now slack-log-bot-weekly.timer
```

### C. 過去メッセージの取り込み（バックフィル）

初回導入時や、過去のメッセージを遡って取り込みたいときに使います。
Slackからコマンドでも実行できます: `@slack-log-bot-private backfill`

```bash
# 全チャンネル・過去90日分（デフォルト）
python backfill.py

# botが参加しているpublic channel全件・過去90日分
python backfill.py --public

# 特定チャンネルのみ
python backfill.py --channel general

# 過去30日分のみ
python backfill.py --days 30
```

> Slackの無料プランでは古いメッセージは既に削除されている場合があります。
> 導入は早ければ早いほどデータを救える量が増えます。

---

## トラブルシューティング

### `エラー 403: access_denied` /「Google の審査プロセスを完了していません」

OAuth同意画面が **「テスト中」** で、自分がテストユーザーに入っていない状態です。
[対象](https://console.cloud.google.com/auth/audience) の画面で **「アプリを公開」** を実行してください
（テストユーザーに自分を追加しても通りますが、その場合トークンが7日で失効します）。

### 1週間ほど動いた後に突然 Google 認証が失敗する

OAuth同意画面が **「テスト中」** のままだと、Googleの仕様でリフレッシュトークンが
7日で失効します。同意画面を **「本番環境」** に切り替えてから、再認証してください。

```bash
python setup.py --reauth
```

### `Google の認証ファイル drive_token.json がありません`

`python setup.py` を実行してください。

### `drive_token.json に必要な権限がありません`

Sheets と Drive の認証が1本化される前のトークンです（Drive権限しか持っていません）。
`python setup.py --reauth` で認証をやり直してください。

### `public スプレッドシートが見つかりません`

親フォルダの `.env` 設定（`GOOGLE_DRIVE_FOLDER_ID`）を確認し、`uv run setup.py` を
実行してください。`public` フォルダと public 用スプレッドシートが自動作成されます。

### スコープ不足のエラーが出る

`python setup.py` の 1/4 が必要なスコープをすべて検証します。不足していれば名前を挙げるので、
`slack-app-manifest.yml` を App Manifest 画面に貼り直し、アプリを再インストールしてください。

### botがチャンネルのメッセージを取得できない

- botがチャンネルに招待されているか確認: `/invite @slack-log-bot-private`
- プライベートチャンネルの場合、`groups:history` と `groups:read` スコープがあるか確認

### botのメンションに反応しない

- Event Subscriptionsで `app_mention` が追加されているか確認
- Socket Modeが有効になっているか確認

---

## テスト

単体テストは Google API をモックしているため、`setup.py` 実行前でも実行できます。
依存関係を同期してから、次を実行します。

```bash
uv sync
uv run python -m unittest discover -s tests -v
```

Google API へ接続せず、Drive のフォルダ作成・移動をモックで検証します。

実際の Slack／Google Drive／Google Sheets との接続確認やバックフィルは、先に
`uv run setup.py` を完了させ、`.env` と `drive_token.json` を用意してから実行してください。

共有ドライブ配下への実 API 保存を確認する場合は、保存先の設定と Google 認証を済ませたうえで、
次を実行します。テスト用のフォルダ、スプレッドシート、添付ファイルを作成し、終了時に削除します。

```bash
SLACK_LOG_INTEGRATION=1 uv run python -m unittest \
  tests.test_google_drive_integration -v
```

共有ドライブの管理設定や bot の権限によって失敗する場合があります。失敗時はテスト用の
フォルダが残ることがあるため、Drive 上で `__slack-log-bot-integration-` を確認してください。

---

## ライセンス

MIT
