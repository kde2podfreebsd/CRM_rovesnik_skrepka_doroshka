import asyncio
from typing import Union
import traceback

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from BackendApp.Database.Models.SupportBot.password_model import Password
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Logger import LogLevel, logger


class PasswordDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def valid_password(self, password):
        passwords = await self.db_session.execute(
            select(Password).where(Password.password == password)
        )

        password = passwords.scalars().first()

        if password:
            return True
        return False

    async def delete_password(self, password):
        password = await self.db_session.execute(
            select(Password).where(Password.password == password)
        )

        password = password.scalars().first()

        if password:
            await self.db_session.delete(password)
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO, 
                    message=f"Password {password.password} deleted successfully",
                    module_name="BackendApp.Database.DAL.SupportBot.password_dal"
                )
                return True
            except Exception as e:
                logger.log(
                    level=LogLevel.ERROR, 
                    message=f"Error in delete_password: {e}. StackTrace: {traceback.format_exc()}",
                    module_name="BackendApp.Database.DAL.SupportBot.password_dal"
                )
                await self.db_session.rollback()
                raise e
        else:
            return False

    async def add_passwords(self, passwords):
        for password in passwords:
            new_password = Password(password=password)
            self.db_session.add(new_password)
        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO, 
                message=f"Password {password} added successfully",
                module_name="BackendApp.Database.DAL.SupportBot.password_dal"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Error in add_password: {e}. StackTrace: {traceback.format_exc()}",
                module_name="BackendApp.Database.DAL.SupportBot.password_dal"
            )
            await self.db_session.rollback()
            raise e

    async def get_passwords(self, number):
        limit = (int(number) * 10) - 10

        obj = await self.db_session.execute(select(Password.password).limit(10).offset(limit))

        return obj.scalars().all()
