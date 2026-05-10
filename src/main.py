import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import psycopg

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.api.hotels import router as hotels_router
from src.api.auth import router as authorization_router
from src.api.rooms import router as rooms_router
from src.api.facilities import router as facilities_router
from src.api.bookings import router as bookings_router
from src.api.images import router as images_router
from src.init import redis_manager
from src.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info(f"Connecting to PostgreSQL {settings.DB_HOST}:{settings.DB_PORT}")
        conn = psycopg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dbname=settings.DB_NAME,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        logger.info(f"Connected to PostgreSQL version {db_version}")
        cursor.close()
        conn.close()
    except psycopg.OperationalError as e:
        logger.error(f"Failed to connect to {settings.DB_HOST}:{settings.DB_PORT}: {e}")
    await redis_manager.connect()
    redis = aioredis.from_url(settings.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")  # type: ignore
    logger.info("FastAPI Cache initialized")
    yield
    await redis_manager.close()


# if settings.MODE == "TEST":
#     FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)

# CORS middleware
origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authorization_router)
app.include_router(hotels_router)
app.include_router(rooms_router)
app.include_router(facilities_router)
app.include_router(images_router)
app.include_router(bookings_router)

app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,  # type: ignore
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)  # type: ignore
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,  # type: ignore
        title=app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@2/bundles/redoc.standalone.js",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
