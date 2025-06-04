from BackendApp.Database.DAL.referrals_dal import ReferralDAL
from BackendApp.Database.Models.referrals_model import Referral
from BackendApp.Database.session import async_session, DBTransactionStatus

from typing import Union
import asyncio

class ReferralMiddleware:

    @staticmethod
    async def create_referral(
            referral_id: int, 
            referrer_id: int 
    ) -> Union[
        DBTransactionStatus.SUCCESS, 
        DBTransactionStatus.ROLLBACK, 
        DBTransactionStatus.ALREADY_EXIST,
        DBTransactionStatus.NOT_EXIST
    ]:
        async with async_session() as session:
            rd = ReferralDAL(session)
            result = await rd.create_referral(
                referral_id=referral_id,
                referrer_id=referrer_id
            )
            return result
    
    @staticmethod
    async def delete_referral(
            referral_id: int,
            referrer_id: int 
    ) -> Union[
        DBTransactionStatus.SUCCESS, 
        DBTransactionStatus.NOT_EXIST
    ]: 
        async with async_session() as session:
            rd = ReferralDAL(session)
            result = await rd.delete_referral(
                referral_id=referral_id,
                referrer_id=referrer_id
            )
            return result
    
    @staticmethod
    async def delete_referral(
            referral_id: int,
            referrer_id: int 
    ) -> Union[
        DBTransactionStatus.SUCCESS, 
        DBTransactionStatus.NOT_EXIST
    ]: 
        async with async_session() as session:
            rd = ReferralDAL(session)
            result = await rd.get(
                referral_id=referral_id,
                referrer_id=referrer_id
            )
            return result
    
    @staticmethod
    async def get_all_referrals() -> list[Referral]:
        async with async_session() as session:
            rd = ReferralDAL(session)
            result = await rd.get_all_referrals()
            return result
    
    @staticmethod
    async def get_all_referrals_by_link(referral_link: str) -> list[Referral]:
        async with async_session() as session:
            rd = ReferralDAL(session)
            result = await rd.get_all_referrals_by_link(referral_link=referral_link)
            return result

    @staticmethod
    async def get_status(referrer_id: int) -> Union[bool, DBTransactionStatus.NOT_EXIST]:
        async with async_session() as session:
            rd = ReferralDAL(session)
            result = await rd.get_status(referrer_id=referrer_id)
            return result
    
    @staticmethod
    async def update_status(referrer_id: int) -> Union[
        DBTransactionStatus.NOT_EXIST, 
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.ALREADY_EXIST,
        DBTransactionStatus.SUCCESS
    ]:
        async with async_session() as session:
            rd = ReferralDAL(session)
            result = await rd.update_status(referrer_id=referrer_id)
            return result
    
    @staticmethod
    async def get_referral(referrer_id: int) -> Union[Referral, DBTransactionStatus.NOT_EXIST]:
        async with async_session() as session:
            rd = ReferralDAL(session)
            result = await rd.get_referrer(referrer_id=referrer_id)
            return result