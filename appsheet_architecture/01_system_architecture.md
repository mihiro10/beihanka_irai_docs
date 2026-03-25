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
