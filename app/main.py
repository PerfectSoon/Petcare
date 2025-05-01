from contextlib import asynccontextmanager

import uvicorn
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.models import Base
from app.database.connection import engine
from app.api.v1 import (
    users_router,
    service_router,
    booking_router,
    pet_router,
    slot_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="PetCare", lifespan=lifespan, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_V1 = "/api/v1"

app.include_router(users_router, prefix=f"{API_V1}/auth", tags=["auth"])
app.include_router(pet_router, prefix=f"{API_V1}/pet", tags=["pet"])
app.include_router(service_router, prefix=f"{API_V1}/service", tags=["service"])
app.include_router(booking_router, prefix=f"{API_V1}/booking", tags=["booking"])
app.include_router(slot_router, prefix=f"{API_V1}/slot", tags=["slot"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run("main:app", reload=True)
