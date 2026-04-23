# プロダクト要件定義書（PRD）：米飯課への製造依頼アプリ

🤖 **AI Assistant Instructions (Cursor Context)**
このドキュメントは、Google AppSheetを利用して構築された「製造依頼システム」の仕様書です。AIアシスタント（Cursor等）は、本プロジェクトのコードや設定を提案・修正する際、以下の前提条件を遵守してください。
- **Tech Stack:** Google AppSheet, Google Sheets (Backend)
- **Naming Convention:** 物理カラム名（Google Sheets上の列名）はすべて英語。AppSheet上の Display Name で日本語化する。
- **Core Logic:** AppSheet特有の機能（Virtual Columns, Slices, Nested Forms, Format Rules）を多用してUI/UXを制御している。数式やロジックを提案する際は、AppSheetの関数仕様に従うこと。

## 1. 概要 (Overview)
惣菜課と米飯課の間で行われる米飯の製造依頼、スケジュール調整、承認プロセスをデジタル化するAppSheetアプリケーションです。Googleスプレッドシートをバックエンドデータベースとし、本番環境として安定稼働させることを目的とします。

## 2. ユーザーと権限 (Users & Security)
現在は共通タブレットでの運用を前提とするため、USEREMAIL()による個人特定は行わず、アプリ内の**「依頼元（担当者）」ドロップダウンから手動で選択**する運用とします。
- **惣菜課（依頼者）:** 定常的な製造予定を入力。既存の依頼を修正したい場合は手動編集ではなく、一度「削除」して再登録する運用（誤操作防止のため）。
- **米飯課（製造者・管理者）:** 全データの閲覧、ステータス変更（確定/差し戻し）。商品マスタの追加・編集権限、および「特注・メンテナンス等による稼働時間の直接入力（キャパシティ消費）」の権限を持つ。

## 3. アプリのコア機能とAppSheetでの実現方法

### A. 現場向けダッシュボード (早朝・昼間 分割型)
シフトによる混乱を防ぐため、「早朝」と「昼間」のダッシュボードをAppSheetの Slice 機能を用いて分離。
- **メインカレンダー:** Requests（製造依頼）を表示。「作業名・数量・予想時間」がひと目でわかる専用ラベルを表示し、ステータスで色分け。
- **直近4日間のタスクリスト:** 4日後までの未処理（Draft）予定を一覧表示し、直接承認アクションを実行可能。

### B. 管理者向け：生産管理ダッシュボード (統合型)
- **統合カレンダー:** シフトに関わらず全ての製造予定を表示。詳細な「品名＋作業名＋数量＋単位」の専用ラベルを利用。
- **統合稼働グラフ (Side-by-side Col Series Chart):**
  - *実装手法:* AppSheet標準グラフの制約を回避するため、Requests テーブルに SELECT 文を用いた日別・シフト別の合計仮想列 (`EstTotalMorning`, `EstTotalDay`) を作成。
  - *重複排除:* `MAXROW` 関数を用いた Slice (`DailyChartData`) を作成し、X軸データが重複しないよう「1日1行」にフィルタリングした上で col series チャートを描画。
- **UIアクション制御:**
  - `Requests` テーブルおよび `DailyChartData` Sliceの標準「Add」アクションに対する表示条件を `NOT(IN(CONTEXT("View"), {"生産管理カレンダー", "統合稼働グラフ", "生産管理ダッシュボード"}))` と設定することで、ダッシュボード上での子レコード直接作成を防止しつつ、親フォーム内のInline Viewにおける「New」ボタンの挙動を維持する。
  - カスタムの特注アクション「新規依頼へ」（式：`LINKTOVIEW("新規依頼")`）を作成し配置。
  - このアクションの表示条件を `CONTEXT("View") = "生産管理ダッシュボード"` とすることで、統合ダッシュボード上にのみ「新規依頼」ボタンを表示させるUI制御を実現。

