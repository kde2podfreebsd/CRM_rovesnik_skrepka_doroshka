from typing import List
from BackendApp.API.affilate_promotions.scheme import PromotionResponse
from BackendApp.Database.Models.affilate_promotions_model import AffilatePromotions

def parse_promotion_into_format(promotion: AffilatePromotions) -> PromotionResponse:
    return PromotionResponse(
        id=promotion.id,
        channel_link=promotion.channel_link,
        promotion_text=promotion.promotion_text,
        promocode_type=promotion.promocode_type,
        short_name=promotion.short_name,
        sub_chat_id=promotion.sub_chat_id,
        bar_id=promotion.bar_id
    )
    
def parse_promotions_into_format(promotions: List[AffilatePromotions]):
    return [parse_promotion_into_format(promotion) for promotion in promotions]

