from BackendApp.API.acquiring.schemas import *
from BackendApp.Database.Models.client_model import Client


def parse_client_into_format(client: Client):
    return ClientForReturn(
        chat_id=client.chat_id,
        iiko_id=client.iiko_id,
        username=client.username,
        first_name=client.first_name,
        last_name=client.last_name,
        spent_amount=client.spent_amount,
        qr_code_paht=client.qr_code_path,
    )
