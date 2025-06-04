from sqlalchemy.future import select
from sqlalchemy import and_
from psycopg2 import IntegrityError

from BackendApp.Logger import logger, LogLevel
from BackendApp.Database.Models.referrals_model import Referral
from BackendApp.Database.Models.client_model import Client
from BackendApp.Database.session import DBTransactionStatus, async_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
import asyncio

class ReferralDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_referral(
            self, 
            referral_id: int, # client.chat_id
            referrer_id: int 
    ) -> Union[
        DBTransactionStatus.SUCCESS, 
        DBTransactionStatus.ROLLBACK, 
        DBTransactionStatus.ALREADY_EXIST,
        DBTransactionStatus.NOT_EXIST
    ]:  
        if (referrer_id == referral_id):
            return 
        referral = await self.db_session.execute(
            select(Client).where(Client.chat_id == referral_id)
        )
        referral = referral.scalars().first()
        if (referral is None):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Referral (Client) with id {referral_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        
        referrer = await self.db_session.execute(
            select(Referral).where(
                and_(
                    Referral.chat_id == referrer_id, 
                    Referral.referral_link == referral.referral_link
                    )
                )
        )
        referrer = referrer.scalars().first()
        if (referrer is not None):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Referral with id {referrer_id} already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST
        
        new_referrer = Referral(
            chat_id = referrer_id,
            referral_link = referral.referral_link
        )

        self.db_session.add(new_referrer)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Referral entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS
        
        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Referral entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
        
    async def delete_referral(
            self, 
            referral_id: int, # client.chat_id
            referrer_id: int 
    ) -> Union[
        DBTransactionStatus.SUCCESS, 
        DBTransactionStatus.NOT_EXIST
    ]: 
        referral = await self.db_session.execute(
            select(Client).where(Client.chat_id == referral_id)
        )
        referral = referral.scalars().first()
        if (referral is None):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Referral (Client) with id {referral_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        referrer = await self.db_session.execute(
            select(Referral).where(
                and_(
                    Referral.chat_id == referrer_id, 
                    Referral.referral_link == referral.referral_link
                    )
                )
        )
        referrer = referrer.scalars().first()

        if (referrer):
            await self.db_session.delete(referrer)
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Referral with id {referrer_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST 

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Referral entity with id {referrer_id} has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting Referral entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def get_all_referrals(self):
        referrals = await self.db_session.execute(select(Referral))
        referrals = referrals.scalars().all()
        return referrals
    
    async def get_all_referrals_by_link(self, referral_link: str):
        referrals = await self.db_session.execute(select(Referral).where(
                Referral.referral_link == referral_link
            )
        )
        referrals = referrals.scalars().all()
        return referrals
    
    async def update_status(self, referrer_id: int) -> Union[
        DBTransactionStatus.NOT_EXIST, 
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.ALREADY_EXIST,
        DBTransactionStatus.SUCCESS
    ]:
        result = await self.db_session.execute(select(Referral).where(Referral.chat_id == referrer_id))
        result = result.scalars().first()
        if (result):
            if(result.got_bonus):
                logger.log(
                    level=LogLevel.WARNING,
                    message=f"A Referral with id {referrer_id} has already got his bonus for using a referral_link"
                )
                return DBTransactionStatus.ALREADY_EXIST
            else:
                result.got_bonus = True
                try:
                    await self.db_session.commit()
                    logger.log(
                        level=LogLevel.INFO,
                        message=f"Referral entity with id {referrer_id} status has been successfully updated"
                    )
                    return DBTransactionStatus.SUCCESS
                except Exception as e:
                    await self.db_session.rollback()
                    logger.log(
                        level=LogLevel.ERROR,
                        message=f"An error occurred while updating status of the Referral entity with id {referrer_id}: {e}"
                    )
                    return DBTransactionStatus.ROLLBACK

        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Referral with id {referrer_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def get_status(self, referrer_id: int) -> Union[bool, DBTransactionStatus.NOT_EXIST]:
        result = await self.db_session.execute(select(Referral).where(Referral.chat_id == referrer_id))
        result = result.scalars().first()
        if (result):
            return result.got_bonus
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Referral with id {referrer_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def get_referrer(self, referrer_id: int) -> Union[Referral, DBTransactionStatus.NOT_EXIST]:
        result = await self.db_session.execute(select(Referral).where(Referral.chat_id == referrer_id))
        result = result.scalars().first()
        if (result):
            return result
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Referral with id {referrer_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

# async def referral_test():
#     async with async_session() as session:
#         rd = ReferralDAL(session)
#         chat_id1 = 1713121214
#         chat_id2 = 54964685
#         chat_id3 = 1314577900
#         result = await rd.create_referral(
#             referral_id=chat_id1,
#             referrer_id=chat_id2
#         )
#         print(result)

# if __name__ == "__main__":
#     asyncio.run(referral_test())