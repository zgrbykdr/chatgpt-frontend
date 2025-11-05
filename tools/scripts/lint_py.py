#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

commands = [
  ['python', '-m', 'black', str(ROOT / 'server'), str(ROOT / 'tools'), '--check'],
  ['python', '-m', 'flake8', str(ROOT / 'server')],
]

for command in commands:
  try:
    subprocess.check_call(command)
  except FileNotFoundError:
    print(f"Skipping command {' '.join(command)} (not installed)")
  except subprocess.CalledProcessError as exc:
    sys.exit(exc.returncode)
