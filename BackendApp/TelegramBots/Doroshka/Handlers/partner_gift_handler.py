from telebot import types
from BackendApp.TelegramBots.Doroshka.Config.bot import bot
from BackendApp.TelegramBots.Doroshka.Middlewares.message_context_middleware import message_context_manager
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Middleware.partner_gift_middleware import PartnerGiftMiddleware
from BackendApp.Middleware.promocodes_middleware import PromocodesMiddleware
from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

BAR_ID = 3

@handler_logging
async def partner_gift_menu(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)

        mp = types.InlineKeyboardMarkup(row_width=1)
        partner_gifts = await PartnerGiftMiddleware.get_by_bar_id(bar_id=BAR_ID)
        msg_text = "Подарки от партнёров 🤩" if partner_gifts else "🍃 Пока что нет подарков от партнёров..."

        for partner_gift in partner_gifts:
            mp.add(
                types.InlineKeyboardButton(
                    text=partner_gift.short_name,
                    callback_data=f"partner_gift#{partner_gift.id}"
                )
            )
        
        mp.add(
            types.InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back_to_promo_menu"
            )
        )
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=mp
        )

        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id, msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in partner_gift_handler.py in partner_gift_menu function: {e}",
            module_name="doroshka_bot"
        )

@handler_logging
async def get_partner_gift_menu(message, partner_gift_id):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)

        mp = types.InlineKeyboardMarkup(row_width=1)
        partner_gift = await PartnerGiftMiddleware.get_by_id(partner_gift_id=partner_gift_id)
        if (message.chat.id in partner_gift.got_gift):
            mp.add(
                types.InlineKeyboardButton(
                    text="🥳 Вы уже получили бесплатный промокод от партнёра",
                    callback_data="nullified"
                )
            )
        else:
            mp.add(
                types.InlineKeyboardButton(
                    text="🎟 Получи бесплатный промокод",
                    callback_data=f"get_free_promocode#{partner_gift_id}"
                )
            )
        mp.add(
            types.InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back_to_partner_gift"
            )
        )

        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=partner_gift.promotion_text,
            reply_markup=mp
        )

        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id, msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in partner_gift_handler.py in get_partner_gift_menu function: {e}",
            module_name="doroshka_bot"
        )

@handler_logging
async def get_free_promocode_menu(message, partner_gift_id):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)
        
        free_promocodes = await PromocodesMiddleware.get_free_promocodes()
        partner_gift = await PartnerGiftMiddleware.get_by_id(partner_gift_id=partner_gift_id)

        msg_text = None
        if (free_promocodes != DBTransactionStatus.NOT_EXIST):
            result = await PromocodesMiddleware.add_client_to_promocode(
                number=free_promocodes[0].number, 
                client_chat_id=message.chat.id
            )
            if (result == DBTransactionStatus.SUCCESS):
                new_got_gift = partner_gift.got_gift
                new_got_gift.append(message.chat.id)
                result = await PartnerGiftMiddleware.update(
                    partner_gift_id=partner_gift_id,
                    got_gift=new_got_gift
                )
                msg_text = "Вам был успешно добавлен случайный новый промокод 🥳 Вы можете посмотреть его наличие в вкладке профиля \"🎟 Мои промокоды\""
            else:
                msg_text = "Произошла ошибка при взаимодействии с базой данных, попробуйте еще раз позже 😔"

        else:
            msg_text = "К сожалению, сейчас нет доступных свободных промокодов в базе данных 😔"
        
        mp = types.InlineKeyboardMarkup(row_width=1)
        mp.add(
            types.InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back_to_partner_gift"
            )
        )
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=mp
        )

        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id, msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in partner_gift_handler.py in get_free_promocode_menu function: {e}",
            module_name="doroshka_bot"
        )
    
