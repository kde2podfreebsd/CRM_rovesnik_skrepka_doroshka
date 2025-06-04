from telebot import types

from BackendApp.TelegramBots.HeadBot.Config import bot
from BackendApp.TelegramBots.HeadBot.Handlers.faq_handler import (
    help_menu
)
from BackendApp.TelegramBots.HeadBot.Handlers.invoice_handler import (
    invoice_menu,
    payment1000,
    payment2500,
    payment5000,
    payment10000,
    payment25000,
    payment100000,
)
from BackendApp.TelegramBots.HeadBot.Handlers.main_menu_handler import main_menu
from BackendApp.TelegramBots.HeadBot.Handlers.profile_handler import profile_menu
from BackendApp.TelegramBots.HeadBot.Handlers.promocodes_handler import (
    promocode_menu,
    activated_promocode_menu
)
from BackendApp.TelegramBots.HeadBot.Handlers.referrals_handler import (
    invite_friend,
    referrers_menu,
)
from BackendApp.TelegramBots.HeadBot.Handlers.support_handler import (
    MyStates,
    add_agent,
    add_message,
    all_agents,
    all_passwords,
    back_admin,
    back_agent,
    confirm_req,
    delete_agent,
    delete_password,
    generate_passwords,
    generate_passwords_and_send,
    my_requests,
    open_request,
    req_files,
    send_file,
    start_support,
    stop_bot,
    take_new_request,
    reservation_request_confirmed
)
from BackendApp.TelegramBots.HeadBot.Handlers.tx_handler import transactions_menu
from BackendApp.TelegramBots.HeadBot.Handlers.review_handler import (
    review_menu, 
    leave_feedback, 
    get_review_award
)
from BackendApp.TelegramBots.HeadBot.Handlers.reservation_handler import reservation_menu
from BackendApp.TelegramBots.HeadBot.Middlewares.message_context_middleware import (
    message_context_manager,
)
from BackendApp.TelegramBots.SupportBot.inline_markup import (
    InlineMarkup as InlineMarkupSupport,
)


@bot.callback_query_handler(func=lambda call: True)
async def HandlerInlineMiddleware(call):
    
    if call.data == "main_menu":
        await bot.delete_state(call.message.chat.id, call.message.chat.id) 
        await main_menu(call.message)

    elif call.data == "profile_menu":
        await profile_menu(call.message)

    elif call.data == "leave_feedback" or call.data == "back_to_leave_feedback":
        await leave_feedback(call.message)

    elif call.data == "rovesnik_feedback":
        await review_menu(call.message, 1)

    elif call.data == "screpka_feedback":
        await review_menu(call.message, 2)

    elif call.data == "doroshka_feedback":
        await review_menu(call.message, 3)
    
    elif call.data == "yandex_maps":
        pass
    
    elif call.data == "my_reservations":
        await reservation_menu(call.message)

    elif call.data == "get_review_award":
        await get_review_award(call.message)

    elif call.data == "faq" or call.data == "back_to_help_menu":
        await help_menu(call.message)

    elif call.data == "transactions":
        await transactions_menu(call.message, 1)

    elif call.data == "invite_friend":
        await invite_friend(call.message)

    elif call.data == "referrals":
        await referrers_menu(call.message, 1)

    elif call.data == "my_promocodes" or call.data == "back_to_promocode_menu":

        await promocode_menu(call.message, 1)
    
    elif "activated_promocodes_slider" == call.data:
        await activated_promocode_menu(call.message, 1)

    elif "promocode_activated_menu" in call.data:
        await activated_promocode_menu(message=call.message, page=int(call.data.split("#")[-1]))
    
    elif "promocode_menu" in call.data:
        await promocode_menu(message=call.message, page=int(call.data.split("#")[-1]))

    elif call.data == "back_to_help_menu":
        await help_menu(call.message)

    elif call.data == "back_to_main_menu":
        await main_menu(call.message)

    elif call.data == "back_to_main_menu_test":
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await main_menu(call.message)

    elif call.data == "back_to_help_menu":
        await help_menu(call.message)

    elif call.data == "back_to_profile_menu":
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)
        await profile_menu(call.message)

    elif call.data == "refill_balance":
        await invoice_menu(call.message)

    elif "referrers_menu" in call.data:
        await referrers_menu(message=call.message, page=int(call.data.split("#")[-1]))

    elif "transactions_menu" in call.data:
        await transactions_menu(message=call.message, page=int(call.data.split("#")[-1]))

    elif "payment" in call.data:
        payment_sum = call.data.split("payment")[1]
        if payment_sum == "1000":
            await payment1000(call.message)
        elif payment_sum == "2500":
            await payment2500(call.message)
        elif payment_sum == "5000":
            await payment5000(call.message)
        elif payment_sum == "10000":
            await payment10000(call.message)
        elif payment_sum == "25000":
            await payment25000(call.message)
        elif payment_sum == "100000":
            await payment100000(call.message)
    
    elif "reservation_request_confirmed" in call.data:
        data = call.data.split("#")
        capacity = data[1]
        reservation_time = data[2]
        action = data[3]
        await reservation_request_confirmed(call.message, capacity, reservation_time, action)

    elif "support_back_to_main_menu" in call.data:
        await start_support(call.message)

    elif "start_support" in call.data:
        await start_support(call.message)

    elif "write_request" in call.data:
        await take_new_request(call.message)

    # elif "my_requests" in call.data:
    #     await my_requests(call.message)

    # еще обработать
    elif (
        ("my_reqs:" in call.data)
        or ("waiting_reqs:" in call.data)
        or ("answered_reqs:" in call.data)
        or ("confirm_reqs:" in call.data)
    ):
        """
        Обработчик кнопок для:

        ✉️ Мои запросы
        ❗️ Ожидают ответа от поддержки,
        ⏳ Ожидают ответа от пользователя
        ✅ Завершенные запросы
        """

        parts = call.data.split(":")
        callback = parts[0]
        number = parts[1] or 1
        markup_and_value = await InlineMarkupSupport.markup_reqs(
            call.message.chat.id, callback, number
        )
        markup_req = markup_and_value[0]
        value = markup_and_value[1]

        await my_requests(call, value, markup_req)

    # Открыть запрос
    elif "open_req:" in call.data:
        await open_request(call)

    # Добавить сообщение в запрос
    elif "add_message:" in call.data:
        await add_message(call)

    # Завершить запрос
    elif "confirm_req:" in call.data:
        await confirm_req(call)

    # Файлы запроса
    elif "req_files:" in call.data:
        await req_files(call)

    # Отправить файл
    elif "send_file:" in call.data:
        await send_file(call)

    # Вернуться назад в панель агента
    elif call.data == "back_agent":
        await back_agent(call)

    # Вернуться назад в панель админа
    elif call.data == "back_admin":
        await back_admin(call)

    # Добавить агента
    elif call.data == "add_agent":
        await add_agent(call)

    # Все агенты
    elif "all_agents:" in call.data:
        await all_agents(call)

    # Удалить агента
    elif "delete_agent:" in call.data:
        await delete_agent(call)

    # Все пароли
    elif "all_passwords:" in call.data:
        await all_passwords(call)

    # Удалить пароль
    elif "delete_password:" in call.data:
        await delete_password(call)

    # Сгенерировать пароли
    elif call.data == "generate_passwords":
        await generate_passwords_and_send(call)

    # Остановить бота
    elif "stop_bot:" in call.data:
        await stop_bot(call)
