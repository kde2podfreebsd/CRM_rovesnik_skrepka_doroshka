import asyncio
from typing import List, Union
from uuid import uuid4

import qrcode
from PIL import Image, ImageDraw, ImageFont
from psycopg2 import IntegrityError
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from BackendApp import basedir
from BackendApp.Logger import logger, LogLevel
from BackendApp.Database.Models.bar_model import Bar
from BackendApp.Database.Models.client_model import Client
from BackendApp.Database.Models.referrals_model import Referral
from BackendApp.Database.Models.transaction_model import Transaction
from BackendApp.Database.session import DBTransactionStatus, async_session


class ClientDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def check_existence(
        self, chat_id: int
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ALREADY_EXIST]:
        existing_user = await self.db_session.execute(
            select(Client).where(and_(Client.chat_id == chat_id))
        )
        existing_user = existing_user.scalars().first()

        if existing_user:
            logger.log(
                level=LogLevel.INFO,
                message=f"Checked client existance: a Client with id {chat_id} already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST
        else:
            logger.log(
                level=LogLevel.INFO,
                message=f"Checked client existance: a Client with id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.SUCCESS

    async def create(
        self,
        chat_id: int,
        username: str,
        first_name: str,
        last_name: str,
        iiko_card: str,
        iiko_id: str,
    ) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.ALREADY_EXIST,
    ]:
        if (
            await self.check_existence(chat_id=chat_id)
            == DBTransactionStatus.ALREADY_EXIST
        ):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with id {chat_id} already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST

        qr_img = await ClientDAL.generate_qr_code(iiko_card=str(iiko_card))
        referral_links = await self.db_session.execute(
            select(Client.referral_link)
        )
        referral_links = referral_links.scalars().first()
        referral_link = str(uuid4())

        if referral_links is not None:
            while referral_link in referral_links:
                referral_link = str(uuid4())

        new_user = Client(
            chat_id=chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            iiko_card=str(iiko_card),
            iiko_id=str(iiko_id),
            referral_link=referral_link if referral_link else None,
            # qr_code_path=rf'{basedir}/qr_codes/{chat_id}.png'
        )

        self.db_session.add(new_user)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Client entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Client entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    @staticmethod
    async def generate_qr_code(iiko_card: int, iiko_id: int = None):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )
        qr.add_data(iiko_card)
        qr.make(fit=True)
