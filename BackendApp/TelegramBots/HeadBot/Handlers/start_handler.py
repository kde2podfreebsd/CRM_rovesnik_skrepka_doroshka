from telebot import types
import re

from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Logger import LogLevel, logger
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.TelegramBots.HeadBot.Config import bot
from BackendApp.TelegramBots.HeadBot.Middlewares.message_context_middleware import message_context_manager
from BackendApp.TelegramBots.HeadBot.Handlers.main_menu_handler import main_menu
from BackendApp.TelegramBots.HeadBot.Handlers.referrals_handler import (
    handle_referral_link,
)
from BackendApp.TelegramBots.HeadBot.Handlers.support_handler import process_reservation_request

from telebot.asyncio_handler_backends import StatesGroup
from telebot.asyncio_handler_backends import State

from BackendApp.TelegramBots.utils.handler_loggining import handler_logging

class RegistrationStates(StatesGroup):
    PhoneInquiry = State()

REFERRAL_LINK = 1
CALLBACK_DATA = 1

@handler_logging
@bot.message_handler(commands=["start"])
async def welcome_handler(message) -> None:
    await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
    await _start_message(message)

@handler_logging
@bot.message_handler(commands=["home"])
async def home_handler(message):
    try:
        result = await ClientMiddleware.get_client(chat_id=message.chat.id)
        if (result == DBTransactionStatus.NOT_EXIST):
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text="❌ Вы еще не были зарегистрированы в боте, для начала взаимодействия напишите <b>/start</b>.",
                parse_mode="HTML"
            )
            message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=msg.id)
        else:
            await main_menu(message)
    
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in start_handler.py in home_handler function: {e}",
            module_name="head_bot"
        )

@handler_logging
async def _start_message(message):
    try:
        result = await ClientMiddleware.get_client(chat_id=message.chat.id)
        payload = [element for element in message.text.split(" ")]

        if (result == DBTransactionStatus.NOT_EXIST):
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text="<i>Происходит регистрация пользователя в системе, это может занять некоторое время...</i>",
                parse_mode="HTML"
            )

            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id,
                msgId=msg.id
            )

            result = await ClientMiddleware.create_client(
                chat_id=message.chat.id,
                username=message.chat.username,
                first_name=message.chat.first_name,
                last_name=message.chat.last_name,
            )

            await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)

            if result == DBTransactionStatus.ROLLBACK:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="❌ Произошла ошибка при создании клиента в базе данных, обратитесь в клиентскую поддержку"
                )
                message_context_manager.add_msgId_to_help_menu_dict(
                    chat_id=message.chat.id,
                    msgId=msg.id
                )

            elif (result == DBTransactionStatus.SUCCESS):
                # link_example: t.me/<bot_name>?start=referal_<referral_number>
                if (len(payload) > 1):
                    if "referal_" in payload[REFERRAL_LINK]:
                        referral_link = payload[REFERRAL_LINK].split("referal_")[1]
                        await handle_referral_link(message=message, referral_link=referral_link)

                await phone_inquery_menu(message)

        else:
            if (len(payload) > 1):
                if "support_reserve_update" in payload[CALLBACK_DATA]:
                    # t.me/crm_head_test_bot?start=support_reserve_update_cancel_capacity_1_date_2024_18_05_23_00
                    capacity = payload[CALLBACK_DATA].split("_capacity_")[-1].split("_date_")[0]
                    date_and_time = payload[CALLBACK_DATA].split("_capacity_")[-1].split("_date_")[1].split("_")
                    date = "-".join(date_and_time[:3])
                    time = ":".join(date_and_time[3:])
                    reservation_time = date + " " + time

                    await process_reservation_request(message, capacity, reservation_time, "update")
                
                elif "support_reserve_cancel" in payload[CALLBACK_DATA]:
                    # t.me/crm_head_test_bot?start=support_reserve_cancel_capacity_1_date_2024_18_05_23_00
                    capacity = payload[CALLBACK_DATA].split("_capacity_")[-1].split("_date_")[0]
                    date_and_time = payload[CALLBACK_DATA].split("_capacity_")[-1].split("_date_")[1].split("_")
                    date = "-".join(date_and_time[:3])
                    time = ":".join(date_and_time[3:])
                    reservation_time = date + " " + time

                    await process_reservation_request(message, capacity, reservation_time, "cancel")

                elif "support_reserve" in payload[CALLBACK_DATA]:
                    # t.me/crm_head_test_bot?start=support_reserve_capacity_1_date_2024_18_05_23_00
                    capacity = payload[CALLBACK_DATA].split("_capacity_")[-1].split("_date_")[0]
                    date_and_time = payload[CALLBACK_DATA].split("_capacity_")[-1].split("_date_")[1].split("_")
                    date = "-".join(date_and_time[:3])
                    time = ":".join(date_and_time[3:])
                    reservation_time = date + " " + time

                    await process_reservation_request(message, capacity, reservation_time, "create")
                else:
                    await main_menu(message)
            else:
                await main_menu(message)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in start_handler.py in _start_message function: {e}",
            module_name="head_bot"
        )

