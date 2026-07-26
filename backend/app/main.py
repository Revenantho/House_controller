from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import SESSION_SECRET_KEY
from .database import Base, SessionLocal, engine
from .registry_singleton import get_registry
from .routers import auth, devices, floors, rooms, scenarios, ws
from .seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    await get_registry().connect_all()
    yield


app = FastAPI(title="Domotique — backend (fake adapter)", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY, same_site="lax")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(floors.router)
app.include_router(rooms.router)
app.include_router(devices.router)
app.include_router(scenarios.router)
app.include_router(ws.router)

# Sert les images de plan (backend/app/static/plans/*.png) référencées par Floor.plan_image_path.
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/api/health")
def health():
    return {"status": "ok"}
