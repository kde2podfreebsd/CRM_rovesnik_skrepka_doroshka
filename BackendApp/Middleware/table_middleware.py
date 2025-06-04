from BackendApp.Database.Models.table_model import Table
from BackendApp.Database.Models.reservation_status import ReservationStatus
from BackendApp.Database.DAL.event_dal import EventDAL
from BackendApp.Database.DAL.table_dal import TableDAL
from BackendApp.Database.DAL.reservation_dal import ReservationDAL
from BackendApp.Database.session import DBTransactionStatus, async_session
import asyncio
from uuid import uuid4
from datetime import datetime, timedelta

class TableMiddleware:
    @staticmethod
    async def create(
        bar_id: int,
        storey: int,
        table_id: int,
        table_uuid: str,
        terminal_group_uuid: str,
        capacity: int,
        is_pool: bool = None,
        is_bowling: bool = None,
        block_start: datetime = None,
        block_end: datetime = None
    ):
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.create(
                bar_id=bar_id,
                storey=storey,
                table_id=table_id,
                table_uuid=table_uuid,
                terminal_group_uuid=terminal_group_uuid,
                capacity=capacity,
                is_pool=is_pool,
                is_bowling=is_bowling,
                block_start=block_start,
                block_end=block_end
            )
            return result
    
    @staticmethod
    async def update(
        table_uuid: str,
        table_id: int = None,
        bar_id: int = None,
        storey: int = None,
        reserved: bool = None,
        terminal_group_uuid: str = None,
        capacity: int = None,
        is_pool: bool = None,
        is_bowling: bool = None,
        block_start: datetime = None,
        block_end: datetime = None
    ):
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.update(
                table_uuid=table_uuid,
                table_id=table_id,
                bar_id=bar_id,
                storey=storey,
                reserved=reserved,
                terminal_group_uuid=terminal_group_uuid,
                capacity=capacity,
                is_pool=is_pool,
                is_bowling=is_bowling,
                block_start=block_start,
                block_end=block_end
            )
            return result
    
    @staticmethod
    async def delete(table_uuid: str):
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.delete(
                table_uuid=table_uuid
            )
            return result
    
    @staticmethod
    async def get_all():
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.get_all()
            return result

    @staticmethod
    async def get_by_id(table_id: int):
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.get_by_id(
                table_id=table_id
            )
            return result
    
    @staticmethod
    async def get_entity_id(
        bar_id: int,
        storey: int,
        table_id: int,
        table_uuid: str,
        terminal_group_uuid: str,
        capacity: int
    ):
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.get_entity_id(
                bar_id=bar_id,
                storey=storey,
                table_id=table_id,
                table_uuid=table_uuid,
                terminal_group_uuid=terminal_group_uuid,
                capacity=capacity
            )
            return result
    
    @staticmethod
    async def get_by_storey(storey: int, bar_id: int):
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.get_by_storey(storey=storey, bar_id=bar_id)
            return result 
    
    @staticmethod
    async def change_status_by_storey(storey: int, bar_id: int):
        async with async_session() as session:
            td = TableDAL(session)
            tables = await td.get_by_storey(storey=storey, bar_id=bar_id)
            data = [(entity.table_uuid, entity.reserved) for entity in tables]
            for piece in data:
                result = await td.update(
                    table_uuid=piece[0],
                    reserved=not(piece[1])
                )
                if (result != DBTransactionStatus.SUCCESS):
                    return result
                
            return result 
    
    @staticmethod
    async def get_by_terminal_group(terminal_group_uuid: str):
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.get_by_terminal_group(terminal_group_uuid=terminal_group_uuid)
            return result
    
    @staticmethod
    async def get_by_uuid(table_uuid: str):
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.get_by_uuid(table_uuid=table_uuid)
            return result
    
    @staticmethod
    async def get_available_tables_by_capacity_and_time(
        bar_id: int,
        datetime: datetime, 
        capacity: int
    ):
        async with async_session() as session:
            td = TableDAL(session)
            rd = ReservationDAL(session)
            ed = EventDAL(session)

            events = await ed.get_all_events(bar_id=bar_id)

            for event in events:
                if (
                    (event.datetime < datetime) and
                    (event.end_datetime > datetime)
                ):
                    return event

            available_tables = []
            tables = await td.get_by_capacity(capacity=capacity, bar_id=bar_id)
            if (tables == DBTransactionStatus.NOT_EXIST):
                return tables
            
            for table in tables:
                reservations = await rd.get_by_table_uuid(table_uuid=table.table_uuid)

                if (table.reserved):
                    continue

                if (not reservations):
                    available_tables.append(table)
                    continue

                is_avalaible = True
                for reservation in reservations:
                    # potential bug
                    if (
                        (reservation.status == ReservationStatus.RESERVED or 
                         reservation.status == ReservationStatus.RESERVED_AND_NOTIFIED) and
                        ((reservation.reservation_start <= datetime and 
                         reservation.reservation_start + timedelta(hours=2) >= datetime) or
                         (reservation.reservation_start <= datetime + timedelta(hours=2) and 
                         reservation.reservation_start + timedelta(hours=2, minutes=30) >= datetime + timedelta(hours=2))
                        )
                    ):
                        is_avalaible = False
                        break
                
                if (is_avalaible):
                    available_tables.append(table)     
            
            return available_tables
    
    async def check_availability(table_uuid: str, datetime: datetime):
        async with async_session() as session:
            td = TableDAL(session)
            rd = ReservationDAL(session)
            ed = EventDAL(session)
            
            table_entity = await td.get_by_uuid(table_uuid=table_uuid)
            events = await ed.get_all_events(bar_id=table_entity.bar_id)

            for event in events:
                if (
                    (event.datetime < datetime) and
                    (event.end_datetime > datetime)
                ):
                    return event
            
            reservations = await rd.get_by_table_uuid(table_uuid=table_uuid)

            table_entity = await td.get_by_uuid(table_uuid=table_uuid)

            if (table_entity.reserved):
                return False

            if (not reservations):
                return True

            for reservation in reservations:
                # potential bug
                if (
                    (reservation.status == ReservationStatus.RESERVED or 
                        reservation.status == ReservationStatus.RESERVED_AND_NOTIFIED) and
                    ((reservation.reservation_start <= datetime and 
                        reservation.reservation_start + timedelta(hours=2) >= datetime) or
                        (reservation.reservation_start <= datetime + timedelta(hours=2) and 
                        reservation.reservation_start + timedelta(hours=2, minutes=30) >= datetime + timedelta(hours=2))
                    )
                ):
                    return False
            
            return True
    
    async def get_bowling():
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.get_bowling()
            return result
    
    async def get_pool():
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.get_pool()
            return result
    
    async def nullify_block_time(table_uuid: str):
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.nullify_block_time(table_uuid=table_uuid)
            return result
    
    async def get_by_storey_and_bar_id(bar_id: int, storey: int):
        async with async_session() as session:
            td = TableDAL(session)
            result = await td.get_by_storey_and_bar_id(
                bar_id=bar_id,
                storey=storey
            )
            return result

if __name__ == "__main__":
    async def main():
        result = await TableMiddleware.create(
            bar_id=1,
            storey=1,
            table_id=1,
            table_uuid=str(uuid4()),
            terminal_group_uuid=str(uuid4()),
            capacity=4
        )

    asyncio.run(main())
