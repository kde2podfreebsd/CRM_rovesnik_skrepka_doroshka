from sqlalchemy import and_
from sqlalchemy.future import select
from BackendApp.Database.session import async_session
from BackendApp.Logger import logger, LogLevel
from BackendApp.Database.Models.review_model import Review
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional, List

import asyncio

class ReviewDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create(
        self,
        chat_id: int,
        text: str,
        bar_id: int = None,
        event_id: int = None
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK
    ]:  
        new_review = Review(
            chat_id=chat_id,
            text=text,
            bar_id=bar_id,
            event_id=event_id
        )
        try:
            self.db_session.add(new_review)
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Review entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Review entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def delete(self, review_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:

        review = await self.db_session.execute(
            select(Review).where(Review.id == review_id)
        )
        review = review.scalars().first()

        if (not review):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Review with id {review_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(review)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Review entity has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting Review entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def get_all(self) -> Optional[List[Review]]:
        result = await self.db_session.execute(select(Review))
        return result.scalars().all()

    async def get_by_id(self, review_id: int) -> Optional[Review]:
        result = await self.db_session.execute(select(Review).where(Review.id == review_id))
        return result.scalars().first()
    
    async def get_by_chat_id(self, chat_id: int) -> Optional[List[Review]]:
        result = await self.db_session.execute(select(Review).where(Review.chat_id == chat_id))
        return result.scalars().all()
    
    async def get_by_chat_id_and_bar_id(self, chat_id: int, bar_id: int) -> Optional[List[Review]]:
        result = await self.db_session.execute(select(Review).where(and_(
            Review.chat_id == chat_id,
            Review.bar_id == bar_id
        )))
        return result.scalars().all()

    async def get_by_chat_id_and_event_id(self, chat_id: int, event_id: int) -> Optional[List[Review]]:
        result = await self.db_session.execute(select(Review).where(and_(
            Review.chat_id == chat_id,
            Review.event_id == event_id
        )))
        return result.scalars().all()
    
    async def get_entity_id(
        self,
        chat_id: int,
        text: str,
        bar_id: int = None,
        event_id: int = None
    ):
        result = await self.db_session.execute(select(Review).where(and_(
            Review.chat_id == chat_id,
            Review.text == text,
            Review.bar_id == bar_id,
            Review.event_id == event_id
        )))
        result = result.scalars().first()
        if (result):
            return result.id
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Review with the given parameters: {chat_id, text, bar_id, event_id} does not exist in the data base"
            )
            return None

if __name__ == "__main__":
    async def main():
        async with async_session() as session:
            rd = ReviewDAL(session)
            
            
    asyncio.run(main())