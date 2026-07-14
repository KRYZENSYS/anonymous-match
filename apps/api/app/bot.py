"""Telegram bot entry point with aiogram 3"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.core.config import settings
from app.core.redis import redis_client
from app.bot.handlers import start, profile, discover, chat, premium, admin, common
from app.bot.middlewares import AuthMiddleware, ThrottleMiddleware, AdminMiddleware

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Bot startup actions"""
    await bot.set_webhook(f"{settings.WEBHOOK_URL}/bot/webhook" if settings.WEBHOOK_URL else None)
    me = await bot.get_me()
    logger.info(f"Bot started: @{me.username}")


async def on_shutdown(bot: Bot):
    """Bot shutdown actions"""
    await bot.delete_webhook()
    await bot.session.close()


def create_bot() -> Bot:
    return Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def create_dispatcher() -> Dispatcher:
    storage = RedisStorage(redis=redis_client)
    dp = Dispatcher(storage=storage)

    # Middlewares (order matters!)
    dp.message.middleware(ThrottleMiddleware(rate_limit=1.0))
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Routers (order matters!)
    dp.include_router(common.router)
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(discover.router)
    dp.include_router(chat.router)
    dp.include_router(premium.router)
    dp.include_router(admin.router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    return dp


async def main_polling():
    """Run bot in polling mode (development)"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    bot = create_bot()
    dp = create_dispatcher()
    await bot.delete_webhook()
    logger.info("Starting bot in polling mode...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def main_webhook():
    """Run bot in webhook mode (production)"""
    bot = create_bot()
    dp = create_dispatcher()

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path="/bot/webhook")
    setup_application(app, dp, bot=bot)

    return app


if __name__ == "__main__":
    asyncio.run(main_polling())
