from telebot import types
from telebot.asyncio_handler_backends import State, StatesGroup

from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Logger import LogLevel, logger
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.TelegramBots.Doroshka.Config import bot
from BackendApp.TelegramBots.Doroshka.Handlers.main_menu_handler import main_menu
from BackendApp.TelegramBots.Doroshka.Handlers.referrals_handler import (
    handle_referral_link,
)

from BackendApp.TelegramBots.Doroshka.Middlewares.message_context_middleware import (
    message_context_manager,
)
from BackendApp.TelegramBots.utils.handler_loggining import handler_logging

from telebot.asyncio_handler_backends import StatesGroup
from telebot.asyncio_handler_backends import State
from dotenv import load_dotenv
import os

load_dotenv()


class RegistrationStates(StatesGroup):
    PhoneInquiry = State()

REFERRAL_LINK = 1

@handler_logging
@bot.message_handler(commands=["start"])
async def start_handler(message) -> None:
    await registration_handler(message)

@bot.message_handler(commands=["home"])
async def home_handler(message) -> None:
    await registration_handler(message)

async def registration_handler(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        result = await ClientMiddleware.get_client(chat_id=message.chat.id)
        if (result == DBTransactionStatus.NOT_EXIST):
            head_bot_name = os.getenv("HEAD_BOT_NAME")
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text=f"❌ Вы еще не были зарегестрированы в головном боте <b>@{head_bot_name}</b>, перейдите в него и пройдите регистрацию!",
                parse_mode="HTML"
            )

            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id,
                msgId=msg.id
            )

        else:
            await main_menu(message)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in start_handler.py in registration_handler function: {e}",
            module_name="doroshka_bot"
        )