import asyncio
import datetime
from typing import Union
import traceback

from sqlalchemy import desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from BackendApp.Database.Models.SupportBot.message_model import Message
from BackendApp.Database.Models.SupportBot.requests_model import Request
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Logger import LogLevel, logger


class RequestDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def new_req(self, user_id, request):
        new_req = Request(user_id=user_id, req_status="waiting")

        dt = datetime.datetime.now() + datetime.timedelta(hours=3)
        date_now = dt.strftime("%d.%m.%Y %H:%M:%S")

        self.db_session.add(new_req)
        await self.db_session.flush()
        await self.db_session.refresh(new_req)

        new_req_id = new_req.req_id

        new_message = Message(req_id=new_req_id, message=request, user_status="user", date=date_now)
        self.db_session.add(new_message)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO, 
                message=f"New request created. ID: {new_req_id}",
                module_name="BackendApp.Database.DAL.SupportBot.requests_dal"
            )
            return new_req_id

        except Exception as e:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Error in new_req: {e}. StackTrace: {traceback.format_exc()}",
                module_name="BackendApp.Database.DAL.SupportBot.requests_dal"
                )
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def get_user_id_of_req(self, req_id):
        user_ids = await self.db_session.execute(
            select(Request.user_id).where(Request.req_id == int(req_id))
        )

        user_id = user_ids.scalars().first()

        if not user_id:
            return DBTransactionStatus.NOT_EXIST

        return user_id

    async def get_req_status(self, req_id):
        req_statuses = await self.db_session.execute(
            select(Request.req_status).where(Request.req_id == int(req_id))
        )

        req_statuses = req_statuses.scalars().first()

        if not req_statuses:
            return DBTransactionStatus.NOT_EXIST

        return req_statuses

    async def get_request_data(self, req_id, callback):
        if "my_reqs" in callback:
            get_dialog_user_status = "user"
        else:
            get_dialog_user_status = "agent"

        result = await self.db_session.execute(select(Message).where(Message.req_id == int(req_id)))

        messages = result.scalars().all()

        data = []
        text = ""
        i = 1

        for message in messages:
            message_value = message.message
            user_status = message.user_status
            date = message.date

            if user_status == "user":
                if get_dialog_user_status == "user":
                    text_status = "👤 Ваше сообщение"
                else:
                    text_status = "👤 Сообщение пользователя"
            elif user_status == "agent":
                text_status = "🧑‍💻 Агент поддержки"

            backup_text = text
            text += f"{text_status}\n{date}\n{message_value}\n\n"

            if len(text) >= 4096:
                data.append(backup_text)
                text = f"{text_status}\n{date}\n{message_value}\n\n"

            if len(messages) == i:
                if len(text) >= 4096:
                    data.append(backup_text)
                    text = f"{text_status}\n{date}\n{message_value}\n\n"

                data.append(text)

            i += 1

        return data

    async def confirm_req(self, req_id):
        await self.db_session.execute(
            update(Request).where(Request.req_id == int(req_id)).values(req_status="confirm")
        )
        logger.log(
            level=LogLevel.INFO, 
            message=f"Request confirmed. ID: {req_id}",
            module_name="BackendApp.Database.DAL.SupportBot.requests_dal"
        )
        await self.db_session.commit()

    async def my_reqs(self, number, user_id):
        limit = (int(number) * 10) - 10

        obj = await self.db_session.execute(
            select(Request, Request)
            .where(Request.user_id == int(user_id))
            .limit(10)
            .offset(limit)
            .order_by(desc(Request.req_id))
        )

        return obj.scalars().all()

    async def get_reqs(self, number, callback):
        limit = (int(number) * 10) - 10
        req_status = callback.replace("_reqs", "")

        obj = await self.db_session.execute(
            select(Request)
            .where(Request.req_status == req_status)
            .limit(10)
            .offset(limit)
            .order_by(desc(Request.req_id))
        )

        return obj.scalars().all()
