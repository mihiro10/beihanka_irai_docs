# App Data Context & Insights

This document summarizes the state of the AppSheet application's data extracted via the AppSheet API. Having this preserved structurally provides context on how the data operates in practice.

## Current Raw Data State
Based on the full API extraction performed on March 20, 2026, the live application data contains:
- **Products:** 22 items
  - These define standard items like `小袋若鶏照焼`.
  - Categories observed: `加工品` (Processed Goods), `生鮮` (Fresh Produce), etc.
- **Users:** 2 entries 
  - Represents test or literal login structures (e.g., Administrator / Requester identities). 
  - Primarily defined by Email, FullName, and Role.
- **RequestGroups:** 34 total groups
  - Acts as the parent container mapping a requester enum to a `ProductId` (e.g., "杉田", "惣菜課担当者A").
- **Requests:** 34 granular child requests
  - These span specific dates and specify granular `TimeSlot` shifts (`早朝` / `昼間`), carrying the calculation burden for capacity visualizations.

## Key Insights & Structure Logic
- **Valid Enum Context:** We identified that `CreatedBy` relies on explicit string labels established in the app settings or the `Users` table (such as `"杉田"` or `"gemini@chikuya.co.jp"`). Attempting to inject unmapped values (like `"惣菜課担当者A"`) results in API rejection (400 Bad Request).
- **Chart Workarounds:** In AppSheet, visualizing a sum of capacity per day requires flattening the data. The data accommodates this by utilizing a `DailyChartData` slice mapped to one `_ROWNUMBER` maximum per `TargetDate`, acting similarly to a `GROUP BY TargetDate` SQL query.
- **Testing Data Setup:** We successfully mapped generated Requests (for April 1st to April 7th, 2026) back to newly created RequestGroups. These were deliberately spread across statuses (`依頼中`, `確定`, `米飯課予定`) to properly stress-test the "統合稼働グラフ" (Integrated Operation Chart) views without harming real past data.

*(The raw JSON array outputs backing this analysis are permanently saved locally at `~/Chikuya_Stuff/beihanka_irai_antigravity/extracted_data/` for rapid future querying).*
