# IDs and Lists

## Workspace

- Workspace ID: `59530`

## User

- Dave user ID: `80264`

## Lists

- Inbox list: `3984798`
- Meeting Notes list: `901107655225`
- Business Development list: `901103985125`

When the user asks for a specific list but doesn't provide an ID, prefer searching / listing options rather than guessing.


## Critical ID-Type Rule

- Task creation endpoint requires a **List ID** (`/list/{list_id}/task`).
- A **Folder ID** is not a valid substitute and can return confusing errors (including 401/404 depending on endpoint).
- Quick check: if the user says "Marketing list," do not assume the Marketing folder ID is the list ID.

## Commonly Confused IDs

- Marketing folder ID: `2906846` (container)
- Marketing list ID: `3985253` (use this for creating tasks in Marketing list)

## Fast Verification Pattern

1. Confirm token validity first (`GET /team` should return 200).
2. Resolve target list ID from folder (`GET /folder/{folder_id}/list`).
3. Create task using the resolved **list** ID.
