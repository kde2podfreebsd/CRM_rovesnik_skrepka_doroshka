import asyncio
import json
from datetime import datetime
from typing import List, Union, Optional

from BackendApp.Logger import LogLevel, logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from BackendApp.Database.Models.ticket_model import Ticket
from BackendApp.Database.session import DBTransactionStatus, async_session


class TicketDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
        self,
        qr_path: str,
        activation_status: bool,
        event_id: int,
        client_chat_id: int,
        hashcode: str,
        friends: list = None,
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK]:
        friends_json = json.dumps(friends) if friends else None

        new_ticket = Ticket(
            qr_path=qr_path,
            activation_status=activation_status,
            friends=friends_json,
            event_id=event_id,
            client_chat_id=client_chat_id,
            hashcode=hashcode,
        )
        self.db_session.add(new_ticket)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Ticket entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Ticket entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def update(
        self,
        ticket_id: int,
        qr_path: str = None,
        activation_status: bool = None,
        event_id: int = None,
        client_chat_id: int = None,
        hashcode: str = None,
        friends: list = None,
        activation_time: datetime = None
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK]:
        try:
            ticket = await self.db_session.execute(select(Ticket).where(Ticket.id == ticket_id))
            ticket = ticket.scalars().first()

            if not ticket:
                logger.log(
                    level=LogLevel.WARNING,
                    message=f"A Ticket with id {ticket_id} does not exist in the data base"
                )
                return DBTransactionStatus.NOT_EXIST

            if qr_path is not None:
                ticket.qr_path = qr_path
            if activation_status is not None:
                ticket.activation_status = activation_status
            if event_id is not None:
                ticket.event_id = event_id
            if client_chat_id is not None:
                ticket.client_chat_id = client_chat_id
            if hashcode is not None:
                ticket.hashcode = hashcode
            if friends is not None:
                ticket.friends = json.dumps(friends)
            if activation_time is not None:
                ticket.activation_time = activation_time

            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Ticket entity with id {ticket_id} has been successfully created"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating Ticket entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_all_tickets(self, client_chat_id: int):
        result = await self.db_session.execute(
            select(Ticket).where(Ticket.client_chat_id == client_chat_id)
        )
        return result.scalars().all()

    async def get_ticket_by_hashcode(self, hashcode: str) -> Optional[Ticket]:
        result = await self.db_session.execute(
            select(Ticket).where(Ticket.hashcode == hashcode)
        )
        tickets = result.scalars().first()
        return tickets


    async def change_ticket_status(
        self, ticket_id: int
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK]:
        try:
            ticket = await self.db_session.execute(select(Ticket).where(Ticket.id == ticket_id))
            ticket = ticket.scalars().first()

            if ticket and not ticket.activation_status:
                ticket.activation_status = True
                await self.db_session.commit()
                return DBTransactionStatus.SUCCESS
            else:
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while changing status of the Ticket entity: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while changing status of the Ticket entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_ticket_by_id(self, ticket_id: int) -> Optional[Ticket]:
        result = await self.db_session.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalars().first()
        return ticket

    
    async def get_by_chat_id(self, chat_id: int):
        result = await self.db_session.execute(select(Ticket).where(Ticket.client_chat_id == chat_id))
        result = result.scalars().all()
        return result
    
    async def get_by_event_id(self, event_id: int) -> Optional[List[Ticket]]:
        result = await self.db_session.execute(select(Ticket).where(Ticket.event_id == event_id))
        result = result.scalars().all()
        return result

    async def delete(
        self, ticket_id: int
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:

        ticket = await self.db_session.execute(select(Ticket).where(Ticket.id == ticket_id))

        ticket = ticket.scalars().first()

        if not ticket:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Ticket with id {ticket_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(ticket)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Ticket entity with id {ticket_id} has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting Ticket entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_entity_id(
        self,
        event_id: int,
        client_chat_id: int
    ):
        result = await self.db_session.execute(select(Ticket).where(and_(
            Ticket.event_id == event_id,
            Ticket.client_chat_id == client_chat_id
        )))
        result = result.scalars().first()
        if (result):
            return result.id
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Ticket with the given parameters {event_id, client_chat_id} does not exist in the data base"
            )
            return None
    
    async def get_registered_clients_id_for_event(self, event_id: int) -> Union[List[int], DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:
        clients_id = await self.db_session.execute(
            select(Ticket.client_chat_id).where(Ticket.event_id == event_id)
        )
        result = clients_id.scalars().all()
        try: 
            if not result:
                logger.log(
                    level=LogLevel.WARNING,
                    message=f"There are no registered clients for the event with id {event_id}"
                )
                return DBTransactionStatus.NOT_EXIST
            return result
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while retrieving clients for the event with id {event_id}: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def get_by_chat_id_and_event_id(self, chat_id: int, event_id: int):
        try: 
            result = await self.db_session.execute(select(Ticket).where(
                Ticket.client_chat_id == chat_id,
                Ticket.event_id == event_id
            ))
            result = result.scalars().first()
            if not result:
                logger.log(
                    level=LogLevel.WARNING,
                    message=f"There are no registered clients for the event with id {event_id}"
                )
                return DBTransactionStatus.NOT_EXIST
            
            return result
        
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while retrieving clients for the event with id {event_id}: {e}"
            )
            return DBTransactionStatus.ROLLBACK

if __name__ == "__main__":

    async def test_dal():
        async with async_session() as session:
            ticket_dal = TicketDAL(session)
            print(
                await ticket_dal.create(
                    qr_path="test_qr_path",
                    activation_status=False,
                    event_id=3,
                    client_chat_id=445756820,
                    hashcode="dtcfgvbkhlnj;kmnjhbgvhbjn",
                    # friends=[
                    #     {"name": "Friend1", "username": "Username1"},
                    #     {"name": "Friend2", "username": "Username2"},
                    # ],
                )
            )

            tickets = await ticket_dal.get_all_tickets(client_chat_id=445756820)
            print("All Tickets:", tickets)

    asyncio.run(test_dal())
