from __future__ import annotations

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..engine import simulation_manager

router = APIRouter()


@router.websocket('/sim')
async def simulation_socket(websocket: WebSocket):
  await websocket.accept()
  queue = await simulation_manager.subscribe()
  try:
    while True:
      snapshot = await queue.get()
      await websocket.send_json(
        {
          'type': 'state',
          'time': snapshot.time,
          'components': snapshot.components,
          'validation': snapshot.validation,
        }
      )
  except WebSocketDisconnect:
    return
  except asyncio.CancelledError:
    return
