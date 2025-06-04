from BackendApp.API.promocodes.schemas import *
from BackendApp.Database.Models.promocode_model import Promocode


def parse_promocode_into_format(promocode: Promocode):
    return Promocode(
        client_chat_id = promocode.client_chat_id,
        type = promocode.type,
        name = promocode.name,
        operational_info = promocode.operational_info,
        description = promocode.description,
        number = promocode.number,
        end_time = promocode.end_time,
        is_activated = promocode.is_activated,
        weight = promocode.weight
    )
