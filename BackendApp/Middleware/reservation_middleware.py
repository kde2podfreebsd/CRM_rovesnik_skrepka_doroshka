from BackendApp.Database.Models.reservation_model import Reservation
from BackendApp.Database.Models.reservation_status import ReservationStatus
from BackendApp.Database.DAL.reservation_dal import ReservationDAL
from BackendApp.Database.DAL.table_dal import TableDAL
from BackendApp.Database.DAL.client_dal import ClientDAL
from BackendApp.Middleware.table_middleware import TableMiddleware
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Database.session import async_session, DBTransactionStatus

from BackendApp.IIKO.classes import (
    CreatingReservationCustomer, 
    InformationForCreatingReservation
)
from BackendApp.IIKO.api.reserves import *
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from enum import Enum
import os
load_dotenv()

API_LOGIN = os.getenv("API_LOGIN")
LIST_OBJECT_ID = 1
RESERVE_INFO_ID = 0


class ReservationResponse(str, Enum):
    NOT_AVAILABLE = "not_available"
    NO_PERMISSION = "no_permission"
    ERROR = "error"

class ReservationMiddleware:
    @staticmethod
    async def create(
        client_chat_id: int,
        order_uuid: str,
        table_uuid: str,
        reservation_start: datetime,
        deposit: float = None,
        is_updating: bool = False
    ):
        async with async_session() as session:
            rd = ReservationDAL(session)
            td = TableDAL(session)
            cd = ClientDAL(session)
            client = await cd.get_client(chat_id=client_chat_id)

            client_reservations = await rd.get_all_by_chat_id(chat_id=client_chat_id)
            order_uuids = [entity.order_uuid for entity in client_reservations]

            if (
                ((not client.reserve_table) and (order_uuid not in order_uuids)) or 
                (not client.change_reservation and is_updating)
            ):
                return ReservationResponse.NO_PERMISSION    
            
            client_iiko = await Reserves.create(API_LOGIN, "Rovesnik")
            table_info = await td.get_by_uuid(table_uuid=table_uuid)

            if (table_info.reserved):
                return ReservationResponse.NOT_AVAILABLE
            
            reservation_customer = CreatingReservationCustomer(
                id=client.iiko_id,
                name=client.first_name,
                surname=client.last_name,
                gender="NotSpecified",
                type="regular"
            )
            info_for_reservation = InformationForCreatingReservation(
                organizationId=client_iiko.name_id_orgranization["Rovesnik"],
                terminalGroupId=table_info.terminal_group_uuid,
                phone=client.phone,
                tableIds=[table_info.table_uuid],
                estimatedStartTime=reservation_start,
                shouldRemind=True,
                customer=reservation_customer
            )
            try:
                reserve_info = await client_iiko.create_banquet_or_reservation(
                    info=info_for_reservation
                )
            except TokenException as e:
                return ReservationResponse.ERROR
            
            format_string = "%Y-%m-%d %H:%M:%S.%f"
            result = await rd.create(
                client_chat_id=client_chat_id,
                order_uuid=order_uuid,
                table_uuid=table_info.table_uuid,
                reservation_start=datetime.strptime(reservation_start, format_string),
                reserve_id=str(reserve_info[LIST_OBJECT_ID][RESERVE_INFO_ID].id),
                deposit=deposit
            )
            
            # if (result == DBTransactionStatus.SUCCESS):
            #     if (order_uuid not in order_uuids):
            #         await cd.update_reserve_table(chat_id=client_chat_id)
            
            return result

    @staticmethod
    async def cancel(
        reserve_id: str,
        cancel_reason: Literal["ClientNotAppeared", "ClientRefused", "Other"],
        organization_id: str = Reserves.name_id_orgranization["Rovesnik"]
    ):
        async with async_session() as session:
            rd = ReservationDAL(session)
            cd = ClientDAL(session)
            td = TableDAL(session)
            client_iiko = await Reserves.create(API_LOGIN, "Rovesnik")

            try:
                await client_iiko.cancel_reservation(
                    organization_id=organization_id,
                    reserve_id=reserve_id,
                    cancel_reason=cancel_reason
                )
            except TokenException as e:
                return ReservationResponse.ERROR

            reservation = await rd.get_by_reserve_id(reserve_id=reserve_id)
            result = await rd.update(
                reservation_id=reservation.id,
                status=ReservationStatus.CANCELLED
            )
            if (result == DBTransactionStatus.SUCCESS):
                reservation = await rd.get_by_reserve_id(reserve_id=reserve_id)
                chat_id = reservation.client_chat_id
                table_uuid = reservation.table_uuid
                deposit = reservation.deposit

                table_entity = await td.get_by_uuid(table_uuid)
                if (table_entity.is_bowling or table_entity.is_pool):
                    await ClientMiddleware.refill_balance(chat_id=chat_id, amount=deposit)
                
                # client = await cd.get_client(chat_id)
                # if (not client.reserve_table):
                #     await cd.update_reserve_table(chat_id)
            
            return result

    @staticmethod
    async def update(
        reserve_id: str,
        client_chat_id: int = None,
        table_uuid: str = None,
        reservation_start: datetime = None,
        deposit: float = None,
    ):
        async with async_session() as session:
            cd = ClientDAL(session)
            rd = ReservationDAL(session)
            td = TableDAL(session)

            reservation = await rd.get_by_reserve_id(reserve_id=reserve_id)
            client = await cd.get_client(chat_id=reservation.client_chat_id)
            table_info = await td.get_by_uuid(
                table_uuid=(table_uuid if table_uuid else reservation.table_uuid)
            )

            if (table_info.reserved):
                return ReservationResponse.NOT_AVAILABLE
                
            # client has exhausted his daily opportunity to change reservation 
            if (not client.change_reservation):
                return ReservationResponse.NO_PERMISSION

            result = await ReservationMiddleware.cancel(
                reserve_id=reserve_id,
                cancel_reason="Other"
            )
            
            if (result == DBTransactionStatus.SUCCESS):

                format_string = "%Y-%m-%d %H:%M:%S.%f"
                reservation = await rd.get_by_reserve_id(reserve_id=reserve_id)
                result = await ReservationMiddleware.create(
                    client_chat_id=(client_chat_id if client_chat_id else reservation.client_chat_id),
                    order_uuid = reservation.order_uuid,
                    table_uuid=(table_uuid if table_uuid else reservation.table_uuid),
                    reservation_start=(reservation_start if reservation_start else datetime.strptime(reservation.reservation_start, format_string)),
                    deposit=(deposit if deposit else reservation.deposit),
                    is_updating=True
                )
                # if (result == DBTransactionStatus.SUCCESS):
                #     reservation = await rd.get_by_reserve_id(reserve_id=reserve_id)
                    # result = await cd.update_change_reservation(client_chat_id if client_chat_id else reservation.client_chat_id)
                # else:
                #     return result
            else:
                return result

            return result
    
    @staticmethod
    async def update_entity(
        reservation_id: int,
        client_chat_id: int = None,
        table_uuid: str = None,
        reservation_start: datetime = None,
        deposit: float = None,
        status: ReservationStatus = None
    ):
        async with async_session() as session:
            rd = ReservationDAL(session)
            result = await rd.update(
                reservation_id=reservation_id,
                client_chat_id=client_chat_id,
                table_uuid=table_uuid,
                reservation_start=reservation_start,
                deposit=deposit,
                status=status
            )
            return result

    @staticmethod
    async def delete(reservation_id: int):
        async with async_session() as session:
            rd = ReservationDAL(session)
            reservation_info = await rd.get_by_id(reservation_id=reservation_id)
            if (reservation_info):
                if (reservation_info.status != ReservationStatus.CANCELLED):
                    result = await ReservationMiddleware.cancel(
                        reserve_id=reservation_info.reserve_id,
                        cancel_reason="Other"
                    )
                    if (result == DBTransactionStatus.SUCCESS):
                        result = await rd.delete(reservation_id=reservation_id)
                    else:
                        return result
                else: 
                    result = await rd.delete(reservation_id=reservation_id)
            else:
                return result
                
            return result

    @staticmethod
    async def get_all():
        async with async_session() as session:
            rd = ReservationDAL(session)
            result = await rd.get_all()
            return result
    
    @staticmethod
    async def get_all_by_chat_id(chat_id: int):
        async with async_session() as session:
            rd = ReservationDAL(session)
            result = await rd.get_all_by_chat_id(chat_id=chat_id)
            return result

    @staticmethod
    async def get_by_id(reservation_id: int):
        async with async_session() as session:
            rd = ReservationDAL(session)
            result = await rd.get_by_id(reservation_id=reservation_id)
            return result
    
    @staticmethod
    async def get_by_reserve_id(reserve_id: str):
        async with async_session() as session:
            rd = ReservationDAL(session)
            result = await rd.get_by_reserve_id(reserve_id=reserve_id)
            return result
    
    @staticmethod
    async def get_by_reserved_status():
        async with async_session() as session:
            rd = ReservationDAL(session)
            result = await rd.get_by_reserved_status()
            return result
    
    @staticmethod
    async def get_all_reserved_statuses_by_chat_id(chat_id: int, bar_id: int):
        async with async_session() as session:
            rd = ReservationDAL(session)
            client_reservations = await rd.get_all_reserved_statuses_by_chat_id(chat_id=chat_id)
            reservations_by_bar_id = []

            for reservation in client_reservations:
                table = await TableMiddleware.get_by_uuid(table_uuid=reservation.table_uuid)
                if (table.bar_id == bar_id):
                    reservations_by_bar_id.append(reservation)

            return reservations_by_bar_id
    
    async def get_all_expired_and_cancelled_by_chat_id(chat_id: int, bar_id: int):
        async with async_session() as session:
            rd = ReservationDAL(session)
            client_reservations = await rd.get_all_expired_and_cancelled_by_chat_id(chat_id=chat_id)
            reservations_by_bar_id = []

            for reservation in client_reservations:
                table = await TableMiddleware.get_by_uuid(table_uuid=reservation.table_uuid)
                if (table.bar_id == bar_id):
                    reservations_by_bar_id.append(reservation)

            return reservations_by_bar_id

    @staticmethod
    async def get_all_reserved_statuses():
        async with async_session() as session:
            rd = ReservationDAL(session)
            result = await rd.get_all_reserved_statuses()
            return result
    
    @staticmethod
    async def get_by_order_uuid(order_uuid: str):
        async with async_session() as session:
            rd = ReservationDAL(session)
            result = await rd.get_by_order_uuid(order_uuid=order_uuid)
            return result

    @staticmethod
    async def get_entity_id(
        client_chat_id: int,
        table_uuid: int,
        reservation_start: datetime,
        order_uuid: str,
        deposit: float # is not used, for the sake of the dumping model
    ):
        async with async_session() as session:
            rd = ReservationDAL(session)
            format_string = "%Y-%m-%d %H:%M:%S.%f"
            result = await rd.get_entity_id(
                client_chat_id=client_chat_id,
                table_uuid=table_uuid,
                reservation_start=datetime.strptime(reservation_start, format_string),
            )
            return result
    

