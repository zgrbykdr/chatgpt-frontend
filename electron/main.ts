import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import { PythonRunner } from './python-runner';

const isDev = process.env.NODE_ENV !== 'production';
let python: PythonRunner | null = null;

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev) {
    win.loadURL('http://localhost:5173');
    win.webContents.openDevTools({ mode: 'detach' });
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

app.on('ready', () => {
  python = new PythonRunner();
  python.start();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  python?.stop();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

ipcMain.handle('python:isAlive', async () => {
  return python?.isAlive() ?? false;
});
