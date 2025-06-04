from BackendApp.API.partner_gift.schemas import *
from BackendApp.Database.Models.partner_gift_model import PartnerGift


def parse_promocode_into_format(partner_gift: PartnerGift):
    return PartnerGiftForReturn(
        id=partner_gift.id,
        short_name=partner_gift.short_name,
        promotion_text=partner_gift.promotion_text,
        got_gift=partner_gift.got_gift,
        bar_id=partner_gift.bar_id
    )