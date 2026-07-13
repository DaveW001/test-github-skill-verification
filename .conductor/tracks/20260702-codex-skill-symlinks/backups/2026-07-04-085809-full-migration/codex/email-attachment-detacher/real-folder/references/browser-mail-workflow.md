# Browser Mail Attachment Workflow

## Candidate Discovery

- Use the mailbox search UI when possible: sender, product name, attachment filename, and `pdf` are good filters.
- In Proton Mail, attachments can appear as buttons in the conversation list. Clicking them may open an in-page preview with a `Download` button.
- Extract candidate rows with sender, date, subject, attachment name, and attachment size before downloading.
- Compare candidates against destination folders before mutating email state.

## Proton Mail Download Pattern

1. Claim the existing Proton tab rather than opening a new unauthenticated session.
2. Capture a DOM snapshot and identify exact attachment button names.
3. Click one attachment.
4. If Proton opens a preview, click the preview `Download` button.
5. Immediately check whether a native Save As dialog appeared. If it did, cancel it and switch strategy.
6. Check the Downloads folder for the newest file. If it has a `.tmp` or opaque name, verify the file signature before moving.
7. Move the file to the final folder with the normalized name.
8. Close the preview before continuing.

## Native Save As Dialogs

Some Windows PDF handlers intercept browser downloads and show a native Save As dialog, often titled `Save As`, with a suggested PDF filename. Browser DOM automation cannot see this dialog.

When the dialog appears:

- Stop the current download loop.
- Run `scripts/Dismiss-SaveAsDialog.ps1 -TitlePattern "Save As"` or ask the user to cancel it.
- Re-check the Downloads folder and target folder before retrying.
- Prefer changing the browser/PDF handling path before continuing, because repeated clicks will repeat the dialog.

Potential mitigations:

- Use the browser downloads button/menu only if it exposes a completed file path.
- Temporarily set Chrome/PDF behavior so PDFs download without opening in Foxit, if the user approves changing browser settings.
- Use a mailbox export/API connector when available instead of browser download clicks.

## Archiving

Archive messages only after all attachments from that message are verified in the final destination. If a conversation contains both relevant and irrelevant attachments, archive only when the user's rule covers the whole conversation.

For Proton Mail, selected conversations can produce multiple visible `Move to archive` controls because row-hover actions and the selected-message toolbar coexist. Do not use a broad text locator when more than one archive button is visible. Prefer the selected-message toolbar control at the top of the message list, verify matching subjects disappear from the inbox after the click, and leave unrelated conversations untouched.
