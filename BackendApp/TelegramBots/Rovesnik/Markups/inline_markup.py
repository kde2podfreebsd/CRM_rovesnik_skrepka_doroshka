import os

from dotenv import load_dotenv
from telebot import formatting, types

from BackendApp.Database.DAL.SupportBot.agent_dal import AgentDAL
from BackendApp.Database.DAL.SupportBot.file_dal import FileDAL
from BackendApp.Database.DAL.SupportBot.password_dal import PasswordDAL
from BackendApp.Database.DAL.SupportBot.requests_dal import RequestDAL
from BackendApp.Database.session import async_session
from BackendApp.TelegramBots.SupportBot.core import (
    get_file_text,
    get_icon_from_status,
)

load_dotenv()

HEAD_BOT_NAME = os.getenv("HEAD_BOT_NAME")
BAR_ID = 1

AFISHA = "https://rovesnik-bot.online/rovesnik/"
MY_TICKETS = "https://rovesnik-bot.online/rovesnik/my/events/"
RESERVE_TABLE = "https://rovesnik-bot.online/rovesnik/reservation/"
MY_RESERVATIONS = "https://rovesnik-bot.online/rovesnik/my/reservations/"

def page(markup, number, list, call, callback_cancel):
    if len(list) != 10:
        max_nums = number
    else:
        max_nums = "None"

    if str(number) == "1":
        item1 = types.InlineKeyboardButton(f"⏹", callback_data=f"None")
    else:
        item1 = types.InlineKeyboardButton(f"◀️", callback_data=f"{call}:{int(number) - 1}")

    if str(number) == str(max_nums):
        item2 = types.InlineKeyboardButton(f"⏹", callback_data=f"None")
    else:
        item2 = types.InlineKeyboardButton(f"▶️", callback_data=f"{call}:{int(number) + 1}")

    item3 = types.InlineKeyboardButton("Назад", callback_data=callback_cancel)

    if callback_cancel != "None":
        markup.add(item1, item3, item2)
    else:
        if str(number) == "1" and str(number) == str(max_nums):
            pass
        else:
            markup.add(item1, item2)

    return markup


