from BackendApp.Database.DAL.affilate_promotions_dal import AffilatePromotionsDAL
from BackendApp.Database.Models.promocode_types import _PromocodeType
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Middleware.subscription_middleware import SubscriptionMiddleware
from BackendApp.Database.session import async_session
from BackendApp.Middleware.classes import AffilatePromotion
from typing import List, Optional, Tuple

from telebot.types import ChatMemberMember, ChatMemberLeft
import asyncio
import pprint

async def create_promotion(
    channel_link: str,
    promotion_text: str,
    promocode_type: _PromocodeType,
    short_name: str,
    bar_id: int
) -> None:
    async with async_session() as session:
        promo_dal = AffilatePromotionsDAL(session)
        
        promotion_create_status = await promo_dal.create(
            channel_link=channel_link,
            promotion_text=promotion_text,
            promocode_type=promocode_type,
            short_name=short_name,
            bar_id=bar_id
        )
        return promotion_create_status
        
        
async def get_all_promotions() -> List[AffilatePromotion]:
    async with async_session() as session:
        promo_dal = AffilatePromotionsDAL(session)
        
        res = [AffilatePromotion(
            channel_link=promo.channel_link,
            promotion_text=promo.promotion_text,
            promocode_type=promo.promocode_type,
            sub_chat_id=promo.sub_chat_id,
            id=promo.id,
            short_name=promo.short_name,
            bar_id=promo.bar_id
        )
        for promo in await promo_dal.get_all()]
        
        return res

async def get_promotion_by_id(
    _id: int
) -> AffilatePromotion:
    
    async with async_session() as session:
        promo_dal = AffilatePromotionsDAL(session)
        
        obj = await promo_dal.get_by_id(promotion_id=_id)
        
        return AffilatePromotion(
            id=obj.id,
            channel_link=obj.channel_link,
            promotion_text=obj.promotion_text,
            promocode_type=obj.promocode_type,
            short_name=obj.short_name,
            sub_chat_id=obj.sub_chat_id,
            bar_id=obj.bar_id
        )
        
        
async def get_promotions_by_channel_link(
    channel_link: str
) -> List[AffilatePromotion]:
    
    async with async_session() as session:
        promo_dal = AffilatePromotionsDAL(session)
                
        res = [AffilatePromotion(
            channel_link=promo.channel_link,
            promotion_text=promo.promotion_text,
            promocode_type=promo.promocode_type,
            short_name=promo.short_name,
            sub_chat_id=promo.sub_chat_id,
            bar_id=promo.bar_id
        )
        for promo in await promo_dal.get_by_channel_link(channel_link=channel_link)]
        
        return res
    
    
async def delete_promotion(
    _id: int
) -> None:
    async with async_session() as session:
        promo_dal = AffilatePromotionsDAL(session)
        
        promotion_delete_status = await promo_dal.delete(promotion_id=_id)
        return promotion_delete_status
        
        
async def update_promotion(
    id: int,
    channel_link: Optional[str] = None,
    promotion_text: Optional[str] = None,
    promocode_type: Optional[_PromocodeType] = None,
    short_name: Optional[str] = None,
    sub_chat_id: Optional[List[str]] = None,
    bar_id: Optional[int] = None
) -> None:
    async with async_session() as session:
        promo_dal = AffilatePromotionsDAL(session)
        
        promotion_update_status = await promo_dal.update(
            promotion_id=id,
            channel_link=channel_link,
            promotion_text=promotion_text,
            promocode_type=promocode_type,
            short_name=short_name,
            sub_chat_id=sub_chat_id,
            bar_id=bar_id
        )
        return promotion_update_status
        

async def get_promo_short_info() -> List[Tuple[str, int]]:
    promotions = await get_all_promotions()
    return [(promo.short_name, promo.id) for promo in promotions]

async def get_promo_short_info_by_bar_id(bar_id: int) -> List[Tuple[str, int]]:
    async with async_session() as session:
        apd = AffilatePromotionsDAL(session)
        promotions = await apd.get_by_bar_id(bar_id=bar_id)
        return [(promo.short_name, promo.id) for promo in promotions]

async def get_entity_id(
    channel_link: str,
    promotion_text: str,
    promocode_type: _PromocodeType,
    short_name: str,
    bar_id: int
):
    async with async_session() as session:
        dal = AffilatePromotionsDAL(session)
        result = await dal.get_entity_id(
            channel_link=channel_link,
            promotion_text=promotion_text,
            promocode_type=promocode_type,
            short_name=short_name,
            bar_id=bar_id
        )
        return result



# if __name__ == "__main__":
#     async def test():
        # 😁
        # new_promo = AffilatePromotion("@postypashki_old_chat", "aaaaaTERC1asdfasdfasdfasdfasdfasdf", "крутая награда", short_name="555") 
        
        # await create_promotion(new_promo)
        # pprint.pprint(await get_all_promotions())
        # pprint.pprint(await get_promotion_by_id(3))
        # pprint.pprint(await get_promotions_by_channel_link("some_link"))
        # await delete_promotion(7)
        # await update_promotion(8, channel_link="some_link")

        # res = await SubscriptionChecker.check(username="@FEGchat", chat_id=1713121214)
        # if (isinstance(res, ChatMemberLeft)):
        #     print("unsub")
        # if (isinstance(res, ChatMemberMember)):
        #     print("sub")
    #     res = await SubscriptionChecker.envoke()

    # asyncio.run(test())

    
