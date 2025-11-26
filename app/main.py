from fastapi import FastAPI

from app.api.router import api_router, ws_router
from app.database import Base, engine
from app.events import ContainerEventManager

app = FastAPI(title="Container Storage API", version="1.0.0")
app.state.event_manager = ContainerEventManager()


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(api_router)
app.include_router(ws_router)


