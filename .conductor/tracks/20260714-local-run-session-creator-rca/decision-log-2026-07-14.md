# P2.3 - serve / --attach adoption decision

## Verdict

`serve`/`--attach` evaluated but not adopted; rationale: measured cold-start benchmark showed a 20.9% wall-time reduction (below the plan's 30% adoption threshold). The schema-compatibility fix (CLI 1.15.10 -> 1.18.1) is what restored reliable local runs; `serve`/`--attach` is a real but sub-threshold cold-start optimization in this environment, not a database repair.

## Evidence

| Path | Run 1 (ms) | Run 2 (ms) | Average (ms) |
| --- | --- | --- | --- |
| Standalone `opencode run --pure --format json -m opencode-go/minimax-m3 "hi"` | 8201 | 6653 | 7427 |
| Attached `opencode run --pure --format json --attach http://127.0.0.1:4097 -m opencode-go/minimax-m3 "hi"` | 6933 | 4822 | 5877.5 |

- Wall-time reduction = (7427 - 5877.5) / 7427 = **20.9%** (< 30% threshold).
- All four runs exited 0; both paths create/persist sessions and messages.
- The attached benchmark server was cleanly shut down (0 listeners on port 4097 afterwards).

## Context / honest scope note

- The 30% threshold is a deliberately conservative bar so `serve`/`--attach` is not adopted on marginal evidence. The measured ~1.5 s average saving is meaningful for batch/headless workloads but does not clear the bar for a general adoption recommendation here.
- This decision does NOT claim `serve` repaired a database defect. The RCA fix is the canonical CLI upgrade; `serve`/`--attach` is an independent operational optimization evaluated separately.