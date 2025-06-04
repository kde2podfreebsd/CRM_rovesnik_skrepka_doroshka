import os

from telebot import types

from BackendApp import basedir
from BackendApp.TelegramBots.Rovesnik.Config import bot
from BackendApp.TelegramBots.Rovesnik.Middlewares.message_context_middleware import (
    message_context_manager,
)
from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

menu_main_folder = f"{basedir}/static/menu/main_rovesnik"
speshl_folder = f"{basedir}/static/menu/speshl_rovesnik"

async def send_documents_from_folder(folder_path, chat_id):
    ids = []
    for filename in os.listdir(folder_path):
        joined_path = os.path.join(folder_path, filename)
        if os.path.isfile(joined_path):
            if (filename.endswith(".pdf")):
                file = open(joined_path, "rb")
                msg = await bot.send_document(
                    chat_id=chat_id,
                    document=file
                )
                ids.append(msg.id)

    return ids


@handler_logging
async def send_menu(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)
        # Отправка документов из папки 'menu_main'
        if (os.path.exists(menu_main_folder)):
            msg_ids = await send_documents_from_folder(menu_main_folder, message.chat.id)
            if (msg_ids):
                for msg_id in msg_ids:
                    message_context_manager.add_msgId_to_help_menu_dict(
                        chat_id=message.chat.id,
                        msgId=msg_id
                    )

        # Отправка документов из папки 'speshl'
        if (os.path.exists(speshl_folder)): 
            msg_ids = await send_documents_from_folder(speshl_folder, message.chat.id)
            if (msg_ids):
                for msg_id in msg_ids:
                    message_context_manager.add_msgId_to_help_menu_dict(
                        chat_id=message.chat.id,
                        msgId=msg_id
                    )
        
        msg = await bot.send_message(
            chat_id = message.chat.id, 
            text = "Меню",
            reply_markup=types.InlineKeyboardMarkup(
                row_width=1,
                keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="🔙 Назад",
                            callback_data="back_to_main_menu"
                        )
                    ]
                ]
            )
        )
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id,
            msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in menu_handler.py in send_menu function: {e}",
            module_name="rovesnik_bot"
        )

