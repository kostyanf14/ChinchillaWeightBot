from app.common.config import Config as CommonConfig
from app.common.config.utils import getenv, getenv_typed


class Config(CommonConfig):
    telegram_bot_token: str
    developer_chat_id: int

    @staticmethod
    def load():
        super(Config, Config).load()
        Config.telegram_bot_token = getenv('TELEGRAM_BOT_TOKEN')
        Config.developer_chat_id = getenv_typed('DEVELOPER_CHAT_ID', int)
