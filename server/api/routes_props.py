from __future__ import annotations

from fastapi import APIRouter

from ..engine import simulation_manager
from ..engine.fluids import get_fluid

router = APIRouter()


@router.get('/list_fluids')
async def list_fluids():
  return simulation_manager.list_fluids()


@router.post('/query')
async def query_properties(request: dict):
  fluid_name = request.get('fluid', 'Water')
  pressure = float(request.get('pressure', 101325))
  temperature = float(request.get('temperature', 298.15))
  fluid = get_fluid(fluid_name)
  return {
    'density': fluid.density(pressure, temperature),
    'cp': fluid.cp(pressure, temperature),
    'enthalpy': fluid.h_from_Tp(temperature, pressure),
  }
