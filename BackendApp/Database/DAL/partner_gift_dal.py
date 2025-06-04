from sqlalchemy import and_
from sqlalchemy.future import select
from BackendApp.Database.Models.partner_gift_model import PartnerGift
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
import asyncio

from BackendApp.Database.session import async_session
from BackendApp.Logger import logger, LogLevel

class PartnerGiftDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create(
        self,
        short_name: str,
        promotion_text: str,
        bar_id: int
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST
    ]:
        existing_partner_gift = await self.db_session.execute(select(PartnerGift).where(and_(
            PartnerGift.short_name == short_name,
            PartnerGift.promotion_text == promotion_text,
            PartnerGift.bar_id == bar_id
        )))
        existing_partner_gift = existing_partner_gift.scalars().first()
        if (existing_partner_gift):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A PartnerGift with the given parameters: {short_name, promotion_text}, - already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST
        
        new_partner_gift = PartnerGift(
            short_name=short_name,
            promotion_text=promotion_text,
            bar_id=bar_id
        )
        try:
            self.db_session.add(new_partner_gift)
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"PartnerGift entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating PartnerGift entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def update(
        self,
        partner_gift_id: int,
        short_name: str = None,
        promotion_text: str = None,
        got_gift: list = None,
        bar_id: int = None
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        partner_gift = await self.db_session.execute(select(PartnerGift).where(PartnerGift.id == partner_gift_id))
        partner_gift = partner_gift.scalars().first()

        if (not partner_gift):
            logger.log(
                level=LogLevel.WARNING,
                message=f"An PartnerGift with id {partner_gift_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if (short_name is not None):
            partner_gift.short_name = short_name
        if (promotion_text is not None):
            partner_gift.promotion_text = promotion_text
        if (got_gift is not None):
            partner_gift.got_gift = got_gift
        if (got_gift is not None):
            partner_gift.bar_id = bar_id
        
        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"PartnerGift with id {partner_gift_id} entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating PartnerGift entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
        
    async def delete(self, partner_gift_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        partner_gift = await self.db_session.execute(
            select(PartnerGift).where(PartnerGift.id == partner_gift_id)
        )
        partner_gift = partner_gift.scalars().first()

        if (not partner_gift):
            logger.log(
                level=LogLevel.WARNING,
                message=f"An PartnerGift with id {partner_gift_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(partner_gift)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"PartnerGift with id {partner_gift_id} entity has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting PartnerGift entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def get_all(self):
        result = await self.db_session.execute(select(PartnerGift))
        return result.scalars().all()
    
    async def get_by_bar_id(self, bar_id: int):
        result = await self.db_session.execute(select(PartnerGift).where(PartnerGift.bar_id == bar_id))
        return result.scalars().all()

    async def get_by_id(self, partner_gift_id: int):
        result = await self.db_session.execute(select(PartnerGift).where(PartnerGift.id == partner_gift_id))
        return result.scalars().first()
    
    async def get_entity_id(
        self,
        short_name: str,
        promotion_text: str,
        bar_id: int
    ):
        result = await self.db_session.execute(select(PartnerGift).where(and_(
            PartnerGift.short_name == short_name,
            PartnerGift.promotion_text == promotion_text,
            PartnerGift.bar_id == bar_id
        )))
        result = result.scalars().first()
        if (result):
            return result.id
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A PartnerGift with the given parameters: {short_name, promotion_text} does not exist in the data base"
            )
            return None

if __name__ == "__main__":
    async def main():
        async with async_session() as session:
            pgd = PartnerGiftDAL(session)

            result = await pgd.create(
                short_name="Акция от партнера №1",
                promotion_text="Самая лучшая компания по производству пирожков, вот наш телеграм канал @complicat9d"
            )
            print(result)
    asyncio.run(main())