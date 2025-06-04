from BackendApp.Database.Models.table_model import Table
from BackendApp.API.reservation.schemas import ReservationForReturn, TableForReturn, ReservationAndTableForReturn
from BackendApp.Database.Models.reservation_model import Reservation


def parse_reservation_into_format(reservation: Reservation):
    return ReservationForReturn(
        reservation_id=reservation.id,
        client_chat_id=reservation.client_chat_id,
        order_uuid=reservation.order_uuid,
        table_uuid=reservation.table_uuid,
        reserve_id=reservation.reserve_id,
        reservation_start=reservation.reservation_start,
        status=reservation.status,
        deposit=reservation.deposit
    )

def parse_table_into_format(table: Table):
    return TableForReturn(
        bar_id=table.bar_id,
        storey=table.storey,
        table_id=table.table_id,
        table_uuid=table.table_uuid,
        terminal_group_uuid=table.terminal_group_uuid,
        capacity=table.capacity,
        reserved=table.reserved,
        is_bowling=table.is_bowling,
        is_pool=table.is_pool
    )

def parse_reservation_and_table_into_format(reservation: Reservation, table: Table):
    return ReservationAndTableForReturn(
        reservation_id=reservation.id,
        client_chat_id=reservation.client_chat_id,
        order_uuid=reservation.order_uuid,
        table_uuid=reservation.table_uuid,
        reserve_id=reservation.reserve_id,
        reservation_start=reservation.reservation_start,
        status=reservation.status,
        deposit=reservation.deposit,
        table=parse_table_into_format(table=table)
    )