@handler_logging
async def phone_inquery_menu(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)

        msg = await bot.send_message(
            chat_id=message.chat.id,
            text="Введите свой номер телефона в формате: <b>+7xxxxxxxxxx</b>. Он будет использоваться для получения уведомлений о бронировании и чеков 🤗",
            reply_markup=types.InlineKeyboardMarkup(
                row_width=1,
                keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="📞 Продолжить без ввода телефона",
                            callback_data="main_menu"
                        )
                    ]
                ]
            ),
            parse_mode="HTML" 
        )

        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id,
            msgId=msg.id
        )
        await bot.set_state(message.chat.id, RegistrationStates.PhoneInquiry)

    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in review_handler.py in get_review_award function: {e}",
            module_name="head_bot"
        )

@handler_logging
@bot.message_handler(state=RegistrationStates.PhoneInquiry)
async def phone_inquery_proceed_menu(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )
        phone = message.text
        pattern = r"\+7\d{10}"

        if (re.match(pattern, phone)):
            result = await ClientMiddleware.update_phone(
                chat_id=message.chat.id,
                phone=phone
            )
            if (result == DBTransactionStatus.SUCCESS):
                msg = await bot.send_message(
                    chat_id=message.chat.id,
                    text="Вы успешно указали свой номер телефона, он был привязан к вашему профилю",
                    reply_markup=types.InlineKeyboardMarkup(
                        row_width=1,
                        keyboard=[
                            [
                                types.InlineKeyboardButton(
                                    text="🔜 Продолжить в главном меню",
                                    callback_data="main_menu"
                                )
                            ]
                        ]
                    )
                )
                message_context_manager.add_msgId_to_help_menu_dict(
                    chat_id=message.chat.id,
                    msgId=msg.id
                )
            else:
                msg = await bot.send_message(
                    chat_id=message.chat.id,
                    text="❌ Произошла ошибка при занесении номера телефона в базу данных: продолжите в главное меню или обратитесь в клиентскую поддержку",
                    reply_markup=types.InlineKeyboardMarkup(
                        row_width=1,
                        keyboard=[
                            [
                                types.InlineKeyboardButton(
                                    text="🔜 Продолжить в главном меню",
                                    callback_data="main_menu"
                                )
                            ]
                        ]
                    )
                )
                message_context_manager.add_msgId_to_help_menu_dict(
                    chat_id=message.chat.id,
                    msgId=msg.id
                )
                await bot.delete_state(message.chat.id, message.chat.id)
        
        else:
            msg = await bot.send_message(
                    chat_id=message.chat.id,
                    text="❌ Вы ввели номер телефона не по формату <b>+7xxxxxxxxxx</b>: продолжите в главное меню или попробуйте ввести его снова",
                    reply_markup=types.InlineKeyboardMarkup(
                        row_width=1,
                        keyboard=[
                            [
                                types.InlineKeyboardButton(
                                    text="🔜 Продолжить в главном меню",
                                    callback_data="main_menu"
                                )
                            ]
                        ]
                    ),
                    parse_mode="HTML"
                )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id,
                msgId=msg.id
            )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in start_handler.py in phone_inquery_proceed_menu function: {e}",
            module_name="head_bot"
        )
