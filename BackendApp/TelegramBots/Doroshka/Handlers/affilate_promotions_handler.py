from telebot import types

from BackendApp.Middleware.promocodes_middleware import PromocodesMiddleware
from BackendApp.TelegramBots.Doroshka.Config import bot
from BackendApp.TelegramBots.Doroshka.Middlewares.message_context_middleware import message_context_manager
from BackendApp.Middleware.quiz_middleware import *
from BackendApp.Middleware.affilate_promotions_middleware import *
from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

BAR_ID = 3

@handler_logging
async def affilate_promotions(message, edit=False):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)

        promo_short_info = await get_promo_short_info_by_bar_id(bar_id=BAR_ID)
        
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        for promo_info in promo_short_info:
            button = types.InlineKeyboardButton(text=promo_info[0], callback_data=str(promo_info[1]) + "_id" + "_affilate_promo")
            keyboard.add(button)

        back = types.InlineKeyboardButton("◀️ Назад", callback_data=f"back_to_promo_menu")
        keyboard.add(back)
        if (promo_short_info):
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text="🎁 Получите новую награду!",
                reply_markup=keyboard
            )
        else:
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text="Здесь нет промоушенов от партнёров... пока что... 🍃",
                reply_markup=keyboard
            )

        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id, msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in affiliate_promotions_handler.py in affiliate_promotions function: {e}",
            module_name="doroshka_bot"
        )

def get_promotion_text(promotion: AffilatePromotion) -> str:
    return f"""
✍ {promotion.promotion_text}

Вам необходимо подписаться на {promotion.channel_link}.

🎁 В качестве награды вы получите: промокод.
"""

@handler_logging
async def promotion_detail_info(message, promotion_id):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        promotion = await get_promotion_by_id(promotion_id)
        
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button_back = types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_affilate_promo")
        reload_button = types.InlineKeyboardButton(text="↻ Обновить", callback_data=str(promotion_id) + "_id_affilate_promo")

        subscribers = promotion.sub_chat_id
        username = "@" + str(promotion.channel_link.split("/")[-1])
        try:
            result = await bot.get_chat_member(chat_id=username, user_id=message.chat.id)
            if (isinstance(result, ChatMemberMember) and (str(message.chat.id) not in subscribers)):
                get_reward = types.InlineKeyboardButton(
                    text="⭐️ Получите награду",
                    callback_data=f"promotion_get_reward#{promotion_id}"
                )
                keyboard.add(get_reward)
        except Exception:
            pass # if a client is unsubscribed, then an exception will be risen
        
        keyboard.add(reload_button)
        keyboard.add(button_back)
        
        
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=get_promotion_text(promotion),
            reply_markup=keyboard
        )
        
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id, msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in affiliate_promotions_handler.py in promotions_detail_info function: {e}",
            module_name="doroshka_bot"
        )

@handler_logging
async def promotion_get_reward(message, promotion_id):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        promotion = await get_promotion_by_id(promotion_id)
        promocodes = await PromocodesMiddleware.get_free_promocodes_by_type(type=promotion.promocode_type)

        mp = types.InlineKeyboardMarkup(row_width=1)
        msg_text = ""
        subscribers = promotion.sub_chat_id
        if (promocodes != DBTransactionStatus.NOT_EXIST):
            result = await PromocodesMiddleware.add_client_to_promocode(
                number=promocodes[0].number,
                client_chat_id=message.chat.id
            )
            if (result == DBTransactionStatus.SUCCESS):
                msg_text = "🥳 Вы успешно получили промокод от партнёра. Вы можете посмотреть его наличие в \"🎟 Мои промокоды\"."
                
                subscribers.append(str(message.chat.id))
                await update_promotion(
                    id=promotion_id,
                    sub_chat_id=subscribers
                )
            else:
                msg_text = "😔 Произошла ошибка при попытки назначения промокода, обратитесь в техническую поддержку."
        else:
            msg_text = "😔 В настоящее время нет подхоядщих по типу промокодов для этой акции"
        
        
        button_back = types.InlineKeyboardButton(
            text="◀️ Назад", 
            callback_data="back_to_affiliate_promotions"
        )
        mp.add(button_back)
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
            message=f"An error occurred in affiliate_promotions_handler.py in promotion_get_reward function: {e}",
            module_name="doroshka_bot"
        )

@bot.callback_query_handler(func=lambda call: "_affilate_promo" in call.data)
async def handle_callback_query(call):   
     
    if "_id" in call.data:
        promotion_id = int(call.data[:call.data.find("_id")])
        await promotion_detail_info(call.message, promotion_id)
        
    if call.data == "back_to_affilate_promo":
        await affilate_promotions(call.message, edit=True)
