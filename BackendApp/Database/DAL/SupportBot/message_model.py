import asyncio
import datetime
from typing import Union
import traceback

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from BackendApp.Database.Models.SupportBot.message_model import Message
from BackendApp.Database.Models.SupportBot.requests_model import Request
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Logger import LogLevel, logger


class MessageDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add_message(self, req_id, message, user_status):
        if user_status == "user":
            req_status = "waiting"
        elif user_status == "agent":
            req_status = "answered"

        dt = datetime.datetime.now()
        date_now = dt.strftime("%d.%m.%Y %H:%M:%S")

        new_message = Message(
            req_id=int(req_id),
            message=message,
            user_status=user_status,
            date=date_now,
        )
        
        req = await self.db_session.execute(select(Request).where(Request.req_id == int(req_id)))
        req = req.scalars().first()
        req.req_status = req_status

        self.db_session.add(new_message)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO, 
                message=f"Message «{message}» added successfully",
                module_name="BackendApp.Database.DAL.SupportBot.message_dal"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Error in add_message: {e}. StackTrace: {traceback.format_exc()}",
                module_name="BackendApp.Database.DAL.SupportBot.message_dal"
            )
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK
