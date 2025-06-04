from BackendApp.Database.DAL.subscriptions_dal import SubscriptionDAL
from BackendApp.Database.session import async_session, DBTransactionStatus

class SubscriptionMiddleware:

    @staticmethod
    async def get_all_subscriptions():
        async with async_session() as session:
            sd = SubscriptionDAL(session)
            result = await sd.get_all_subscriptions()
            return result
    
    @staticmethod
    async def get_subscription_by_client_id(client_id: int):
        async with async_session() as session:
            sd = SubscriptionDAL(session)
            result = await sd.get_subscription_by_client_id(client_id=client_id)
            return result
    
    @staticmethod
    async def add_sub(client_id: int, promotion_id: str):
        async with async_session() as session:
            sd = SubscriptionDAL(session)
            result = await sd.add_sub(client_id=client_id, promotion_id=promotion_id)
            return result
    
    @staticmethod
    async def remove_sub(client_id: int, promotion_id: str):
        async with async_session() as session:
            sd = SubscriptionDAL(session)
            result = await sd.remove_sub(client_id=client_id, promotion_id=promotion_id)
            return result
    