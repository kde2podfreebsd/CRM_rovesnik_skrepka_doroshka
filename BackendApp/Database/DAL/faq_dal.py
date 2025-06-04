from sqlalchemy.future import select
from BackendApp.Database.Models.faq_model import FAQ
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from BackendApp.Logger import logger, LogLevel
from typing import Union
import asyncio


class FAQDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
            self,
            text: str,
            bar_id: int
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST]:
        existing_faq = await self.db_session.execute(
            select(FAQ).where(FAQ.bar_id == bar_id)
        )

        existing_faq = existing_faq.scalars().first()

        if existing_faq:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A FAQ with the given parameters: {bar_id, text}, - already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST

        new_faq = FAQ(
            text=text,
            bar_id=bar_id
        )

        self.db_session.add(new_faq)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"FAQ entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating FAQ entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def update(
            self,
            faq_id: int,
            text: str = None,
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:
        faq = await self.db_session.execute(
            select(FAQ).where(FAQ.id == faq_id)
        )

        faq = faq.scalars().first()

        if not faq:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An FAQ with id {faq_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if text is not None:
            faq.text = text

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"FAQ entity with id {faq_id} has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating FAQ entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def delete(self, faq_id: int) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        faq = await self.db_session.execute(
            select(FAQ).where(FAQ.id == faq_id)
        )

        faq = faq.scalars().first()

        if not faq:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An FAQ with id {faq_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(faq)

        try:
            logger.log(
                level=LogLevel.INFO,
                message=f"FAQ entity with id {faq_id} has been successfully deleted"
            )
            await self.db_session.commit()
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting FAQ entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_all(self):
        result = await self.db_session.execute(select(FAQ))
        return result.scalars().all()

    async def get_by_id(self, faq_id: int):
        result = await self.db_session.execute(select(FAQ).where(FAQ.id == faq_id))
        return result.scalars().first()
    
    async def get_by_bar_id(self, bar_id: int):
        result = await self.db_session.execute(select(FAQ).where(FAQ.bar_id == bar_id))
        return result.scalars().first()

    async def get_entity_id(self, text: str, bar_id: int) -> Union[DBTransactionStatus.NOT_EXIST, FAQ]:
        result = await self.db_session.execute(select(FAQ).where(FAQ.text == text, FAQ.bar_id == bar_id))
        result = result.scalars().first()
        if (result):
            return result.id
        
        logger.log(
            level=LogLevel.WARNING,
            message=f"A FAQ with the given parameters: {text, bar_id} does not exist in the data base"
        )
        return DBTransactionStatus.NOT_EXIST


if __name__ == "__main__":
    async def faq_test():
        from BackendApp.Database.session import async_session

        async with async_session() as session:
            faq_dal = FAQDAL(session)

            # faq_create_status = await faq_dal.create(short_name="question1", answer="answer1")
            # print("FAQ Create Status:", faq_create_status)
            #
            # faq_update_status = await faq_dal.update(faq_id=1, answer="updated answer")
            # print("FAQ Update Status:", faq_update_status)
            #
            # faq_delete_status = await faq_dal.delete(faq_id=1)
            # print("FAQ Delete Status:", faq_delete_status)
            #
            # all_faqs = await faq_dal.get_all()
            # print("All FAQs:", [faq.short_name for faq in all_faqs])

            # faq_by_id = await faq_dal.get_by_id(faq_id=1)
            # print("FAQ By ID:", faq_by_id.id if faq_by_id else None)

            # faq_by_short_name = await faq_dal.get_by_short_name(short_name="question2")
            # print("FAQ By Short Name:", faq_by_short_name.id if faq_by_short_name else None)

    asyncio.run(faq_test())
