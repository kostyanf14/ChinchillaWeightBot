import asyncio
import logging

from telegram.ext import ApplicationBuilder

from app.config import Config

logger = logging.getLogger(__name__)


async def tg_send_msg(chat_id: int, text: str):
    application = ApplicationBuilder().token(Config.telegram_bot_token).build()
    await application.bot.sendMessage(chat_id=chat_id, text=text)


def run_tg_send_msg(chat_id: int, text: str):
    asyncio.run(tg_send_msg(chat_id, text))


def init_hooks():
    pass
