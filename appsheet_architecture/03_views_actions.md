# 📱 Views & Actions (UI & Behavior Schema)

※ `tests_and_data/app_documentation.txt` から自動生成・更新されます。

## 📱 Views (画面・UX)
| ビュー名 | ビュータイプ | 表示条件 (Show If) | 備考 (Context / Business Logic) |
| :--- | :--- | :--- | :--- |
| **生産管理ダッシュボード** | dashboard | `=IN(LOOKUP(USEREMAIL(), "Users", "Email", "Role"), {"生産管理", "Admin"})` | **生産管理のホーム画面:** 左側にカレンダー、右側に「統合稼働グラフ」を配置。米飯課ユーザーには絶対に表示されない。追加依頼ボタン（新規依頼）もここに配置されている。 |
| **米飯課予定登録** | form | `-` | 米飯課が「清掃」や「ミーティング」などの独自予定（ブロック）を積むためのポップアップフォーム。 |
| **昼間ダッシュボード** | dashboard | `-` | - |
| **早朝ダッシュボード** | dashboard | `-` | - |
| **ユーザー管理** | table | `=LOOKUP(USEREMAIL(), "Users", "Email", "Role") = "Admin"` | アプリの`Role`や部署を管理する画面。現場のタブレットは共用Emailを使うため、ここで`UserId`を基に疑似ログインを管理する。 |
| **依頼マスタ** | table | `=IN(LOOKUP(USEREMAIL(), "Users", "Email", "Role"), {"生産管理", "Admin"})` | - |
| **確定後の変更履歴** | table | `=IN(LOOKUP(USEREMAIL(), "Users", "Email", "Role"), {"米飯課", "Admin"})` | - |
| **4日後承認** | deck | `-` | 米飯課が毎朝確認する「未確定案件を右スワイプで承認（確定）していく」ためのTinderライクなUI（Deckビュー）。新設した`Memo`（メモ）をSecondary/Summary列で表示推奨。 |
| **4日後承認早朝** | deck | `-` | 早朝分の未確定案件Deckビュー。`Memo`列を表示。 |
| **4日後承認昼間** | deck | `-` | 昼間分の未確定案件Deckビュー。`Memo`列を表示。 |
| **ChangeLogs_Detail** | detail | `-` | - |
| **ChangeLogs_Form** | form | `-` | - |
| **ChangeLogs_Inline** | table | `-` | - |
| **DailyChartData_Detail** | detail | `-` | - |
| **DailyChartData_Form** | form | `-` | - |
| **Products_Detail** | detail | `-` | - |
| **Products_Form** | form | `-` | - |
| **RequestGroups_Detail** | detail | `-` | - |
| **RequestGroups_Form** | form | `-` | - |
| **RequestGroups_Inline** | table | `-` | - |
| **Requests_Detail** | detail | `-` | - |
| **Requests_Form** | form | `-` | - |
| **Requests_Inline** | table | `-` | - |
| **早朝作業詳細** | detail | `-` | - |
| **Requests_早朝_Form** | form | `-` | - |
| **昼間作業詳細** | detail | `-` | - |
| **Requests_昼間_Form** | form | `-` | - |
| **Tasks_To_Approve_Detail** | detail | `-` | - |
| **Tasks_To_Approve_Form** | form | `-` | - |
| **Tasks_To_Approve_早朝_Detail** | detail | `-` | - |
| **Tasks_To_Approve_早朝_Form** | form | `-` | - |
| **Tasks_To_Approve_昼間_Detail** | detail | `-` | - |
| **Tasks_To_Approve_昼間_Form** | form | `-` | - |
| **Users_Detail** | detail | `-` | - |
| **Users_Form** | form | `-` | - |
| **新規依頼** | form | `-` | 生産管理がダッシュボードから新規依頼フォームへジャンプするためのナビゲーションボタン。 |
| **早朝カレンダー** | calendar | `-` | - |
| **早朝稼働グラフ** | chart | `-` | - |
| **昼間カレンダー** | calendar | `-` | - |
| **昼間稼働グラフ** | chart | `-` | - |
| **生産管理カレンダー** | calendar | `-` | - |
| **米飯課カレンダー** | calendar | `-` | - |
| **米飯課ダッシュボード** | dashboard | `-` | - |
| **米飯課フォーム用データ_Detail** | detail | `-` | - |
| **米飯課フォーム用データ_Form** | form | `-` | - |
| **統合稼働グラフ（分）** | chart | `-` | 1日のキャパシティである上限目安ライン（例：180分）に対し、製品製造にかかる総分数＋米飯課の事前予定分数を積み上げる「横積みヒストグラム」。空き時間が直感でわかる最重要グラフのひとつ。 |

