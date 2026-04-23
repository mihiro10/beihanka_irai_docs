# 🗄 データベース・スキーマ定義 (Database Schema)

※ `tests_and_data/app_documentation.txt` から自動生成・更新されます。

## 🗂 テーブル: `Requests` (全 31 カラム)

| カラム名 | データ型 | 表示名 (Display Name) | 仮想 | App Formula / Initial Value / Description |
| :--- | :--- | :--- | :---: | :--- |
| **_RowNumber** | Number |  | - | **Desc:** Number of this row |
| **RequestId** | Text | =依頼ID | - | **Initial:** `UNIQUEID()` |
| **GroupId** | Ref | =グループID | - | - |
| **TargetDate** | Date | =製造日 | - | **Initial:** `TODAY()` |
| **ProductId** | Ref | =品目ID | - | **Initial:** `=[GroupId].[ProductId]` |
| **LotCount** | Decimal | =ロット数 | - | - |
| **LotSize** | Number | =ロット内数量 | - | **Initial:** `=[GroupId].[ProductId].[StdLotSize]` |
| **UnitType** | Enum | =数量種類（単位） | - | **Initial:** `=[ProductId].[StdUnitType]` |
| **Status** | Enum | =ステータス | - | **Initial:** `=IF(CONTAINS([ProductId].[ProductName], "米飯課予定"), "米飯課予定", "依頼中")` |
| **Requester** | Enum | =依頼元（作成者） | - | **Initial:** `=[GroupId].[CreatedBy]` |
| **CreatedAt** | DateTime | =依頼日時（作成日） | - | **Initial:** `=NOW()` |
| **Approver** | Ref | =承認者 | - | - |
| **ApprovedAt** | DateTime | =承認日時 | - | - |
| **ReturnReason** | Text | =差し戻し理由 | - | - |
| **Timeslot** | Enum | =時間帯 | - | **Initial:** `=[ProductId].[DefaultTimeSlot]` |
| **OverrideTime** | Number | =米飯稼働予定時間（分） | - | - |
| **Reason** | Text | =依頼対応不可の理由 | - | - |
| **TaskName** | Text | =作業名（表示用） | ✅ | **Formula:** `=[ProductId].[TaskName]` |
| **TotalAmount** | Decimal | =総製造数 | ✅ | **Formula:** `=IF([UnitType]="kg", [LotCount] * [LotSize], ROUND([LotCount] * [LotSize]))` |
| **EstTime** | Number | =予想稼働時間（分） | ✅ | **Formula:** `=IF([OverrideTime] > 0, [OverrideTime], ROUND([TotalAmount] * [ProductId].[TimePerUnit]))` |
| **ProductName** | Text | =品目名（表示用） | ✅ | **Formula:** `=[ProductId].[ProductName]` |
| **CalendarLabel** | Text | =カレンダー表示用 | ✅ | **Formula:** `=IF([Status] = "米飯課予定", "🚧 " & [Reason] & " (" & [EstTime] & "分)", [ProductId].[TaskName] & " : " & [TotalAmount] & [ProductId].[StdUnitType] & " (" & [EstTime] & "分)")` |
| **StatusColor** | Color |  | ✅ | **Formula:** `=SWITCH([Status], "依頼中", "Yellow", "確定", "Green", "差し戻し", "Red", "米飯課予定", "Purple", "Gray")` |
| **EstTimeMorning** | Number | =早朝稼働時間 | ✅ | **Formula:** `=IF([TimeSlot] = "早朝", [EstTime], 0)` |
| **EstTimeDay** | Number | =昼間稼働時間 | ✅ | **Formula:** `=IF([TimeSlot] = "昼間", [EstTime], 0)` |
| **ProdCalendarLabel** | Text | =統合ダッシュボード用 | ✅ | **Formula:** `=IF([Status] = "米飯課予定", "🚧 " & [Reason] & " (" & [EstTime] & "分)", [ProductName] & " - " & [TaskName] & " : " & [TotalAmount] & [UnitType] & " (" & [EstTime] & "分)")` |
| **DateAndSlot** | Text |  | ✅ | **Formula:** `=TEXT([TargetDate], "M/D") & " " & [Timeslot]` |
| **EstTotalMorning** | Number | =早朝 | ✅ | **Formula:** `=SUM(SELECT(Requests[EstTime], AND([TargetDate] = [_THISROW].[TargetDate], [TimeSlot] = "早朝")))` |
| **EstTotalDay** | Number | =昼間 | ✅ | **Formula:** `=SUM(SELECT(Requests[EstTime], AND([TargetDate] = [_THISROW].[TargetDate], [TimeSlot] = "昼間")))` |
| **Related ChangeLogs** | List | ="変更履歴" | ✅ | **Formula:** `REF_ROWS("ChangeLogs", "RequestId")`<br>**Desc:** ChangeLogs entries that reference this entry in the RequestId column |
| **Date_Instruction** | Show |  | ✅ | **Formula:** `=""` |
| **Memo** | Text | =メモ | ✅ | **Formula:** `=IF(ISBLANK([GroupId].[Memo]), "　", [GroupId].[Memo])`<br>**Desc:** グループに紐づくメモを表示（空欄時もレイアウト崩れを防ぐため全角スペースを返す） |

