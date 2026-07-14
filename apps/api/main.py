"""Anonymous Match — FastAPI entry point."""
from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

import sentry_sdk
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.api.v1 import api_router
from app.bot import start_bot, stop_bot, BotHolder
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis_client import init_redis, close_redis

# ===== Logging =====
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(colors=False) if settings.APP_DEBUG else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
log = structlog.get_logger()

# ===== Metrics =====
REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])
BOT_COMMANDS = Counter("bot_commands_total", "Bot commands", ["command"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App startup va shutdown."""
    log.info("🚀 Anonymous Match API starting...", env=settings.APP_ENV)

    # Sentry
    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.APP_ENV)

    # Init resources
    await init_redis()
    await init_db()

    # Bot task
    bot_task = None
    if settings.BOT_TOKEN:
        bot_task = asyncio.create_task(start_bot())
        log.info("🤖 Telegram bot task started")

    log.info("✅ API ready", env=settings.APP_ENV)

    try:
        yield
    finally:
        log.info("🛑 Shutting down...")
        if bot_task:
            await stop_bot(bot_task)
        await close_redis()
        await close_db()
        log.info("👋 Shutdown complete")


# ===== App =====
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Anonymous Match — Telegram orqali anonim tanishuv. Tinder kabi swipe, real-time chat, premium tizim.",
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
    openapi_url="/openapi.json" if settings.APP_DEBUG else None,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# ===== Middleware =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
if not settings.APP_DEBUG:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter


@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start
        LATENCY.labels(method=request.method, endpoint=request.url.path).observe(duration)
        REQUESTS.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        return response
    except Exception as e:
        log.error("Request error", path=request.url.path, error=str(e))
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


# ===== Routes =====
app.include_router(api_router, prefix="/api/v1")


# ===== Health & Metrics =====
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "env": settings.APP_ENV,
        "docs": "/docs" if settings.APP_DEBUG else None,
    }


@app.get("/health")
async def health():
    from app.core.database import check_db
    from app.core.redis_client import check_redis
    return {
        "status": "ok",
        "db": await check_db(),
        "redis": await check_redis(),
        "bot": "active" if BotHolder.bot else "disabled",
        "timestamp": time.time(),
    }


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ===== Rate limit handler =====
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        {"detail": "Rate limit oshib ketdi. Biroz kuting."},
        status_code=429,
    )


# ===== Static files =====
media_path = Path(settings.MEDIA_DIR)
media_path.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(media_path)), name="media")
