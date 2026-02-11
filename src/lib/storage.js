const fs = require('fs');
const path = require('path');

function ensureDirFor(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function saveCampaignToDisk(campaign, targetPath) {
  const finalPath = targetPath || path.join(process.cwd(), 'campaign.json');
  ensureDirFor(finalPath);
  const next = { ...campaign, updatedAt: new Date().toISOString(), filePath: finalPath };
  fs.writeFileSync(finalPath, JSON.stringify(next, null, 2), 'utf-8');
  return { finalPath, campaign: next };
}

function loadCampaignFromDisk(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}

function createSnapshotBackup(filePath, keep = 5) {
  if (!fs.existsSync(filePath)) return;
  const backupDir = path.join(path.dirname(filePath), '.backups');
  fs.mkdirSync(backupDir, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const base = path.basename(filePath, path.extname(filePath));
  const ext = path.extname(filePath) || '.json';
  const backupPath = path.join(backupDir, `${base}-${stamp}${ext}`);
  fs.copyFileSync(filePath, backupPath);

  const files = fs
    .readdirSync(backupDir)
    .filter((f) => f.startsWith(base))
    .sort()
    .reverse();
  files.slice(keep).forEach((f) => fs.unlinkSync(path.join(backupDir, f)));
}

module.exports = { saveCampaignToDisk, loadCampaignFromDisk, createSnapshotBackup };
