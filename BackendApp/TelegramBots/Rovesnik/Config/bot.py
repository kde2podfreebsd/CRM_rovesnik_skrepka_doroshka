import os

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import (
    ForwardFilter,
    IsDigitFilter,
    IsReplyFilter,
    StateFilter,
)
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage

from BackendApp.TelegramBots.Rovesnik.Middlewares.exception_middleware import (
    ExceptionHandler,
)

load_dotenv()

bot = AsyncTeleBot(
    str(os.getenv("ROVESNIK_TELEGRAM_BOT_TOKEN")),
    # exception_handler=ExceptionHandler(),
    state_storage=StateMemoryStorage(),
)


class MyStates(StatesGroup):
    get_password_message = State()
    get_additional_message = State()
    get_agent_id_message = State()
    get_new_request = State()


provider_token = os.getenv("ROVESNIK_PAYMENT_TOKEN")
