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
生産管理部門は主に**PC（ブラウザ）**を利用し、向こう2週間分の製造計画を立案・入力します。

```mermaid
flowchart TD
    A([作業開始]) --> B{米飯課の<br>事前ブロック確認}
    B -->|空きあり| C[製造依頼の作成]
    B -->|空きなし| D[他の日付・時間帯へ調整]
    
    C --> E{14日以内か?}
    E -->|Yes| F[自動で個別タスクへ分解]
    E -->|No| G[エラー: 14日以上先は入力不可]
    
    F --> H{製造日まで4日以内か?}
    H -->|No| I([通常登録完了 / 自由編集可能])
    H -->|Yes| J[システムロック発動]
    
    J --> K[「管理者日程調整」ボタンで強制上書き実行]
    K --> L[変更理由の入力・監査ログ打刻]
    L --> M([緊急登録完了])
```

### 👨‍🍳 米飯課 (Rice Department) のフロー
米飯課は主に製造現場の**共有iPad**を利用し、当日のスケジュール確認と「米飯課主導の事前予定」の枠取りを行います。

```mermaid
flowchart TD
    A([作業開始 / 出社]) --> B{保守や大口の<br>事前作業があるか?}
    
    B -->|あり| C[「米飯課予定」をiPadで事前登録]
    C --> D[稼働グラフの枠上限を即座に消費]
    D --> E
    
    B -->|なし| E[当日のダッシュボード確認]
    
    E --> F{生産管理から依頼された<br>タスクの実行可否}
    F -->|問題なし| G[製造日の4日前になったら「確定」押下]
    G --> H([製造実行])
    
    F -->|人員/機械不足等で製造不可| I[生産管理へ直接電話/LINE WORKS連絡]
    I --> J([生産管理側でシステム上のリスケ対応])
```
