import enum

class _PromocodeType(str, enum.Enum):
    ONE_TIME_FREE_MENU_ITEM = "ONE_TIME_FREE_MENU_ITEM"  # Единоразовая бесплатная позиция из меню (напитки, еда, мерч, игра в бильярд/боулинг и тд)
    DISCOUNT_ON_ACCOUNT = "DISCOUNT_ON_ACCOUNT"  # Единоразовая скидка на счет
    DISCOUNT_ON_DISH = "DISCOUNT_ON_DISH"  # Единоразовая скидка на определенное блюдо
    DISCOUNT_FOR_PAID_EVENT = "DISCOUNT_FOR_PAID_EVENT"  # Скидка на платное мероприятие
    FREE_EVENT_TICKET = "FREE_EVENT_TICKET"  # Бесплатный билет на платное мероприятие
    REFILLING_BALANCE = "REFILLING_BALANCE"  # Промокод на сумму N
    PARTY_WITHOUT_DEPOSIT = (
        "PARTY_WITHOUT_DEPOSIT"  # Вход на бесплатную вечеринку без депозита (проходка)
    )
    GIFT_FROM_PARTNER = "GIFT_FROM_PARTNER"  # Подарок от партнера
    CUSTOM = "CUSTOM"  # Кастомный промик
