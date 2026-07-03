# Review Diff Summary — `20260702-slack-skill-validation`

**Reviewer:** `conductor-plan-reviewer` (Stage 2) on `opencode-go/minimax-m3`
**Reviewed:** 2026-07-02 19:26
**Target document:** `C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\plan.md`

Three tasks were rewritten in `plan.md` after dry-run evidence showed the originals were non-executable. All rewrites were dry-run-verified end-to-end against copies of the real targets. No other Conductor artifacts were modified.

---

## Change 1 — Task 1.3 `secrets-index.jsonc` update (BLOCKING -> Ready)

### Why it changed

The plan's `$old` literal was `'"consumers": ["cursor-clickup-mcp", "conductor-reporter"]'`. The actual file content is `'"consumers": ["C:\\development\\cursor-clickup-mcp", "C:\\development\\conductor-reporter"]'`. Every consumer in `secrets-index.jsonc` is a full Windows path; the plan's bare-name pattern matched zero bytes in the real JSONC, so the original command would always throw `"Expected consumers array not found"` and never modify the file. This is the primary deliverable per the spec; it had to work.

### Dry-run evidence

```
$old = '"consumers": ["cursor-clickup-mcp", "conductor-reporter"]'
$text.Contains($old) -> False
Exception: Expected consumers array not found
```

After fix with full-path literals:

```
$old = '"consumers": ["C:\\development\\cursor-clickup-mcp", "C:\\development\\conductor-reporter"]'
$text.Contains($old) -> True
SECRETS_INDEX_EMAIL_TRIAGE_CONSUMER_PRESENT

# Post-write JSON parse (after stripping // comments):
$parsed.secrets.'slack.bot_token'.consumers
-> C:\development\cursor-clickup-mcp, C:\development\conductor-reporter, C:\development\email-triage
```

### Concrete text replaced

**Old `$old` / `$new`:**

```powershell
$old = '"consumers": ["cursor-clickup-mcp", "conductor-reporter"]'
$new = '"consumers": ["cursor-clickup-mcp", "conductor-reporter", "email-triage"]'
```

**New `$old` / `$new` (with full Windows path and post-write token guard):**

```powershell
$emailTriagePath = "C:\\development\\email-triage"
if ($text.Contains("`"$emailTriagePath`"")) { "SECRETS_INDEX_ALREADY_HAS_EMAIL_TRIAGE"; exit 0 }
$old = '"consumers": ["C:\\development\\cursor-clickup-mcp", "C:\\development\\conductor-reporter"]'
$new = '"consumers": ["C:\\development\\cursor-clickup-mcp", "C:\\development\\conductor-reporter", "C:\\development\\email-triage"]'
# ... (post-write check rejects the file if it now contains any xoxb- literal)
```

Also: post-write verification changed from `Contains($new)` to `Contains("C:\\development\\email-triage") -and -not Contains("xoxb-")` so the executor fails fast if the replace accidentally pastes in a token.

---

## Change 2 — Task 2.1 final content validation (Needs Work -> Ready)

### Why it changed

`secrets` check used `Contains('"email-triage"')` (with both leading and trailing quotes). The actual JSONC element is `C:\\development\\email-triage"` (path + closing quote only). Dry-run on the post-edit file:

```
===Checks===
secrets                        False
agents                         True
mcpSkill                       True
sendSkill                      True
```

Even after Task 1.3 succeeds, this final gate would still return `secrets -> False` and the whole track would fail its own validation.

### Dry-run evidence after fix

`Contains("C:\\development\\email-triage")` against the post-edit file returns **True**. The other three checks were already passing.

### Concrete text replaced

**Old:**

```powershell
secrets = (Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc").Contains('"email-triage"')
```

**New (also adds a `noTokenAdded` paranoid guard):**

```powershell
secrets = (Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc").Contains("C:\\development\\email-triage")
noTokenAdded = -not (Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc").Contains("xoxb-")
```

---

## Change 3 — Task 2.4 diff review (BLOCKING -> Ready)

### Why it changed

