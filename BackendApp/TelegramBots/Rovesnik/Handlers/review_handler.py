from telebot import types
from BackendApp.TelegramBots.Rovesnik.Config.bot import bot
from BackendApp.TelegramBots.HeadBot.Config.bot import bot as head_bot
from BackendApp.TelegramBots.Rovesnik.Middlewares.context_manager import context_manager
from BackendApp.TelegramBots.Rovesnik.Middlewares.message_context_middleware import message_context_manager
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Middleware.bar_middleware import BarMiddleware
from BackendApp.Middleware.event_middleware import EventMiddleware
from BackendApp.Middleware.ticket_middleware import TicketMiddleware
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Middleware.review_middleware import ReviewMiddleware
from BackendApp.Middleware.promocodes_middleware import PromocodesMiddleware
from BackendApp.TelegramBots.Rovesnik.Markups.inline_markup import InlineMarkup

from telebot.asyncio_handler_backends import StatesGroup
from telebot.asyncio_handler_backends import State

from math import ceil

from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

from dotenv import load_dotenv
import os

load_dotenv()

BAR_ID = 1 # this param should be changed when expanding functionallity on all 3 bots
BUTTONS_PER_PAGE = 10
REVIEW_GROUP_CHAT_ID = os.getenv("REVIEW_GROUP_CHAT_ID")

class ReviewStates(StatesGroup):
    ReviewLeftBar = State()
    ReviewLeftEvent = State()

@handler_logging
async def review_menu(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        await bot.delete_state(message.chat.id)
        mp = types.InlineKeyboardMarkup(row_width=1)
        leave_feedback_bar = types.InlineKeyboardButton(
            text="Оставить отзыв на бар",
            callback_data="leave_feedback_bar"
        )
        leave_feedback_event = types.InlineKeyboardButton(
            text="Оставить отзыв на прошедшее мероприятие",
            callback_data="leave_feedback_event"
        )
        yandex_maps = types.InlineKeyboardButton(
            text="Yandex Maps",
            callback_data="yandex_maps"
        )
        back_to_main_menu = types.InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back_to_main_menu"
        )
        mp.add(leave_feedback_bar, leave_feedback_event)
        reviews = await ReviewMiddleware.get_by_chat_id(chat_id=message.chat.id)
        client = await ClientMiddleware.get_client(chat_id=message.chat.id)

        if (reviews and not client.got_review_award):
            get_reward = types.InlineKeyboardButton(
                text="🎟 Получи бесплатный промокод за свой отзыв",
                callback_data="get_review_award"
            )
            mp.add(get_reward)

        mp.add(back_to_main_menu)

        msg = await bot.send_message(
            chat_id=message.chat.id,
            text="Напишите свой отзыв о баре или о прошедшем эвенте",
            reply_markup=mp
        )
        message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=msg.id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in review_handler.py in review_menu function: {e}",
            module_name="rovesnik_bot"
        )

@handler_logging
async def review_menu_bar(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text="🤗 Напишите свой отзыв о баре, нам очень важно ваше мнение",
            reply_markup=types.InlineKeyboardMarkup(
                row_width=1,
                keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="🔙 Назад",
                            callback_data="back_to_leave_feedback"
                        )
                    ]
                ]
            )
        )
        message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=msg.id)
        await bot.set_state(message.chat.id, ReviewStates.ReviewLeftBar)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in review_handler.py in review_menu_bar function: {e}",
            module_name="rovesnik_bot"
        )

@handler_logging
@bot.message_handler(state=ReviewStates.ReviewLeftBar)
async def review_bar_has_been_left(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text="Cпасибо за ваш отзыв, мы обязательно его учтем",
            reply_markup=types.InlineKeyboardMarkup(
                row_width=1,
                keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="🔙 Назад",
                            callback_data="back_to_leave_feedback"
                        )
                    ]
                ]
            )
        )
        message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=msg.id)

        review_text = message.text
        result = await ReviewMiddleware.create(
            chat_id=message.chat.id,
            text=review_text,
            bar_id=BAR_ID
        )
        await bot.delete_state(message.chat.id)

        if (result == DBTransactionStatus.SUCCESS):
            bar = await BarMiddleware.get_by_id(bar_id=BAR_ID)
            bar_name = bar.bar_name

            client = await ClientMiddleware.get_client(chat_id=message.chat.id)

            await head_bot.send_message(
                chat_id=REVIEW_GROUP_CHAT_ID,
                text=f"Бар: {bar_name}\nКлиент: @{client.username}\nОтзыв: {review_text}"
            )

    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in review_handler.py in review_bar_has_been_left function: {e}",
            module_name="rovesnik_bot"
        )

