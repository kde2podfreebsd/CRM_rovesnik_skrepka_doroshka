from BackendApp.TelegramBots.HeadBot.Config.bot import bot
from BackendApp.TelegramBots.HeadBot.Markups.message_text import MessageText
from BackendApp.TelegramBots.HeadBot.Markups.inline_markup import InlineMarkup
from BackendApp.TelegramBots.HeadBot.Middlewares.message_context_middleware import message_context_manager

async def reservation_menu(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)

    msg = await bot.send_message(
        chat_id=message.chat.id,
        text=MessageText.reservation_text(),
        reply_markup=InlineMarkup.my_reservations_menu()
    )

    message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id,
        msgId=msg.id
    )
