# Troubleshooting and Validation

Use these deeper references when Firebase deployments succeed but the site behaves incorrectly, builds fail, or routing differs between local and hosted.

## Authentication errors (service account)

If you see errors like "Your credentials are no longer valid" or you want to avoid browser login, authenticate the Firebase CLI via a service account key using `GOOGLE_APPLICATION_CREDENTIALS`.

Windows (PowerShell):

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:/development/opencode/firebase/pa-margin-calc-firebase-19150fc9bc89.json"
firebase projects:list
```

Git Bash / bash shells:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/c/development/opencode/firebase/pa-margin-calc-firebase-19150fc9bc89.json"
firebase projects:list
```

Notes:
- Set the env var in the same shell session you run `firebase deploy`.
- Ensure the service account has deploy roles for Hosting/Functions/Firestore, plus Firebase Extensions access (Viewer/Admin) and Service Usage Admin.

## 403 from firebaseextensions.googleapis.com

Symptom:
- Deploying functions fails with `Request to https://firebaseextensions.googleapis.com/... had HTTP Error: 403, The caller does not have permission`.

Cause:
- The service account can deploy functions/build artifacts but cannot list Firebase Extensions instances (the CLI checks this during function deploy).

Fix:
- Grant one of these roles to the deploy service account on the Firebase project:
  - `Firebase Extensions Viewer` (minimum)
  - `Firebase Extensions Admin` (superset)
- Also grant `Service Usage Admin` if API enablement checks fail during deploy.

Validation:
```bash
GOOGLE_APPLICATION_CREDENTIALS="/c/development/opencode/firebase/pa-margin-calc-firebase-19150fc9bc89.json" firebase deploy --only functions --project pa-margin-calc-firebase
```

## Node 24+ build failure (WasmHash)

Symptom during `next build` (often triggered by `firebase deploy` running a build):
- `TypeError: Cannot read properties of undefined (reading 'length')` at `WasmHash._updateWithBuffer`

Cause:
- Known incompatibility between Node 24+ and some webpack hashing defaults used by Next.js/webpack.

Fix:
- In `next.config.mjs`, override the webpack hash function:

```js
webpack: (config) => {
  config.output.hashFunction = 'sha256'
  return config
},
```

Notes:
- Keep this in place as long as the environment runs Node 24+.
- If upgrading Next.js resolves the issue in the future, re-test before removing.

## Prerendering errors during build

Symptoms:
- Errors like `Cannot read properties of undefined (reading 'call')` during prerendering.

Likely causes:
- A server-only module imported into a client context.
- Environment variables missing at build time.

What to do:
1. Inspect `firebase-debug.log` for the full stack trace.
2. Re-run `npm run build` locally with the same env vars you expect in CI.

## Dynamic routes return 404 on Firebase (but work locally)

Symptoms:
- A route like `/solution/[slug]` works locally but returns 404 after deploy.

Likely causes:
- The Cloud Function backing SSR is failing, timing out, or misrouted.

Primary mitigation:
- Prefer SSG for known slugs by implementing `generateStaticParams` so the pages are pre-rendered and served directly by Hosting.

## Post-deploy validation checklist

Run these after every deploy to confirm the site works beyond "deploy succeeded":

1. Check HTTP status:

```bash
# Home page
curl -I https://<your-site>.web.app/

# A critical dynamic route - replace with a known valid slug
curl -I https://<your-site>.web.app/solution/<known-slug>
```

2. If you see 404/500, inspect function logs:

```bash
firebase functions:log
```

3. Confirm Firebase project + target:
- `firebase use`
- `firebase target:list`

4. If the function is crashing, re-check:
- runtime Node version configured for functions
- required env vars for SSR paths
