# AppSheet Data Extraction Summary

All current data from the AppSheet API has been successfully fetched and saved securely to the local workspace for future context and reference!

## Saved Locations
The raw JSON arrays are stored in the user's workspace:
`~/Chikuya_Stuff/beihanka_irai_antigravity/extracted_data/`

| Table | File | Rows | Notes |
|-------|------|------|-------|
| **Products** | `products.json` | 22 | The master list of items including required time per unit, categories, and standard lot sizes. |
| **Users** | `users.json` | 2 | Holds User emails, FullNames, Departments, and Roles. |
| **RequestGroups** | `requestgroups.json` | 34 | High-level parent groupings of the manufacturing requests. |
| **Requests** | `requests.json` | 34 | Granular daily child records containing the exact lot counts, dates, and statuses. |

## Why this is helpful
By having these records saved dynamically, the structural context of the app is preserved entirely. Moving forward, any specific bug investigations, dashboard previews, or data consistency checks can easily refer directly to the extracted json files without needing additional API hits!
