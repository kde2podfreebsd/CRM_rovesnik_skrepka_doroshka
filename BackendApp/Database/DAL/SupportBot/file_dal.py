import asyncio
from typing import Union
import traceback

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from BackendApp.Database.Models.SupportBot.file_model import File
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Logger import LogLevel, logger


class FileDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add_file(self, req_id, file_id, file_name, type):
        existing_File = await self.db_session.execute(select(File).where(File.file_id == file_id))

        existing_File = existing_File.scalars().first()

        if existing_File:
            return DBTransactionStatus.ALREADY_EXIST

        new_File = File(req_id=int(req_id), file_id=file_id, file_name=file_name, type=type)

        self.db_session.add(new_File)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO, 
                message=f"File {file_id} added successfully",
                module_name="BackendApp.Database.DAL.SupportBot.file_dal"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Error in add_file: {e}. StackTrace: {traceback.format_exc()}",
                module_name="BackendApp.Database.DAL.SupportBot.file_dal"
            )
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def get_file_id(self, id):
        file = await self.db_session.execute(select(File.file_id).where(File.id == int(id)))

        file = file.scalars().first()

        if not file:
            return DBTransactionStatus.NOT_EXIST

        return file

    async def get_files(self, number, req_id):
        limit = (int(number) * 10) - 10
        files = await self.db_session.execute(
            select(File).where(File.req_id == int(req_id)).limit(10).offset(limit)
        )
        return files.scalars().all()
