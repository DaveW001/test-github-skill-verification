---
tool_context:
  with_tools: [bash]
name: email-to-clickup
description: Converts an email into an actionable ClickUp task and then archives the email to reach Inbox Zero. Intended for use when triaging emails that require deeper work.
triggers:
  intent:
    - task offloading
    - email to clickup
  user_phrases:
    - turn this email into a task
    - send this to clickup
    - make a task out of this
  execution_layer: graph-powershell
  cmdlets: [Get-MgUserMessage, Move-MgUserMessage]
  priority: normal
  suggest_only: false
compatibility: OpenCode skills system; Integrates Microsoft Graph PowerShell with the local ClickUp Python scripts.
---

# Email to ClickUp Task

This skill bridges the gap between your inbox and your task manager. It takes a context-heavy email and pipes it directly into ClickUp as an actionable task, enabling the user to archive the email and keep the inbox clean.

## Graph PowerShell Execution

See [reference.md](reference.md) for PowerShell cmdlets and syntax.

## Default Routing Rules
Unless overridden by the user, immediately use these defaults:
- **ClickUp Workspace ID**: `59530`
- **Dave's User ID (Assignee)**: `80264`
- **Inbox List ID**: `3984798`

## Workflow

1. **Extract Email Details**
   - Identify the source email (from a previous `outlook-inbox-triage` step or immediate user request).
   - Grab the Subject, absolute Outlook Web Link, Sender, and a short summary of the actionable body.

2. **Construct the Task Data**
   - **Task Name**: Clear, action-oriented phrase based on the email (e.g., "[Email] Review Q3 Draft from Sarah").
   - **Description**: Include a quick 1-line AI summary of *what needs to be done*, followed by the `Outlook Web Link`, and finally the raw email transcript for reference. Use Markdown formatting.

3. **Execute the Creation**
   - Ensure the ClickUp skill scripts are locally available (typically via `python C:/Users/DaveWitkin/.gemini/antigravity/skills/clickup/scripts/create_task.py`).
   - Run the bash command passing the variables:
     ```bash
     python C:/Users/DaveWitkin/.gemini/antigravity/skills/clickup/scripts/create_task.py --name "Task Name" --description "Content with markdown" --list_id 3984798 --assignees 80264
     ```
   - *Note: Adapt the bash command to the actual expected script arguments for `create_task.py` found in the clickup skill.*

4. **Archive the Email**
   - Move the email out of the main Inbox to `Archive` using Graph PowerShell:
     ```powershell
     # Resolve Archive folder ID
     $folders = Get-MgUserMailFolder -UserId $userId -Property "id,displayName"
     $archiveFolder = $folders | Where-Object { $_.DisplayName -eq 'Archive' } | Select-Object -First 1
     # Move the message
     Move-MgUserMessage -UserId $userId -MessageId $messageId -DestinationId $archiveFolder.Id
     ```
   - **Important:** Message ID changes after move. Use the returned ID for subsequent operations.

5. **Confirmation**
   - Return the link to the generated ClickUp task and confirm the email was archived.
