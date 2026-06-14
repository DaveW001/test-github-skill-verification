# Plan: OpenCode Desktop Config Troubleshooting

Important: `plan.md` is the authoritative source of truth for task progress.

## Phase 1 - Evidence Baseline

- [x] Locate OpenCode repo and existing conductor state.
- [x] Check May 18 git commits and working tree changes in `C:\development\opencode`.
- [x] Search config, Desktop state, and cache files modified on May 18.
- [x] Read May 18 Desktop logs and extract first-pass anomalies.
- [x] Capture exact current versions and paths:
  - `where opencode`
  - `opencode --version`
  - `opencode debug config`
  - relevant `OPENCODE_*` and `XDG_*` environment variables
- [x] Identify the relevant prior dual-subscription track.
- [x] Confirm current config contains `go-dave` and `go-tiberius` provider blocks.
- [x] Confirm the Go API key variables are not set in Windows User or current Process environment.
- [x] Confirm prior Desktop env-var documentation says `.env` does not reliably propagate into Desktop.
- [x] Snapshot current global config, Desktop state inventory, and plugin cache inventory into `artifacts/`.
- [x] Review prior conductor tracks for intended final state and rollback notes.

## Phase 2 - Reproduce And Classify

- [ ] Ask user for the exact Desktop symptom if not observable locally.
- [x] Start Desktop or inspect latest Desktop logs after a fresh restart.
- [ ] Classify failure as one of:
  - Go provider missing API key in Desktop
  - Go provider display/switching ambiguity in `/models`
  - startup/config parse failure
  - plugin loading failure
  - skill loading/duplication failure
  - provider/model/auth failure
  - scheduler/Desktop state failure
  - unrelated app state issue
- [ ] Record the failure signature in `execution-log.md`.

## Phase 3 - Config And State Diff

- [x] Compare `opencode.jsonc` against the latest relevant backups:
  - `opencode.jsonc.backup-20260517-dual-go-sub`
  - `opencode.jsonc.backup-20260509-remove-snippets`
  - `opencode.jsonc.backup-20260517-dual-go-sub`
- [x] Compare `tui.json` against the effective plugin/config expectation.
- [ ] Check whether Desktop `.dat` files contain stale workspace roots or stale config references.
- [ ] Confirm whether both `skill` and `skills` directories are present and whether either is a junction.
- [ ] Confirm whether `.agents\skills` and `.config\opencode\skills` point to the same lazy vault or duplicate real files.
- [ ] Inspect Skillful config and cache for its active `basePath` list.
- [x] Compare `.env`-only Go key storage against Windows user-level env-var requirements documented in `docs\reference\environment-variables.md`.
- [x] Determine whether native provider names `go-dave` and `go-tiberius` can be made visible in `/models`, or whether OpenCode normalizes both to `opencode-go`.

## Phase 4 - Fix Candidate

- [ ] Choose the smallest reversible fix based on evidence:
  - remove or rename stale duplicate skill root
  - repair junction target
  - correct Skillful basePath
  - restore missing CLI path/sync target
  - clear only targeted Desktop cache/state after backup
  - restore plugin entry or provider model setting
  - promote `OPENCODE_GO_DAVE_API_KEY` and `OPENCODE_GO_TIBERIUS_API_KEY` to Windows user-level env vars and document them
  - adjust provider/model naming if `/models` cannot distinguish the two subscriptions
- [x] Create timestamped backups for every file or state artifact changed.
- [x] Apply one fix at a time; do not combine unrelated changes.
- [x] Record exact commands and file changes in `execution-log.md`.

## Phase 5 - Validation

- [x] Run `opencode debug config` and confirm:
  - plugin list matches intended global config
  - `oc-codex-multi-auth` is present
  - model defaults and OpenAI/Google providers parse
- [x] Confirm `OPENCODE_GO_DAVE_API_KEY` and `OPENCODE_GO_TIBERIUS_API_KEY` resolve in a fresh process without reading `.env`.
- [x] Confirm `opencode models` exposes the Go model catalog and document whether it differentiates accounts.
- [x] Run a CLI smoke test with `opencode run -m opencode-go/glm-5.1`.
- [x] Restart OpenCode Desktop and capture the newest log.
- [x] Verify the newest log has no repeated Skillful initialization loop.
- [x] Verify duplicate skill warnings are gone or reduced to documented expected duplicates.
- [x] Run a Desktop smoke test:
  - load a normal workspace
  - invoke one lazy skill search/use path
  - run one OpenAI/Codex model prompt
  - verify no auth loop or provider model error
- [x] Document residual warnings and whether they are blocking.

## Phase 6 - Closeout

- [ ] Write final diagnostic report with root cause, fix, validation evidence, and rollback.
- [ ] Update `metadata.json` status/phase.
- [ ] Update `.conductor/tracks-ledger.md`.
- [ ] Do not mark complete until validation passes and artifacts are present.
