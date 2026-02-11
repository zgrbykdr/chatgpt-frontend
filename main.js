const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

const { createDefaultCampaign, migrateCampaign } = require('./src/lib/models');
const { saveCampaignToDisk, loadCampaignFromDisk, createSnapshotBackup } = require('./src/lib/storage');
const { parseFeatTxt } = require('./src/lib/txtFeatParser');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1500,
    height: 950,
    minWidth: 1200,
    minHeight: 760,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: false,
      nodeIntegration: true,
    },
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('dialog:pick-feat-txt', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    title: 'Import Feats TXT',
    filters: [{ name: 'Text files', extensions: ['txt', 'tsv', 'csv'] }],
    properties: ['openFile'],
  });
  if (canceled || filePaths.length === 0) return null;
  const filePath = filePaths[0];
  const raw = fs.readFileSync(filePath, 'utf-8');
  const parsed = parseFeatTxt(raw, filePath);
  return parsed;
});

ipcMain.handle('dialog:pick-json', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    title: 'Import JSON Data Pack',
    filters: [{ name: 'JSON', extensions: ['json'] }],
    properties: ['openFile'],
  });
  if (canceled || filePaths.length === 0) return null;
  const raw = fs.readFileSync(filePaths[0], 'utf-8');
  return { filePath: filePaths[0], json: JSON.parse(raw) };
});

ipcMain.handle('campaign:new', async () => createDefaultCampaign());
ipcMain.handle('campaign:migrate', async (_evt, campaign) => migrateCampaign(campaign));

ipcMain.handle('campaign:save', async (_evt, { campaign, targetPath }) => {
  const saveResult = saveCampaignToDisk(campaign, targetPath);
  createSnapshotBackup(saveResult.finalPath, 5);
  return saveResult;
});

ipcMain.handle('campaign:load', async (_evt, filePath) => {
  if (!filePath) {
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
      title: 'Load Campaign',
      filters: [{ name: 'Campaign JSON', extensions: ['json'] }],
      properties: ['openFile'],
    });
    if (canceled || filePaths.length === 0) return null;
    filePath = filePaths[0];
  }
  const campaign = loadCampaignFromDisk(filePath);
  return { campaign: migrateCampaign(campaign), filePath };
});

ipcMain.handle('campaign:export-characters', async (_evt, { characters }) => {
  const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
    title: 'Export Characters',
    defaultPath: 'characters-export.json',
    filters: [{ name: 'JSON', extensions: ['json'] }],
  });
  if (canceled || !filePath) return null;
  fs.writeFileSync(filePath, JSON.stringify({ exportedAt: new Date().toISOString(), characters }, null, 2), 'utf-8');
  return filePath;
});

ipcMain.handle('campaign:pick-save-path', async () => {
  const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
    title: 'Save Campaign As',
    defaultPath: 'campaign.json',
    filters: [{ name: 'Campaign JSON', extensions: ['json'] }],
  });
  if (canceled || !filePath) return null;
  return filePath;
});
