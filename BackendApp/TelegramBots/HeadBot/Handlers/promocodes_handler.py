from BackendApp.TelegramBots.HeadBot.Middlewares.message_context_middleware import message_context_manager
from BackendApp.Middleware.promocodes_middleware import PromocodesMiddleware
from BackendApp.Database.Models.promocode_model import Promocode
from BackendApp.Database.session import DBTransactionStatus
from BackendApp import basedir

from BackendApp.TelegramBots.HeadBot.Config import bot

from BackendApp.TelegramBots.HeadBot.Markups.inline_markup import InlineMarkup

from telebot import types
from dotenv import load_dotenv
import os

from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

load_dotenv()

BOT_NAME = os.getenv("HEAD_BOT_NAME")

async def parse_promocode(promocode: Promocode):
    return f"Название: {promocode.name}\nИдентификационный номер: {promocode.number}\nОписание: {promocode.description}\n"

@handler_logging
async def promocode_menu(message, page):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )

        promocodes = await PromocodesMiddleware.get_not_activated_promocodes_for_client(chat_id=message.chat.id)
        activated_promocodes = await PromocodesMiddleware.get_activated_promocodes_for_client(chat_id=message.chat.id)

        if (promocodes == DBTransactionStatus.NOT_EXIST):
            mp = types.InlineKeyboardMarkup(row_width=1)
            if (activated_promocodes != DBTransactionStatus.NOT_EXIST):
                activated_promocodes = types.InlineKeyboardButton(
                    text="✔️ Активированные промокоды",
                    callback_data=f"activated_promocodes_slider",
                )
                mp.add(activated_promocodes)
            back = types.InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back_to_profile_menu"
            )
            mp.add(back)
                        
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text="У вас нет не активированных промокодов... пока что... 🍃",
                reply_markup=mp
            )
        else:

            data_to_display = promocodes[page - 1]
            msg_text = await parse_promocode(promocode=data_to_display)
            qr_code_path = f"{basedir}/static/promocodes/{message.chat.id}_{data_to_display.hashcode}.png"
            file = types.InputFile(open(qr_code_path, "rb"))
            msg = await bot.send_photo(
                chat_id=message.chat.id,
                photo=file
            )

            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id,
                msgId=msg.id
            )
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text=msg_text,
                reply_markup=InlineMarkup.promocode_slider(
                    page=page,
                    amount_of_pages=len(promocodes),
                    add_button=(False if activated_promocodes == DBTransactionStatus.NOT_EXIST else True)
                )
            )


        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id,
            msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in promocode_handler.py in promocode_menu function: {e}",
            module_name="head_bot"
        )  

@handler_logging
async def activated_promocode_menu(message, page):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )

        activated_promocodes = await PromocodesMiddleware.get_activated_promocodes_for_client(chat_id=message.chat.id)

        data_to_display = activated_promocodes[page - 1]
        msg_text = await parse_promocode(promocode=data_to_display)
        qr_code_path = f"{basedir}/static/promocodes/{message.chat.id}_{data_to_display.hashcode}.png"
        file = types.InputFile(open(qr_code_path, "rb"))
        msg = await bot.send_photo(
            chat_id=message.chat.id,
            photo=file
        )

        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id,
            msgId=msg.id
        )
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=InlineMarkup.activated_promocode_slider(
                page=page,
                amount_of_pages=len(activated_promocodes)
            )
        )


        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id,
            msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in promocode_handler.py in activated_promocode_menu function: {e}",
            module_name="head_bot"
        )  