### C. 製造予定の入力機能 (Forms & Actions)
Nested Form（親子フォーム）により、柔軟かつスピーディな入力UIを実現。
- **親フォーム（RequestGroups）:** 「依頼元」と「対象品目」を選択。
- **子フォーム（Requests）:** Inline Viewで「New」を押し、「製造日」と「ロット数」だけを連続追加。※親の `ProductId` を初期値として引き継ぎ、空振りを防止。
- **自動計算 (Auto Compute):** マスタ（Products）から `LotSize`, `UnitType`, `DefaultTimeSlot` を自動プレフィル。
- **時間ブロック（キャパシティ消費）:** 米飯課は専用フォームから `OverrideTime`（手動時間入力）を入力可能。入力時は `Reason`（理由）を必須とする。

### D. 承認ワークフローと履歴記録 (Slices & Actions)
- **承認:** 「確定する」ボタン（Data Change Action）によりステータスを更新。
- **日程変更 (Admin Audit Flow):** 現場の判断による「差戻し」などの複雑なループ・後退ステータスは完全廃止。対象の変更依頼が発生した際は、対象依頼を一度「確定」状態にロックした上で、特権アクション「管理者日程調整」を開く。これにより専用の `ChangeLogs` テーブルへ履歴を書き出し、『新規製造日』・『新規ロット数』・『変更理由』を必ず入力させる。保存後、AppSheet Automation(Bot) が元の `Requests` の数値を自動的に書き換える（変更経緯と責任の完璧な追跡保証）。

## 4. データスキーマ (Database Schema)

### テーブル1: Requests (依頼データ / 子テーブル)
AppSheet上の主軸となるトランザクションテーブル。
| Physical Column | Display Name | Type | Formula / Constraints / Notes |
|---|---|---|---|
| RequestId | 依頼ID | Key (Text) | `UNIQUEID()` |
| GroupId | グループID | Ref | `RequestGroups`を参照。IsPartOf = TRUE |
| TargetDate | 製造日 | Date | Required |
| TimeSlot | 時間帯（シフト） | Enum | 早朝, 昼間。Initial value: `[ProductId].[DefaultTimeSlot]` |
| ProductId | 品目ID | Ref | `Products`を参照。Initial value: `[GroupId].[ProductId]` |
| LotCount | ロット数 | Decimal | 端数(0.666等)入力可 |
| LotSize | ロット内数量 | Number | Initial value: `[ProductId].[StdLotSize]` |
| UnitType | 数量種類（単位） | Enum | 個, 切, kg等。Initial value: `[ProductId].[StdUnitType]` |
| OverrideTime | 手動時間入力(分) | Number | Show_If: `[Status]="米飯課予定"` |
| Reason | 手動入力の理由 | Text | Required_If: `[OverrideTime] > 0` |
| Status | ステータス | Enum | 依頼中, 確定, 差し戻し, 米飯課予定 |
| Requester | 依頼元（作成者） | Enum | Initial value: `[GroupId].[CreatedBy]` |
| CreatedAt | 依頼日時（作成日） | DateTime | Initial value: `NOW()` |
| Approver | 承認者 | Text | 承認アクション時に記録 |
| ApprovedAt | 承認日時 | DateTime | 承認アクション時に記録 |
| ReturnReason | 差戻し理由 | LongText | `[_INPUT]` アクションで記録 |

**Virtual Columns (Requests)**
- `TotalAmount` = `IF([UnitType]="kg", [LotCount] * [LotSize], ROUND([LotCount] * [LotSize]))`
- `EstTime` = `IF([OverrideTime] > 0, [OverrideTime], ROUND([LotCount] * [ProductId].[RequiredTime]))`
- `EstTotalMorning` = `SUM(SELECT(Requests[EstTime], AND([TargetDate] = [_THISROW].[TargetDate], [TimeSlot] = "早朝")))`
- `EstTotalDay` = `SUM(SELECT(Requests[EstTime], AND([TargetDate] = [_THISROW].[TargetDate], [TimeSlot] = "昼間")))`
- `TaskName` = `[ProductId].[TaskName]`
- `ProductName` = `[ProductId].[ProductName]`
- `CalendarLabel` = `IF([Status] = "米飯課予定", "🚧 " & [Reason], [TaskName] & " : " & [TotalAmount] & [UnitType] & " (" & [EstTime] & "分)")`
- `ProdCalendarLabel` = `IF([Status] = "米飯課予定", "🚧 " & [Reason] & " (" & [EstTime] & "分)", [ProductName] & " - " & [TaskName] & " : " & [TotalAmount] & [UnitType] & " (" & [EstTime] & "分)")`
- `StatusColor` = `SWITCH([Status], "依頼中", "Yellow", "確定", "Green", "差し戻し", "Red", "米飯課予定", "Purple", "Black")`

