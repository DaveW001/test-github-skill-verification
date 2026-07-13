---
name: firebase-deployment-specialist
description: Handles Firebase deployment for a Next.js project using Firebase Hosting/Functions.
triggers:
  intent:
    - firebase deployment
    - firebase nextjs deployment
    - hosting and functions rollout
  user_phrases:
    - deploy to firebase
    - deploy firebase production
    - firebase hosting
  file_context:
    extensions: [json, js, ts]
    paths: [firebase/**, functions/**, app/**]
  tool_context:
    before_tools: [bash]
    with_tools: [bash]
  error_context:
    - deploy failure
    - firebase auth or project mismatch
  priority: high
  suggest_only: true
compatibility:
  firebase_cli: ">= 12"
  node: ">= 18"
  nextjs: ">= 13"
---

# Firebase Deployment Specialist

Deploy and troubleshoot a Next.js app on Firebase Hosting (and Functions when SSR is enabled).

## When to activate

Use this skill when you need to:
- Deploy (`firebase deploy`) and verify a release.
- Fix deploy-time build failures (Next.js build, Functions build, Node runtime issues).
- Diagnose runtime issues on Firebase (404s on dynamic routes, SSR function errors).
- Configure Firebase Hosting rewrites, Functions, and environment variables.

## Activation examples

- "Deploy the current Next.js app to Firebase and verify it's live."
- "`firebase deploy` succeeded but `/solution/foo` is 404 on production."
- "Next build fails during deploy on Node 24 with a WasmHash error."
- "Hosting works but SSR routes return 500; check Functions logs and rewrites."

## Operating guidelines

- Prefer running `npm run build` before `firebase deploy` to catch errors earlier.
- Treat a successful deploy as only step 1; always validate real routes afterward.
- If a route works locally but not on Firebase, assume a Hosting rewrite / Functions SSR mismatch until proven otherwise.

## Authentication (service account)

If you want the Firebase CLI to use a service account key (instead of a personal browser login), set `GOOGLE_APPLICATION_CREDENTIALS` in the same shell session you run `firebase` commands.

Default key path used by this environment:
- `C:/development/opencode/firebase/pa-margin-calc-firebase-19150fc9bc89.json`

Windows (PowerShell):

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:/development/opencode/firebase/pa-margin-calc-firebase-19150fc9bc89.json"

# Quick verification
firebase projects:list
```

Git Bash / bash shells:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/c/development/opencode/firebase/pa-margin-calc-firebase-19150fc9bc89.json"
firebase projects:list
```

Notes:
- The key file is a secret; do not commit it and keep file permissions tight.
- Ensure the service account has deploy roles for Hosting/Functions/Firestore plus Firebase Extensions access (Viewer or Admin) and Service Usage Admin.
- If `firebase projects:list` returns no projects due org policy, verify auth by running a direct command with `--project <project-id>` (for example `firebase deploy --only firestore:rules --project pa-margin-calc-firebase`).

## Quick commands

```bash
# Deploy from repo root
firebase deploy

# Watch logs when SSR/Functions are involved
firebase functions:log

# Confirm active project/targets
firebase use
firebase target:list
```

## Progressive disclosure

Detailed troubleshooting and post-deploy validation live in:
- `references/troubleshooting-and-validation.md`
