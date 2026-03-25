# 🍚 米飯課への製造依頼 (AppSheet Documentation)

AppSheetアプリ「米飯課への製造依頼」の全仕様・マニュアル・バックアップを含む統合リポジトリです。本リポジトリは、将来にわたる機能拡張やAIアシスタントの引き継ぎを目的として最適化されています。

## 📂 ディレクトリ構成 (Repository Structure)

*   **[`/user_guides/`](user_guides/)**: 現場（生産管理・米飯課）向けの操作マニュアル。
*   **[`/appsheet_architecture/`](appsheet_architecture/)**: テーブル定義、Slices、Views、Actionsの詳細な設計仕様書。完全な開発者・AI用。
*   **[`/automation_tools/`](automation_tools/)**: AppSheetの定義HTMLから仕様書（Markdown）を破壊せずに自動更新するPythonスクリプトおよびパーサー群。
*   **[`/archive/`](archive/)**: 過去の要件定義書や、抽出した生データ（JSONバックアップ）の保管庫。

## 🔄 スキーマの更新方法
アプリの機能（自動化・カラムなど）を追加・変更した際は、[`automation_tools/README.md`](automation_tools/README.md) に沿って自動更新ツールを実行し、リポジトリの設計書群を最新状態に保ってください。
