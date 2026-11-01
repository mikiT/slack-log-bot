---
title: プライバシーポリシー
---

# プライバシーポリシー

最終更新日: 2026年11月1日

## 1. 概要

本プライバシーポリシーは、Slack Log Bot（以下「本 bot」）が Slack のメッセージと添付ファイルを Google Sheets および Google Drive に保存する際の、データの取り扱いを説明するものです。

本 bot は、設定された Slack ワークスペースと Google アカウントの管理者が運用する個人利用または限定利用のツールです。一般向けサービスとして利用者の情報を収集・販売するものではありません。

## 2. 取得する情報

本 bot は、Slack API を通じて次の情報を取得します。

- bot が参加している channel のメッセージとスレッド返信
- メッセージの投稿者 ID、表示名、ユーザー名
- private channel のアクセス制御に必要な Slack ユーザーのメールアドレス
- メッセージに含まれる添付ファイル
- channel の ID、名前、公開・非公開の状態、メンバー情報

## 3. 利用目的

取得した情報は、次の目的に限って利用します。

- Slack のログを Google Sheets に保存する
- Slack の添付ファイルを Google Drive に保存する
- private channel ごとの閲覧権限を Google Drive と Google Sheets に反映する
- メッセージの編集・削除、channel の名前変更、メンバーの参加・退出を保存先へ反映する

## 4. 保存先とアクセス制御

Google Sheets と Google Drive は、bot の管理者が指定した Google アカウントまたは共有ドライブに保存されます。

public channel のログは public 用のスプレッドシートに保存されます。private channel のログは channel ごとの専用フォルダとスプレッドシートに保存され、その channel のメンバーだけに共有されます。

共有ドライブを使用する場合、private channel のフォルダは Google Drive の限定アクセス設定を使用します。Google Workspace の管理者設定や共有ドライブの権限によって、この設定が利用できない場合があります。

## 5. 第三者提供

本 bot の運用者は、取得した情報を広告目的で利用したり、第三者へ販売したりしません。データは、ログ保存のために Google Sheets API、Google Drive API、Slack API を通じて各サービスへ送信されます。各サービスの利用規約とプライバシーポリシーも適用されます。

## 6. 保存期間と削除

データは、bot の運用者がログ保存のために必要とする期間保存されます。削除を希望する場合は、bot の運用者へ連絡してください。Slack でメッセージが削除された場合、本 bot は対応する行を削除し、関連する添付ファイルを Google Drive のゴミ箱へ移動します。

## 7. OAuth 権限の取り消し

Google アカウントから本 bot へのアクセスは、[Google アカウントの第三者アクセス管理](https://myaccount.google.com/permissions) からいつでも取り消せます。アクセスを取り消すと、本 bot は Google Sheets と Google Drive へログを保存できなくなります。

## 8. 連絡先

本ポリシーやデータの取り扱いに関する問い合わせは、[リポジトリ](https://github.com/mikiT/slack-log-bot) の Issue から連絡してください。