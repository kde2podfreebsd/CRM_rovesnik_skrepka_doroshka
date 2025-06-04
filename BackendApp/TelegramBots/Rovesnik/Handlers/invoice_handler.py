import asyncio
import os

from dotenv import load_dotenv
from typing import List
from telebot.types import LabeledPrice
from telebot.types import ShippingOption

from BackendApp.TelegramBots.Rovesnik.Config import bot
from BackendApp.TelegramBots.HeadBot.Config import bot as head_bot
from BackendApp.TelegramBots.Rovesnik.Config.bot import provider_token
from BackendApp.TelegramBots.Rovesnik.Middlewares.message_context_middleware import message_context_manager

from BackendApp.TelegramBots.Rovesnik.Markups.message_text import MessageText
from BackendApp.TelegramBots.Rovesnik.Markups.inline_markup import InlineMarkup

from BackendApp.Database.Models.client_model import Client
from BackendApp.Database.Models.referrals_model import Referral
from BackendApp.Database.Models.event_model import Event

from BackendApp.Database.session import async_session, DBTransactionStatus
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Middleware.transaction_middleware import TransactionMiddleware, TX_TYPES
from BackendApp.Middleware.referrals_middleware import ReferralMiddleware
from BackendApp.Middleware.event_middleware import EventMiddleware
from BackendApp.Middleware.ticket_middleware import TicketMiddleware
from BackendApp.Middleware.bar_middleware import BarMiddleware
from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel


load_dotenv()

BAR_ID = 1
INVITE_YOUR_FRIEND_BONUS = 200 * 100

class Prices:

    prices1000 = [
        LabeledPrice(label="1000₽ + 3% - cashback", amount=1000 * 100)
    ]

    prices2500 = [
        LabeledPrice(label="2500₽ + 4% - cashback", amount=2500 * 100)
    ]

    prices5000 = [
        LabeledPrice(label="5000₽ + 5% - cashback", amount=5000 * 100)
    ]

    prices10000 = [
        LabeledPrice(label="10 000₽ + 7% - cashback", amount=10000 * 100)
    ]

    prices25000 = [
        LabeledPrice(label="25 000₽ + 9% - cashback", amount=25000 * 100)
    ]

    prices100000 = [
        LabeledPrice(label="100 000₽ +15% - cashback", amount=100000 * 100)
    ]

@handler_logging
async def invoice_menu(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        msg = await bot.send_message(
            message.chat.id,
            MessageText.invoice_menu(),
            parse_mode="html",
            reply_markup=InlineMarkup.PaymentBtnList(chat_id=message.chat.id)
        )

        message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=msg.message_id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in invoice_handler.py in help_menu function: {e}",
            module_name="rovesnik_bot"
        )


@handler_logging
async def payment1000(message):

    msg = await bot.send_invoice(
        message.chat.id,  # chat_id
        "Пополнить баланс на 1000₽",  # title
        "Пополнить баланс на 1000₽ + 3% cashback = 1030₽",  # description
        "Пополнить баланс на 1000₽",  # invoice_payload
        provider_token,
        "RUB",
        Prices.prices1000
    )
    message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id,
        msgId=msg.id
    )

@handler_logging
async def payment2500(message):

    msg = await bot.send_invoice(
        message.chat.id,  # chat_id
        "Пополнить баланс на 2500₽",  # title
        "Пополнить баланс на 2500₽ + 4% cashback = 2600₽",  # description
        "Пополнить баланс на 2500₽",  # invoice_payload
        provider_token,
        "RUB",
        Prices.prices2500
    )
    message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id,
        msgId=msg.id
    )

@handler_logging
async def payment5000(message):

    msg = await bot.send_invoice(
        message.chat.id,  # chat_id
        "Пополнить баланс на 5000₽",  # title
        "Пополнить баланс на 5000₽ + 5% cashback = 5250₽",  # description
        "Пополнить баланс на 5000₽",  # invoice_payload
        provider_token,
        "RUB",
        Prices.prices5000
    )
    message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id,
        msgId=msg.id
    )

