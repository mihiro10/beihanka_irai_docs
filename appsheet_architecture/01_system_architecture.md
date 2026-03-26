# 🏗 システム仕様・アーキテクチャ設計

本ドキュメントは、「米飯課への製造依頼システム」のデータベース設計、AppSheet特有の制約ロジック、およびステートマシン（状態遷移）を解説します。

## 1. データベースアーキテクチャ (ER図)
Google Spreadsheetsを完全なバックエンドデータベースとして利用しています。
*(注意: 現場では共有iPadを利用するため、`USEREMAIL()`ではなく独自の`UserId`キーを用いて認証・記録を行っています)。*

```mermaid
flowchart TD
    %% Entities
    APP[AppSheet Frontend]
    SHEET[(Google Sheets Backend)]
    API[External API / Scripts]
    
    %% Tables
    USERS[(Users Table)]
    PRODUCTS[(Products Master)]
    GROUPS[(RequestGroups)]
    REQUESTS[(Requests - Child)]
    CHANGELOG[(ChangeLogs - Audit)]
    
    %% Relationships
    APP <-->|Reads & Writes| SHEET
    API <-->|Reads & Writes JSON| SHEET
    
    SHEET --- USERS
    SHEET --- PRODUCTS
    SHEET --- GROUPS
    
    GROUPS -->|1:N 子タスク| REQUESTS
    REQUESTS -->|1:N 監査ログ| CHANGELOG
```

## 2. 状態遷移と4日ルール (State Machine)
依頼データ（Requests）は、製造日までの残日数（4日ルール）によって厳密に操作権限が変化します。

```mermaid
stateDiagram-v2
    [*] --> 依頼中 : 生産管理がPCから作成
    
    state 依頼中 {
        [*] --> 4日以上先 : 自由に修正・削除可能
        [*] --> 4日以内 : 編集ロック (Read-Only)
    }
    
    4日以上先 --> 4日以内 : 日付経過 (TODAY() + 4)
    
    4日以内 --> 確定 : 米飯課がiPadで承認
    4日以内 --> 管理者日程調整 : 生産管理による強制上書き
    
    管理者日程調整 --> 依頼中 : ※必ず「変更理由」を強制入力
    
    確定 --> [*]
    
    %% 米飯課ブロック
    [*] --> 米飯課予定 : 米飯課が事前ブロック (14日ルール)
    米飯課予定 --> [*] : 稼働グラフ上限を即座に消費
```

## 3. 統合稼働グラフと枠制限設定
各時間帯（早朝・昼間）には「製造可能な上限時間（枠）」のパラメータが存在し、これを元に容量をコントロールしています。
*   **グラフの制限:** 統合稼働グラフは最大180分（例）までのゲージで表示されます。
*   **先取りブロック優先:** 米飯課が「予定ブロック」を入力すると、その分が事前に稼働グラフの下地として積み上げられ、生産管理側は残りの空き時間（キャパシティ）にのみジョブを割り当てられます。
*   **AppSheet APIを活用したデータ連携:** 上記のような予定データや利用枠データの抽出・外部挿入は、AppSheet APIを通じて外部システムと直接連携可能です（`tests_and_data/`参照）。

## 4. 部署別ワークフロー (Departmental Workflows)

### 👨‍💼 生産管理部門 (Production Management) のフロー
生産管理部門は主に**PC（ブラウザ）**を利用し、製造計画を立案・入力します。

```mermaid
flowchart TB
    Start(["アプリを開く"]) --> Dash["生産管理ダッシュボードを確認"]
    Dash --> Create["「新規依頼」から製造予定を追加（4日以上先の予定）"]
    Dash --> Modify{"既存の依頼を変更・削除したい"}
    Create --> Draft["依頼中としてカレンダーに登録される"]
    Modify --> CheckStatus{"現在のステータスは？"}
    CheckStatus -- 4日以内の確定済み --> Admin["通常の「削除」は不可。<br>米飯課に連絡を入れて必ず<br>「管理者日程調整」ボタンで<br>理由を入力して更新"]
    CheckStatus -- 依頼中 --> CheckDays{"対象日までの日数は？"}
    CheckDays -- 4日以上先 --> Free["変更したい依頼を「削除」し、<br>新規依頼を入れる"]
    Admin --> Log["「変更履歴」に証拠ログが保存され、<br>カレンダーの総製造数が自動更新される"]
```

### 👨‍🍳 米飯課 (Rice Department) のフロー
米飯課は主に製造現場の**共有iPad**を利用し、当日のスケジュール確認と「米飯課主導の事前予定」の枠取りを行います。
※現場の清掃や特別な作業予定は、生産管理が依頼を入れる前に枠を確保するため、必ず**14日以上前**に「米飯課予定登録」を行う必要があります。

```mermaid
flowchart TB
    A(["1日1回"]) --> B{"大口の特注、イベント<br>作業があるか?"}
    B -- あり --> C{"14日以上先か?"}
    C -- はい --> D["「米飯課予定」をiPadで事前登録"]
    C -- いいえ --> E["システム上、直前の入力は不可<br>至急「生産管理」へ直接連絡・相談する"]
    D --> F["生産管理に指定した稼働時間は対応不可となる"]
    F --> G["昼間・早朝のダッシュボード確認"]
    B -- なし --> G
    E --> G
    G --> H{"依頼された<br>4日以内の作業の実行可否"}
    H -- 問題なし --> I["「確定」押す"]
    H -- 人員/機械不足等で製造不可 --> K["生産管理へ直接電話/LINE WORKS連絡"]
    K --> L(["生産管理側でシステム上のリスケ対応"])
    L -- 調整内容の反映後 --> G
```
