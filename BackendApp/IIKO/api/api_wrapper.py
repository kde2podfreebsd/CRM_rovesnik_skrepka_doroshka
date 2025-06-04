import asyncio
import pprint
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from BackendApp.IIKO.api.core import TokenException
from BackendApp.IIKO.api.reserves import Reserves
from BackendApp.IIKO.classes import *

"""
    TODO: 
        - organization_id в каждый класс, как поле.
"""


api_login = "a061da2d-0f0"
organization_id = "9cb23610-e67b-4b76-af30-75bd8a1785f4"


async def get_tables(bar_name: str) -> List[FrontendTableInfo]:
    # Тут сначало надо выбрать класс, от которого будем всё вызывать.
    # В каждом классе будет свой organization_id
    client = await Reserves.create(api_login)

    try:

        terminal_groups_info = await client.get__groups_with_booking([organization_id])
        terminal_group_ids = [
            terminal_group_id["id"]
            for terminal_group_id in terminal_groups_info["terminalGroups"][0]["items"]
        ]
        # Здесь 0-й индекс, т.к. мы будем делать запрос только по одной организации, но будет возвращен список. Мы просто обратимся к первой и единственной организации в этом списке

        restaurant_section_info = await client.get_restaurant_sections_with_booking(
            terminal_group_ids
        )
        tables = []
        section_ids = []
        for section in restaurant_section_info[1]:
            section_ids.append(str(section.id))
            for table in section.tables:
                tables.append(
                    FrontendTableInfo(
                        organization_id=organization_id,
                        section_name=section.name,
                        table_id=table.id,
                        table_name=table.name,
                        capacity=table.seatingCapacity,
                        is_deleted=table.isDeleted,
                        table_status="free",
                    )
                )
        # pprint.pprint(tables)

        # print(section_ids)

        current_datetime = datetime.now()
        time_delta = timedelta(hours=2)
        time_after_2h = current_datetime + time_delta
        print(
            current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
            time_after_2h.strftime("%Y-%m-%d %H:%M:%S.%f"),
        )

        data = await client.get_reservations_for_sections(section_ids, "2024-02-29 19:00:00.000")
        pprint.pprint(data)

    except TokenException as e:
        print("Error:", e)

    await client.close_session()


if __name__ == "__main__":

    asyncio.run(get_tables("rovesnik"))
