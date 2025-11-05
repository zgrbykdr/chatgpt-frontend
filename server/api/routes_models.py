from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

CORRELATIONS = {
  'boiling': ['Chen', 'Shah', 'Kandlikar'],
  'condensation': ['Shah'],
  'twoPhasePressureDrop': ['LockhartMartinelli'],
}

DEFAULTS = {
  'Evaporator': {
    'modeling': 'MB',
    'area': 12.0,
    'length': 5.0,
    'massFlow': 0.3,
  },
  'Condenser': {
    'modeling': 'MB',
    'area': 10.0,
    'length': 4.5,
    'massFlow': 0.3,
  },
  'Compressor': {
    'modeling': 'LUMPED',
    'eta_is': 0.75,
    'speed': 45.0,
  },
}


@router.get('/correlations')
async def list_correlations():
  return CORRELATIONS


@router.get('/defaults')
async def list_defaults():
  return DEFAULTS
