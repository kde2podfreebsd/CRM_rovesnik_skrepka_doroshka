from BackendApp.Database.DAL.client_dal import ClientDAL
from BackendApp.Database.session import async_session
from BackendApp.Database.DAL.event_dal import EventDAL
from BackendApp.Database.DAL.ticket_dal import TicketDAL
from BackendApp.IIKO.api import Client
from BackendApp.Middleware.event_middleware import EVENT_TYPE
from BackendApp.TelegramBots.Rovesnik.Config.bot import bot
from BackendApp import basedir
import enum
from datetime import datetime
from typing import List, Union
import asyncio
import qrcode
import secrets
import hashlib
from BackendApp.Database.session import DBTransactionStatus



class TicketMiddleware:

    @staticmethod
    async def create(
        qr_path: str,
        activation_status: bool,
        event_id: int,
        client_chat_id: int,
        hashcode: str,
        friends: list = None
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK]:
        async with async_session() as session:
            ticket_dal = TicketDAL(session)
            result = await ticket_dal.create(
                qr_path=qr_path,
                activation_status=activation_status,
                event_id=event_id,
                client_chat_id=client_chat_id,
                hashcode=hashcode,
                friends=friends
            )
            return result 

    @staticmethod
    async def purchase_ticket(
            event_id: int,
            client_chat_id: int,
            friends: List[dict] = None
    ):
        async with async_session() as session:
            ticket_dal = TicketDAL(session)

            # Check if ticket already purchased for the client_chat_id
            user_tickets = await ticket_dal.get_all_tickets(client_chat_id=client_chat_id)
            
            if any(ticket.event_id == event_id for ticket in user_tickets):
                return False # Такой билет уже есть

            # qrcode -----------------------------------------------
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            hashcode = TicketMiddleware.generate_random_hash()
            qr.add_data(hashcode)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            qr_img_path = rf'{basedir}/static/tickets/{client_chat_id}_{hashcode}.png'
            qr_img.save(qr_img_path)
            # qrcode -----------------------------------------------

            await ticket_dal.create(
                qr_path=qr_img_path,
                activation_status=False,
                event_id=event_id,
                client_chat_id=client_chat_id,
                friends=friends,
                hashcode=hashcode
            )

            return True # Билет успешно создан

    @staticmethod
    def generate_random_hash(length=32):
        random_string = secrets.token_hex(length // 2)
        hash_code = hashlib.sha256(random_string.encode()).hexdigest()
        return hash_code

    @staticmethod
    async def get_all_tickets(client_chat_id: int):
        async with async_session() as session:
            ticket_dal = TicketDAL(session)

            user_tickets = await ticket_dal.get_all_tickets(client_chat_id=client_chat_id)
            return user_tickets

    @staticmethod
    async def get_ticket_by_id(ticket_id: int):
        async with async_session() as session:
            ticket_dal = TicketDAL(session)

            ticket = await ticket_dal.get_ticket_by_id(ticket_id=ticket_id)

            return ticket
    
    @staticmethod
    async def get_by_event_id(event_id: int):
        async with async_session() as session:
            ticket_dal = TicketDAL(session)

            ticket = await ticket_dal.get_by_event_id(event_id=event_id)

            return ticket


    @staticmethod
    async def get_ticket_by_hashcode(hashcode: str):
        async with async_session() as session:
            ticket_dal = TicketDAL(session)

            ticket = await ticket_dal.get_ticket_by_hashcode(hashcode=hashcode)

            if ticket is None:
                return False

            return ticket
    
    @staticmethod
    async def get_by_chat_id(chat_id: int):
        async with async_session() as session:
            td = TicketDAL(session)
            result = await td.get_by_chat_id(chat_id=chat_id)
            return result

    @staticmethod
    async def validate_ticket(hashcode: str):
        async with async_session() as session:
            ticket_dal = TicketDAL(session)

            ticket = await ticket_dal.get_ticket_by_hashcode(hashcode=hashcode)

            if ticket is None:
                return False

            status = await ticket_dal.change_ticket_status(ticket_id=ticket.id)

            return status
        
    @staticmethod
    async def delete_ticket(id: int):
        async with async_session() as session:
            ticket_dal = TicketDAL(session)
            
            status = await ticket_dal.delete(id)
            
            if status == DBTransactionStatus.SUCCESS:
                return True
            return False
        
    @staticmethod
    async def update_ticket(
        ticket_id: int,
        qr_path: str = None,
        activation_status: bool = None,
        event_id: int = None,
        client_chat_id: int = None,
        hashcode: str = None,
        friends: list = None,
        activation_time: datetime = None
    ):
        async with async_session() as session:
            ticket_dal = TicketDAL(session)
            return await ticket_dal.update(
                ticket_id=ticket_id,
                qr_path=qr_path,
                activation_status=activation_status,
                event_id=event_id,
                client_chat_id=client_chat_id,
                hashcode=hashcode,
                friends=friends,
                activation_time=activation_time
            )
        
    @staticmethod
    async def get_entity_id(
        event_id: int,
        client_chat_id: int,
    ):
        async with async_session() as session:
            dal = TicketDAL(session)
            result = await dal.get_entity_id(
                event_id=event_id,
                client_chat_id=client_chat_id
            )
            return result
        
    @staticmethod
    async def get_registered_clients_for_event(
        event_id: int
    ) -> Union[
        DBTransactionStatus.ROLLBACK, 
        DBTransactionStatus.NOT_EXIST, 
        List[Client]
    ]:
        async with async_session() as session:
            ticket_dal = TicketDAL(session)
            client_dal = ClientDAL(session)
            clients_ids = await ticket_dal.get_registered_clients_id_for_event(event_id=event_id)
            if clients_ids != DBTransactionStatus.NOT_EXIST and clients_ids != DBTransactionStatus.ROLLBACK:
                return [await client_dal.get_client(chat_id=client_id) for client_id in clients_ids]
            else:
                return clients_ids
    
    async def get_by_chat_id_and_event_id(chat_id: int, event_id: int):
        async with async_session() as session:
            dal = TicketDAL(session)
            result = await dal.get_by_chat_id_and_event_id(
                chat_id=chat_id, 
                event_id=event_id
            )
            return result


if __name__ == "__main__":
    async def test_ticket_middleware():
        event_id = 2
        client_chat_id = 406149871
        friends = [
            {"name": "Friend1", "username": "username1"},
            {"name": "Friend2", "username": "username2"}
        ]

        # await TicketMiddleware.purchase_ticket(
        #     event_id=event_id,
        #     client_chat_id=client_chat_id,
        #     # event_type=EVENT_TYPE.FREE,
        #     friends=friends
        # )

        # user_tickets = await TicketMiddleware.get_all_tickets(client_chat_id=client_chat_id)
        # print("All user tickets:", user_tickets)
        #
        # ticket_by_hashcode = await TicketMiddleware.get_tickets_by_hashcode(hashcode='1e59a07629dea0f516aacef518e7e23e79c2de0c8e780dbb5d83df64324a6a2e')
        # print("Ticket by hashcode:", ticket_by_hashcode)
        #
        validation_status = await TicketMiddleware.validate_ticket(hashcode='1e59a07629dea0f516aacef518e7e23e79c2de0c8e780dbb5d83df64324a6a2e')
        print("Validation status:", validation_status)


    asyncio.run(test_ticket_middleware())