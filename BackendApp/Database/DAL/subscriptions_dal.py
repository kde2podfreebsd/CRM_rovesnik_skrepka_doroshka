from sqlalchemy.future import select
from BackendApp.Database.Models.subscriptions_model import Subscription
from BackendApp.Database.Models.client_model import Client
from BackendApp.Database.session import DBTransactionStatus, async_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
import asyncio

class SubscriptionDAL:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_subscription(
            self,
            client_id: int
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST]:

        existing_subscription = await self.db_session.execute(select(Subscription).where(
                Subscription.client_id == client_id
            )
        )
        existing_subscription = existing_subscription.scalars().first()
        if (existing_subscription):
            return DBTransactionStatus.ALREADY_EXIST
        
        new_subscription = Subscription(
            client_id=client_id
        )

        self.db_session.add(new_subscription)

        try:
            await self.db_session.commit()
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            print(e)
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def add_sub(
            self,
            client_id: int,
            promotion_id: str
            
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST]:

        subscription = await self.db_session.execute(
            select(Subscription).where(Subscription.client_id == client_id)
        )
        subscription = subscription.scalars().first()

        if (promotion_id in subscription.subs_ids):
            return DBTransactionStatus.ALREADY_EXIST
        else:
            subscription.subs_ids.append(promotion_id)
            try:
                await self.db_session.commit()
                return DBTransactionStatus.SUCCESS

            except Exception as e:
                await self.db_session.rollback()
                return DBTransactionStatus.ROLLBACK
    
    async def remove_sub(
            self,
            client_id: int,
            promotion_id: int
            
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        subscription = await self.db_session.execute(
            select(Subscription).where(Subscription.client_id == client_id)
        )
        subscription = subscription.scalars().first()

        if (promotion_id not in subscription.subs_ids):
            return DBTransactionStatus.NOT_EXIST
        else:
            subscription.subs_ids.remove(promotion_id)
            try:
                await self.db_session.commit()
                return DBTransactionStatus.SUCCESS

            except Exception as e:

                await self.db_session.rollback()
                return DBTransactionStatus.ROLLBACK

    async def delete_subscription(
        self, 
        client_id: int
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        promotion = await self.db_session.execute(
            select(Subscription).where(Subscription.client_id == client_id)
        )

        promotion = promotion.scalars().first()

        if not promotion:
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(promotion)

        try:
            await self.db_session.commit()
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def get_all_subscriptions(self):
        result = await self.db_session.execute(select(Subscription))
        return result.scalars().all()

    async def get_subscription_by_client_id(self, client_id: int):
        result = await self.db_session.execute(select(Subscription).where(Subscription.client_id == client_id))
        return result.scalars().first()

async def test_subs():
    async with async_session() as session:
        sd = SubscriptionDAL(session)
        result = await sd.get_subscription_by_client_id(client_id=2)
        print(result)
    
if __name__ == "__main__":
    asyncio.run(test_subs())