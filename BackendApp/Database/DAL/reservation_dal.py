from sqlalchemy import and_, or_
from sqlalchemy.future import select
from BackendApp.Logger import logger, LogLevel
from BackendApp.Database.Models.reservation_model import Reservation
from BackendApp.Database.Models.reservation_status import ReservationStatus
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, List, Optional
import asyncio

from datetime import datetime, timedelta
from uuid import uuid4

from BackendApp.Database.session import async_session

class ReservationDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create(
        self,
        client_chat_id: int,
        order_uuid: str,
        table_uuid: str,
        reservation_start: datetime,
        reserve_id: str,
        deposit: float = None
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST
    ]:
        existing_reservation = await self.db_session.execute(select(Reservation).where(and_(
            Reservation.client_chat_id == client_chat_id,
            Reservation.order_uuid == order_uuid,
            Reservation.table_uuid == table_uuid,
            Reservation.reservation_start == reservation_start,
            Reservation.deposit == deposit,
            Reservation.status != ReservationStatus.CANCELLED
        )))
        existing_reservation = existing_reservation.scalars().first()
        if (existing_reservation):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Reservation with the given parameters: {client_chat_id, order_uuid, table_uuid, reservation_start, deposit}, - already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST
        
        new_reservation = Reservation(
            client_chat_id=client_chat_id,
            order_uuid=order_uuid,
            table_uuid=table_uuid,
            reservation_start=reservation_start,
            reserve_id=reserve_id,
            status=ReservationStatus.RESERVED,
            deposit=deposit
        )
        try:
            self.db_session.add(new_reservation)
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Reservation entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Reservation entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def update(
        self,
        reservation_id: int,
        client_chat_id: int = None,
        table_uuid: str = None,
        reservation_start: datetime = None,
        deposit: float = None,
        status: ReservationStatus = None
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        reservation = await self.db_session.execute(select(Reservation).where(Reservation.id == reservation_id))
        reservation = reservation.scalars().first()

        if (not reservation):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Reservation with id {reservation_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if (client_chat_id is not None):
            reservation.client_chat_id = client_chat_id
        if (table_uuid is not None):
            reservation.table_uuid = table_uuid
        if (reservation_start is not None):
            reservation.reservation_start = reservation_start
        if (deposit is not None):
            reservation.deposit = deposit
        if (status is not None):
            reservation.status = status

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Reservation entity with id {reservation_id} has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating Reservation entity with id {reservation_id}: {e}"
            )
            return DBTransactionStatus.ROLLBACK
        
    async def delete(self, reservation_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        reservation = await self.db_session.execute(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        reservation = reservation.scalars().first()

        if (not reservation):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Reservation with id {reservation_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(reservation)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Reservation entity with id {reservation_id} has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting Reservation entity with id {reservation_id}: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def get_all(self) -> Optional[List[Reservation]]:
        result = await self.db_session.execute(select(Reservation))
        return result.scalars().all()
    
    async def get_all_by_chat_id(self, chat_id: int) -> Optional[List[Reservation]]:
        result = await self.db_session.execute(select(Reservation).where(Reservation.client_chat_id == chat_id))
        return result.scalars().all()

    async def get_by_id(self, reservation_id: int) -> Reservation:
        result = await self.db_session.execute(select(Reservation).where(Reservation.id == reservation_id))
        return result.scalars().first()
    
    async def get_by_reserve_id(self, reserve_id: str) -> Reservation:
        result = await self.db_session.execute(select(Reservation).where(Reservation.reserve_id == reserve_id))
        return result.scalars().first()
    
    async def get_by_order_uuid(self, order_uuid: str) -> Reservation:
        result = await self.db_session.execute(select(Reservation).where(Reservation.order_uuid == order_uuid))
        return result.scalars().first()
    
    async def get_by_table_uuid(self, table_uuid: str) -> Optional[List[Reservation]]:
        result = await self.db_session.execute(select(Reservation).where(and_(
            Reservation.table_uuid == table_uuid
        )))
        return result.scalars().all()
    
    async def get_by_reserved_status(self) -> Optional[List[Reservation]]:
        result = await self.db_session.execute(select(Reservation).where(Reservation.status == ReservationStatus.RESERVED))
        return result.scalars().all()
    
    async def get_all_reserved_statuses(self) -> Optional[List[Reservation]]:
        result = await self.db_session.execute(select(Reservation).where(or_(
            Reservation.status == ReservationStatus.RESERVED,
            Reservation.status == ReservationStatus.RESERVED_AND_NOTIFIED
        )))
        return result.scalars().all()

    async def get_all_reserved_statuses_by_chat_id(self, chat_id: int) -> Optional[List[Reservation]]:
        result = await self.db_session.execute(select(Reservation).where(and_(
            or_(Reservation.status == ReservationStatus.RESERVED,
            Reservation.status == ReservationStatus.RESERVED_AND_NOTIFIED),
            Reservation.client_chat_id == chat_id
        )))
        return result.scalars().all()
    
    async def get_all_expired_and_cancelled_by_chat_id(self, chat_id: int) -> Optional[List[Reservation]]:
        result = await self.db_session.execute(select(Reservation).where(and_(
            or_(Reservation.status == ReservationStatus.EXPIRED,
            Reservation.status == ReservationStatus.CANCELLED),
            Reservation.client_chat_id == chat_id
        )))
        return result.scalars().all()
    
    async def get_by_order_uuid(self, order_uuid: str) -> Optional[List[Reservation]]:
        result = await self.db_session.execute(select(Reservation).where(
            Reservation.order_uuid == order_uuid
        ))
        return result.scalars().all()

    async def get_entity_id(
        self,
        client_chat_id: int,
        table_uuid: str,
        reservation_start: datetime,
    ):
        result = await self.db_session.execute(select(Reservation).where(and_(
            Reservation.client_chat_id == client_chat_id,
            Reservation.table_uuid == table_uuid,
            Reservation.reservation_start == reservation_start
        )))
        result = result.scalars().first()
        if (result):
            return result.id
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Reservation with the given parameters: {client_chat_id, table_uuid, reservation_start} does not exist in the data base"
            )
            return None

if __name__ == "__main__":
    async def main():
        async with async_session() as session:
            rd = ReservationDAL(session)

            result = await rd.create(
                client_chat_id=1713121214,
                order_uuid=str(uuid4()),
                bar_id=1,
                storey=1,
                table_id=1,
                reservation_start=datetime(2024, 5, 3, 15, 0, 0),
                reserve_id=uuid4()
            )
            print(result)
    asyncio.run(main())