**Slices (Requests)**
- **Slice Name:** DailyChartData
- **Source Table:** Requests
- **Row Filter Condition:** `[_THISROW] = MAXROW("Requests", "_ROWNUMBER", ([TargetDate] = [_THISROW].[TargetDate]))`
- **Purpose:** 生産管理ダッシュボードのグラフ用に、日付の重複を排除して「1日1行」の集計データを提供する。

### テーブル2: Products (商品マスタ)
| Physical Column | Display Name | Type | Notes |
|---|---|---|---|
| ProductId | 品目ID | Key (Text) | `UNIQUEID()` |
| ProductName | 品目名 | Text | 例: 「小袋8品目のお煮しめ」 |
| Category | 区分 | Text | 例: 「加工品」「生鮮」等 |
| TaskName | 作業名 | Text | 例: 「揚げ半ぺん」 |
| LotUnit | ロット単位 | Text | 例: 「1バット」「1釜」等 |
| RequiredTime | 所要時間(分) | Number | 1ロットあたりの製造時間 |
| StdLotSize | 標準ロット内数量 | Number | 1ロットあたりの数 |
| StdUnitType | 標準数量種類 | Enum | 個, 切, kg など |
| StorageLoc | 入庫先 | Text | |
| DefaultTimeSlot | 基本シフト | Enum | 早朝, 昼間 |

### テーブル3: RequestGroups (一括依頼グループ / 親テーブル)
| Physical Column | Display Name | Type | Notes |
|---|---|---|---|
| GroupId | グループID | Key (Text) | `UNIQUEID()` |
| ProductId | 対象品目ID | Ref | `Products`を参照 |
| Memo | メモ | Text | |
| CreatedBy | 入力者（依頼元） | Enum | |
| CreatedAt | 入力日時 | DateTime | `NOW()` |

**Virtual Columns (RequestGroups)**
- `DisplayTimeSlot` = `[ProductId].[DefaultTimeSlot]` (親フォームでの事前シフト確認用)

### テーブル4: Users (ユーザーマスタ)
| Physical Column | Display Name | Type | Notes |
|---|---|---|---|
| Email | メールアドレス | Key (Email) | 将来的なログイン制御用 |
| FullName | 氏名 | Text | 担当者名 |
| Department | 部署名 | Enum | 惣菜課, 米飯課 など |
| Role | 権限ロール | Enum | Admin, User など |

## 5. 現在の開発進捗 (Progress Tracker)
- [x] TimePerUnit の仕様回避と UNIQUEID 自動採番の設定完了
- [x] スプレッドシートへの OverrideTime と Reason の追加
- [x] 米飯課のキャパシティ消費機能（ステータス自動化、Reason必須化）の実装
- [x] RequestGroups と Requests の親子連携の確立および、子フォーム ProductId の空振り問題修正
- [x] 親フォームでのシフト事前確認 UI (DisplayTimeSlot) の実装
- [x] SELECT 集計と重複排除スライス (DailyChartData) を組み合わせた「日別・時間帯別横並び比較グラフ(col series)」の構築
- [x] 端数ロット（2/3など）入力時の「総製造数」「予想稼働時間」の小数表示を防止するため、ROUND関数による整数化を実装（ただし、単位が `kg` の場合は小数を許容するよう数式を分離：`IF([UnitType]="kg", [LotCount]*[LotSize], ROUND([LotCount]*[LotSize]))`）
