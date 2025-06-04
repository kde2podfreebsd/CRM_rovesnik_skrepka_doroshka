import asyncio
from pprint import pprint

from BackendApp.Database.DAL.table_dal import TableDAL
from BackendApp.Database.Models.table_model import Table
from BackendApp.Database.session import DBTransactionStatus, async_session
from BackendApp.IIKO.api.reserves import Reserves
from BackendApp.Middleware.client_middleware import API_LOGIN

rovesnik_test_id = "9cb23610-e67b-4b76-af30-75bd8a1785f4"
rovesnik_id = "1ea3ff3c-b31c-45dc-8964-224fb096e578"
dorozhka_id = "5d6ce4a7-9f8c-4bc6-a513-da69b0c939fc"
skrepka_id = "647c7cf3-b841-45c9-8e07-35509675ec9b"


async def export_tables():
    rovesnik_terminal_id = "c4923c8b-1747-b52f-016d-f7c0c79c00cd"
    table_capacity = {
        1: {
            2: 8,
            4: 2,
            5: 2,
            6: 4,
            7: 4,
            8: 4,
            9: 4,
            10: 4,
            11: 4,
            14: 4,
            15: 4,
            16: 4,
            17: 4,
        },
        2: {
            1: 5,
            2: 2,
            3: 2,
            4: 2,
            5: 5,
            6: 8,
            8: 4,
            9: 4,
            10: 4,
            11: 4,
            12: 4,
            13: 4,
            14: 4,
            15: 4,
            16: 4,
            17: 4,
            18: 4,
            19: 4,
            20: 4,
        },
        3: {
            1: 5,
            3: 2,
            4: 2,
            5: 5,
            6: 5,
            7: 2,
            8: 2,
            10: 2,
        },
    }
    async with async_session() as session:
        table_dal = TableDAL(session)
        client_iiko = await Reserves.create(API_LOGIN, "Rovesnik")
        # print(await client_iiko.get_terminal_groups_with_booking([rovesnik_test_id]))
        data = await client_iiko.get_restaurant_sections_with_booking(
            [rovesnik_terminal_id]
        )
        print(data)
        for idx, section in enumerate(data[1][:3]):
            for table in section.tables:
                if table.number in table_capacity[idx + 1].keys():
                    if await table_dal.get_by_uuid(str(table.id)):
                        await table_dal.update(
                            table_id=table.number,
                            table_uuid=str(table.id),
                            terminal_group_uuid=str(section.terminalGroupId),
                            capacity=table_capacity[idx + 1][table.number],
                            bar_id=1,
                            storey=idx + 1,
                        )
                    else:
                        await table_dal.create(
                            table_id=table.number,
                            table_uuid=str(table.id),
                            terminal_group_uuid=str(section.terminalGroupId),
                            capacity=table_capacity[idx + 1][table.number],
                            bar_id=1,
                            storey=idx + 1,
                        )
        return "Таблицы экспортированы."
    
async def export_dorozhka_tables():
    dorozhka_terminal_id = "89464c04-d204-4c86-a819-65dda6405b1f"
    async with async_session() as session:
        api_login = "49c34288-3b94-4713-977a-f99d173ee6aa"
        table_dal = TableDAL(session)
        client_iiko = await Reserves.create(api_login, "Rovesnik")
        data = await client_iiko.get_restaurant_sections_with_booking([dorozhka_terminal_id])
        for section in data[1]:
            if str(section.id) == "590a4b16-7c5e-43da-8cd3-04a799cdd4ec":
                for table in section.tables:
                    if await table_dal.get_by_uuid(str(table.id)):
                        await table_dal.update(table_id=table.number, table_uuid=str(table.id), terminal_group_uuid=str(section.terminalGroupId), is_bowling=True, capacity=8, storey=1, bar_id=3)
                    else:
                        await table_dal.create(table_id=table.number, table_uuid=str(table.id), terminal_group_uuid=str(section.terminalGroupId), is_bowling=True, capacity=8, storey=1, bar_id=3)
            if str(section.id) == "644ac387-70ea-4d2a-b085-6af03050b972":
                for table in section.tables:
                    if table.number not in [7, 8, 9, 23, 25, 26, 27, 29, 30]:
                        if await table_dal.get_by_uuid(str(table.id)):
                            await table_dal.update(table_id=table.number, table_uuid=str(table.id), terminal_group_uuid=str(section.terminalGroupId), capacity=4, storey=1, bar_id=3)
                        else:
                            await table_dal.create(table_id=table.number, table_uuid=str(table.id), terminal_group_uuid=str(section.terminalGroupId), capacity=4, storey=1, bar_id=3)
                    if table.number in [25, 26, 27]:
                        if await table_dal.get_by_uuid(str(table.id)):
                            await table_dal.update(table_id=table.number, table_uuid=str(table.id), terminal_group_uuid=str(section.terminalGroupId), capacity=4, is_pool=True, storey=1, bar_id=3)
                        else:
                            await table_dal.create(table_id=table.number, table_uuid=str(table.id), terminal_group_uuid=str(section.terminalGroupId), capacity=4, is_pool=True, storey=1, bar_id=3)
    print("Перенос столов дорожки завершен")
        
async def export_skrepka_tables():
    async with async_session() as session:
        hall_capacity = {1: 4, 2: 4, 3: 4, 4: 5, 5: 5, 6: 2, 7: 2, 8: 2, 9: 2, 10: 4, 11: 2, 12: 2}
        veranda_capacity = {1: 4, 2: 6, 3: 4, 4: 4, 5: 4, 6: 6}
        api_login = "49c34288-3b94-4713-977a-f99d173ee6aa"
        table_dal = TableDAL(session)
        client_iiko = await Reserves.create(api_login, "Rovesnik")
        skrepka_terminal_id = "992525d5-052c-4159-852c-19690f13b5d2"
        data = await client_iiko.get_restaurant_sections_with_booking([skrepka_terminal_id])
        for section in data[1]:
            if str(section.id) == "804faeae-d581-404d-bdca-3cf8177a51b6": # Зал
                for table in section.tables:
                    if table.number in hall_capacity.keys():
                        if await table_dal.get_by_uuid(str(table.id)):
                            await table_dal.update(table_id=table.number, table_uuid=str(table.id), terminal_group_uuid=str(section.terminalGroupId), capacity=hall_capacity[table.number], storey=1, bar_id=2)
                        else:
                            await table_dal.create(table_id=table.number, table_uuid=str(table.id), terminal_group_uuid=str(section.terminalGroupId), capacity=hall_capacity[table.number], storey=1, bar_id=2)
            if str(section.id) == "9577af6a-c417-4df7-b4cb-6df4bc823822": # Веранда
                for table in section.tables:
                    if table.number in veranda_capacity.keys():
                        if await table_dal.get_by_uuid(str(table.id)):
                            await table_dal.update(table_id=table.number, table_uuid=str(table.id), terminal_group_uuid=str(section.terminalGroupId), capacity=veranda_capacity[table.number], storey=1, bar_id=2)
                        else:
                            await table_dal.create(table_id=table.number, table_uuid=str(table.id), terminal_group_uuid=str(section.terminalGroupId), capacity=veranda_capacity[table.number], storey=1, bar_id=2)
        print("Перенос столов скрепки завершен")

if __name__ == "__main__":
    async def main():
        await export_tables()
        await export_skrepka_tables()
        await export_dorozhka_tables()
    asyncio.run(main())