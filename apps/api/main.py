"""Firdavs-style entry point for Anonymous Match FastAPI app."""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis_client import init_redis, close_redis
from app.core.limiter import limiter
from app.api.v1 import api_router
from app.bot import start_bot, stop_bot

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Anonymous Match API starting...")
    await init_db()
    await init_redis()
    bot_task = None
    if settings.BOT_TOKEN:
        bot_task = asyncio.create_task(start_bot(), name="telegram-bot")
        logger.info("🤖 Telegram bot scheduled")
    yield
    # Shutdown
    logger.info("👋 Shutting down...")
    if bot_task:
        await stop_bot(bot_task)
    await close_redis()
    await close_db()


app = FastAPI(
    title="Anonymous Match API",
    description="Anonim tanishuv platformasi — REST + WebSocket API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "request_id": getattr(request.state, "request_id", None)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "service": "anonymous-match", "version": "1.0.0"}


app.include_router(api_router, prefix="/api/v1")
