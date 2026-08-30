from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.days import router as days_router
from app.api.routers.tasks import router as tasks_router
from app.api.routers.quarantine import router as quarantine_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(days_router)
app.include_router(tasks_router)
app.include_router(quarantine_router)


