import logging # noqa
import os

from telebot.callback_data import CallbackData

from .bot import bot  # noqa

import telebot # noqa
from dotenv import load_dotenv # noqa

basedir = f"{os.path.abspath(os.path.dirname(__file__))}/../"

provider_token = os.getenv("PROVIDER_YOOKASSA_TEST")

load_dotenv()
# logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)

invoice_factory = CallbackData('product_id', prefix='products')