# Backup Comparison and Contradiction Report

Date: 2026-07-26

## Scope

Compared all nine active policy targets against their SHA256-verified pre-edit backups using `git diff --no-index --numstat`.

| Target | Added | Deleted | Comparator exit |
|---|---:|---:|---:|
| conductor/SKILL.md | 33 | 1 | 1 (intentional difference) |
| conductor-pipeline/SKILL.md | 67 | 15 | 1 (intentional difference) |
| conductor-pipeline/references/stage-prompts.md | 63 | 6 | 1 (intentional difference) |
| conductor-pipeline/references/threshold-policy.md | 47 | 7 | 1 (intentional difference) |
| conductor track-plan.template.md | 22 | 10 | 1 (intentional difference) |
| conductor track-metadata.template.json | 10 | 2 | 1 (intentional difference) |
| conductor-pipeline/README.md | 29 | 7 | 1 (intentional difference) |
| commands/conductor-pipeline.md | 41 | 9 | 1 (intentional difference) |
| agent/conductor-pipeline-orchestrator.md | 41 | 14 | 1 (intentional difference) |

## Contradiction checks

- Active legacy bypass patterns that permit Stage 0 or Stage 2 to be skipped: 0
- Surfaces containing the explicit `gpt-5.4-mini` prohibition: 6 of 6
- Active Conductor agent assignments checked: 13
- Prohibited mini/nano/economy assignments: 0
- Metadata template JSON parse: PASS

Verdict: PASS
