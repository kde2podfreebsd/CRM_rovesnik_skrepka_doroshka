from telebot import formatting
from telebot import types

from BackendApp.Middleware.transaction_middleware import TX_TYPES

class MessageText(object):

    _faq_text = None
    _contact_text = None
    _faq_menu = None
    _menu_text = None
    _after_register: str = None
    _share_contact_text: str = None
    _start_message: str = None

    @classmethod
    def start_message_text(cls):
        cls._start_message = "Start message"
        return cls._start_message

    @classmethod
    def menu_text(cls):
        cls._menu_text = "<b>Menu text</b>"
        return cls._menu_text
    
    @classmethod
    def promotions_text(cls):
        return "promotions text"

    @classmethod
    def afisha_menu_text(cls):
        return "afisha menu text"

    @classmethod
    def booking_menu_text(cls):
        return "booking menu text"

    @classmethod
    def profile_text(cls, level_name: str, required_money_spend: float, spent_amount: float, discount_percentage, balance: float):
        message_text = f'''
Баланс: {balance}₽
Уровень лояльности: {level_name}
До следующего уровня лояльности: {spent_amount} / {required_money_spend}
Скидка на заказы: {discount_percentage}%

'''
        return message_text

    @classmethod
    def invoice_menu(cls):
        text = '''
Пакеты пополнений

1️⃣ 1000₽ + 3% cashback = 1030₽
2️⃣ 2500₽ + 4% cashback = 2600₽
3️⃣ 5000₽ + 5% cashback = 5250₽
🥉 10000₽ + 7% cashback = 10 700₽
🥈 25000₽ + 9% cashback = 27 250₽
🥇 100000₽ +15% cashback = 115 000₽
'''
        return text