---

## ⚡ Actions (ボタン・振る舞い)
| アクション名 | 対象テーブル | 実行内容 (Do This) | 実行条件 (Condition) | 備考 (Context / Business Logic) |
| :--- | :--- | :--- | :--- | :--- |
| **Delete** | Requests | DELETE_RECORD | `=AND(` | 条件に注目。**「すでに確定している」または「4日前の正午以降に入っている」場合は削除アイコンが消滅し、押せなくなるガード**が実装されている。 |
| **Add** | Requests | ADD_RECORD | `=CONTEXT("ViewType") = "Form"` | - |
| **View Ref (GroupId)** | Requests | NAVIGATE_APP | `NOT(ISBLANK([GroupId]))` | - |
| **Edit** | Products | EDIT_RECORD | `-` | - |
| **Compose Email (Email)** | Users | EMAIL | `NOT(ISBLANK([Email]))` | - |
| **View Ref (ProductId)** | RequestGroups | NAVIGATE_APP | `NOT(ISBLANK([ProductId]))` | - |
| **View Ref (Approver)** | Requests | NAVIGATE_APP | `NOT(ISBLANK([Approver]))` | - |
| **Approve** | Requests | SET_COLUMN_VALUE | `=AND([Status] = "依頼中", OR([TargetDate] < TODAY() + 4, AND([TargetDate] = TODAY() + 4, TIME(NOW()) >= "12:00:00")))` | **米飯課の確定ボタン:** 4日前の正午以降に入ってきた案件のみを「確定」ステータスに変化させるアクション。Deckビューのスワイプに紐付いている。 |
| **差し戻し** | Requests | SET_COLUMN_VALUE | `=FALSE` | - |
| **Chart Data for 昼間稼働グラフ** | Requests | NAVIGATE_APP | `=CONTEXT("View") = "昼間稼働グラフ"` | - |
| **Chart Data for 早朝稼働グラフ** | Requests | NAVIGATE_APP | `=CONTEXT("View") = "早朝稼働グラフ"` | - |
| **新規依頼** | Requests | NAVIGATE_APP | `=CONTEXT("View") = "生産管理ダッシュボード"` | 生産管理がダッシュボードから新規依頼フォームへジャンプするためのナビゲーションボタン。 |
| **管理者日程調整** | Requests | NAVIGATE_APP | `=AND([Status]="確定", IN(CONTEXT("View"), {"生産管理ダッシュボード", "Requests_Detail"}))` | **強制リスケ用アクション:** 4日ロックが掛かった（＝「確定」済み）案件に対し、生産管理がどうしても割り込みや変更を行いたい場合に使うボタン。これをトリガーに`ChangeLogs`（監査ログ）発行が必須となる仕様。 |
| **View Ref (RequestId)** | ChangeLogs | NAVIGATE_APP | `NOT(ISBLANK([RequestId]))` | - |
| **Update from ChangeLog** | Requests | SET_COLUMN_VALUE | `true` | 自動Botが`ChangeLogs`のデータを元に、本体である`Requests`の数量や日付を更新する際のシステム動作用アクション。 |
| **New step Action - 1** | ChangeLogs | REF_ACTION | `true` | - |
| **予定登録追加** | Requests | NAVIGATE_APP | `=IN(CONTEXT("View"), {"昼間ダッシュボード", "早朝ダッシュボード"})` | 米飯課が独自ブロック予定（例：ミーティング120分など）をカレンダーへ入れるためのForm呼び出しボタン。 |
| **Chart Data for 統合稼働グラフ（分）** | Requests | NAVIGATE_APP | `=CONTEXT("View") = "統合稼働グラフ（分）"` | - |
