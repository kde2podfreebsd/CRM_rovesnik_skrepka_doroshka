from BackendApp.API.client.schemas import *
from BackendApp.Database.Models.client_model import Client


def parse_client_into_format(client: Client, balance: float, loyalty_info: list):
    return ClientForReturn(
        chat_id=client.chat_id,
        iiko_id=client.iiko_id,
        iiko_card=client.iiko_card,
        username=client.username,
        first_name=client.first_name,
        last_name=client.last_name,
        phone=client.phone,
        spent_amount=client.spent_amount,
        qr_code_path=client.qr_code_path,
        referral_link=client.referral_link,
        change_reservation=client.change_reservation,
        reserve_table=client.reserve_table,
        got_review_award=client.got_review_award,
        got_yandex_maps_award=client.got_yandex_maps_award,
        balance=balance,
        loyalty_info=loyalty_info
    )

def parse_client_chat_id_and_username(client: Client):
    return ChatIdAndUsernameForReturn(
        chat_id=client.chat_id,
        username=client.username
    )
