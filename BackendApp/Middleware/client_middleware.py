import asyncio
import os
from typing import Union

from telebot import types
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

from BackendApp import basedir
from BackendApp.Database.DAL.client_dal import ClientDAL
from BackendApp.Database.session import DBTransactionStatus, async_session
from BackendApp.IIKO.api import Client
from BackendApp.Middleware.loyalty_middleware import LoyaltyMiddleware
from BackendApp.Middleware.ticket_middleware import TicketMiddleware
from BackendApp.Middleware.transaction_middleware import TransactionMiddleware
from BackendApp.TelegramBots.HeadBot.Config.bot import (
    bot,
    provider_token
)


load_dotenv()

API_LOGIN = os.getenv("API_LOGIN")


class ClientMiddleware:

    @staticmethod
    async def create_client(
        chat_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
    ):
        async with async_session() as session:
            client_dal = ClientDAL(session)
            client_iiko = await Client.create(API_LOGIN, "Rovesnik")
            result = await client_dal.check_existence(chat_id=chat_id)
            if result != DBTransactionStatus.ALREADY_EXIST:
                iiko_user = await client_iiko.full_create_customer(
                    name=first_name, sur_name=last_name
                )
                await client_dal.create(
                    chat_id=chat_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    iiko_id=iiko_user.id,
                    iiko_card=iiko_user.cards[0]["number"],
                )

            return result

    @staticmethod
    async def refill_balance(chat_id: int, amount: float) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.NOT_EXIST,
        str,
    ]:
        async with async_session() as session:
            client_dal = ClientDAL(session)
            client = await client_dal.get_client(chat_id=chat_id)

            if client == DBTransactionStatus.NOT_EXIST:
                return DBTransactionStatus.NOT_EXIST

            client_iiko = await Client.create(API_LOGIN, "Rovesnik")
            iiko_user = await client_iiko.get_customer_info(id=client.iiko_id)
            try:
                if amount > 0:
                    await client_iiko.refill_customer_balance(
                        client.iiko_id,
                        iiko_user.walletBalances[0]["id"],
                        amount,
                    )
                    await client_dal.update_spend_money(chat_id=chat_id, spend_money=amount)
                else:
                    if iiko_user.walletBalances[0]["balance"] + amount >= 0:
                        await client_iiko.withdraw_balance(
                            client.iiko_id,
                            iiko_user.walletBalances[0]["id"],
                            -amount,
                        )
                    else:
                        return "Not enough balance"
            except Exception as e:
                return DBTransactionStatus.ROLLBACK

            await LoyaltyMiddleware.check_client_level(chat_id)
            return DBTransactionStatus.SUCCESS

    @staticmethod
    async def get_client_by_iiko_id(iiko_id: str) -> Client:
        async with async_session() as session:
            client_dal = ClientDAL(session)
            client = await client_dal.get_client_by_iiko_id(iiko_id=iiko_id)
            return client

    @staticmethod
    async def get_client_by_iiko_card(iiko_card: str) -> Client:
        async with async_session() as session:
            client_dal = ClientDAL(session)
            client = await client_dal.get_client_by_iiko_card(iiko_card=iiko_card)
            return client

    @staticmethod
    async def purchase_by_bonus_points(
        chat_id: int, bar_id: int, amount: float, event_id: int
    ) -> bool:
        async with async_session() as session:
            client_dal = ClientDAL(session)
            client = await client_dal.get_client(chat_id=chat_id)

            refill_status = await ClientMiddleware.refill_balance(chat_id=chat_id, amount=-amount)
            if refill_status != DBTransactionStatus.SUCCESS:
                return "Билет не куплен, произошла ошибка"

            ticket_purchase_status = await TicketMiddleware.purchase_ticket(
                event_id=event_id, client_chat_id=chat_id
            )

            if not ticket_purchase_status:
                return "Билет не куплен, произошла ошибка"

            await TransactionMiddleware.create_tx(
                bar_id=bar_id,
                amount=amount,
                final_amount=amount,
                client_chat_id=chat_id,
                tx_type="reduce_balance",
            )

            try:
                await session.commit()
                return "Успешно куплен билет"

            except Exception as e:
                await session.rollback()
                print("Ошибка:", e)
                return "Билет не куплен, произошла ошибка"

    @staticmethod
    def generate_image(
        user,
        balance,
        user_level_loyalty,
        next_level_loyalty,
        additional_loyalty,
        actual_spend_money_amount,
        qr_code_path,
        background_path,
    ):
        spent_amount, nickname, id = user.spent_amount, user.first_name or user.username or user.id, user.iiko_id
        loyalty_name, level, cashback = user_level_loyalty.name, user_level_loyalty.level, user_level_loyalty.cashback
        additional_cashback = additional_loyalty.cashback if additional_loyalty else 0
        
        # Открываем изображения
        background = Image.open(background_path).convert('RGBA')
        qr_code = Image.open(qr_code_path).convert('RGBA')
        progress_bar_base = Image.open(f"{basedir}/static/user_info/source/progress_bar.png").convert('RGBA')
        progress_fill = Image.open(f"{basedir}/static/user_info/source/Rectangle.png").convert('RGBA')
        ellipse_white = Image.open(f"{basedir}/static/user_info/source/Ellipse_white.png").convert('RGBA')
        ellipse_gray = Image.open(f"{basedir}/static/user_info/source/Ellipse_gray.png").convert('RGBA')

        # Вставка QR-кода в картину
        background.paste(qr_code, (142, 435), qr_code)
        
        draw = ImageDraw.Draw(background)

        # Подбор подходящего шрифта и размера текста для никнейма
        nickname_font_size = 64
        nickname_font_path = f"{basedir}/static/user_info/source/Montserrat.ttf"
        nickname_font = ImageFont.truetype(nickname_font_path, nickname_font_size)
        nickname_text_bbox = draw.textbbox((0, 0), nickname, font=nickname_font)
        nickname_text_width, nickname_text_height = nickname_text_bbox[2] - nickname_text_bbox[0], nickname_text_bbox[3] - nickname_text_bbox[1]

        # Уменьшение размера шрифта, если текст никнейма выходит за границы изображения
        while nickname_text_width > 466 - 20:
            nickname_font_size -= 1
            nickname_font = ImageFont.truetype(nickname_font_path, nickname_font_size)
            nickname_text_bbox = draw.textbbox((0, 0), nickname, font=nickname_font)
            nickname_text_width, nickname_text_height = nickname_text_bbox[2] - nickname_text_bbox[0], nickname_text_bbox[3] - nickname_text_bbox[1]

        # Позиция текста никнейма
        nickname_text_x = (background.width - nickname_text_width) // 2
        nickname_text_y = 268

        # Рисование текста никнейма на изображении
        draw.text((nickname_text_x, nickname_text_y), nickname, font=nickname_font, fill="white")

        # Подбор подходящего шрифта и размера текста для баланса
        balance_font_size = 44
        balance_font = ImageFont.truetype(nickname_font_path, balance_font_size)
        balance_text_bbox = draw.textbbox((0, 0), f"Баланс: {balance}₽", font=balance_font)
        balance_text_width, balance_text_height = balance_text_bbox[2] - balance_text_bbox[0], balance_text_bbox[3] - balance_text_bbox[1]

        # Позиция текста баланса
        balance_text_x = (background.width - balance_text_width) // 2
        balance_text_y = 1002

        # Рисование текста баланса на изображении
        draw.text((balance_text_x, balance_text_y), f"Баланс: {balance}₽", font=balance_font, fill="white")

        # Подбор подходящего шрифта и размера текста для кэшбэка
        cashback_font_size = 40
        cashback_font = ImageFont.truetype(nickname_font_path, cashback_font_size)
        cashback_text_bbox = draw.textbbox((0, 0), f"Кэшбэк: {cashback + additional_cashback}%", font=cashback_font)
        cashback_text_width, cashback_text_height = cashback_text_bbox[2] - cashback_text_bbox[0], cashback_text_bbox[3] - cashback_text_bbox[1]

        # Позиция текста кэшбэка
        cashback_text_x = (background.width - cashback_text_width) // 2
        cashback_text_y = 1078

        # Рисование текста кэшбэка на изображении
        draw.text((cashback_text_x, cashback_text_y), f"Кэшбэк: {cashback + additional_cashback}%", font=cashback_font, fill="#8E8E8E")

        if next_level_loyalty is None:
            # Если next_level_loyalty отсутствует, заполняем прогресс-бар полностью и используем белый эллипс для обоих концов
            progress_percent = 100
            ellipse_right = ellipse_white
        else:
            # Рассчитываем процент прогресса
            progress_percent = ((spent_amount - actual_spend_money_amount) / (next_level_loyalty.spend_money_amount - actual_spend_money_amount)) * 100
            ellipse_right = ellipse_gray

        # Размеры прогресс-бара
        progress_bar_width, progress_bar_height = progress_bar_base.size

        # Рассчитываем длину синей части прогресс-бара
        blue_bar_length = int(progress_percent / 100 * progress_bar_width)

        # Обрезаем прогресс-бар по необходимую длину синей части
        progress_fill = progress_fill.crop((0, 0, blue_bar_length, progress_bar_height))

        # Позиция прогресс-бара
        progress_bar_x = (background.width - progress_bar_width) // 2
        progress_bar_y = 1238

        # Вставляем основу прогресс-бара на изображение
        background.paste(progress_bar_base, (progress_bar_x, progress_bar_y), progress_bar_base)

        # Вставляем заполнение прогресс-бара на изображение
        background.paste(progress_fill, (progress_bar_x, progress_bar_y), progress_fill)

        # Позиция белого эллипса (слева)
        ellipse_white_x = progress_bar_x - (ellipse_white.width // 2)
        ellipse_white_y = progress_bar_y + (progress_bar_height // 2) - (ellipse_white.height // 2)

        # Позиция эллипса справа (в зависимости от условия)
        ellipse_right_x = progress_bar_x + progress_bar_width - (ellipse_right.width // 2)
        ellipse_right_y = progress_bar_y + (progress_bar_height // 2) - (ellipse_right.height // 2)

        # Вставляем эллипсы на изображение
        background.paste(ellipse_white, (ellipse_white_x, ellipse_white_y), ellipse_white)
        background.paste(ellipse_right, (ellipse_right_x, ellipse_right_y), ellipse_right)

        # Подбор подходящего шрифта и размера текста для уровней
        level_font_size = 44
        level_font = ImageFont.truetype(nickname_font_path, level_font_size)
        
        # Позиция текста текущего уровня (слева под прогресс-баром)
        level_text_bbox = draw.textbbox((0, 0), str(level), font=level_font)
        level_text_width, level_text_height = level_text_bbox[2] - level_text_bbox[0], level_text_bbox[3] - level_text_bbox[1]
        level_text_x = ellipse_white_x + (ellipse_white.width - level_text_width) // 2
        level_text_y = 1280

        # Рисование текста текущего уровня
        draw.text((level_text_x, level_text_y), str(level), font=level_font, fill="white")

        if next_level_loyalty is None:
            # Позиция значка бесконечности (справа под прогресс-баром)
            infinity_symbol = "∞"
            infinity_text_bbox = draw.textbbox((0, 0), infinity_symbol, font=level_font)
            infinity_text_width, infinity_text_height = infinity_text_bbox[2] - infinity_text_bbox[0], infinity_text_bbox[3] - infinity_text_bbox[1]
            infinity_text_x = ellipse_right_x + (ellipse_right.width - infinity_text_width) // 2
            infinity_text_y = 1280

            # Рисование значка бесконечности
            draw.text((infinity_text_x, infinity_text_y), infinity_symbol, font=level_font, fill="white")
        else:
            # Позиция текста следующего уровня (справа под прогресс-баром)
            next_level_text_bbox = draw.textbbox((0, 0), str(next_level_loyalty.level), font=level_font)
            next_level_text_width, next_level_text_height = next_level_text_bbox[2] - next_level_text_bbox[0], next_level_text_bbox[3] - next_level_text_bbox[1]
            next_level_text_x = ellipse_right_x + (ellipse_right.width - next_level_text_width) // 2
            next_level_text_y = 1280

            # Рисование текста следующего уровня
            draw.text((next_level_text_x, next_level_text_y), str(next_level_loyalty.level), font=level_font, fill="white")

        # Подбор подходящего шрифта и размера текста для loyalty_name
        loyalty_font_size = 44
        loyalty_font = ImageFont.truetype(nickname_font_path, loyalty_font_size)
        loyalty_text_bbox = draw.textbbox((0, 0), loyalty_name, font=loyalty_font)
        loyalty_text_width, loyalty_text_height = loyalty_text_bbox[2] - loyalty_text_bbox[0], loyalty_text_bbox[3] - loyalty_text_bbox[1]

        # Позиция текста loyalty_name
        loyalty_text_x = (background.width - loyalty_text_width) // 2
        loyalty_text_y = 1280

        # Рисование текста loyalty_name на изображении
        draw.text((loyalty_text_x, loyalty_text_y), loyalty_name, font=loyalty_font, fill="white")

        # Сохранение результата
        output_path = f"{basedir}/static/user_info/{id}.png"
        background.save(output_path)
        return output_path





    @staticmethod
    async def get_client(
        chat_id: int,
    ) -> Union[Client, DBTransactionStatus.NOT_EXIST]:
        async with async_session() as session:
            cd = ClientDAL(session)
            result = await cd.get_client(chat_id=chat_id)
            return result

    @staticmethod
    async def get_client_by_ref_link(
        referral_link: str,
    ) -> Union[Client, DBTransactionStatus.NOT_EXIST]:
        async with async_session() as session:
            cd = ClientDAL(session)
            result = await cd.get_client_by_ref_link(referral_link=referral_link)
            return result

    @staticmethod
    async def get_client_by_username(
        username: str,
    ) -> Union[Client, DBTransactionStatus.NOT_EXIST]:
        async with async_session() as session:
            cd = ClientDAL(session)
            result = await cd.get_client_by_username(username=username)
            return result

    @staticmethod
    async def get_all_referrers_by_link(
        referral_link: str,
    ) -> Union[str, DBTransactionStatus.NOT_EXIST]:
        async with async_session() as session:
            client_dal = ClientDAL(session)
            result = await client_dal.get_all_referrers_by_link(referral_link=referral_link)
            return result

    @staticmethod
    async def get_referral_link(
        chat_id: int,
    ) -> Union[str, DBTransactionStatus.NOT_EXIST]:
        async with async_session() as session:
            client_dal = ClientDAL(session)
            result = await client_dal.get_referral_link(chat_id=chat_id)
            return result

    @staticmethod
    async def get_all_clients():
        async with async_session() as session:
            client_dal = ClientDAL(session)
            result = await client_dal.get_all_clients()
            return result

    @staticmethod
    async def update_change_reservation(chat_id: int):
        async with async_session() as session:
            client_dal = ClientDAL(session)
            result = await client_dal.update_change_reservation(chat_id=chat_id)
            return result

    @staticmethod
    async def update_phone(chat_id: int, phone: str):
        async with async_session() as session:
            client_dal = ClientDAL(session)
            result = await client_dal.update_phone(chat_id=chat_id, phone=phone)
            return result

    @staticmethod
    async def update_first_name(chat_id: int, first_name: str):
        async with async_session() as session:
            client_dal = ClientDAL(session)
            result = await client_dal.update_first_name(chat_id=chat_id, first_name=first_name)
            return result

    @staticmethod
    async def update_last_name(chat_id: int, last_name: str):
        async with async_session() as session:
            client_dal = ClientDAL(session)
            result = await client_dal.update_last_name(chat_id=chat_id, last_name=last_name)
            return result

    @staticmethod
    async def update_reserve_table(chat_id: int):
        async with async_session() as session:
            client_dal = ClientDAL(session)
            result = await client_dal.update_reserve_table(chat_id=chat_id)
            return result
    
    @staticmethod
    async def update_got_review_award(chat_id: int):
        async with async_session() as session:
            client_dal = ClientDAL(session)
            result = await client_dal.update_got_review_award(chat_id=chat_id)
            return result
    
    @staticmethod
    async def update_got_yandex_maps_award(chat_id: int):
        async with async_session() as session:
            client_dal = ClientDAL(session)
            result = await client_dal.update_got_yandex_maps_award(chat_id=chat_id)
            return result
    
    @staticmethod
    async def send_shipping_query(chat_id: int, capacity: int):
        try:
            msg = await bot.send_invoice(
                chat_id,  # chat_id
                f"Внести депозит на сумму {capacity*1000}₽",  # title
                f"Внести депозит на сумму {capacity*1000}₽ за бронь столов больше, чем на 10 человек. Вы должны это сделать в течение 12 часов, в противном случае администратор закроет вашу заявку, а шлюз на внесение депозита будет удален.",  # description
                f"Внести депозит на сумму {capacity*1000}₽",  # invoice_payload
                provider_token,
                "RUB",
                [types.LabeledPrice(label=f"Депозит за бронь {capacity*1000}₽", amount=capacity*1000 * 100)]
            )
            return msg
        except Exception as e:
            return e
    
    @staticmethod
    async def update_client_data(chat_id, username, first_name, last_name):
        async with async_session() as session:
            client_dal = ClientDAL(session)
            result = await client_dal.update_client(
                chat_id=chat_id, 
                username=username, 
                first_name=first_name, 
                last_name=last_name
            )
            return result

def generate_experience_bar(experience_percentage):
    # Создаем изображение для полоски опыта
    img = Image.new("RGB", (400, 50), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Определяем размеры полосы заполнения опыта на основе процентного значения
    bar_width = int(400 * (experience_percentage / 100))

    # Рисуем пустую полосу
    draw.rectangle([0, 0, 400, 50], fill=(200, 200, 200))
    # Рисуем заполненную часть полосы
    draw.rectangle([0, 0, bar_width, 50], fill=(0, 255, 0))

    return img



# if __name__ == "__main__":

#     async def client_test():
#         await ClientMiddleware.refill_balance(chat_id=445756820, amount=-1030)

#     asyncio.run(client_test())
