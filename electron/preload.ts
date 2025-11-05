import { contextBridge, ipcRenderer } from 'electron';

declare global {
  interface Window {
    electronAPI: {
      isPythonAlive: () => Promise<boolean>;
    };
  }
}

contextBridge.exposeInMainWorld('electronAPI', {
  isPythonAlive: async () => {
    return ipcRenderer.invoke('python:isAlive');
  },
});
