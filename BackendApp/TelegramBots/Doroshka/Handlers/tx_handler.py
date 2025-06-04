from math import ceil

from telebot import types

from BackendApp.Database.Models.transaction_model import Transaction
from BackendApp.Middleware.bar_middleware import BarMiddleware
from BackendApp.Middleware.transaction_middleware import TX_TYPES, TransactionMiddleware
from BackendApp.TelegramBots.Doroshka.Config import bot
from BackendApp.TelegramBots.Doroshka.Markups.inline_markup import InlineMarkup
from BackendApp.TelegramBots.Doroshka.Middlewares.message_context_middleware import (
    message_context_manager,
)
from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

STRINGS_PER_PAGE = 10

async def parse_tx(tx: Transaction, number: int):
    bar_name = (await BarMiddleware.get_by_id(bar_id=tx.bar_id)).bar_name
    if (tx.tx_type == TX_TYPES.INCREASE_BALANCE):
        return f"""{number}. Бар: {bar_name} | Ваш баланс был пополнен на {tx.final_amount}₽ | Время: {str(tx.time_stamp).split(".")[0]}\n"""
    elif (tx.tx_type == TX_TYPES.REDUCE_BALANCE):
        return f"""{number}. Бар: {bar_name} | С вашего баланса было снято {tx.final_amount}₽ | Время: {str(tx.time_stamp).split(".")[0]}\n"""

    
@handler_logging
async def transactions_menu(message, page):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )
        
        txs = await TransactionMiddleware.get_all_tx(
            client_chat_id=message.chat.id
        )

        if (len(txs) == 0):
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text="🍃 Слишком пусто... Вы не произвели ни одной транзакции",
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
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id,
                msgId=msg.id
            )
        else:
            amount_of_pages = ceil(len(txs)/STRINGS_PER_PAGE)
            
            chunks = []
            i = 0
            while i < len(txs):
                chunks.append(txs[i:i + STRINGS_PER_PAGE])
                i += STRINGS_PER_PAGE

            data_to_display = chunks[page - 1]

            msg_text = ""
            number = 1 + (page - 1)*STRINGS_PER_PAGE
            for data in data_to_display:
                msg_text += await parse_tx(tx=data, number=number)
                number += 1

            msg = await bot.send_message(
                chat_id=message.chat.id,
                text=msg_text,
                reply_markup=InlineMarkup.transactions_slider(
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
            message=f"An error occurred in tx_handler.py in transaction_menu function: {e}",
            module_name="doroshka_bot"
        )
