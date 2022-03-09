import logging

from aiogram import Bot, Dispatcher

from app import config

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
    level=logging.INFO,
)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot=bot)

# noinspection PyUnresolvedReferences
import app.handlers
