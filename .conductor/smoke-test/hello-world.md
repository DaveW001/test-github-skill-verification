# Conductor Pipeline Smoke Test Fixture

This file is a deterministic smoke-test fixture for the `/conductor-pipeline` command. It lives inside the workspace git repository at `C:\development\opencode` so that the pipeline's scope verification can use native `git diff` against a pre-edit backup.

It intentionally contains no `## Hello World` section in its baseline state. A clean pipeline run appends exactly one such section and nothing else. To reset between runs, restore this baseline (see RUNBOOK.md).

## Hello World
This section is a toy documentation example created by the Conductor pipeline as a smoke test. It is a sanity-check addition that proves the pipeline can append a small, well-scoped Markdown section without disturbing existing content. The example is intentionally simple so reviewers can verify the change quickly and confidently.
