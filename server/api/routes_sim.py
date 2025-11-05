from __future__ import annotations

from fastapi import APIRouter

from ..engine import simulation_manager

router = APIRouter()


@router.post('/load')
async def load_simulation(project: dict):
  return await simulation_manager.load(project)


@router.post('/run')
async def run_simulation(request: dict):
  mode = request.get('mode', 'continuous')
  step = request.get('step')
  return await simulation_manager.run(mode, step)


@router.post('/pause')
async def pause_simulation():
  return await simulation_manager.pause()


@router.post('/reset')
async def reset_simulation():
  return await simulation_manager.reset()