@handler_logging
async def payment5000(message):

    msg = await bot.send_invoice(
        message.chat.id,  # chat_id
        "Пополнить баланс на 5000₽",  # title
        "Пополнить баланс на 5000₽ + 5% cashback = 5250₽",  # description
        "Пополнить баланс на 5000₽",  # invoice_payload
        provider_token,
        "RUB",
        Prices.prices5000
    )
    message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id,
        msgId=msg.id
    )

@handler_logging
async def payment10000(message):

    msg = await bot.send_invoice(
        message.chat.id,  # chat_id
        "Пополнить баланс на 10 000₽",  # title
        "Пополнить баланс на 10 000₽ + 7% cashback = 10 700₽",  # description
        "Пополнить баланс на 10 000₽",  # invoice_payload
        provider_token,
        "RUB",
        Prices.prices10000
    )
    message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id,
        msgId=msg.id
    )

@handler_logging
async def payment25000(message):

    msg = await bot.send_invoice(
        message.chat.id,  # chat_id
        "Пополнить баланс на 25 000₽",  # title
        "Пополнить баланс на 25 000₽ + 9% cashback = 27 250₽",  # description
        "Пополнить баланс на 25 000₽",  # invoice_payload
        provider_token,
        "RUB",
        Prices.prices25000
    )
    message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id,
        msgId=msg.id
    )

@handler_logging

async def payment100000(message):

    msg = await bot.send_invoice(
        message.chat.id,  # chat_id
        "Пополнить баланс на 100 000₽",  # title
        "Пополнить баланс на 100 000₽ + 15% cashback = 115 000₽",  # description
        "Пополнить баланс на 100 000₽",  # invoice_payload
        provider_token,
        "RUB",
        Prices.prices100000
    )
    message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id,
        msgId=msg.id
    )

@handler_logging
async def db_communication_error(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)
        msg = await bot.send_message(
            message.chat.id,
            f"<b>❌ Произошла ошибка при обращении к базе данных, попробуйте еще раз через некоторое время или обратитесь в тех поддержку</b> ",
            reply_markup=InlineMarkup.main_menu(),
            parse_mode='html'
        )
        message_context_manager.add_msgId_to_help_menu_dict(message.chat.id, msg.id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in invoice_handler.py in db_communication_error function: {e}",
            module_name="rovesnik_bot"
        )

@handler_logging
async def successful_tx(message, cashback):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)
        msg = await bot.send_message(
            message.chat.id,
            f"<b>✅ Ваша оплата успешно прошла!</b> Спасибо за пополнение баланса на сумму {(message.successful_payment.total_amount / 100) * cashback} {message.successful_payment.currency}.",
            reply_markup=InlineMarkup.main_menu(),
            parse_mode='html'
        )
        message_context_manager.add_msgId_to_help_menu_dict(message.chat.id, msg.id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in invoice_handler.py in successful_tx function: {e}",
            module_name="rovesnik_bot"
        )


async def register_client_to_events(events: List[Event], chat_id: str):
    for event in events:
        await TicketMiddleware.purchase_ticket(
            event_id=event.id,
            client_chat_id=chat_id,
            friends=None
        )

async def send_referral_notification(referral: Client, referrer: Referral):
    client = await ClientMiddleware.get_client(chat_id=referrer.chat_id)
    msg_text = ""
    if (client.username):
        msg_text = f"🤠 Ваш реферал {client.username} пополнил баланс профиля в первый раз и вам было начислено 200 бонусов"
    elif (client.first_name):
        if (client.last_name):
            msg_text = f"🤠 Ваш реферал {client.first_name} {client.last_name} пополнил баланс профиля в первый раз и вам было начислено 200 бонусов"
        else:
            msg_text = f"🤠 Ваш реферал {client.first_name} пополнил баланс профиля в первый раз и вам было начислено 200 бонусов"
    else:
        msg_text = f"🤠 Один из ваших рефералов пополнил баланс профиля в первый раз и вам было начислено 200 бонусов"
    
    try:
        msg = await head_bot.send_message(
            chat_id=referral.chat_id,
            text=msg_text
        )
    except Exception: 
        # a client can be not authorised in the head bot, but a bot cannot send a message to them, unless they had sent him a message,
        # resulting in not sending the referral message: 'Bad Request: chat not found'
        pass

