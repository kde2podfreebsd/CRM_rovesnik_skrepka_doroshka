from telebot import types
from BackendApp.TelegramBots.HeadBot.Config.bot import bot
from BackendApp.TelegramBots.HeadBot.Middlewares.context_manager import context_manager
from BackendApp.TelegramBots.HeadBot.Middlewares.message_context_middleware import message_context_manager
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Middleware.bar_middleware import BarMiddleware
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Middleware.review_middleware import ReviewMiddleware
from BackendApp.Middleware.promocodes_middleware import PromocodesMiddleware
from BackendApp.TelegramBots.HeadBot.Markups.message_text import MessageText
from BackendApp.TelegramBots.HeadBot.Markups.inline_markup import InlineMarkup


from telebot.asyncio_handler_backends import StatesGroup
from telebot.asyncio_handler_backends import State

from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

from dotenv import load_dotenv
import os

load_dotenv()

REVIEW_GROUP_CHAT_ID = os.getenv("REVIEW_GROUP_CHAT_ID")

class ReviewStates(StatesGroup):
    ReviewLeft = State()

async def leave_feedback(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        mp = types.InlineKeyboardMarkup(row_width=1)

        rovesnik_feedback = types.InlineKeyboardButton(
            text="Ровесник", 
            callback_data="rovesnik_feedback"
        )
        screpka_feedback = types.InlineKeyboardButton(
            text="Скрепка", 
            callback_data="screpka_feedback"
        )
        doroshka_feedback = types.InlineKeyboardButton(
            text="Дорожка", 
            callback_data="doroshka_feedback"
        )
        yandex_maps = types.InlineKeyboardButton(
            text="Yandex Maps", 
            callback_data="yandex_maps"
        )
        back_to_help_menu = types.InlineKeyboardButton(
            text="🔙 Назад", 
            callback_data="back_to_main_menu"
        )
        mp.add(rovesnik_feedback, screpka_feedback, doroshka_feedback)

        reviews = await ReviewMiddleware.get_by_chat_id(chat_id=message.chat.id)
        client = await ClientMiddleware.get_client(chat_id=message.chat.id)
        if (reviews and not client.got_review_award):
            get_reward = types.InlineKeyboardButton(
                text="🎟 Получи бесплатный промокод за свой отзыв",
                callback_data="get_review_award"
            )
            mp.add(get_reward)

        # add logic for yandex maps

        mp.add(back_to_help_menu)
        
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=MessageText.leave_feedback_text(),
            reply_markup=mp,
        )
        message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=msg.message_id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in review_handler.py in leave_feedback function: {e}",
            module_name="head_bot"
        )  

@handler_logging
async def review_menu(message, bar_id):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        await bot.delete_state(message.chat.id)
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
        context_manager.update_bar_id(message.chat.id, bar_id)
        await bot.set_state(message.chat.id, ReviewStates.ReviewLeft)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in review_handler.py in review_menu function: {e}",
            module_name="head_bot"
        )  
    
@bot.message_handler(state=ReviewStates.ReviewLeft)
async def review_has_been_left(message):
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
            bar_id=context_manager.context[message.chat.id]
        )
        await bot.delete_state(message.chat.id)

        if (result == DBTransactionStatus.SUCCESS):
            bar = await BarMiddleware.get_by_id(
                bar_id=context_manager.context[message.chat.id]
            )
            bar_name = bar.bar_name

            client = await ClientMiddleware.get_client(chat_id=message.chat.id)

            await bot.send_message(
                chat_id=REVIEW_GROUP_CHAT_ID,
                text=f"Бар: {bar_name}\nКлиент: @{client.username}\nОтзыв: {review_text}"
            )

    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in review_handler.py in review_has_been_left function: {e}",
            module_name="head_bot"
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
            module_name="head_bot"
        )