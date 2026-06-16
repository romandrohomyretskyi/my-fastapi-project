from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from models import Base
from routers.articles import router as articles_router
from routers.files import router as files_router
from settings.db import engine, ping

app = FastAPI()


@app.get("/")
def index_root():
    return {"message": "Hello World!"}


@app.get("/healthcheck", status_code=status.HTTP_200_OK)
async def db_healthcheck():
    is_alive = await ping()
    if not is_alive:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )
    return {"status": "healthy", "database": "connected"}


app.include_router(articles_router)
app.include_router(files_router)
