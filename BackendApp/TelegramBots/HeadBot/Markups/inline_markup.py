import os

from dotenv import load_dotenv
from telebot import formatting, types

load_dotenv()

BAR_ID = 1

AFISHA = "https://rovesnik-bot.online/rovesnik/"
MY_TICKETS = "https://rovesnik-bot.online/rovesnik/my/events/"
MY_RESERVATIONS_ROVESNIK = "https://rovesnik-bot.online/rovesnik/my/reservations/"
MY_RESERVATIONS_SKREPKA = "https://rovesnik-bot.online/skrepka/my/reservations/"
MY_RESERVATIONS_DOROSHKA = "https://rovesnik-bot.online/doroshka/my/reservations/"

class InlineMarkup(object):

    @classmethod
    def PaymentBtnList(cls, chat_id: int):
        return types.InlineKeyboardMarkup(
            row_width=1,
            keyboard=[
                [types.InlineKeyboardButton("Пополнить на 1000₽", callback_data=f"payment1000")],
                [types.InlineKeyboardButton("Пополнить на 2500₽", callback_data=f"payment2500")],
                [types.InlineKeyboardButton("Пополнить на 5000₽", callback_data=f"payment5000")],
                [types.InlineKeyboardButton("Пополнить на 10000₽", callback_data=f"payment10000")],
                [types.InlineKeyboardButton("Пополнить на 25000₽", callback_data=f"payment25000")],
                [
                    types.InlineKeyboardButton(
                        "Пополнить на 100000₽", callback_data=f"payment100000"
                    )
                ],
                [types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main_menu")],
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
    def back_to_help_menu(cls):
        mp = types.InlineKeyboardMarkup(row_width=1)
        mp.add(types.InlineKeyboardButton(text="🔙Назад", callback_data="back_to_help_menu"))

        return mp

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
        mp = types.InlineKeyboardMarkup(row_width=3)

        rovesnik_name = os.getenv("ROVESNIK_BOT_NAME")
        skrepka_name = os.getenv("SKREPKA_BOT_NAME")
        doroshka_name = os.getenv("DOROSHKA_BOT_NAME")

        profile = types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile_menu")

        refill_balance = types.InlineKeyboardButton(
            text="🛒 Пополнить баланс", callback_data="refill_balance"
        )

        rovesnik = types.InlineKeyboardButton(text="Ровесник", url=f"http://t.me/{rovesnik_name}")

        skrepka = types.InlineKeyboardButton(text="Скрепка", url=f"http://t.me/{skrepka_name}")

        doroshka = types.InlineKeyboardButton(text="Дорожка", url=f"http://t.me/{doroshka_name}")

        leave_feedback = types.InlineKeyboardButton(
            text="📝 Оставить отзыв", callback_data="leave_feedback"
        )

        faq = types.InlineKeyboardButton(text="❗️ F.A.Q.", callback_data="faq")

        support = types.InlineKeyboardButton(
            text="📧 Тех.поддержка",
            callback_data=f"start_support",
        )

        mp.add(profile)
        mp.add(refill_balance)
        mp.add(rovesnik, skrepka, doroshka)
        mp.add(leave_feedback, faq)
        mp.add(support)

        return mp

    @classmethod
    def profile_menu(cls):
        mp = types.InlineKeyboardMarkup(row_width=2)

        transactions = types.InlineKeyboardButton(
            text="💰 Мои транзакции", callback_data="transactions"
        )

        my_reservations = types.InlineKeyboardButton(
            text="📆 Мои брони",
            callback_data="my_reservations"
        )

        web_app_afisha = types.WebAppInfo(f"{MY_TICKETS}?barId=1")
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

        mp.add(transactions)
        mp.add(afisha_my_tickets)
        mp.add(my_reservations)
        mp.add(invite_friend)
        mp.add(referrals)
        mp.add(promocodes)
        mp.add(back_to_main_menu)

        return mp
    
    @classmethod
    def my_reservations_menu(cls):
        mp = types.InlineKeyboardMarkup(row_width=1)

        web_app_rovesnik_reservations = types.WebAppInfo(f"{MY_RESERVATIONS_ROVESNIK}?barId=1")
        my_reservations_rovesnik = types.InlineKeyboardButton(
            text="Ровесник", 
            web_app=web_app_rovesnik_reservations
        )

        web_app_skrepka_reservations = types.WebAppInfo(f"{MY_RESERVATIONS_SKREPKA}?barId=2")
        my_reservations_skrepka = types.InlineKeyboardButton(
            text="Скрепка", 
            web_app=web_app_skrepka_reservations
        )

        web_app_doroshka_reservations = types.WebAppInfo(f"{MY_RESERVATIONS_DOROSHKA}?barId=3")
        my_reservations_doroshka = types.InlineKeyboardButton(
            text="Дорожка", 
            web_app=web_app_doroshka_reservations
        )

        back_to_profile_menu = types.InlineKeyboardButton(
            text="🔙 Назад", callback_data="back_to_profile_menu"
        )

        mp.add(my_reservations_rovesnik, my_reservations_skrepka, my_reservations_doroshka, back_to_profile_menu)

        return mp
