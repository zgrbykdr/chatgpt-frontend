import asyncio
import json
import os
import pytest

from ..core.manager import SimulationManager


@pytest.mark.asyncio
async def test_en14511_w10_w35_cop_reasonable():
  path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'scenarios', 'w10_w35_mb.hpsim.json')
  scenario = json.load(open(path, 'r', encoding='utf-8'))
  manager = SimulationManager()
  await manager.load(scenario)
  for _ in range(10):
    await manager.run('step', step=60.0)
  state = manager.current_state()
  comp = state.components['comp']
  heat = state.components['cond']['heatDuty']
  cop = heat / max(comp['power'], 1e-6)
  assert 1.0 <= cop <= 10.0


@pytest.mark.asyncio
async def test_en14511_b0_w35_energy_balance():
  path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'scenarios', 'w10_w35_fvm_evap.hpsim.json')
  scenario = json.load(open(path, 'r', encoding='utf-8'))
  manager = SimulationManager()
  await manager.load(scenario)
  for _ in range(8):
    await manager.run('step', step=60.0)
  state = manager.current_state()
  evap_heat = state.components['evap']['heatDuty']
  cond_heat = state.components['cond']['heatDuty']
  comp_power = state.components['comp']['power']
  balance = abs(cond_heat - evap_heat - comp_power)
  assert balance <= max(0.5 * abs(cond_heat), 5e3)