@handler_logging
async def review_menu_event_slider(message, page):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        await bot.delete_state(message.chat.id)
        past_events = await EventMiddleware.get_past_events_by_bar(bar_id=BAR_ID)
        past_events_ids = [event.id for event in past_events]
        client_tickets = await TicketMiddleware.get_by_chat_id(chat_id=message.chat.id)
        client_visited_events = []
        for ticket in client_tickets:
            if (ticket.activation_status):
                event = await EventMiddleware.get_event_by_id(event_id=ticket.event_id)
                if (event.id in past_events_ids):
                    client_visited_events.append(event)
        
        if (not client_visited_events):
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text="🍃 Слишком пусто... Сейчас нет ни одного прошедшего мероприятия",
                reply_markup=types.InlineKeyboardMarkup(
                    row_width=1, 
                    keyboard=[
                        [
                            types.InlineKeyboardButton(
                                text="🔙 Назад",
                                callback_data="back_to_leave_feedback"
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
            amount_of_pages = ceil(len(past_events)/BUTTONS_PER_PAGE)
            
            chunks = past_events[((page - 1)*BUTTONS_PER_PAGE) : page*BUTTONS_PER_PAGE]
            buttons = []
            for event in chunks:
                buttons.append(types.InlineKeyboardButton(
                    text=event.short_name,
                    callback_data=f"past_event_leave_feedback#{event.id}"
                ))
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text="Выберите прошедшее мероприятие, на которое хотите оставить отзыв",
                reply_markup=InlineMarkup.past_events_slider(
                    page=page,
                    amount_of_pages=amount_of_pages,
                    buttons=buttons
                )
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id,
                msgId=msg.id
            )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in review_handler.py in review_menu_event_slider function: {e}",
            module_name="rovesnik_bot"
        )

@handler_logging
async def review_menu_event(message, event_id):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text="🤗 Напишите свой отзыв о мероприятии, нам очень важно ваше мнение",
            reply_markup=types.InlineKeyboardMarkup(
                row_width=1,
                keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="🔙 Назад",
                            callback_data="back_to_leave_feedback_event"
                        )
                    ]
                ]
            )
        )
        message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=msg.id)
        context_manager.update_event_id(message.chat.id, event_id)
        await bot.set_state(message.chat.id, ReviewStates.ReviewLeftEvent)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in review_handler.py in review_menu_event function: {e}",
            module_name="rovesnik_bot"
        )

@handler_logging
@bot.message_handler(state=ReviewStates.ReviewLeftEvent)
async def review_event_has_been_left(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text="Cпасибо за ваш отзыв, мы обязательно его учтем",
            reply_markup=types.InlineKeyboardMarkup(
                row_width=1,
                keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="🔙 Назад",
                            callback_data="back_to_leave_feedback_event"
                        )
                    ]
                ]
            )
        )
        message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=msg.id)

        review_text = message.text
        result = await ReviewMiddleware.create(
            chat_id=message.chat.id,
            text=review_text,
            event_id=context_manager.context[message.chat.id]
        )
        await bot.delete_state(message.chat.id)

        if (result == DBTransactionStatus.SUCCESS):
            event = await EventMiddleware.get_event_by_id(
                event_id=context_manager.context[message.chat.id]
            )
            event_short_name = event.short_name
            bar_id = event.bar_id

            bar = await BarMiddleware.get_by_id(bar_id=bar_id)
            bar_name = bar.bar_name

            client = await ClientMiddleware.get_client(chat_id=message.chat.id)

            await head_bot.send_message(
                chat_id=REVIEW_GROUP_CHAT_ID,
                text=f"Бар: {bar_name}\nНазвание мероприятия: {event_short_name}\nКлиент: @{client.username}\nОтзыв: {review_text}"
            )

    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in review_handler.py in review_event_has_been_left function: {e}",
            module_name="rovesnik_bot"
        )

@handler_logging
async def get_review_award(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)
        promocodes = await PromocodesMiddleware.get_free_promocodes()
        msg_text = None
        if (promocodes != DBTransactionStatus.NOT_EXIST):
            promocode_to_give = promocodes[0]
            result = await PromocodesMiddleware.add_client_to_promocode(
                number=promocode_to_give.number,
                client_chat_id=message.chat.id
            )
            if (result == DBTransactionStatus.SUCCESS):
                msg_text = "🥳 Вы успешно получили промокод за оставленный отзыв. Вы можете посмотреть его наличие в \"🎟 Мои промокоды\"."
                await ClientMiddleware.update_got_review_award(message.chat.id)
            else:
                msg_text = "😔 Произошла ошибка при попытки назначения промокода, обратитесь в техническую поддержку."
            
        else:
            msg_text = "😔 В настоящее время нет промокодов в базе данных."
        
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=types.InlineKeyboardMarkup(
                row_width=1,
                keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="🔙 Назад",
                            callback_data="back_to_leave_feedback"
                        )
                    ]
                ]
            )
        )
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id, msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in review_handler.py in get_review_award function: {e}",
            module_name="rovesnik_bot"
        )
