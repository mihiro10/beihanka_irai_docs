# 🔄 Schema Updater (`update_app_schema.py`)

このツールは、手作業で追記した「Business Logic/Context（備考）」のコメントを消去することなく、GitHubリポジトリ内のAppSheet定義（スキーマ）を常に**最新かつ正確な状態**に保つための自動化スクリプトです。

## 実行のタイミング
AppSheet上で「新しいVirtual Column（仮想カラム）」「新しいAction（自動化動作ボタン）」「新しいSlice」を追加・変更した際にこのスクリプトを実行してください。
リポジトリ直下にある `docs/04_database_schema.md` と `docs/05_views_actions.md` が自動的に最新の状態に再構築されます。

## 使い方 (スキーマ自動更新の手順)

1. ブラウザであなたのAppSheetのアプリエディタ画面を開きます。
2. 左側の黒いサイドバーにある **歯車 (Settings)** アイコンをクリックします。
3. **Information** ＞ **App Properties** ＞ **App Documentation** の順に開きます。
4. 全データスキーマや数式（App Formula）が記載された巨大な白いテキストページが表示されます。
5. ブラウザのメニューから **「ファイル」＞「ページを別名で保存...」** （または右クリック＞名前を付けて保存）を選択します。
6. ファイル名を必ず **`Application Documentation.html`** （または `app_documentation.html`）とし、**このプロジェクトの一番上のフォルダ（ルートディレクトリ:`beihanka_irai_antigravity/`）**に保存してください。
7. Macのターミナル（Terminal.app）を開き、本リポジトリの直下で以下の実行コマンドを入力します：
   ```bash
   python3 tests_and_data/update_app_schema.py
   ```
8. **完了です！** スクリプトが自動的にHTMLファイルを裏で解析・クリーンアップし、`04_database_schema.md` と `05_views_actions.md` のMarkdownを再描写します。その際、あなたが手動で入力していた「人間向けの備考（Context）」データは、安全に旧ファイルから読み込まれ、新しい定義の隣に引き継がれます。
