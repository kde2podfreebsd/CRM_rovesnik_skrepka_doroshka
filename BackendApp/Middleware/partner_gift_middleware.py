from BackendApp.Database.DAL.partner_gift_dal import PartnerGiftDAL
from BackendApp.Database.Models.partner_gift_model import PartnerGift
from BackendApp.Database.session import async_session

class PartnerGiftMiddleware:

    @staticmethod
    async def create(
        short_name: str, 
        promotion_text: str,
        bar_id: int
    ):
        async with async_session() as session:
            pgd = PartnerGiftDAL(session)
            result = await pgd.create(
                short_name=short_name,
                promotion_text=promotion_text,
                bar_id=bar_id
            )
            return result
    
    @staticmethod
    async def update(
        partner_gift_id: int,
        short_name: str = None, 
        promotion_text: str = None,
        got_gift: list = None,
        bar_id: int = None
    ):
        async with async_session() as session:
            pgd = PartnerGiftDAL(session)
            result = await pgd.update(
                partner_gift_id=partner_gift_id,
                short_name=short_name,
                promotion_text=promotion_text,
                got_gift=got_gift,
                bar_id=bar_id
            )
            return result
    
    @staticmethod
    async def delete(partner_gift_id: int):
        async with async_session() as session:
            pgd = PartnerGiftDAL(session)
            result = await pgd.delete(
                partner_gift_id=partner_gift_id
            )
            return result
    
    @staticmethod
    async def get_all():
        async with async_session() as session:
            pgd = PartnerGiftDAL(session)
            result = await pgd.get_all()
            return result
    
    @staticmethod
    async def get_by_id(partner_gift_id: int):
        async with async_session() as session:
            pgd = PartnerGiftDAL(session)
            result = await pgd.get_by_id(partner_gift_id=partner_gift_id)
            return result
    
    @staticmethod
    async def get_by_bar_id(bar_id: int):
        async with async_session() as session:
            pgd = PartnerGiftDAL(session)
            result = await pgd.get_by_bar_id(bar_id=bar_id)
            return result

    @staticmethod
    async def get_entity_id(
        short_name: str, 
        promotion_text: str,
        bar_id: int
    ):
        async with async_session() as session:
            pgd = PartnerGiftDAL(session)
            result = await pgd.get_entity_id(
                short_name=short_name,
                promotion_text=promotion_text,
                bar_id=bar_id
            )
            return result