from sqlalchemy import and_
from sqlalchemy.future import select
from BackendApp.Database.Models.affilate_promotions_model import AffilatePromotions
from BackendApp.Database.Models.promocode_types import _PromocodeType
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, List
import asyncio
from BackendApp.Logger import logger, LogLevel


class AffilatePromotionsDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
            self,
            channel_link: str,
            promotion_text: str,
            promocode_type: _PromocodeType,
            short_name: str,
            bar_id: int
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST]:
        existing_promotion = await self.db_session.execute(select(AffilatePromotions).where(
            AffilatePromotions.channel_link == channel_link,
            AffilatePromotions.promotion_text == promotion_text,
            AffilatePromotions.promocode_type == promocode_type,
            AffilatePromotions.short_name == short_name,
            AffilatePromotions.bar_id == bar_id
        ))
        existing_promotion = existing_promotion.scalars().first()

        if (existing_promotion):
            logger.log(
                level=LogLevel.WARNING,
                message=f"An AffiliatePromotions with the given parameters: {channel_link, promotion_text, promocode_type, short_name}, - already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST

        new_promotion = AffilatePromotions(
            channel_link=channel_link,
            promotion_text=promotion_text,
            promocode_type=promocode_type,
            short_name=short_name,
            sub_chat_id=[],
            bar_id=bar_id
        )

        self.db_session.add(new_promotion)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"AffiliatePromotion entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating AffiliatePromotion entity: {e}"
            )
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def update(
            self,
            promotion_id: int,
            channel_link: str = None,
            promocode_type: _PromocodeType = None,
            promotion_text: str = None,
            short_name: str = None,
            sub_chat_id: List[str] = None,
            bar_id: int = None
            
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        promotion = await self.db_session.execute(
            select(AffilatePromotions).where(AffilatePromotions.id == promotion_id)
        )

        promotion = promotion.scalars().first()

        if not promotion:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An AffiliatePromotions with id {promotion_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if channel_link is not None:
            promotion.channel_link = channel_link
        if promotion_text is not None:
            promotion.promotion_text = promotion_text
        if promocode_type is not None:
            promotion.promocode_type = promocode_type
        if short_name is not None:
            promotion.short_name = short_name
        if sub_chat_id is not None:
            promotion.sub_chat_id = sub_chat_id
        if bar_id is not None:
            promotion.bar_id = bar_id

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"AffiliatePromotion entity with id {promotion_id} has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating AffiliatePromotion entity: {e}"
            )
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def delete(self, promotion_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        promotion = await self.db_session.execute(
            select(AffilatePromotions).where(AffilatePromotions.id == promotion_id)
        )

        promotion = promotion.scalars().first()

        if not promotion:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An AffiliatePromotions with id {promotion_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(promotion)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"AffiliatePromotion entity with id {promotion_id} has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting AffiliatePromotion entity: {e}"
            )
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def get_all(self):
        result = await self.db_session.execute(select(AffilatePromotions))
        return result.scalars().all()

    async def get_by_id(self, promotion_id: int):
        result = await self.db_session.execute(select(AffilatePromotions).where(AffilatePromotions.id == promotion_id))
        return result.scalars().first()

    async def get_by_channel_link(self, channel_link: str):
        result = await self.db_session.execute(select(AffilatePromotions).where(AffilatePromotions.channel_link == channel_link))
        return result.scalars().all()

    async def get_by_bar_id(self, bar_id: int):
        result = await self.db_session.execute(select(AffilatePromotions).where(AffilatePromotions.bar_id == bar_id))
        return result.scalars().all()
    
    async def get_entity_id(
        self,
        channel_link: str,
        promotion_text: str,
        promocode_type: _PromocodeType,
        short_name: str,
        bar_id: int
    ):
        result = await self.db_session.execute(select(AffilatePromotions).where(and_(
            AffilatePromotions.channel_link == channel_link,
            AffilatePromotions.promotion_text == promotion_text,
            AffilatePromotions.promocode_type == promocode_type,
            AffilatePromotions.short_name == short_name,
            AffilatePromotions.bar_id == bar_id
        )))
        result = result.scalars().first()
        if (result):
            return result.id
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An AffiliatePromotions with the given parameters: {channel_link, promotion_text, promocode_type, short_name} does not exist in the data base"
            )
            return None


if __name__ == "__main__":
    async def affilate_promotions_test():
        from BackendApp.Database.session import async_session

        async with async_session() as session:
            affilate_promotions_dal = AffilatePromotionsDAL(session)

            # Тестирование CRUD функций

            # Создание промоакции
            # promotion_create_status = await affilate_promotions_dal.create(
            #     channel_link="https://t.me/complicat9d",
            #     promotion_text="Самые лучшие что-то, подпишись ",
            #     reward="Получи 100 рублей на счет",
            #     short_name="Телеграм канал по лучшему чему-то"
            # )
            # print("Promotion Create Status:", promotion_create_status)

            # Обновление промоакции
            # promotion_update_status = await affilate_promotions_dal.update(promotion_id=1, promotion_text="Updated promotion text")
            # print("Promotion Update Status:", promotion_update_status)

            # Удаление промоакции
            # promotion_delete_status = await affilate_promotions_dal.delete(promotion_id=1)
            # print("Promotion Delete Status:", promotion_delete_status)

            # Получение всех промоакций
            # all_promotions = await affilate_promotions_dal.get_all()
            # print("All Promotions:", [promotion.channel_link for promotion in all_promotions])

            # Получение промоакции по идентификатору
            # promotion_by_id = await affilate_promotions_dal.get_by_id(promotion_id=2)
            # print("Promotion By ID:", promotion_by_id.id if promotion_by_id else None)

            # Получение промоакции по каналу
            # promotion_by_channel_link = await affilate_promotions_dal.get_by_channel_link(channel_link="some_link")
            # print("Promotion By Channel Link:", promotion_by_channel_link.id if promotion_by_channel_link else None)


    asyncio.run(affilate_promotions_test())
