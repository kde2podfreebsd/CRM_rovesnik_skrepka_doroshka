from BackendApp.Database.DAL.client_dal import ClientDAL
from BackendApp.Database.session import async_session
from BackendApp.Logger import LogLevel, logger
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.TelegramBots.HeadBot.Config import bot
from BackendApp.TelegramBots.HeadBot.Markups.inline_markup import InlineMarkup
from BackendApp.TelegramBots.HeadBot.Markups.message_text import MessageText
from BackendApp.TelegramBots.HeadBot.Middlewares.message_context_middleware import (
    message_context_manager,
)
from BackendApp.TelegramBots.utils.handler_loggining import handler_logging

@handler_logging
async def main_menu(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        await ClientMiddleware.update_client_data(
            chat_id=message.chat.id, 
            username=message.chat.username, 
            first_name=message.chat.first_name, 
            last_name=message.chat.last_name, 
        )
        msg = await bot.send_message(
            message.chat.id,
            MessageText.menu_text(),
            reply_markup=InlineMarkup.main_menu(),
            parse_mode="HTML",
        )
        message_context_manager.add_msgId_to_help_menu_dict(chat_id=msg.chat.id, msgId=msg.message_id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in main_menu_handler.py in main_menu function: {e}",
            module_name="head_bot"
        )  
