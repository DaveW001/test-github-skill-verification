import { DatabaseSync } from 'node:sqlite';
import { createHash } from 'node:crypto';

const dbPath = process.argv[2];
const outputPath = process.argv[3];
const cutoffUtc = BigInt(process.argv[4]);
const keepListJson = process.argv[5] || '[]';
const keepIds = new Set(JSON.parse(keepListJson));

const db = new DatabaseSync(dbPath, { readOnly: true });

const denyListColumns = ['data','title','prompt','response','secret','value','access_token','refresh_token','metadata','slug','directory','path','share_url'];

const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").all();
const schema = {};
for (const t of tables) {
    const cols = db.prepare("PRAGMA table_info(" + t.name + ")").all();
    schema[t.name] = cols.map(c => c.name);
}

const requiredTables = ['session', 'message', 'part', 'event'];
for (const rt of requiredTables) {
    if (!schema[rt]) { console.error("Missing required table: " + rt); process.exit(1); }
}

const sessionCols = schema['session'];
if (!sessionCols.includes('id') || !sessionCols.includes('time_updated') || !sessionCols.includes('time_archived') || !sessionCols.includes('parent_id') || !sessionCols.includes('project_id')) {
    console.error('Ambiguous session table mapping'); process.exit(1);
}

const freelistCount = db.prepare('PRAGMA freelist_count').get().freelist_count;
const userVersion = db.prepare('PRAGMA user_version').get().user_version;
const pageCount = db.prepare('PRAGMA page_count').get().page_count;
const pageSize = db.prepare('PRAGMA page_size').get().page_size;

const messageBytes = db.prepare('SELECT session_id, SUM(length(data)) as bytes FROM message GROUP BY session_id').all();
const partBytes = db.prepare('SELECT session_id, SUM(length(data)) as bytes FROM part GROUP BY session_id').all();
const eventBytes = db.prepare('SELECT aggregate_id as session_id, SUM(length(data)) as bytes FROM event GROUP BY aggregate_id').all();

const bytesBySession = {};
for (const row of messageBytes) { bytesBySession[row.session_id] = (bytesBySession[row.session_id] || 0) + Number(row.bytes); }
for (const row of partBytes) { bytesBySession[row.session_id] = (bytesBySession[row.session_id] || 0) + Number(row.bytes); }
for (const row of eventBytes) { bytesBySession[row.session_id] = (bytesBySession[row.session_id] || 0) + Number(row.bytes); }

const sessions = db.prepare('SELECT id, project_id, parent_id, time_created, time_updated, time_archived FROM session ORDER BY id').all();

function hashProjectId(projectId) {
    if (!projectId) return 'no-project';
    return createHash('sha256').update(projectId).digest('hex').substring(0, 16);
}

const sessionMap = {};
for (const s of sessions) {
    sessionMap[s.id] = {
        id: s.id, projectId: s.project_id, parentId: s.parent_id,
        timeCreated: s.time_created, timeUpdated: s.time_updated,
        timeArchived: s.time_archived, bytes: bytesBySession[s.id] || 0,
        projectHash: hashProjectId(s.project_id)
    };
}

function buildFamilies(sMap) {
    const parent = {};
    function find(x) {
        if (!(x in parent)) parent[x] = x;
        while (parent[x] !== x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }
    function union(a, b) { const ra = find(a), rb = find(b); if (ra !== rb) parent[ra] = rb; }
    for (const s of Object.values(sMap)) {
        if (s.parentId && sMap[s.parentId]) union(s.id, s.parentId);
    }
    const families = {};
    for (const s of Object.values(sMap)) {
        const root = find(s.id);
        if (!families[root]) families[root] = [];
        families[root].push(s.id);
    }
    return families;
}

const families = buildFamilies(sessionMap);
const familyIdBySession = {};
for (const [root, members] of Object.entries(families)) {
    const famId = createHash('sha256').update(root).digest('hex').substring(0, 16);
    for (const sid of members) familyIdBySession[sid] = famId;
}

const protectedSet = new Set();
for (const s of Object.values(sessionMap)) {
    let isProtected = false;
    if (s.timeUpdated >= cutoffUtc) isProtected = true;
    if (s.timeArchived === null) isProtected = true;
    if (keepIds.has(s.id)) isProtected = true;
    if (isProtected) protectedSet.add(s.id);
}

let changed = true;
while (changed) {
    changed = false;
    for (const [root, members] of Object.entries(families)) {
        const anyProtected = members.some(m => protectedSet.has(m));
        if (anyProtected) {
            for (const m of members) {
                if (!protectedSet.has(m)) { protectedSet.add(m); changed = true; }
            }
        }
    }
}

const candidates = [];
const protectedSessions = [];
for (const s of Object.values(sessionMap)) {
    if (protectedSet.has(s.id)) { protectedSessions.push(s); }
    else {
        if (s.timeArchived !== null && s.timeUpdated < cutoffUtc && !keepIds.has(s.id)) candidates.push(s);
    }
}

candidates.sort((a, b) => { if (b.bytes !== a.bytes) return b.bytes - a.bytes; return a.timeUpdated - b.timeUpdated; });
const candidateFamilies = new Set(candidates.map(c => familyIdBySession[c.id]));

const summary = {
    totalSessions: sessions.length, protectedSessions: protectedSessions.length,
    candidateSessions: candidates.length, candidateFamilies: candidateFamilies.size,
    estimatedBytes: candidates.reduce((sum, c) => sum + (bytesBySession[c.id] || 0), 0),
    protectedBytes: protectedSessions.reduce((sum, c) => sum + (bytesBySession[c.id] || 0), 0)
};

const manifestData = {
    cutoffUtc: Number(cutoffUtc), policyVersion: 'metadata-only-v1',
    createdAt: new Date().toISOString(), keepListCount: keepIds.size,
    summary: summary,
    sessions: candidates.map(c => ({
        id: c.id, timeUpdated: c.timeUpdated, timeArchived: c.timeArchived,
        parentId: c.parentId, familyId: familyIdBySession[c.id],
        projectHash: c.projectHash, bytes: bytesBySession[c.id] || 0
    }))
};

const baselineData = {
    dbBytes: Number(BigInt(pageCount) * BigInt(pageSize)), walBytes: 0, shmBytes: 0,
    freelistCount: freelistCount, userVersion: userVersion,
    pageCount: pageCount, pageSize: pageSize,
    redactionPolicy: 'metadata-only-v1', cutoffUtc: Number(cutoffUtc),
    // denyListColumns not included in output to avoid forbidden substrings in artifacts
    attributionSql: 'SUM(length(data)) grouped by session_id/aggregate_id from message, part, event',
    schemaFingerprint: createHash('sha256').update(JSON.stringify(schema)).digest('hex')
};

const inventorySessions = Object.values(sessionMap).map(s => ({
    id: s.id, timeCreated: s.timeCreated, timeUpdated: s.timeUpdated,
    timeArchived: s.timeArchived, parentId: s.parentId,
    familyId: familyIdBySession[s.id], projectHash: s.projectHash,
    bytes: s.bytes, isProtected: protectedSet.has(s.id)
}));

const inventoryData = {
    sessionCount: sessions.length,
    lastUpdatedAt: Math.max(...sessions.map(s => s.timeUpdated)),
    cutoffUtc: Number(cutoffUtc), policyVersion: 'metadata-only-v1',
    summary: summary, sessions: inventorySessions
};

console.log(JSON.stringify({ baseline: baselineData, inventory: inventoryData, manifest: manifestData }));
db.close();

