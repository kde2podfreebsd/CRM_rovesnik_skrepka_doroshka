from telebot import types

from BackendApp.TelegramBots.HeadBot.Config import bot
from BackendApp.TelegramBots.HeadBot.Middlewares.message_context_middleware import message_context_manager
from BackendApp.TelegramBots.HeadBot.Markups.message_text import MessageText
from BackendApp.TelegramBots.HeadBot.Markups.inline_markup import InlineMarkup
from BackendApp.Middleware.faq_middleware import FAQMiddleware
from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

BAR_ID = 0

@handler_logging
async def help_menu(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)

        entity = await FAQMiddleware.get_by_bar_id(bar_id=BAR_ID)
        if (entity):
            msg = await bot.send_message(
                message.chat.id,
                entity.text,
                reply_markup=InlineMarkup.help_menu(),
                parse_mode = "MarkDown",
            )
        else:
            msg = await bot.send_message(
                message.chat.id,
                text="😔 Это секция пока что не была заполнена, вернитесь позже",
                reply_markup=InlineMarkup.help_menu(),
                parse_mode = "MarkDown",
            )

        message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=msg.message_id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in faq_handler.py in send_next_quiz function: {e}",
            module_name="head_bot"
        )    
