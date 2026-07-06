# Lazy-Vault Repair Report

Repaired only rows whose preview action was `repair`. Skipped rows were not guessed.

## Repair totals
- Repaired (self-referential junction with confirmed OneDrive source): 62
- Skipped (missing OneDrive source): 2
- Skipped (not self-referential / already correct): 12

## Recurrence hypothesis
OpenCode desktop or lazy-vault reconciliation may be re-pointing vault junctions to their own local paths.

## Skipped entries
- _archived_skills: skip-not-self-referential-junction
- .system: skip-not-self-referential-junction
- conductor: skip-not-self-referential-junction
- conductor-pipeline: skip-not-self-referential-junction
- git-push: skip-not-self-referential-junction
- image-to-html-reconstruction: skip-missing-source
- microsoft-graph: skip-not-self-referential-junction
- nlm-skill: skip-not-self-referential-junction
- opencode-scheduler: skip-not-self-referential-junction
- osgrep: skip-not-self-referential-junction
- perplexity-search: skip-not-self-referential-junction
- pptx-to-pdf-converter: skip-missing-source
- session-handoff: skip-not-self-referential-junction
- skill-discovery: skip-not-self-referential-junction