# Создание изображения QR-кода без фона
        qr_img = qr.make_image(fill='black', back_color='white').convert('RGBA')

        # Изменение размера изображения с использованием фильтра ресэмплинга
        qr_img = qr_img.resize((466, 466), Image.LANCZOS)

        qr_img.save(rf"{basedir}/static/user_qrcode/{iiko_card}.png")

        # Применение дизайна, если указан
        # if qr_design:
        #     qr_img = apply_design(qr_img, qr_design)

        return qr_img

    # def apply_design(qr_img, qr_design):
    #     # Применение дизайна к изображению QR-кода
    #     # Например, изменение цвета и добавление логотипа
    #     # В qr_design можно передать параметры дизайна, такие как цвет фона, цвет элементов и т. д.
    #     # Подробнее о настройке дизайна QR-кода можно узнать из документации библиотеки qrcode
    #
    #     # Пример: изменение цвета фона
    #     qr_img = qr_img.convert("RGBA")
    #     qr_img_data = qr_img.getdata()
    #     new_qr_img_data = []
    #     for item in qr_img_data:
    #         if item[0] == 255 and item[1] == 255 and item[2] == 255:
    #             # Прозрачный пиксель
    #             new_qr_img_data.append((255, 255, 255, 0))
    #         else:
    #             # Цвет фона
    #             new_qr_img_data.append((255, 255, 255, 255))
    #     qr_img.putdata(new_qr_img_data)
    #
    #     # Пример: добавление логотипа
    #     if 'logo_path' in qr_design:
    #         logo = Image.open(qr_design['logo_path'])
    #         logo_size = int(qr_img.size[0] * 0.2)  # Размер логотипа
    #         qr_img.paste(logo, ((qr_img.size[0] - logo_size) // 2, (qr_img.size[1] - logo_size) // 2), logo)
    #
    #     return qr_img
    #
    # # Пример использования
    # data = "https://example.com"
    # qr_design = {
    #     'logo_path': 'logo.png',  # Путь к логотипу
    #     # Другие параметры дизайна, например цвета
    # }
    # qr_code = generate_qr_code(data, qr_design)
    # qr_code.show()  # Показать QR-код

    async def get_client(
        self, chat_id: int
    ) -> Union[Client, DBTransactionStatus.NOT_EXIST]:
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )

        client = client.scalars().first()

        if client:
            logger.log(
                level=LogLevel.INFO,
                message=f"Client entity with id {chat_id} has been successfully retrieved"
            )
            return client

        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def get_client_by_iiko_id(
        self, iiko_id: int
    ) -> Union[Client, DBTransactionStatus.NOT_EXIST]:
        client = await self.db_session.execute(
            select(Client).where(Client.iiko_id == iiko_id)
        )

        client = client.scalars().first()

        if client:
            logger.log(
                level=LogLevel.INFO,
                message=f"Client entity with iiko_id {iiko_id} has been successfully retrieved"
            )
            return client

        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with iiko_id {iiko_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def get_client_by_iiko_card(
        self, iiko_card: str
    ) -> Union[Client, DBTransactionStatus.NOT_EXIST]:
        client = await self.db_session.execute(
            select(Client).where(Client.iiko_card == iiko_card)
        )
        if client:
            logger.log(
                level=LogLevel.INFO,
                message=f"Client entity with iiko_card {iiko_card} has been successfully retrieved"
            )
            return client.scalars().first()
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with iiko_card {iiko_card} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def get_client_by_ref_link(
        self, referral_link: str
    ) -> Union[Client, DBTransactionStatus.NOT_EXIST]:
        client = await self.db_session.execute(
            select(Client).where(Client.referral_link == referral_link)
        )

        client = client.scalars().first()

        if client:
            logger.log(
                level=LogLevel.INFO,
                message=f"Client entity with referral_link {referral_link} has been successfully retrieved"
            )
            return client

        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with referral_link {referral_link} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def get_client_by_username(self, username: str) -> Union[Client, DBTransactionStatus.NOT_EXIST]:
        client = await self.db_session.execute(select(Client).where(Client.username == username))
        client = client.scalars().first()
        if (client):
            logger.log(
                level=LogLevel.INFO,
                message=f"Client entity with username {username} has been successfully retrieved"
            )
            return client
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with username {username} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def get_all_clients(
        self,
    ) -> Union[List[Client], DBTransactionStatus.NOT_EXIST]:
        clients = await self.db_session.execute(select(Client))
        clients = clients.scalars().all()

        if clients:
            logger.log(
                level=LogLevel.INFO,
                message=f"Client entities have been successfully retrieved"
            )
            return clients
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"There are no Client entities in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def get_all_referrers_by_link(
        self, referral_link: str
    ) -> Union[str, DBTransactionStatus.NOT_EXIST]:
        referrers = await self.db_session.execute(
            select(Referral).where(Referral.referral_link == referral_link)
        )
        if referrers:
            logger.log(
                level=LogLevel.INFO,
                message=f"Referrers Client entities with referral_link {referral_link} have been successfully retrieved"
            )
            return [referrer[0] for referrer in referrers]
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"There are no referrers Client entities with referral_link {referral_link} in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def get_referral_link(
        self, chat_id: int
    ) -> Union[str, DBTransactionStatus.NOT_EXIST]:
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )
        client = client.scalars().first()
        if client:
            logger.log(
                level=LogLevel.INFO,
                message=f"Referral link for Client entity with chat_id {chat_id} has been successfully retireved"
            )
            return client.referral_link
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with chat_id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    # obsolete
    async def update_client_loyalty(self, chat_id: int, loyalty_id: str):
        """
        Updates the loyalty ID of a client with the given chat ID.

        Args:
            chat_id (int): The chat ID of the client.
            loyalty_id (str): The new loyalty ID.

        Returns:
            Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.NOT_EXIST]:
                - DBTransactionStatus.SUCCESS if the update was successful.
                - DBTransactionStatus.NOT_EXIST if the client was not found.

        """
        # Find the client with the given chat ID
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )
        client = client.scalars().first()

        if client:
            # Update the loyalty ID of the client
            client.loyalty_id = loyalty_id
            await self.db_session.commit()
            return DBTransactionStatus.SUCCESS
        else:
            return DBTransactionStatus.NOT_EXIST

    async def update_spend_money(self, chat_id: int, spend_money: float):
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )
        client = client.scalars().first()

        if client:
            client.spent_amount += spend_money
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Client with chat_id {chat_id} spent money has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with chat_id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def update_change_reservation(self, chat_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )
        client = client.scalars().first()

        if client:
            client.change_reservation = not(client.change_reservation)
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Client with chat_id {chat_id} change_reservation has been successfully updated"
                )
                return DBTransactionStatus.SUCCESS
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating Client entity change_reservation: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with chat_id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def update_phone(self, chat_id: int, phone: str) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )
        client = client.scalars().first()

        if client:
            client.phone = phone
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Client with chat_id {chat_id} phone has been successfully updated"
                )
                return DBTransactionStatus.SUCCESS
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating Client entity phone: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with chat_id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def update_first_name(self, chat_id: int, first_name: str) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )
        client = client.scalars().first()

        if client:
            client.first_name = first_name
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Client with chat_id {chat_id} first_name has been successfully updated"
                )
                return DBTransactionStatus.SUCCESS
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating Client entity first_name: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with chat_id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def update_last_name(self, chat_id: int, last_name: str) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )
        client = client.scalars().first()

        if client:
            client.last_name = last_name
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Client with chat_id {chat_id} last_name has been successfully updated"
                )
                return DBTransactionStatus.SUCCESS
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating Client entity last_name: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with chat_id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def update_reserve_table(self, chat_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )
        client = client.scalars().first()

        if client:
            client.reserve_table = not(client.reserve_table)
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Client with chat_id {chat_id} reserve_table has been successfully updated"
                )
                return DBTransactionStatus.SUCCESS
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating Client entity reserve_table: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with chat_id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def update_got_review_award(self, chat_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )
        client = client.scalars().first()

        if client:
            client.got_review_award = not(client.got_review_award)
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Client with chat_id {chat_id} got_review_award has been successfully updated"
                )
                return DBTransactionStatus.SUCCESS
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating Client entity got_review_award: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with chat_id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def update_got_yandex_maps_award(self, chat_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )
        client = client.scalars().first()

        if client:
            client.got_yandex_maps_award = not(client.got_yandex_maps_award)
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Client with chat_id {chat_id} got_yandex_maps_award has been successfully updated"
                )
                return DBTransactionStatus.SUCCESS
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating Client entity got_yandex_maps_award: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with chat_id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        
    async def update_client(
        self, 
        chat_id: int, 
        username: str = None, 
        first_name: str = None, 
        last_name: str = None,
        
        ) -> Union[
        DBTransactionStatus.SUCCESS, 
        DBTransactionStatus.ROLLBACK, 
        DBTransactionStatus.NOT_EXIST
        ]:
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == chat_id)
        )  
        client = client.scalars().first()
        if client:
            if username:
                client.username = username
            if first_name:
                client.first_name = first_name
            if last_name:
                client.last_name = last_name
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Client with chat_id {chat_id} has been successfully updated"
                )
                return DBTransactionStatus.SUCCESS
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating Client entity: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with chat_id {chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    

# the order in which tables should be created:
# - Loaylty
# - Client
# - Bar
# - Transaction

if __name__ == "__main__":

    async def client_test():
        async with async_session() as session:
            chat_id = 1713121214
            client_dal = ClientDAL(session)
            #             client = await client_dal.get_client(chat_id=chat_id)
            #             result = await client_dal.get_all_referrers_by_link(referral_link=client.referral_link)
            #             print(result[0].chat_id)

            # ❗️ почему-то при добавлении Loyalty level_name должен быть уникальным, хотя
            # может быть несколько людей с одинаковыми уравнями???

            # nl = Loyalty(loyalty_id=1, level_name="dgkjdgdgg", discount_percentage=85.123, required_money_spend=120000)
            # print(nl)
            # session.add(nl)
            # await session.commit()
            # nb = Bar(bar_id = 1, bar_name = "Rovesnik")
            # session.add(nb)
            # nt = Transaction(bar_id = 1, client_chat_id = chat_id, amount = 5000, final_amount = 15000)
            # session.add(nt)
            # await session.commit()


#             await client_dal.create(
#                 chat_id=1713121214,
#                 username="etepoetpe",
#                 first_name="sasha",
#                 last_name="ivanov",
#                 iiko_card="card2",
#                 iiko_id="card#card2"
#             )


#             print(uuid4())


# asyncio.run(client_test())