The plan used `git -C "C:\development\opencode" diff -- <four external paths>`. All four target files live in `C:\Users\DaveWitkin\.config\opencode\` or `C:\Users\DaveWitkin\.opencode-lazy-vault\`, which are not inside the opencode git repo. `git diff` errors out with `fatal: ... is outside repository` and exits 128, but the plan's authoritative acceptance check (`Output ends with DIFF_REVIEW_COMMAND_COMPLETED`) still passes because the literal string is echoed regardless of the fatal. A less capable executor would mark the task complete while the diff was actually empty and an error was suppressed.

### Dry-run evidence

```
git -C "C:\development\opencode" diff -- "C:\Users\DaveWitkin\.config\opencode\AGENTS.md" ...
fatal: ... is outside repository at 'C:/development/opencode'
DIFF_REVIEW_COMMAND_COMPLETED
===EXIT CODE: 128===
```

After fix with `git diff --no-index` against backups:

```
git diff --no-index <backup> <target>
diff --git "a/.../secrets-index.jsonc.original" "b/.../secrets-index.jsonc"
@@ -19,7 +19,7 @@
...
-    "slack.bot_token": { ... "consumers": ["C:\\development\\cursor-clickup-mcp", "C:\\development\\conductor-reporter"], ... }
+    "slack.bot_token": { ... "consumers": ["C:\\development\\cursor-clickup-mcp", "C:\\development\\conductor-reporter", "C:\\development\\email-triage"], ... }
```

Exit code 1 (diff found), no token literal anywhere in the rendered diff, just the metadata change.

### Concrete text replaced

**Old:**

```powershell
git -C "C:\development\opencode" diff -- "C:\...\AGENTS.md" "C:\...\secrets-index.jsonc" "C:\...\slack-messaging\SKILL.md" "C:\...\slack-send-message\SKILL.md"
"DIFF_REVIEW_COMMAND_COMPLETED"
```

**New (per-file `git diff --no-index` against backups, with token-presence guard and exit-code handling):**

```powershell
$backupDir = "C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\backups-20260702"
$pairs = @(
  @{ backup = "$backupDir\secrets-index.jsonc.bak"; target = "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc" }
  @{ backup = "$backupDir\AGENTS.md.bak"; target = "C:\Users\DaveWitkin\.config\opencode\AGENTS.md" }
  @{ backup = "$backupDir\slack-messaging-SKILL.md.bak"; target = "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-messaging\SKILL.md" }
)
# ... iterates, checks $LASTEXITCODE (0=no diff, 1=found, 128=hard error),
# scans captured diff for xoxb-/xoxp-/xoxo- and aborts if found,
# ends with "DIFF_REVIEW_COMMAND_COMPLETED lines=$diffLines"
```

---

## Items NOT changed (Ready as-is, with notes)

- Task 0.1, 0.2 — trivial existence / backup checks; no changes needed.
- Task 1.1 — dry-run passes; LF/CRLF fragility is real but the live file is LF and out of scope for this revision.
- Task 1.2 — dry-run passes; regex correctly skips `#fragment` and `mailto:`.
- Task 1.4 — dry-run passes; anchor `### Microsoft 365 / Outlook / Email / Calendar` confirmed at line 49 of AGENTS.md.
- Task 1.5 — dry-run passes; idempotency guard works; "Related Skills" appended cleanly.
- Task 1.6 — dry-run passes; all three conditions true.
- Task 2.2, 2.3 — trivial `Set-Content` writes; no changes needed.

## Items flagged for user decision (not applied)

- Whether to create `metadata.json` and upsert `tracks.md` / `tracks-ledger.md`. Spec does not require it; Stage 4 prompt implies it. Asking the user.
- Whether to add a behavioral test of the Python / PowerShell scripts (e.g. `--help` parse, AST parse). Out of scope per spec ("do not modify scripts") but worth flagging.

## Net effect

After applying these three rewrites, every task in the plan has a dry-run-verified authoritative acceptance check. Projected readiness: **60% -> 85%**.