class InlineMarkup(object):

    @classmethod
    def support_back_to_main_menu(cls):
        return types.InlineKeyboardMarkup(
            row_width=1,
            keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data="support_back_to_main_menu"
                    )
                ]
            ],
        )

    @classmethod
    def support_back_to_agent_menu(cls):
        return types.InlineKeyboardMarkup(
            row_width=1,
            keyboard=[[types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_agent")]],
        )

    @classmethod
    def back_to_main_menu(cls):
        return types.InlineKeyboardMarkup(
            row_width=1,
            keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data="support_back_to_main_menu"
                    )
                ]
            ],
        )

    @classmethod
    def PaymentBtnList(cls, chat_id: int):
        return types.InlineKeyboardMarkup(
            row_width=2,
            keyboard=[
                [
                    types.InlineKeyboardButton(
                        "Пополнить на 1000₽", callback_data=f"payment1000"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        "Пополнить на 2500₽", callback_data=f"payment2500"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        "Пополнить на 5000₽", callback_data=f"payment5000"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        "Пополнить на 10000₽", callback_data=f"payment10000"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        "Пополнить на 25000₽", callback_data=f"payment25000"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        "Пополнить на 100000₽", callback_data=f"payment100000"
                    )
                ],
                [types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_profile_menu")],
            ],
        )

    @classmethod
    def help_menu(cls):
        return types.InlineKeyboardMarkup(
            row_width=1,
            keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="🔙Назад", 
                        callback_data="back_to_main_menu"
                    )
                ],
            ],
        )

    @classmethod
    def faq_questions(cls, questions: list):
        faq_qst_markup = types.InlineKeyboardMarkup(row_width=1)

        if questions is None:
            faq_qst_markup.add(
                types.InlineKeyboardButton(text="🔙Назад", callback_data="back_to_help_menu")
            )

        else:
            for qst in questions:
                faq_qst_markup.add(
                    types.InlineKeyboardButton(
                        text=f"{qst.short_name}", callback_data=f"faq_id#{qst.id}"
                    )
                )

            faq_qst_markup.add(
                types.InlineKeyboardButton(text="🔙Назад", callback_data="back_to_help_menu")
            )

        return faq_qst_markup

    @classmethod
    def back_to_faq_list(cls):
        mp = types.InlineKeyboardMarkup(row_width=1)
        mp.add(types.InlineKeyboardButton(text="🔙Назад", callback_data="back_to_faq_list"))

        return mp

    @classmethod
    def referres_slider(cls, page: int, amount_of_pages: int):
        mp = types.InlineKeyboardMarkup(row_width=3)
        if amount_of_pages != 1:
            back = types.InlineKeyboardButton(
                text="<", callback_data=f"referrers_menu#{page - 1 if page - 1 >= 1 else page}"
            )
            page_cntr = types.InlineKeyboardButton(
                text=f"{page}/{amount_of_pages}", callback_data="nullified"
            )
            forward = types.InlineKeyboardButton(
                text=">",
                callback_data=f"referrers_menu#{page + 1 if page + 1 <= amount_of_pages else page}",
            )
            mp.add(back, page_cntr, forward)

        back_to_profile_menu = types.InlineKeyboardButton(
            text="🔙 Назад", callback_data="back_to_profile_menu"
        )
        mp.add(back_to_profile_menu)

        return mp

    @classmethod
    def transactions_slider(cls, page: int, amount_of_pages: int):
        mp = types.InlineKeyboardMarkup(row_width=3)
        if amount_of_pages != 1:
            back = types.InlineKeyboardButton(
                text="<", callback_data=f"transactions_menu#{page - 1 if page - 1 >= 1 else page}"
            )
            page_cntr = types.InlineKeyboardButton(
                text=f"{page}/{amount_of_pages}", callback_data="nullified"
            )
            forward = types.InlineKeyboardButton(
                text=">",
                callback_data=f"transactions_menu#{page + 1 if page + 1 <= amount_of_pages else page}",
            )
            mp.add(back, page_cntr, forward)

        back_to_profile_menu = types.InlineKeyboardButton(
            text="🔙 Назад", callback_data="back_to_profile_menu"
        )
        mp.add(back_to_profile_menu)

        return mp

    @classmethod
    def quiz_slider(cls, page: int, amount_of_pages: int, keyboard: types.InlineKeyboardMarkup):
        if amount_of_pages != 1:
            back = types.InlineKeyboardButton(
                text="<", callback_data=f"quiz_menu#{page - 1 if page - 1 >= 1 else page}"
            )
            page_cntr = types.InlineKeyboardButton(
                text=f"{page}/{amount_of_pages}", callback_data="nullified"
            )
            forward = types.InlineKeyboardButton(
                text=">",
                callback_data=f"quiz_menu#{page + 1 if page + 1 <= amount_of_pages else page}",
            )
            keyboard.add(back, page_cntr, forward)

        back_to_profile_menu = types.InlineKeyboardButton(
            text="🔙 Назад", callback_data="back_to_promo_menu"
        )
        keyboard.add(back_to_profile_menu)

    @classmethod
    def promocode_slider(cls, page: int, amount_of_pages: int, add_button: bool):
        mp = types.InlineKeyboardMarkup(row_width=3)
        if amount_of_pages != 1:
            back = types.InlineKeyboardButton(
                text="<", callback_data=f"promocode_menu#{page - 1 if page - 1 >= 1 else page}"
            )
            page_cntr = types.InlineKeyboardButton(
                text=f"{page}/{amount_of_pages}", callback_data="nullified"
            )
            forward = types.InlineKeyboardButton(
                text=">",
                callback_data=f"promocode_menu#{page + 1 if page + 1 <= amount_of_pages else page}",
            )
            mp.add(back, page_cntr, forward)

        if (add_button):
            activated_promocodes = types.InlineKeyboardButton(
                text="✔️ Активированные промокоды",
                callback_data=f"activated_promocodes_slider",
            )
            mp.add(activated_promocodes)

        back_to_profile_menu = types.InlineKeyboardButton(
            text="🔙 Назад", callback_data="back_to_profile_menu"
        )
        mp.add(back_to_profile_menu)

        return mp
    
    @classmethod
    def past_events_slider(cls, page: int, amount_of_pages: int, buttons: list):
        mp = types.InlineKeyboardMarkup(row_width=3)
        
        for button in buttons:
            mp.add(button)

        if amount_of_pages != 1:
            back = types.InlineKeyboardButton(
                text="<", callback_data=f"past_events_menu#{page - 1 if page - 1 >= 1 else page}"
            )
            page_cntr = types.InlineKeyboardButton(
                text=f"{page}/{amount_of_pages}", callback_data="nullified"
            )
            forward = types.InlineKeyboardButton(
                text=">",
                callback_data=f"past_events_menu#{page + 1 if page + 1 <= amount_of_pages else page}",
            )
            mp.add(back, page_cntr, forward)

        back_to_leave_feedback = types.InlineKeyboardButton(
            text="🔙 Назад", callback_data="back_to_leave_feedback"
        )
        mp.add(back_to_leave_feedback)

        return mp
    
    @classmethod
    def activated_promocode_slider(cls, page: int, amount_of_pages: int):
        mp = types.InlineKeyboardMarkup(row_width=3)
        if amount_of_pages != 1:
            back = types.InlineKeyboardButton(
                text="<", callback_data=f"promocode_activated_menu#{page - 1 if page - 1 >= 1 else page}"
            )
            page_cntr = types.InlineKeyboardButton(
                text=f"{page}/{amount_of_pages}", callback_data="nullified"
            )
            forward = types.InlineKeyboardButton(
                text=">",
                callback_data=f"promocode_activated_menu#{page + 1 if page + 1 <= amount_of_pages else page}",
            )
            mp.add(back, page_cntr, forward)

        back_to_profile_menu = types.InlineKeyboardButton(
            text="🔙 Назад", callback_data="back_to_promocode_menu"
        )
        mp.add(back_to_profile_menu)

        return mp

    @classmethod
    def main_menu(cls):
        mp = types.InlineKeyboardMarkup(row_width=2)

        profile = types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile_menu")

        web_app_afisha_buy_tickets = types.WebAppInfo(f"{AFISHA}?barId={BAR_ID}")
        afisha_buy_tickets = types.InlineKeyboardButton(text="🎉 Афиша", web_app=web_app_afisha_buy_tickets)

        web_app_reserve_table = types.WebAppInfo(f"{RESERVE_TABLE}?barId={BAR_ID}")
        reserve_table = types.InlineKeyboardButton(
            text="📔 Бронь столов", web_app=web_app_reserve_table
        )

        menu = types.InlineKeyboardButton(text="🍽 Меню", callback_data="restaurant_menu")

        leave_feedback = types.InlineKeyboardButton(
            text="📝 Оставить отзыв", callback_data="leave_feedback"
        )

        partner = types.InlineKeyboardButton(text="🎁 Партнер", callback_data="partner")

        faq = types.InlineKeyboardButton(text="❗️ F.A.Q.", callback_data="faq")

        support = types.InlineKeyboardButton(
            text="📧 Тех.поддержка",
            callback_data=f"start_support",
        )

        back_to_head_bot = types.InlineKeyboardButton(
            text="🔙 В головного бота",
            url=f"t.me/{HEAD_BOT_NAME}"
        )

        mp.add(profile)
        mp.add(menu, reserve_table)
        mp.add(afisha_buy_tickets, leave_feedback)
        mp.add(partner, faq)
        mp.add(support)
        mp.add(back_to_head_bot)

        return mp

    @classmethod
    def promotions_menu(cls):
        mp = types.InlineKeyboardMarkup(row_width=2)

        quiz = types.InlineKeyboardButton(text="📋 Квизы", callback_data="quiz")

        affiliate_promotions = types.InlineKeyboardButton(
            text="🎁 Акции партнёров", callback_data="affiliate_promotions"
        )

        award_from_partner = types.InlineKeyboardButton(
            text="🥳 Подарок от партнёра", callback_data="award_from_partner"
        )

        back_to_main_menu = types.InlineKeyboardButton(
            text="🔙 Назад", callback_data="back_to_main_menu"
        )
        mp.add(quiz, affiliate_promotions)
        mp.add(award_from_partner)
        mp.add(back_to_main_menu)

        return mp

    @classmethod
    def profile_menu(cls):
        mp = types.InlineKeyboardMarkup(row_width=2)

        refill_balance = types.InlineKeyboardButton(
            text="🛒 Пополнить баланс", callback_data="refill_balance"
        )

        transactions = types.InlineKeyboardButton(
            text="💰 Мои транзакции", callback_data="transactions"
        )

        web_app_reservations = types.WebAppInfo(f"{MY_RESERVATIONS}?barId={BAR_ID}")
        my_reservations = types.InlineKeyboardButton(
            text="📆 Мои брони", web_app=web_app_reservations
        )

        web_app_afisha = types.WebAppInfo(f"{MY_TICKETS}?barId={BAR_ID}")
        afisha_my_tickets = types.InlineKeyboardButton(text="🎫 Мои билеты", web_app=web_app_afisha)

        invite_friend = types.InlineKeyboardButton(
            text="➕ Пригласить друга", callback_data="invite_friend"
        )

        referrals = types.InlineKeyboardButton(
            text="👨‍👩‍👧‍👦 Мои рефералы", callback_data="referrals"
        )

        promocodes = types.InlineKeyboardButton(
            text="🎟 Мои промокоды", callback_data="my_promocodes"
        )

        back_to_main_menu = types.InlineKeyboardButton(
            text="🔙 Назад", callback_data="back_to_main_menu"
        )
        mp.add(refill_balance)
        mp.add(transactions)
        mp.add(afisha_my_tickets)
        mp.add(my_reservations)
        mp.add(invite_friend)
        mp.add(referrals)
        mp.add(promocodes)
        mp.add(back_to_main_menu)

        return mp

    @classmethod
    def support_markup_main(cls):
        markup_main = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton("✏️ Написать запрос", callback_data="write_request")
        item2 = types.InlineKeyboardButton("✉️ Мои запросы", callback_data="my_reqs:")
        back_to_main_menu = types.InlineKeyboardButton(
            "🔙 Назад", callback_data="back_to_main_menu"
        )
        markup_main.add(item1)
        markup_main.add(item2)
        markup_main.add(back_to_main_menu)

        return markup_main

    @classmethod
    async def markup_reqs(cls, user_id, callback, number):
        async with async_session() as session:
            request_dal = RequestDAL(session)
            if callback == "my_reqs":
                reqs = await request_dal.my_reqs(number, user_id)
                user_status = "user"
                callback_cancel = "None"
            else:
                reqs = await request_dal.get_reqs(number, callback)
                user_status = "agent"
                callback_cancel = "back_agent"

        markup_my_reqs = types.InlineKeyboardMarkup(row_width=3)
        for req in reqs:
            req_id = req.req_id
            req_status = req.req_status
            req_icon = get_icon_from_status(req_status, user_status)
            # ❗️, ⏳, ✅

            item = types.InlineKeyboardButton(
                f"{req_icon} | ID: {req_id}", callback_data=f"open_req:{req_id}:{callback}-{number}"
            )
            markup_my_reqs.add(item)

        markup_my_reqs = page(markup_my_reqs, number, reqs, callback, callback_cancel)
        if callback == "my_reqs":
            markup_my_reqs.add(
                types.InlineKeyboardButton("Назад", callback_data="support_back_to_main_menu")
            )

        return markup_my_reqs, len(reqs)

    def markup_request_action(req_id, req_status, callback):
        formatted_callback = callback.replace("-", ":")

        markup_request_action = types.InlineKeyboardMarkup(row_width=1)

        if req_status == "confirm":
            item1 = types.InlineKeyboardButton(
                "🗂 Показать файлы", callback_data=f"req_files:{req_id}:{callback}:1"
            )
            item2 = types.InlineKeyboardButton("Назад", callback_data=formatted_callback)

            markup_request_action.add(item1, item2)

        elif req_status == "answered" or req_status == "waiting":
            if "my_reqs:" in formatted_callback:
                status_user = "user"
            else:
                status_user = "agent"

            item1 = types.InlineKeyboardButton(
                "✏️ Добавить сообщение", callback_data=f"add_message:{req_id}:{status_user}"
            )
            item2 = types.InlineKeyboardButton(
                "🗂 Показать файлы", callback_data=f"req_files:{req_id}:{callback}:1"
            )

            if status_user == "user":
                item3 = types.InlineKeyboardButton(
                    "✅ Завершить запрос", callback_data=f"confirm_req:wait:{req_id}"
                )

            item4 = types.InlineKeyboardButton("Назад", callback_data=formatted_callback)

            if status_user == "user":
                markup_request_action.add(item1, item2, item3, item4)
            else:
                markup_request_action.add(item1, item2, item4)

        return markup_request_action

    def markup_confirm_req(req_id):
        markup_confirm_req = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton(
            "✅ Подтвердить", callback_data=f"confirm_req:true:{req_id}"
        )
        markup_confirm_req.add(item1)

        return markup_confirm_req

    async def markup_files(number, req_id, callback):
        async with async_session() as session:
            file_dal = FileDAL(session)
            files = await file_dal.get_files(number=number, req_id=req_id)

        markup_files = types.InlineKeyboardMarkup(row_width=3)
        for file in files:
            id = file.id
            file_name = file.file_name
            type = file.type

            file_text = get_file_text(file_name, type)
            # 📷 | Фото 27.12.2020 14:21:50

            item = types.InlineKeyboardButton(file_text, callback_data=f"send_file:{id}:{type}")
            markup_files.add(item)
        markup_files = page(
            markup_files,
            number,
            files,
            f"req_files:{req_id}:{callback}",
            f"open_req:{req_id}:{callback}",
        )

        return markup_files, len(files)

    def markup_agent():
        markup_agent = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton(
            "❗️ Ожидают ответа от поддержки", callback_data="waiting_reqs:1"
        )
        item2 = types.InlineKeyboardButton(
            "⏳ Ожидают ответа от пользователя", callback_data="answered_reqs:1"
        )
        item3 = types.InlineKeyboardButton("✅ Завершенные запросы", callback_data="confirm_reqs:1")
        markup_agent.add(item1, item2, item3)

        return markup_agent

    def markup_admin():
        markup_admin = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton(
            "✅ Добавить агента поддержки", callback_data="add_agent"
        )
        item2 = types.InlineKeyboardButton("🧑‍💻 Агенты поддержки", callback_data="all_agents:1")
        item3 = types.InlineKeyboardButton("🔑 Одноразовые пароли", callback_data="all_passwords:1")
        item4 = types.InlineKeyboardButton(
            "🎲 Сгенерировать одноразовые пароли", callback_data="generate_passwords"
        )
        item5 = types.InlineKeyboardButton("⛔️ Выключить бота", callback_data="stop_bot:wait")
        markup_admin.add(item1, item2, item3, item4, item5)

        return markup_admin

    async def markup_agents(number):
        async with async_session() as session:
            agent_dal = AgentDAL(session)
            agents = await agent_dal.get_agents(int(number))

        markup_agents = types.InlineKeyboardMarkup(row_width=3)
        for agent in agents:
            agent_id = agent

            item = types.InlineKeyboardButton(
                f"🧑‍💻 | {agent_id}", callback_data=f"delete_agent:{agent_id}"
            )
            markup_agents.add(item)

        markup_agents = page(markup_agents, number, agents, "all_agents", "back_admin")

        return markup_agents, len(agents)

    async def markup_passwords(number):
        async with async_session() as session:
            password_dal = PasswordDAL(session)
            passwords = await password_dal.get_passwords(number)

        markup_passwords = types.InlineKeyboardMarkup(row_width=3)
        for password in passwords:
            password_value = password

            item = types.InlineKeyboardButton(
                password_value, callback_data=f"delete_password:{password_value}"
            )
            markup_passwords.add(item)

        markup_passwords = page(markup_passwords, number, passwords, "all_passwords", "back_admin")

        return markup_passwords, len(passwords)

    def markup_confirm_stop():
        markup_confirm_stop = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton("Да", callback_data="stop_bot:confirm")
        item2 = types.InlineKeyboardButton("Нет", callback_data="back_admin")
        markup_confirm_stop.add(item1, item2)

        return markup_confirm_stop
    
    
