import os

from telebot import types

from BackendApp import basedir
from BackendApp.Database.DAL.client_dal import ClientDAL
from BackendApp.Database.session import async_session
from BackendApp.IIKO.api import Client
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Middleware.loyalty_middleware import (
    LoyaltyMiddleware,
    NextLevelNotExistException,
)
from BackendApp.Middleware.transaction_middleware import TransactionMiddleware
from BackendApp.TelegramBots.Skrepka.Config import bot
from BackendApp.TelegramBots.Skrepka.Markups.inline_markup import InlineMarkup
from BackendApp.TelegramBots.Skrepka.Markups.message_text import MessageText
from BackendApp.TelegramBots.Skrepka.Middlewares.message_context_middleware import (
    message_context_manager,
)
from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

API_LOGIN = os.getenv("API_LOGIN")


@handler_logging
async def profile_menu(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        
        warning = await bot.send_message(
            chat_id=message.chat.id,
            text="<i>Пожалуйста, подождите...</i>",
            parse_mode="html",
        )
        message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=warning.message_id)
        await LoyaltyMiddleware.check_client_level(message.chat.id)
        async with async_session() as session:
            client_dal = ClientDAL(session)
            user = await client_dal.get_client(chat_id=message.chat.id)
            client_iiko = await Client.create(API_LOGIN, "Rovesnik")
            iiko_client_info = await client_iiko.get_customer_info(id=user.iiko_id)
            loyalty_info = await client_iiko.get_customer_loyalty_info(user.iiko_id)
            
            
            additional_loyalty = None
            for loyalty in loyalty_info:
                if loyalty.category == "level":
                    user_level_loyalty = loyalty
                if loyalty.category == "additional":
                    additional_loyalty = loyalty 

        # open(rf'{basedir}/qr_codes/{loyalty_info["iiko_card"]}.png', "rb")

        all_loyalties = await client_iiko.get_full_customer_categories()
        next_level_loyalty = await LoyaltyMiddleware.get_next_level(all_loyalties, user_level_loyalty)

        if loyalty_info:
            msg = await bot.send_photo(
                chat_id=message.chat.id,
                photo=open(
                    ClientMiddleware.generate_image(
                        user=user,
                        balance=iiko_client_info.walletBalances[0]["balance"],
                        user_level_loyalty=user_level_loyalty,
                        next_level_loyalty=next_level_loyalty,
                        additional_loyalty=additional_loyalty,
                        actual_spend_money_amount=user_level_loyalty.spend_money_amount,
                        qr_code_path=(f"{basedir}/static/user_qrcode/{user.iiko_card}.png"),
                        background_path=(f"{basedir}/static/user_info/source/user_profile_s.jpg"),
                    ),
                    "rb",
                ),
                reply_markup=InlineMarkup.profile_menu(),
                parse_mode="html",
            )
            await message_context_manager.delete_msgId_from_help_menu_dict(
                chat_id=message.chat.id
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text="Failed to retrieve loyalty information. Please try again later.",
            )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in profile_handler.py in profile_menu function: {e}",
            module_name="skrepka_bot"
        )