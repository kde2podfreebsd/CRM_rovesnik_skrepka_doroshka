from BackendApp.Database.Models.review_model import Review
from BackendApp.Database.DAL.review_dal import ReviewDAL
from BackendApp.Database.session import DBTransactionStatus, async_session

class ReviewMiddleware:
    @staticmethod
    async def create(
        chat_id: int,
        text: str,
        bar_id: int = None,
        event_id: int = None
    ):
        async with async_session() as session:
            rd = ReviewDAL(session)
            result = await rd.create(
                chat_id=chat_id,
                text=text,
                bar_id=bar_id,
                event_id=event_id
            )
            return result
    
    @staticmethod
    async def delete(
        review_id: int
    ):
        async with async_session() as session:
            rd = ReviewDAL(session)
            result = await rd.delete(review_id=review_id)
            return result
    
    @staticmethod
    async def get_all():
        async with async_session() as session:
            rd = ReviewDAL(session)
            result = await rd.get_all()
            return result
    
    @staticmethod
    async def get_by_id(review_id: int):
        async with async_session() as session:
            rd = ReviewDAL(session)
            result = await rd.get_by_id(review_id=review_id)
            return result
    
    @staticmethod
    async def get_by_chat_id_and_bar_id(chat_id: int, bar_id: int):
        async with async_session() as session:
            rd = ReviewDAL(session)
            result = await rd.get_by_chat_id_and_bar_id(chat_id=chat_id, bar_id=bar_id)
            return result
    
    @staticmethod
    async def get_by_chat_id_and_event_id(chat_id: int, event_id: int):
        async with async_session() as session:
            rd = ReviewDAL(session)
            result = await rd.get_by_chat_id_and_event_id(chat_id=chat_id, event_id=event_id)
            return result
    
    @staticmethod
    async def get_by_chat_id(chat_id: int):
        async with async_session() as session:
            rd = ReviewDAL(session)
            result = await rd.get_by_chat_id(chat_id=chat_id)
            return result
    
    @staticmethod
    async def get_entity_id(
        chat_id: int,
        text: str,
        bar_id: int = None,
        event_id: int = None
    ):
        async with async_session() as session:
            rd = ReviewDAL(session)
            result = await rd.get_entity_id(
                chat_id=chat_id,
                text=text,
                bar_id=bar_id,
                event_id=event_id
            )
            return result