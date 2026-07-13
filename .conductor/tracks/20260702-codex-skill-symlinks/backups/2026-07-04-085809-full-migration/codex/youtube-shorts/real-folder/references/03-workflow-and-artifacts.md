# Workflow and Artifacts (youtube-shorts)

## Typical workflow

1. Collect inputs: topic, target persona (default "Claire"), framework, and a key evidence point.
2. Generate a draft script using the templates in `templates/`.
3. Run a quick inline review (JSON verdict) and auto-refine if needed.
4. Save the final script.
5. Optionally run a full CIO persona review and save a timestamped critique.

## Output conventions

- Topic folder: `{slug}/`
- Script filename: `sfXX-{slug}-script.md`
- Full critic review filename: `YYYY-MM-DD-HHMM-critic-review.md`

## Flags

- `--skip-review`: skips the automatic CIO review step

## Troubleshooting

- If generation returns empty output, confirm `gemini` works from your shell and that it's authenticated.
- If the script feels generic, provide a sharper evidence input (specific memo/report/policy) and re-run.
