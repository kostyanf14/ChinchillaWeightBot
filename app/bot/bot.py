import asyncio
import logging
from typing import Any, Optional

from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ConversationHandler, MessageHandler, filters)

from app.config import Config

from . import handlers
from .handlers import WeightConversationState

logger = logging.getLogger(__name__)


class SingletonMeta(type):
    _instances = dict['SingletonMeta', 'SingletonMeta']()

    def __call__(cls, *args: tuple[Any, ...], **kwargs: Any):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Bot(metaclass=SingletonMeta):
    loop: Optional[asyncio.AbstractEventLoop]

    def __init__(self) -> None:
        logger.info("Initializing bot")
        self.application = Application.builder().token(Config.telegram_bot_token).build()
        self.loop = None
        self.__register_handlers__()

    def __register_handlers__(self) -> None:
        logger.info("Registering handlers")

        self.application.add_handler(CommandHandler(
            'start', handlers.sc_start, block=False))
        self.application.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler('add_weight', handlers.sc_add_weight, block=False)
            ],
            states={
                WeightConversationState.CHINCHILA: [
                    CallbackQueryHandler(handlers.sc_select_chinchila, pattern='.*', block=False)
                ],
                WeightConversationState.WEIGHT: [
                    MessageHandler(filters.TEXT, handlers.sc_enter_weight, block=False)
                ],
                WeightConversationState.FINISH: [
                    CallbackQueryHandler(handlers.sc_save_weight, pattern='^save$', block=False),
                    CallbackQueryHandler(handlers.sc_reset_weight, pattern='^reset$', block=False),
                ],
            },
            fallbacks=[
                CommandHandler("cancel", handlers.sc_reset_weight)
            ],
        ))
        self.application.add_handler(CommandHandler(
            'help', handlers.help_cmd, block=False))

        logger.debug("Registering error handlers")
        self.application.add_error_handler(handlers.error_handler)

    def start(self) -> None:
        logger.info('Starting bot polling')
        self.loop = asyncio.get_event_loop()
        self.application.run_polling()
        logger.debug('Run polling exited')

    def stop(self) -> None:
        logger.info('Stopping bot')
        if self.loop is None:
            logger.warning('Bot appears to not be running (loop is None)')
        else:
            self.loop.stop()
        logger.debug('Stopped current event loop')
