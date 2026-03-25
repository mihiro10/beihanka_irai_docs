# Product Requirements Document (PRD): 米飯課への製造依頼

This document serves as the persistent source of truth regarding the behavior, intent, and schema rules for the "米飯課への製造依頼" AppSheet application.

## 1. Overview & Purpose
A **Manufacturing Request System** built with Google AppSheet and Google Spreadsheets backend. Its goal is to digitize the scheduling, requesting, and approval process of rice food production between two departments:
- **惣菜課 (Delicatessen Dept):** Requester. Inputs regular production schedules.
- **米飯課 (Rice Cooked Food Dept):** Manufacturer/Admin. Reviews requests, manages master data, inputs capacity constraints (`OverrideTime`), and approves requests.

## 2. Core Architecture
- **Tech Stack:** Google AppSheet (UI/Logic), Google Sheets (Backend / Source of Truth).
- **Identity Handling:** Run on shared tablets. `USEREMAIL()` is not used for personal identification. Requesters are selected manually via a dropdown.
- **Modification Policy:** To prevent operational errors, requesters must **delete and re-register** incorrect requests instead of directly editing existing ones.

## 3. Workflows & State Machine
The core lifecycle of a `Request` shifts through the following statuses, driven by AppSheet Action behaviors:
- `依頼中` (Requesting) ➔ Initial state upon creation by 惣菜課.
- `確定` (Confirmed) ➔ Final approval by 米飯課.
- `差し戻し` (Returned) ➔ Sent back for rework. Requires a `ReturnReason`.
- `米飯課予定` (Rice Dept Scheduled) ➔ In progress/Capacity modified by admins.

## 4. Key Business Rules
- Manual working hour constraints: If an admin modifies working hours (`OverrideTime > 0`), a `Reason` is explicitly required.
- AppSheet Visuals: The UI logic heavily relies on Virtual Columns, Slices (especially `DailyChartData`), Nested Forms (Parent-Child views), and Format Rules (e.g. `StatusColor`).
- Data consistency: Any changes to the AppSheet Schema, View, or Slice formulas *must* be tracked in a CHANGELOG.

## 5. Schema Outline
The physical Tables map specifically to English identifiers but display as Japanese labels in the app:
- **Products:** Master items list (`StdLotSize`, `RequiredTime`, `DefaultTimeSlot`).
- **Users:** Future login management (currently bypassed by the shared tablet approach).
- **RequestGroups:** Parent form clustering requests by `ProductId` and `CreatedBy`.
- **Requests:** Child form tracking the exact `TargetDate`, `LotCount`, calculated `EstTime` / `TotalAmount`, and tracking the `Status`.
