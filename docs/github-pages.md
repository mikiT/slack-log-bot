# GitHub Pages の設定

Google OAuth のホームページとプライバシーポリシーを公開するために、GitHub Pages を使用します。

## 公開される内容

GitHub Actions が `privacy-policy/` ディレクトリだけを Pages artifact として公開します。
`docs/` やリポジトリ全体が公開されるわけではありません。

公開 URL:

```text
https://mikiT.github.io/slack-log-bot/
https://mikiT.github.io/slack-log-bot/privacy-policy.html
```

## GitHub 側の設定

リポジトリの **Settings → Pages** を開き、Source を **GitHub Actions** に設定します。

workflow は次のブランチへの push で実行されます。

- `feat/private-channel-drive-layout`（作業中の確認用）
- `main`（マージ後の正式公開用）

feature ブランチで試す場合、`github-pages` environment の **Deployment branches and tags** に
`feat/private-channel-drive-layout` を追加してください。設定されていない場合、環境保護ルールによって
デプロイが拒否されます。

## Google OAuth の入力値

Google Auth Platform のブランディング画面には、次を入力します。

```text
承認済みドメイン: mikiT.github.io
アプリケーションのホームページ: https://mikiT.github.io/slack-log-bot/
プライバシーポリシー: https://mikiT.github.io/slack-log-bot/privacy-policy.html
```

`mikiT.github.io` の所有権確認を求められた場合は、Google Search Console の案内に従って確認してください。
