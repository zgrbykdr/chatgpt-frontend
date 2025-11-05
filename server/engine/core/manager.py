from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..graphs.schemas import parse_project, ProjectGraph
from ..fluids import get_fluid, AVAILABLE_FLUIDS
from ..components.heat_exchanger import MovingBoundaryHX, FiniteVolumeHX
from ..components.compressor import Compressor
from ..components.pump import Pump
from ..components.valve import ExpansionValve
from ..components.sensor import Sensor


@dataclass
class SimulationSnapshot:
  time: float
  components: Dict[str, Dict[str, float]]
  validation: Dict[str, Any]


class SimulationManager:
  def __init__(self) -> None:
    self.project: Optional[ProjectGraph] = None
    self.components: Dict[str, Any] = {}
    self.fluids: Dict[str, Any] = {}
    self.time: float = 0.0
    self.validation: Dict[str, Any] = {
      'energyResidual': 0.0,
      'jacobianCondition': 1.0,
      'warnings': [],
    }
    self._queues: List[asyncio.Queue[SimulationSnapshot]] = []
    self._task: Optional[asyncio.Task[None]] = None
    self._lock = asyncio.Lock()

  async def load(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    async with self._lock:
      project = parse_project(payload)
      self.project = project
      self.fluids = {}
      for fluid in project.fluids:
        if isinstance(fluid, str):
          name = fluid
        else:
          name = fluid['name']
        self.fluids[name] = get_fluid(name)
      self.components = {}
      for component in project.components:
        model = self._create_component(component)
        model.initialize()
        self.components[component.id] = model
      self.time = project.simulation.start
      self.validation = {
        'energyResidual': 0.0,
        'jacobianCondition': 1.0,
        'warnings': [],
      }
      return {
        'status': 'ok',
        'components': list(self.components.keys()),
      }

  def _create_component(self, component: Any):
    params = component.params
    if component.type in ('Evaporator', 'Condenser', 'PlateHX'):
      if component.modeling == 'FVM':
        return FiniteVolumeHX(component.id, component.type, component.modeling, params)
      return MovingBoundaryHX(component.id, component.type, component.modeling, params)
    if component.type == 'Compressor':
      return Compressor(component.id, component.type, component.modeling, params)
    if component.type == 'Pump':
      return Pump(component.id, component.type, component.modeling, params)
    if component.type in ('ExpansionValve', 'EEV', 'TXV'):
      return ExpansionValve(component.id, component.type, component.modeling, params)
    return Sensor(component.id, component.type, component.modeling, params)

  async def run(self, mode: str, step: Optional[float] = None) -> Dict[str, Any]:
    if self.project is None:
      raise RuntimeError('Project not loaded')
    if mode == 'continuous':
      if self._task and not self._task.done():
        return {'status': 'running'}
      self._task = asyncio.create_task(self._run_loop())
      return {'status': 'started'}
    if mode == 'step':
      dt = step or 1.0
      snapshot = await self._advance(dt)
      await self._broadcast(snapshot)
      return {'status': 'step', 'time': snapshot.time}
    raise ValueError(f'Unknown mode: {mode}')

  async def pause(self) -> Dict[str, Any]:
    if self._task and not self._task.done():
      self._task.cancel()
      try:
        await self._task
      except asyncio.CancelledError:
        pass
    return {'status': 'paused'}

  async def reset(self) -> Dict[str, Any]:
    async with self._lock:
      if not self.project:
        return {'status': 'idle'}
      for component in self.components.values():
        component.initialize()
      self.time = self.project.simulation.start
      self.validation = {
        'energyResidual': 0.0,
        'jacobianCondition': 1.0,
        'warnings': [],
      }
      snapshot = SimulationSnapshot(self.time, self._collect_outputs(), self.validation.copy())
      await self._broadcast(snapshot)
      return {'status': 'reset'}

  async def subscribe(self) -> asyncio.Queue[SimulationSnapshot]:
    queue: asyncio.Queue[SimulationSnapshot] = asyncio.Queue()
    self._queues.append(queue)
    return queue

  async def _run_loop(self) -> None:
    assert self.project is not None
    dt = 1.0
    while self.time < self.project.simulation.stop:
      snapshot = await self._advance(dt)
      await self._broadcast(snapshot)
      await asyncio.sleep(0)

  async def _advance(self, dt: float) -> SimulationSnapshot:
    assert self.project is not None
    outputs = {}
    total_residual = 0.0
    for component in self.components.values():
      fluid_map = {name: state for name, state in self.fluids.items()}
      result = component.step(fluid_map, dt)
      outputs[component.id] = result
      total_residual += abs(result.get('energyResidual', 0.0))
    self.time += dt
    warnings: List[str] = []
    if total_residual > 1e4:
      warnings.append('High energy residual')
    self.validation = {
      'energyResidual': total_residual,
      'jacobianCondition': 1.5,
      'warnings': warnings,
    }
    return SimulationSnapshot(time=self.time, components=outputs, validation=self.validation.copy())

  async def _broadcast(self, snapshot: SimulationSnapshot) -> None:
    for queue in self._queues:
      await queue.put(snapshot)

  def list_fluids(self) -> List[str]:
    return AVAILABLE_FLUIDS

  def current_state(self) -> SimulationSnapshot:
    return SimulationSnapshot(self.time, self._collect_outputs(), self.validation.copy())

  def _collect_outputs(self) -> Dict[str, Dict[str, float]]:
    return {component.id: component.output() for component in self.components.values()}
