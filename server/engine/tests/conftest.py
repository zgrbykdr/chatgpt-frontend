import asyncio
import json
import os
import pytest

from ..core.manager import SimulationManager


def pytest_configure(config):
  os.environ.setdefault('PYTHONPATH', os.getcwd())


@pytest.fixture
async def manager():
  mgr = SimulationManager()
  yield mgr
  await mgr.pause()


@pytest.fixture
def scenario_mb_path():
  return os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'scenarios', 'w10_w35_mb.hpsim.json')


@pytest.fixture
def scenario_mb(scenario_mb_path):
  with open(scenario_mb_path, 'r', encoding='utf-8') as stream:
    return json.load(stream)
