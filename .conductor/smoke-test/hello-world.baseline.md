# Conductor Pipeline Smoke Test Fixture

This file is a deterministic smoke-test fixture for the `/conductor-pipeline` command. It lives inside the workspace git repository at `C:\development\opencode` so that the pipeline's scope verification can use native `git diff` against a pre-edit backup.

It intentionally contains no `## Hello World` section in its baseline state. A clean pipeline run appends exactly one such section and nothing else. To reset between runs, restore this baseline (see RUNBOOK.md).
