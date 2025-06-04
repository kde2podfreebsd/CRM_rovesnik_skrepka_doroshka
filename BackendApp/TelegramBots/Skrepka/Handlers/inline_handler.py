from telebot import types

from BackendApp.Database.DAL.SupportBot.agent_dal import AgentDAL
from BackendApp.Database.DAL.SupportBot.file_dal import FileDAL
from BackendApp.Database.DAL.SupportBot.password_dal import PasswordDAL
from BackendApp.Database.DAL.SupportBot.requests_dal import RequestDAL
from BackendApp.TelegramBots.Skrepka.Config import bot
from BackendApp.TelegramBots.Skrepka.Handlers.affilate_promotions_handler import (
    affilate_promotions,
    promotion_get_reward
)
from BackendApp.TelegramBots.Skrepka.Handlers.faq_handler import (
    help_menu
)
from BackendApp.TelegramBots.Skrepka.Handlers.invoice_handler import *
from BackendApp.TelegramBots.Skrepka.Handlers.invoice_handler import (
    invoice_menu,
    payment1000,
    payment2500,
    payment5000,
    payment10000,
    payment25000,
    payment100000,
)
from BackendApp.TelegramBots.Skrepka.Handlers.main_menu_handler import main_menu
from BackendApp.TelegramBots.Skrepka.Handlers.menu_handler import send_menu
from BackendApp.TelegramBots.Skrepka.Handlers.partner_gift_handler import (
    get_free_promocode_menu,
    get_partner_gift_menu,
    partner_gift_menu,
)
from BackendApp.TelegramBots.Skrepka.Handlers.profile_handler import profile_menu
from BackendApp.TelegramBots.Skrepka.Handlers.promocodes_handler import (
    activated_promocode_menu,
    promocode_menu,
)
from BackendApp.TelegramBots.Skrepka.Handlers.promotions_handler import promotions
from BackendApp.TelegramBots.Skrepka.Handlers.referrals_handler import (
    invite_friend,
    referrers_menu,
)
from BackendApp.TelegramBots.Skrepka.Handlers.review_handler import (
    review_menu,
    review_menu_bar,
    review_menu_event,
    review_menu_event_slider,
    get_review_award
)
from BackendApp.TelegramBots.Skrepka.Handlers.support_handler import (
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
)
from BackendApp.TelegramBots.Skrepka.Handlers.test_handler import (
    get_award_for_test,
    test,
)
from BackendApp.TelegramBots.Skrepka.Handlers.tx_handler import transactions_menu

BAR_ID = 2 # this param should be changed when expanding functionallity on all 3 bots

@bot.callback_query_handler(func=lambda call: True)
async def HandlerInlineMiddleware(call):

    if call.data == "main_menu" or call.data == "back_to_main_menu":
        await bot.delete_state(call.message.chat.id, call.message.chat.id) 
        await main_menu(call.message)

    elif call.data == "profile_menu":
        await profile_menu(call.message)

    elif call.data == "restaurant_menu":
        await send_menu(call.message)

    elif call.data == "back_to_help_menu":
        await help_menu(call.message)

    elif call.data == "leave_feedback" or call.data == "back_to_leave_feedback":
        await review_menu(call.message)
    
    elif call.data == "leave_feedback_bar":
        await review_menu_bar(call.message)
    
    elif call.data == "leave_feedback_event" or call.data == "back_to_leave_feedback_event":
        await review_menu_event_slider(call.message, 1)

    elif "past_events_menu" in call.data:
        await review_menu_event_slider(message=call.message, page=int(call.data.split("#")[-1]))
    
    elif "past_event_leave_feedback" in call.data:
        await review_menu_event(message=call.message, event_id=int(call.data.split("#")[-1]))
    
    elif call.data == "yandex_maps":
        pass

    elif call.data == "get_review_award":
        await get_review_award(call.message)

    elif call.data == "partner":
        await promotions(call.message)

    elif call.data == "faq":
        await help_menu(call.message)

    elif call.data == "quiz":
        await test(call.message, 1)

    elif call.data == "affiliate_promotions" or call.data == "back_to_affiliate_promotions":
        await affilate_promotions(call.message)
    
    elif "promotion_get_reward" in call.data:
        promotion_id = int(call.data.split("#")[-1])
        await promotion_get_reward(call.message, promotion_id)

    elif call.data == "award_from_partner" or call.data == "back_to_partner_gift":
        await partner_gift_menu(call.message)

    elif "partner_gift" in call.data:
        partner_gift_id = int(call.data.split("#")[-1])
        await get_partner_gift_menu(call.message, partner_gift_id)

    elif "get_free_promocode" in call.data:
        partner_gift_id = int(call.data.split("#")[-1])
        await get_free_promocode_menu(call.message, partner_gift_id)
    
    elif "get_award_for_test" in call.data:
        result_id = int(call.data.split("#")[1])
        test_name = str(call.data.split("#")[2])
        await get_award_for_test(call.message, result_id=result_id, test_name=test_name)

    elif call.data == "refill_balance":
        await invoice_menu(call.message)

    elif call.data == "transactions":
        await transactions_menu(call.message, 1)

    elif call.data == "invite_friend":
        await invite_friend(call.message)

    elif call.data == "my_promocodes" or call.data == "back_to_promocode_menu":
        await promocode_menu(call.message, 1)
    
    elif "activated_promocodes_slider" == call.data:
        await activated_promocode_menu(call.message, 1)

    elif "promocode_activated_menu" in call.data:
        await activated_promocode_menu(message=call.message, page=int(call.data.split("#")[-1]))
    
    elif "promocode_menu" in call.data:
        await promocode_menu(message=call.message, page=int(call.data.split("#")[-1]))

    elif call.data == "referrals":
        await referrers_menu(call.message, 1)

    elif call.data == "back_to_help_menu":
        await help_menu(call.message)

    elif call.data == "back_to_main_menu":
        await main_menu(call.message)

    elif call.data == "back_to_main_menu_test":
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await main_menu(call.message)

    elif call.data == "back_to_help_menu":
        await help_menu(call.message)

    elif call.data == "back_to_promo_menu":
        await promotions(call.message)

    elif call.data == "back_to_profile_menu":
        await profile_menu(call.message)

    elif "referrers_menu" in call.data:
        await referrers_menu(message=call.message, page=int(call.data.split("#")[-1]))

    elif "transactions_menu" in call.data:
        await transactions_menu(message=call.message, page=int(call.data.split("#")[-1]))

    elif "quiz_menu" in call.data:
        await test(message=call.message, page=int(call.data.split("#")[-1]))

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
        markup_and_value = await InlineMarkup.markup_reqs(call.message.chat.id, callback, number)
        markup_req = markup_and_value[0]
        value = markup_and_value[1]
        await bot.answer_callback_query(call.id)
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
