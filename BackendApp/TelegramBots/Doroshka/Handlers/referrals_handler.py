from BackendApp.TelegramBots.Doroshka.Middlewares.message_context_middleware import message_context_manager
from BackendApp.Middleware.referrals_middleware import ReferralMiddleware
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Database.Models.client_model import Client
from BackendApp.Database.Models.referrals_model import Referral
from BackendApp.Database.session import DBTransactionStatus

from BackendApp.TelegramBots.Doroshka.Config import bot

from BackendApp.TelegramBots.Doroshka.Markups.inline_markup import InlineMarkup

from telebot import types
from math import ceil
from dotenv import load_dotenv
import os

from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

load_dotenv()

BOT_NAME = os.getenv("HEAD_BOT_NAME")
STRINGS_PER_PAGE = 10

async def parse_referrer(referrer: Referral, number: int):
    try:
        client = await ClientMiddleware.get_client(
            chat_id=referrer.chat_id
        )
        msg_text = ""
        if (client.username):
            msg_text = f"{number}. Реферал: @{client.username}\n"
        elif (client.first_name):
            if (client.last_name):
                msg_text = f"{number}. Реферал: {client.first_name} {client.last_name}\n"
            else:
                msg_text = f"{number}. Реферал: {client.first_name}\n"

        return msg_text
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in referrals_handler.py in parse_referrer function: {e}",
            module_name="doroshka_bot"
        )


@handler_logging
async def referrers_menu(message, page):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )

        referral = await ClientMiddleware.get_client(
            chat_id=message.chat.id
        )

        referrers = await ClientMiddleware.get_all_referrers_by_link(
            referral_link=referral.referral_link
        )
        if (len(referrers) == 0):
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text="Вашей реферальной ссылкой никто не воспользовался... пока что... 🍃",
                reply_markup=types.InlineKeyboardMarkup(
                    row_width=1, 
                    keyboard=[
                        [
                            types.InlineKeyboardButton(
                                text="🔙 Назад",
                                callback_data="back_to_profile_menu"
                            )
                        ]
                    ]
                )
            )
        else:
            amount_of_pages = ceil(len(referrers)/STRINGS_PER_PAGE)
            
            chunks = []
            i = 0
            while i < len(referrers):
                chunks.append(referrers[i:i + STRINGS_PER_PAGE])
                i += STRINGS_PER_PAGE

            data_to_display = chunks[page - 1]

            msg_text = ""
            number = 1 + (page - 1)*STRINGS_PER_PAGE
            for data in data_to_display:
                msg_text += await parse_referrer(referrer=data, number=number)
                number += 1

            msg = await bot.send_message(
                chat_id=message.chat.id,
                text=msg_text,
                reply_markup=InlineMarkup.referres_slider(
                    page=page,
                    amount_of_pages=amount_of_pages
                )
        )
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id,
            msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in referrals_handler.py in referrers_menu function: {e}",
            module_name="doroshka_bot"
        )

@handler_logging
async def invite_friend(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )
        referral_link = await ClientMiddleware.get_referral_link(
            chat_id=message.chat.id
        )
        full_referral_link = f"t.me/{BOT_NAME}?start=referal_{referral_link}"
        switch_inline_query_text = f"\n Нажми на эту ссылку, чтобы получить 200 рублей при пополнении баланса профиля {full_referral_link}"
        msg_ref_link = await bot.send_message(
            chat_id=message.chat.id,
            text=
            f"""*Система рефералов:*
            ▪️ Любой человек, использовавший твою ссылку при регистрации в одном из ботов нашего заведения, становится твоим рефералом
            ▪️ Ты получишь 200 баллов на баланс профиля, если человек, использовавший твою ссылку, пополнит баланс
            ▪️ Твои рефёреры получат 200 баллов на баланс при первом пополнении баланса
            """,
            reply_markup=types.InlineKeyboardMarkup(
                row_width=1, 
                keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="🔗 Поделись своей реферальной ссылкой",
                            switch_inline_query=switch_inline_query_text
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="🔙 Назад",
                            callback_data="back_to_profile_menu"
                        )
                    ]
                ]
            ),
            parse_mode="MarkDown"
        )    
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id,
            msgId=msg_ref_link.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in referrals_handler.py in invite_friend function: {e}",
            module_name="doroshka_bot"
        )


@handler_logging
async def handle_referral_link(message, referral_link: str):
    try:
        client = await ClientMiddleware.get_client_by_ref_link(referral_link=referral_link)
        referrals = await ReferralMiddleware.get_all_referrals()

        if (message.chat.id in [referral.chat_id for referral in referrals]):
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text=f"❌Вы уже использовали реферальную ссылку",
                parse_mode="HTML"
            )
            return None
        
        elif (not(isinstance(client, Client))):
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text=f"❌Не существует такого пользователя с реферальной ссылкой {referral_link}",
                parse_mode="HTML"
            )
            return None

        else:
            result = await ReferralMiddleware.create_referral(
                referral_id=client.chat_id,
                referrer_id=message.chat.id
            )
            if (result == DBTransactionStatus.SUCCESS):
                to_insert = client.chat_id if client.username == None else client.username
                msg = await bot.send_message(
                    chat_id=message.chat.id,
                    text=f"✅Реферальная ссылка была успешно использована, теперь вы являетесь рефералом {to_insert}",
                    parse_mode="HTML"
                )
                await bot.delete_state(message.chat.id, message.chat.id)
            else:
                msg = await bot.send_message(
                    chat_id=message.chat.id,
                    text=f"❌Произошла ошибка при добавлении реферала пользователю с ссылкой {referral_link}, повторите попытку еще раз",
                    parse_mode="HTML"
                )
            return None
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in referrals_handler.py in handle_referral_link function: {e}",
            module_name="doroshka_bot"
        )

    
