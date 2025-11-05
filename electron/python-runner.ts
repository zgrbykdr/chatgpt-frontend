import { ChildProcessWithoutNullStreams, spawn } from 'child_process';
import path from 'path';
import os from 'os';

export class PythonRunner {
  private process: ChildProcessWithoutNullStreams | null = null;

  start() {
    if (this.process) {
      return;
    }

    const pythonExecutable = this.resolvePython();
    const serverEntry = path.join(__dirname, '..', 'server', 'main.py');
    this.process = spawn(pythonExecutable, [serverEntry], {
      cwd: path.join(__dirname, '..'),
      env: {
        ...process.env,
        PYTHONUNBUFFERED: '1',
      },
    });

    this.process.stdout.on('data', (data) => {
      console.log(`[python] ${data}`.trim());
    });
    this.process.stderr.on('data', (data) => {
      console.error(`[python-error] ${data}`.trim());
    });
    this.process.on('exit', (code) => {
      console.log(`Python process exited with code ${code}`);
      this.process = null;
    });
  }

  stop() {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }

  isAlive(): boolean {
    return !!this.process && !this.process.killed;
  }

  private resolvePython(): string {
    if (process.env.HPSIM_PYTHON) {
      return process.env.HPSIM_PYTHON;
    }
    if (process.platform === 'win32') {
      return path.join(__dirname, '..', 'venv', 'Scripts', 'python.exe');
    }
    const candidate = path.join(__dirname, '..', 'venv', 'bin', 'python');
    return candidate;
  }
}
