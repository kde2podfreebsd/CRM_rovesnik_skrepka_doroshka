import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Union
from typing import List, Optional, Union
from uuid import uuid4

import qrcode
import secrets
import hashlib
from PIL import Image, ImageDraw, ImageFont
from psycopg2 import IntegrityError
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from BackendApp import basedir
from BackendApp.Logger import logger, LogLevel
from BackendApp.Database.Models.promocode_model import Promocode
from BackendApp.Database.Models.promocode_types import _PromocodeType
from BackendApp.Database.session import DBTransactionStatus, async_session


class PromocodeDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
        self,
        number: int,
        name: str,
        operational_info: str,
        description: str,
        type: _PromocodeType,
        client_chat_id: int = None,
        end_time: datetime = None,
        is_activated: bool = False,
        weight: int = None
    ) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.ALREADY_EXIST,
    ]:
        existing_promocode = await self.db_session.execute(
            select(Promocode).where(Promocode.number == number)
        )
        if existing_promocode.scalars().first():
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with number {number} already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST
        
        if (client_chat_id == 0 or client_chat_id == None):
            new_promocode = Promocode(
                client_chat_id=client_chat_id,
                number=number,
                name=name,
                operational_info=operational_info,
                description=description,
                type=type,
                end_time=end_time,
                is_activated=is_activated,
                weight=weight
            )
        else:
            hashcode = secrets.token_hex(16)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(hashcode)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            qr_path = rf'{basedir}/static/promocodes/{client_chat_id}_{hashcode}.png'
            qr_img.save(qr_path)
            new_promocode = Promocode(
                client_chat_id=client_chat_id,
                number=number,
                name=name,
                operational_info=operational_info,
                description=description,
                type=type,
                end_time=end_time,
                is_activated=is_activated,
                qr_path=qr_path,
                hashcode=hashcode,
                weight=weight
            )

        self.db_session.add(new_promocode)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Promocode entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Promocode entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def update_promocode(
        self,
        number: int,
        name: str = None,
        operational_info: str = None,
        description: str = None,
        type: _PromocodeType = None,
        client_chat_id: int = None,
        is_activated: bool = None,
        weight: int = None
    ):
        promocode = await self.db_session.execute(
            select(Promocode).where(and_(Promocode.number == number))
        )
        promocode = promocode.scalars().first()
        if (not promocode):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with number {number} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if (name is not None):
            promocode.name = name
        if (operational_info is not None):
            promocode.operational_info = operational_info
        if (description is not None):
            promocode.description = description
        if (type is not None):
            promocode.type = type
        if (client_chat_id is not None):
            promocode.client_chat_id = client_chat_id
        if (is_activated is not None):
            promocode.is_activated = is_activated
        if (weight is not None):
            promocode.weight = weight

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Promocode with number {number} entity has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating Promocode entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def delete_promocode(
        self, number: int
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        exist_promocode = await self.db_session.execute(
            select(Promocode).where(and_(Promocode.number == number))
        )
        exist_promocode = exist_promocode.scalars().first()

        if not exist_promocode:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with number {number} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(exist_promocode)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Promocode with number {number} entity has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting Promocode entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def check_promocodes_validity(
        self, client_chat_id: int
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK]:
        promocodes = await self.db_session.execute(
            select(Promocode).where(Promocode.client_chat_id == client_chat_id)
        )
        for promocode in promocodes.scalars().all():
            if (
                promocode.end_time is not None
                and promocode.end_time < datetime.now()
            ):
                promocode.is_activated = True

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"All Promocode entities owned by the client with id {client_chat_id} has been validated"
            )
            return DBTransactionStatus.SUCCESS

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while checking validity of Promocode entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def validate_promocode_by_number(self, number: int) -> Union[bool, DBTransactionStatus.NOT_EXIST]:
        promocode = await self.db_session.execute(select(Promocode).where(Promocode.number == number))
        promocode = promocode.scalars().first()
        if (promocode):
            if (promocode.end_time):
                if (promocode.end_time < datetime.now()):
                    return False
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with number {number} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        logger.log(
            level=LogLevel.INFO,
            message=f"A Promocode entity with number {number} has been validated"
        )
        return True
    
    async def validate_promocode_by_hashcode(self, hashcode: int) -> Union[bool, DBTransactionStatus.NOT_EXIST]:
        promocode = await self.db_session.execute(select(Promocode).where(Promocode.hashcode == hashcode))
        promocode = promocode.scalars().first()
        if (promocode):
            if (promocode.end_time):
                if (promocode.end_time < datetime.now()):
                    return False
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with hashcode {hashcode} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        logger.log(
            level=LogLevel.INFO,
            message=f"A Promocode entity with hashcode {hashcode} has been validated"
        )
        return True

    async def get_user_promocodes(
        self, client_chat_id: int
    ) -> Optional[List[Promocode]]:
        await self.check_promocodes_validity(client_chat_id)
        promocodes = await self.db_session.execute(
            select(Promocode).where(Promocode.client_chat_id == client_chat_id)
        )
        return promocodes.scalars().all()

    async def get_all_promocodes(self) -> Union[List[Promocode], DBTransactionStatus.NOT_EXIST]:
        promocodes = await self.db_session.execute(select(Promocode))
        result = promocodes.scalars().all()
        if result:
            return result
        logger.log(
            level=LogLevel.WARNING,
            message=f"There are no Promocode entities in the data base"
        )
        return DBTransactionStatus.NOT_EXIST

    async def get_promocode_by_id(
        self, promocode_id: int
    ) -> Union[Promocode, DBTransactionStatus.NOT_EXIST]:
        promocode = await self.db_session.execute(
            select(Promocode).where(Promocode.id == promocode_id)
        )

        result = promocode.scalars().first()
        if result:
            return result
        
        logger.log(
            level=LogLevel.WARNING,
            message=f"A Promocode with id {promocode_id} does not exist in the data base"
        )
        return DBTransactionStatus.NOT_EXIST

    async def get_free_promocodes(self) -> Union[List[Promocode], DBTransactionStatus.NOT_EXIST]:
        promocodes = await self.db_session.execute(
            select(Promocode).where(or_(Promocode.client_chat_id == None, Promocode.client_chat_id == 0))
        )
        result = promocodes.scalars().all()
        if result:
            return result
        logger.log(
            level=LogLevel.WARNING,
            message=f"There are no Promocode entities with client_chat_id 0 in the data base"
        )
        return DBTransactionStatus.NOT_EXIST

    async def add_client_to_promocode(
        self, number: int, client_chat_id: int
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST, DBTransactionStatus.ALREADY_EXIST
    ]:
        promocode = await self.db_session.execute(
            select(Promocode).where(Promocode.number == number)
        )

        promocode = promocode.scalars().first()

        if not promocode:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with number {number} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if (promocode.client_chat_id != 0):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A client has already been added to the promocode with number {number}"
            )
            return DBTransactionStatus.ALREADY_EXIST

        promocode.client_chat_id = client_chat_id

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Client with chat_id {client_chat_id} has successfully been added to the promocode with number {number}"
            )
            return DBTransactionStatus.SUCCESS

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.INFO,
                message=f"An error occurred while adding client with chat_id {client_chat_id} to the promocode with number {number}: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def activate_promocode(
        self, number: int
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        promocode = await self.db_session.execute(
            select(Promocode).where(Promocode.number == number)
        )

        promocode = promocode.scalars().first()

        if not promocode:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with number {number} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        promocode.is_activated = True

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Promocode with number {number} has been successfully activated"
            )
            return DBTransactionStatus.SUCCESS

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.INFO,
                message=f"An error occurred while activating promocode with number {number}: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def activate_promocode_by_hashcode(
        self, hashcode: str
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        promocode = await self.db_session.execute(
            select(Promocode).where(Promocode.hashcode == hashcode)
        )

        promocode = promocode.scalars().first()

        if not promocode:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with hashcode {hashcode} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        promocode.is_activated = True

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Promocode with hashcode {hashcode} has been successfully activated"
            )
            return DBTransactionStatus.SUCCESS

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.INFO,
                message=f"An error occurred while activating promocode with hashcode {hashcode}: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_free_promocodes_by_type(
        self, promocode_type: _PromocodeType
    ) -> Union[List[Promocode], DBTransactionStatus.NOT_EXIST]:
        promocodes = await self.db_session.execute(
            select(Promocode).where(
                Promocode.type == promocode_type,
                Promocode.client_chat_id == 0
            )
        )
        result = promocodes.scalars().all()
        if result:
            return result
        logger.log(
            level=LogLevel.WARNING,
            message=f"There are no Promocode entities with promocode_type {promocode_type} and client_chat_id 0 in the data base"
        )
        return DBTransactionStatus.NOT_EXIST

    async def update_hashcode(self, number: int, hashcode: str) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        promocode = await self.db_session.execute(select(Promocode).where(Promocode.number == number))
        promocode = promocode.scalars().first()

        if (promocode is None):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with number {number} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        
        promocode.hashcode = hashcode
        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Promocode with number {number} haschode has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.INFO,
                message=f"An error occurred while updating hashcode in the promocode with number {number}: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def update_qr_path(self, number: int, qr_path: str) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        promocode = await self.db_session.execute(select(Promocode).where(Promocode.number == number))
        promocode = promocode.scalars().first()

        if (not(promocode)):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with number {number} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        
        promocode.qr_path = qr_path
        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Promocode with number {number} qr_path has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.INFO,
                message=f"An error occurred while updating qr_path in the promocode with number {number}: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def update_activation_time(self, number: int):
        promocode = await self.db_session.execute(select(Promocode).where(Promocode.number == number))
        promocode = promocode.scalars().first()

        if (not(promocode)):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with number {number} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        
        promocode.activation_time = datetime.now()
        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Promocode with number {number} activation_time has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.INFO,
                message=f"An error occurred while updating activation_time in the promocode with number {number}: {e}"
            )
            return DBTransactionStatus.ROLLBACK
        
    async def get_entity_id(self, number: int) -> Union[
        int, DBTransactionStatus.NOT_EXIST
    ]:
        promocode = await self.db_session.execute(select(Promocode).where(Promocode.number == number))
        promocode = promocode.scalars().first()

        if (not(promocode)):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with number {number} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        return promocode.id

    async def get_promocode_by_hashcode(self, hashcode: str) -> Union[
        Promocode, DBTransactionStatus.NOT_EXIST
    ]:
        promocode = await self.db_session.execute(select(Promocode).where(Promocode.hashcode == hashcode))
        promocode = promocode.scalars().first()

        if (not(promocode)):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with hashcode {hashcode} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        return promocode
    
    async def get_not_activated_promocodes_for_client(self, chat_id: int):
        promocode = await self.db_session.execute(select(Promocode).where(and_(
            Promocode.client_chat_id == chat_id,
            Promocode.is_activated == False
        )))
        promocode = promocode.scalars().all()

        if (not(promocode)):
            logger.log(
                level=LogLevel.WARNING,
                message=f"There are no not activated Promocode entities for client_chat_id {chat_id} in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        
        return promocode

    async def get_activated_promocodes_for_client(self, chat_id: int):
        promocode = await self.db_session.execute(select(Promocode).where(and_(
            Promocode.client_chat_id == chat_id,
            Promocode.is_activated == True
        )))
        promocode = promocode.scalars().all()

        if (not(promocode)):
            logger.log(
                level=LogLevel.WARNING,
                message=f"There are no activated Promocode entities for client_chat_id {chat_id} in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        
        return promocode
    
    async def get_by_number(self, number: int) -> Union[
        Promocode, DBTransactionStatus.NOT_EXIST
    ]:
        result = await self.db_session.execute(select(Promocode).where(Promocode.number == number))
        result = result.scalars().first()
        if (result):
            return result
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Promocode with number {number} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

if __name__ == "__main__":

    async def main():
        async with async_session() as session:
            dal = PromocodeDAL(session)
            print(
                await dal.create(
                    client_chat_id=445756820,
                    number=123,
                    name="test_promocode",
                    description="test_promocode",
                    type=_PromocodeType.REFILLING_BALANCE,
                    end_time=datetime.now() + timedelta(days=1),
                    operational_info="test_promocode",
                )
            )
            print(await dal.get_user_promocodes(445756820))

    asyncio.run(main())
