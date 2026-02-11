const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('dmApp', {
  pickFeatTxt: () => ipcRenderer.invoke('dialog:pick-feat-txt'),
  pickJson: () => ipcRenderer.invoke('dialog:pick-json'),
  newCampaign: () => ipcRenderer.invoke('campaign:new'),
  migrateCampaign: (campaign) => ipcRenderer.invoke('campaign:migrate', campaign),
  saveCampaign: (payload) => ipcRenderer.invoke('campaign:save', payload),
  loadCampaign: (filePath) => ipcRenderer.invoke('campaign:load', filePath),
  pickSavePath: () => ipcRenderer.invoke('campaign:pick-save-path'),
  exportCharacters: (payload) => ipcRenderer.invoke('campaign:export-characters', payload),
});