@bot.shipping_query_handler(func=lambda query: True)
async def shipping(shipping_query):
    await bot.answer_shipping_query(
        shipping_query.id,
        ok=True,
        # shipping_options=Prices.shipping_options,
        error_message="Ошибка, попробуйте позже или напишите в тех поддержку",
    )


@bot.pre_checkout_query_handler(func=lambda query: True)
async def checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True,
        error_message="Что-то случилось на стороне эквайринга, попробуйте позже или напишите в тех поддержку",
    )

@handler_logging
@bot.message_handler(content_types=["successful_payment"])
async def got_payment(message):
    try:
        if message.successful_payment.total_amount / 100 == 1000:
            cashback = 1.03

        if message.successful_payment.total_amount / 100 == 2500:
            cashback = 1.04

        if message.successful_payment.total_amount / 100 == 5000:
            cashback = 1.05

        if message.successful_payment.total_amount / 100 == 10000:
            cashback = 1.07

        if message.successful_payment.total_amount / 100 == 25000:
            cashback = 1.09

        if message.successful_payment.total_amount / 100 == 100000:
            cashback = 1.15

        referrer_status = await ReferralMiddleware.get_status(
            referrer_id=message.chat.id
        )
        
        events = await EventMiddleware.get_all_today_deposit_events()

        await register_client_to_events(
            events=events, chat_id=message.chat.id
        )

        if (referrer_status is False):
            is_refilled = await ClientMiddleware.refill_balance(
                chat_id=message.chat.id,
                amount=(message.successful_payment.total_amount / 100) * cashback + INVITE_YOUR_FRIEND_BONUS / 100
            )

            if (is_refilled != DBTransactionStatus.SUCCESS): 
                await db_communication_error(message)
                return

            is_updated = await ReferralMiddleware.update_status(
                referrer_id=message.chat.id
            )

            if (is_updated != DBTransactionStatus.SUCCESS):
                await db_communication_error(message)
                return

            referrer = await ReferralMiddleware.get_referral(referrer_id=message.chat.id)
            if (referrer == DBTransactionStatus.NOT_EXIST):
                await db_communication_error(message)
                return

            referral_link = referrer.referral_link
            referral = await ClientMiddleware.get_client_by_ref_link(
                referral_link=referral_link
            )
            if (referral == DBTransactionStatus.NOT_EXIST):
                await db_communication_error(message)
                return

            is_referral_refilled = await ClientMiddleware.refill_balance(
                chat_id=referral.chat_id,
                amount=INVITE_YOUR_FRIEND_BONUS / 100
            )
            if (is_referral_refilled != DBTransactionStatus.SUCCESS):
                await db_communication_error(message)
                return
            
            await TransactionMiddleware.create_tx(
                bar_id=BAR_ID,
                amount=INVITE_YOUR_FRIEND_BONUS / 100,
                final_amount=INVITE_YOUR_FRIEND_BONUS / 100,
                client_chat_id=referral.chat_id,
                tx_type=TX_TYPES.INCREASE_BALANCE
            )

            await TransactionMiddleware.create_tx(
                bar_id=BAR_ID,
                amount=message.successful_payment.total_amount / 100,
                final_amount=(message.successful_payment.total_amount / 100) * cashback + INVITE_YOUR_FRIEND_BONUS / 100,
                client_chat_id=referrer.chat_id,
                tx_type=TX_TYPES.INCREASE_BALANCE
            )

            await successful_tx(message, cashback)
            await send_referral_notification(referral=referral, referrer=referrer)

        else: # referrer_status is either True or DBTransactionStatus.NOT_EXIST
            is_refilled = await ClientMiddleware.refill_balance(
                chat_id=message.chat.id,
                amount=(message.successful_payment.total_amount / 100) * cashback
            )
            if (is_refilled != DBTransactionStatus.SUCCESS):
                await db_communication_error(message)
                return
            await TransactionMiddleware.create_tx(
                bar_id=BAR_ID,
                amount=message.successful_payment.total_amount / 100,
                final_amount=(message.successful_payment.total_amount / 100) * cashback,
                client_chat_id=message.chat.id,
                tx_type=TX_TYPES.INCREASE_BALANCE
            )

            await successful_tx(message, cashback)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in invoice_handler.py in got_payment function: {e}",
            module_name="rovesnik_bot"
        )