---

## 🗂 テーブル: `ChangeLogs` (全 13 カラム)

| カラム名 | データ型 | 表示名 (Display Name) | 仮想 | App Formula / Initial Value / Description |
| :--- | :--- | :--- | :---: | :--- |
| **_RowNumber** | Number |  | - | **Desc:** Number of this row |
| **LogId** | Text |  | - | **Initial:** `UNIQUEID()` |
| **RequestId** | Ref | ="対象依頼" | - | - |
| **NewDate** | Date | ="新規製造日" | - | - |
| **NewLotCount** | Decimal | ="新規ロット数" | - | - |
| **Reason** | Text | ="変更内容と理由" | - | - |
| **ChangedBy** | Enum | ="変更者" | - | - |
| **Timestamp** | DateTime | ="変更日時" | - | **Initial:** `NOW()` |
| **NewTotalAmount** | Decimal | =新・総製造数 | ✅ | **Formula:** `=IF([RequestId].[UnitType]="kg", [NewLotCount] * [RequestId].[LotSize], ROUND([NewLotCount] * [RequestId].[LotSize]))` |
| **TargetProductName** | Text | =”品名” | ✅ | **Formula:** `=[RequestId].[ProductName]` |
| **TargetTaskName** | Text | =”作業名” | ✅ | **Formula:** `=[RequestId].[TaskName]` |
| **Instance Id** | Text |  | - | - |
| **New step** | Ref |  | - | - |

---

## 🗂 テーブル: `Products` (全 15 カラム)

| カラム名 | データ型 | 表示名 (Display Name) | 仮想 | App Formula / Initial Value / Description |
| :--- | :--- | :--- | :---: | :--- |
| **_RowNumber** | Number |  | - | **Desc:** Number of this row |
| **ProductId** | Text | =品目ID | - | **Initial:** `=UNIQUEID()` |
| **ProductName** | Text | =品目名 | - | - |
| **Category** | Enum | =区分 | - | - |
| **TaskName** | Text | =作業名 | - | - |
| **LotUnit** | Text | =ロット単位 | - | - |
| **RequiredTime** | Number | =所要時間（分） | - | - |
| **StdLotSize** | Number | =標準ロット内数量 | - | - |
| **StdUnitType** | Enum | =標準数量種類 | - | - |
| **StorageLocation** | Text | =入庫先 | - | - |
| **DefaultTimeSlot** | Enum | =担当部署 | - | - |
| **Related RequestGroups** | List |  | ✅ | **Formula:** `REF_ROWS("RequestGroups", "ProductId")`<br>**Desc:** RequestGroups entries that reference this entry in the ProductId column |
| **Related Requests** | List |  | ✅ | **Formula:** `REF_ROWS("Requests", "ProductId")`<br>**Desc:** Requests entries that reference this entry in the ProductId column |
| **TimePerUnit** | Decimal | =単位あたりの予想時間 | ✅ | **Formula:** `=([RequiredTime] * 1.0) / [StdLotSize]` |
| **DisplayName** | Text | =品名＋作業名 | ✅ | **Formula:** `=[ProductName] & " - " & [TaskName]` |

---

## 🗂 テーブル: `RequestGroups` (全 10 カラム)

