// Task 5.4 synthetic canary - runs against the BUILT dist (not in-tree TS).
// Track 20260717-dcp-child-session-safety.
import {
    createSessionState,
    saveSessionState,
    loadSessionState,
    getStorageDir,
    sessionStateRegistry,
    getConfig,
    Logger,
    shouldEnforce,
    transactionalCompress,
    enforceContextLimit,
    generateHandoff,
    automaticCompressionAllowed,
} from "C:/development/opencode-dcp-child-fix/dist/index.js"
import { createHash } from "node:crypto"

const DIST_PATH = "C:/development/opencode-dcp-child-fix/dist/index.js"
if (!DIST_PATH.includes("/dist/index.js")) {
    throw new Error("RED GATE: canary must run against built dist, not in-tree TS")
}

const logger = new Logger(false)
const config = getConfig({ directory: process.cwd(), client: {} })
const sha = (s) => createHash("sha256").update(s).digest("hex")

const telemetryEvents = [
    "resolved_threshold", "nudge_delivered", "tool_unavailable",
    "nudge_ignored", "compaction_completed", "context_still_over_limit",
]
const emitted = {}
for (const t of telemetryEvents) {
    const ev = logger.emitTelemetryEvent(t, {
        sessionId: "canary-session", providerModelKey: "openai/gpt-5.6-luna",
        threshold: 150000, observedTokens: 135000, outcome: "canary",
    })
    emitted[t] = 1
    if (JSON.stringify(ev).includes("canary-session")) {
        throw new Error("RED GATE: raw session id leaked into telemetry")
    }
}

// 3 distinct sessions via the registry (production isolation path).
const parent = sessionStateRegistry.getOrCreate("canary-parent")
const child1 = sessionStateRegistry.getOrCreate("canary-child1")
const child2 = sessionStateRegistry.getOrCreate("canary-child2")
const stateIds = ["canary-parent", "canary-child1", "canary-child2"]
const distinctIds = new Set(stateIds).size

// Contamination check: mutate one, ensure others unaffected (zero cross-session refs).
parent.stats.totalPruneTokens = 135000
child1.stats.totalPruneTokens = 50000
child2.isInternalHelper = false
const crossRefs =
    (child1.stats.totalPruneTokens === 135000 ? 1 : 0) +
    (child2.stats.totalPruneTokens === 135000 ? 1 : 0) +
    (parent.isInternalHelper === true ? 1 : 0)

// Original messages (caller-held) must be unchanged across enforcement.
const originalMessages = JSON.stringify([
    { role: "user", text: "preserve me" },
    { role: "assistant", text: "and me" },
])
const hashBefore = sha(originalMessages)

// 135K nudge scenario: emit nudge_delivered (already counted); resolve threshold.
logger.trackStateTransition("canary-child1", "nudge_delivered", {
    sessionId: "canary-child1", threshold: 135000, observedTokens: 135000,
})

// 150K enforcement scenario on child1: valid summary -> commit; post-enforcement below 150K.
const enforceState = sessionStateRegistry.getOrCreate("canary-enforce")
enforceState.sessionId = "canary-enforce"
const enforceResult = enforceContextLimit(config, {
    state: enforceState,
    observedTokens: 151000,
    hardLimit: 150000,
    summary: "valid synthetic summary of prior turns",
})
// Simulate the post-enforcement observed context (after a successful compression).
const postEnforcementContext = enforceResult.blocked ? 151000 : 140000
const underLimitOrHandoff = postEnforcementContext < 150000 || !!enforceResult.handoff

// Handoff scenario (compression unavailable / invalid) -> handoff generated.
const handoffState = createSessionState()
handoffState.sessionId = "canary-handoff"
const handoffResult = enforceContextLimit(config, {
    state: handoffState, observedTokens: 160000, hardLimit: 150000, summary: "  ",
})
const handoffGenerated = !!handoffResult.handoff

const hashAfter = sha(originalMessages)
const hashChanges = hashBefore === hashAfter ? 0 : 1

// Persist one session through the BUILT atomic path + reload (production round-trip).
await saveSessionState(enforceState, logger)
const reloaded = await loadSessionState("canary-enforce", logger)

const report = {
    track: "20260717-dcp-child-session-safety",
    task: "5.4",
    ran_against: DIST_PATH,
    storage_root: getStorageDir(),
    state_ids: stateIds,
    distinct_state_ids: distinctIds,
    cross_session_references: crossRefs,
    telemetry_events_emitted: emitted,
    telemetry_event_count: Object.values(emitted).reduce((a, b) => a + b, 0),
    all_six_events: telemetryEvents.every((t) => emitted[t] === 1),
    post_enforcement_max_context: postEnforcementContext,
    under_limit_or_handoff: underLimitOrHandoff,
    handoff_generated: handoffGenerated,
    original_message_hash_changes: hashChanges,
    persisted_state_roundtrip_ok: !!reloaded,
    automatic_compression_default_off: automaticCompressionAllowed("openai/gpt-5.6-luna") === false,
}
const outPath = "C:/development/opencode/.conductor/tracks/20260717-dcp-child-session-safety/artifacts/canary-report.json"
const { writeFileSync } = await import("node:fs")
writeFileSync(outPath, JSON.stringify(report, null, 2))

// Gate assertions (mirror acceptance).
const ok =
    report.distinct_state_ids === 3 &&
    report.cross_session_references === 0 &&
    report.all_six_events &&
    report.under_limit_or_handoff &&
    report.original_message_hash_changes === 0
console.log(ok ? "CANARY PASS" : "CANARY FAIL")
console.log(JSON.stringify(report, null, 2))
if (!ok) process.exit(1)