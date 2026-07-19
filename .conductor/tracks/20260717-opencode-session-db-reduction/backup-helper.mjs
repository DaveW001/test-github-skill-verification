import { DatabaseSync } from 'node:sqlite';
import { createHash } from 'node:crypto';

const sourcePath = process.argv[2];
const backupPath = process.argv[3];

const source = new DatabaseSync(sourcePath, { readOnly: true });

try { source.backup(backupPath); } catch (e) {
  console.error('Backup API failed: ' + e.message);
  process.exit(1);
}

const backup = new DatabaseSync(backupPath, { readOnly: true });
const sourceQC = source.prepare('PRAGMA quick_check').get();
const backupQC = backup.prepare('PRAGMA quick_check').get();
const sourceSchema = source.prepare("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name").all();
const backupSchema = backup.prepare("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name").all();
const sourceSchemaHash = createHash('sha256').update(JSON.stringify(sourceSchema)).digest('hex');
const backupSchemaHash = createHash('sha256').update(JSON.stringify(backupSchema)).digest('hex');
const sourceUV = source.prepare('PRAGMA user_version').get().user_version;
const backupUV = backup.prepare('PRAGMA user_version').get().user_version;

source.close();
backup.close();

console.log(JSON.stringify({
  sourceQuickCheck: sourceQC['quick_check'] || 'ok',
  backupQuickCheck: backupQC['quick_check'] || 'ok',
  sourceSchemaSha256: sourceSchemaHash,
  backupSchemaSha256: backupSchemaHash,
  sourceUserVersion: sourceUV,
  backupUserVersion: backupUV
}));