| カラム名 | データ型 | 表示名 (Display Name) | 仮想 | App Formula / Initial Value / Description |
| :--- | :--- | :--- | :---: | :--- |
| **_RowNumber** | Number |  | - | **Desc:** Number of this row |
| **GroupId** | Text | =グループID | - | **Initial:** `UNIQUEID()` |
| **ProductId** | Ref | ="対象品目ID" | - | - |
| **LotSize** | Number | =ロット内数量 | - | - |
| **UnitType** | Enum | =数量種類（単位） | - | - |
| **Memo** | Text | =メモ | - | - |
| **CreatedBy** | Text | =入力者 | - | - |
| **CreatedAt** | DateTime | =入力時 | - | **Initial:** `=NOW()` |
| **Related Requests** | List | =作業日程追加 | ✅ | **Formula:** `REF_ROWS("Requests", "GroupId")` |
| **DisplayTimeSlot** | Text | =時間帯 | ✅ | **Formula:** `=[ProductId].[DefaultTimeSlot]` |

---

## 🗂 テーブル: `Users` (全 7 カラム)

| カラム名 | データ型 | 表示名 (Display Name) | 仮想 | App Formula / Initial Value / Description |
| :--- | :--- | :--- | :---: | :--- |
| **_RowNumber** | Number |  | - | **Desc:** Number of this row |
| **UserId** | Text |  | - | **Initial:** `=UNIQUEID()` |
| **Email** | Email | =メールアドレス | - | **Desc:** =グーグルアドレス |
| **FullName** | Text | =氏名 | - | **Desc:** =アプリ画面上に表示される名前（例: 山田太郎、スペースなしで） |
| **Department** | Enum | =部署名 | - | **Desc:** =惣菜課 米飯課 （この値で権限を分ける） |
| **Role** | Enum | =権限ロール | - | **Desc:** =User Admin など（必要に応じて設定） |
| **Related Requests By Approver** | List |  | ✅ | **Formula:** `REF_ROWS("Requests", "Approver")`<br>**Desc:** Requests entries that reference this entry in the Approver column |

---

## 6. Slices (データスライス)
物理テーブルをフィルタリングする仮想ビュー。

| スライス名 | ソーステーブル | フィルター条件 (Row Filter) | 備考 (Context / Business Logic) |
| :--- | :--- | :--- | :--- |
| **Tasks_To_Approve** | Requests | `=AND([TargetDate] >= TODAY(), OR([TargetDate] < TODAY() + 4, AND([TargetDate] = TODAY() + 4, TIME(NOW()) >= "11:00:00")))` | **【中核ロジック】** 「4日前午前11時ルール」の根幹。製造日に対して今日から4日前の午前11時以降（かつ過去でない）依頼だけを抽出し、米飯課の承認待ちボードに送るための最重要スライス。 |
| **Requests_早朝** | Requests | `=[TimeSlot] = "早朝"` | カレンダーやグラフで「早朝」の案件だけを表示するための基礎フィルター。 |
| **Requests_昼間** | Requests | `=[TimeSlot] = "昼間"` | カレンダーやグラフで「昼間」の案件だけを表示するための基礎フィルター。 |
| **Tasks_To_Approve_昼間** | Requests | `=AND([TimeSlot] = "昼間", [TargetDate] >= TODAY(), OR([TargetDate] < TODAY() + 4, AND([TargetDate] = TODAY() + 4, TIME(NOW()) >= "11:00:00")))` | 4日前の午前11時以降の承認待ちデータをさらに「昼間」のみに絞ったもの。 |
| **Tasks_To_Approve_早朝** | Requests | `=AND([TimeSlot] = "早朝", [TargetDate] >= TODAY(), OR([TargetDate] < TODAY() + 4, AND([TargetDate] = TODAY() + 4, TIME(NOW()) >= "11:00:00")))` | 4日前の午前11時以降の承認待ちデータをさらに「早朝」のみに絞ったもの。 |
| **DailyChartData** | Requests | `=AND(` | 日別の稼働グラフで棒グラフの基底となるデータを揃えるためのスライス。 |
| **米飯課フォーム用データ** | Requests | `=True` | 米飯課が180分の予定ブロックを行うフォーム用の専用スライス。 |
