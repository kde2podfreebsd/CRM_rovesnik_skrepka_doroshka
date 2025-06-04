from BackendApp.TelegramBots.Doroshka.Config import bot
from BackendApp.TelegramBots.Doroshka.Markups.message_text import MessageText
from BackendApp.TelegramBots.Doroshka.Markups.inline_markup import InlineMarkup
from BackendApp.TelegramBots.Doroshka.Middlewares.message_context_middleware import message_context_manager
from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

@handler_logging
async def promotions(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        
        msg = await bot.send_message(
            message.chat.id,
            MessageText.promotions_text(),
            reply_markup=InlineMarkup.promotions_menu(),
            parse_mode="html"
        )
        
        message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=msg.message_id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in promotions_handler.py in promotions function: {e}",
            module_name="doroshka_bot"
        )

