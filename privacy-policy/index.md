---
title: Slack Log Bot
---

# Slack Log Bot

Slack のメッセージ、スレッド返信、添付ファイルを、Google Sheets と Google Drive に保存する bot です。

## 保存先

- public channel: 共通スプレッドシートのチャンネル別タブに保存
- private channel: チャンネルごとの専用 Drive フォルダに保存
- private channel のフォルダ、スプレッドシート、添付ファイルはチャンネルメンバーにのみ共有

## 使用する Google サービス

この bot はログ保存のために、Google Sheets API と Google Drive API を使用します。
取得した Google OAuth トークンは bot の実行環境に保存し、第三者へ提供しません。

詳細は [プライバシーポリシー](privacy-policy.html) を確認してください。

ソースコード: [mikiT/slack-log-bot](https://github.com/mikiT/slack-log-bot)
