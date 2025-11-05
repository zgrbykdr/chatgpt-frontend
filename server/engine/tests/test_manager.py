import asyncio
import pytest

from ..core.manager import SimulationManager
from ..graphs.schemas import validate_project


@pytest.mark.asyncio
async def test_manager_loads_scenario(scenario_mb, manager: SimulationManager):
  result = await manager.load(scenario_mb)
  assert result['status'] == 'ok'
  assert 'evap' in result['components']


@pytest.mark.asyncio
async def test_manager_run_step_updates_time(scenario_mb, manager: SimulationManager):
  await manager.load(scenario_mb)
  response = await manager.run('step', step=10.0)
  assert response['time'] == pytest.approx(10.0)


@pytest.mark.asyncio
async def test_manager_reset_returns_to_start(scenario_mb, manager: SimulationManager):
  await manager.load(scenario_mb)
  await manager.run('step', step=5.0)
  await manager.reset()
  state = manager.current_state()
  assert state.time == scenario_mb['simulation']['start']


@pytest.mark.asyncio
async def test_manager_pause_stops_background(scenario_mb, manager: SimulationManager):
  await manager.load(scenario_mb)
  await manager.run('continuous')
  await asyncio.sleep(0)
  await manager.pause()
  assert manager.current_state().time >= scenario_mb['simulation']['start']


def test_validate_project_rejects_invalid():
  project = {
    'version': '1.0.0',
    'fluids': [],
    'components': [],
    'connections': [],
    'simulation': {
      'start': 0,
      'stop': 1,
      'integrator': 'BDF2',
      'scenario': None,
      'tolerances': {'absolute': 1e-6, 'relative': 1e-6},
    },
    'units': {'temperature': 'C', 'pressure': 'bar', 'massFlow': 'kg/s'},
  }
  with pytest.raises(ValueError):
    validate_project(project)


@pytest.mark.asyncio
async def test_manager_subscription_receives_updates(scenario_mb, manager: SimulationManager):
  await manager.load(scenario_mb)
  queue = await manager.subscribe()
  await manager.run('step', step=1.0)
  snapshot = await asyncio.wait_for(queue.get(), timeout=1.0)
  assert snapshot.time > 0
  assert 'comp' in snapshot.components


@pytest.mark.asyncio
async def test_manager_energy_residual_below_threshold(scenario_mb, manager: SimulationManager):
  await manager.load(scenario_mb)
  await manager.run('step', step=1.0)
  state = manager.current_state()
  assert state.validation['energyResidual'] >= 0


@pytest.mark.asyncio
async def test_manager_handles_multiple_steps(scenario_mb, manager: SimulationManager):
  await manager.load(scenario_mb)
  for _ in range(5):
    await manager.run('step', step=60.0)
  assert manager.current_state().time == pytest.approx(300.0)
