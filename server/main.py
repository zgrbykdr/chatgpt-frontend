from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .api.routes_sim import router as sim_router
from .api.routes_models import router as models_router
from .api.routes_props import router as props_router
from .api.ws import router as ws_router

app = FastAPI(title='HeatPumpSim API', version='0.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(sim_router, prefix='/sim', tags=['simulation'])
app.include_router(models_router, prefix='/models', tags=['models'])
app.include_router(props_router, prefix='/props', tags=['props'])
app.include_router(ws_router, prefix='/ws', tags=['ws'])


if __name__ == '__main__':
    uvicorn.run('server.main:app', host='0.0.0.0', port=8000, reload=False)
