from BackendApp.API.referrals.schemas import *
from BackendApp.Database.Models.client_model import Client
from BackendApp.Database.Models.referrals_model import Referral

def parse_referral_into_format(referral: Referral):
    return ReferralForReturn(
        chat_id=referral.chat_id,
        referral_link=referral.referral_link,
        got_bonus=referral.got_bonus
    )