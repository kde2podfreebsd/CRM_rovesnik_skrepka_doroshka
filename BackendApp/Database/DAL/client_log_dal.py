import asyncio
from datetime import datetime, timedelta
from typing import List, Union

from psycopg2 import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from BackendApp.Logger import logger, LogLevel
from BackendApp.Database.Models.client_log_model import ClientActionLog
from BackendApp.Database.Models.client_model import Client
from BackendApp.Database.session import DBTransactionStatus, async_session


class ClientLogDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def create(
        self, client_chat_id: int, action: str
        ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:
        client = await self.db_session.execute(
            select(Client).where(Client.chat_id == client_chat_id)
        )
        if not client.scalars().first():
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Client with chat_id {client_chat_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        
        new_log = ClientActionLog(
            client_chat_id=client_chat_id,
            action=action,
            created_at=(datetime.now() + timedelta(hours=3)),
            
        )
        self.db_session.add(new_log)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"ClientActionLog entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating ClientActionLog entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
        
    async def get_logs(self) -> List[ClientActionLog]:
        logs = await self.db_session.execute(select(ClientActionLog))
        return logs.scalars().all()
    
    async def get_logs_for_client(self, client_chat_id: int) -> Union[List[ClientActionLog], None]:
        logs = await self.db_session.execute(select(ClientActionLog).where(ClientActionLog.client_chat_id == client_chat_id))
        return logs.scalars().all()
