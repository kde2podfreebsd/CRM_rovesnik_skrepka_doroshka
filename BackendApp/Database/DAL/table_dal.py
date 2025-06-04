from sqlalchemy import and_
from sqlalchemy.future import select
from BackendApp.Logger import logger, LogLevel
from BackendApp.Database.Models.table_model import Table
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional, List

import asyncio
from uuid import uuid4
from datetime import datetime

from BackendApp.Database.session import async_session

class TableDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create(
        self,
        bar_id: int,
        storey: int,
        table_id: int,
        table_uuid: str,
        terminal_group_uuid: str,
        capacity: int,
        is_pool: bool = None,
        is_bowling: bool = None,
        block_start: datetime = None,
        block_end: datetime = None
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST
    ]:
        existing_table = await self.db_session.execute(select(Table).where(and_(
            Table.bar_id == bar_id,
            Table.storey == storey,
            Table.table_id == table_id,
            Table.table_uuid == table_uuid,
            Table.terminal_group_uuid == terminal_group_uuid,
            Table.capacity == capacity
        )))
        existing_table = existing_table.scalars().first()
        if (existing_table):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Table with the given parameters: {bar_id, storey, table_id, table_uuid, terminal_group_uuid, capacity}, - already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST
        
        new_table = Table(
            bar_id=bar_id,
            storey=storey,
            table_id=table_id,
            table_uuid=table_uuid,
            terminal_group_uuid=terminal_group_uuid,
            capacity=capacity,
            is_pool=(is_pool if is_pool else False),
            is_bowling=(is_bowling if is_bowling else False),
            block_start=block_start,
            block_end=block_end
        )
        try:
            self.db_session.add(new_table)
            logger.log(
                level=LogLevel.INFO,
                message=f"Table entity has been successfully created"
            )
            await self.db_session.commit()
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Table entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def update(
        self,
        table_uuid: str,
        table_id: int = None,
        bar_id: int = None,
        storey: int = None,
        reserved: bool = None,
        terminal_group_uuid: str = None,
        capacity: int = None,
        is_pool: bool = None,
        is_bowling: bool = None,
        block_start: datetime = None,
        block_end: datetime = None
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        table = await self.db_session.execute(select(Table).where(Table.table_uuid == table_uuid))
        table = table.scalars().first()

        if (not table):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Table with uuid {table_uuid} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        
        if (table_id is not None):
            table.table_id = table_id
        if (bar_id is not None):
            table.bar_id = bar_id
        if (storey is not None):
            table.storey = storey
        if (reserved is not None):
            table.reserved = reserved
        if (table_uuid is not None):
            table.table_uuid = table_uuid
        if (terminal_group_uuid is not None):
            table.terminal_group_uuid = terminal_group_uuid
        if (capacity is not None):
            table.capacity = capacity
        if (is_bowling is not None):
            table.is_bowling = is_bowling
        if (is_pool is not None):
            table.is_pool = is_pool
        if (block_start is not None):
            table.block_start = block_start
        if (block_end is not None):
            table.block_end = block_end
        
        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Table entity with uuid {table_uuid} has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating Table entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
        
    async def delete(self, table_uuid: str) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:

        table = await self.db_session.execute(
            select(Table).where(Table.table_uuid == table_uuid)
        )
        table = table.scalars().first()

        if (not table):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Table with uuid {table_uuid} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(table)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Table entity with uuid {table_uuid} has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting Table entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def get_all(self) -> Optional[List[Table]]:
        result = await self.db_session.execute(select(Table))
        return result.scalars().all()

    async def get_by_id(self, table_id: int) -> Optional[Table]:
        result = await self.db_session.execute(select(Table).where(Table.table_id == table_id))
        return result.scalars().first()
    
    async def get_by_uuid(self, table_uuid: str) -> Optional[Table]:
        result = await self.db_session.execute(select(Table).where(Table.table_uuid == table_uuid))
        return result.scalars().first()
    
    async def get_by_storey(self, storey: int, bar_id: int) -> Optional[List[Table]]:
        result = await self.db_session.execute(select(Table).where(and_(
            Table.storey == storey,
            Table.bar_id == bar_id
        )))
        return result.scalars().all()
    
    async def get_by_terminal_group(self, terminal_group_uuid: str) -> Optional[List[Table]]:
        result = await self.db_session.execute(select(Table).where(Table.terminal_group_uuid == terminal_group_uuid))
        return result.scalars().all()
    
    async def get_by_capacity(self, capacity: int, bar_id: int) -> Union[List[Table], DBTransactionStatus.NOT_EXIST]:
        result = await self.db_session.execute(select(Table).where(and_(
            Table.capacity == capacity,
            Table.bar_id == bar_id
        )))
        result = result.scalars().all()
        if (result):
            return result 
        logger.log(
            level=LogLevel.WARNING,
            message=f"There are no Table entities with capacity {capacity} in the bar with id {bar_id} in the data base"
        )
        return DBTransactionStatus.NOT_EXIST
    
    async def get_bowling(self):
        result = await self.db_session.execute(select(Table).where(and_(
            Table.is_bowling == True
        )))
        return result.scalars().all()

    async def get_pool(self):
        result = await self.db_session.execute(select(Table).where(and_(
            Table.is_pool == True
        )))
        return result.scalars().all()

    async def get_entity_id(
        self,
        bar_id: int,
        storey: int,
        table_id: int,
        table_uuid: str,
        terminal_group_uuid: str,
        capacity: int
    ):
        result = await self.db_session.execute(select(Table).where(and_(
            Table.bar_id == bar_id,
            Table.storey == storey,
            Table.table_id == table_id,
            Table.table_uuid == table_uuid,
            Table.terminal_group_uuid == terminal_group_uuid,
            Table.capacity == capacity
        )))
        result = result.scalars().first()
        if (result):
            return result.id
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Review with the given parameters: {bar_id, storey, table_id, table_uuid, terminal_group_uuid, capacity} does not exist in the data base"
            )
            return None
    
    async def nullify_block_time(self, table_uuid: str) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST
    ]:
        table = await self.db_session.execute(select(Table).where(Table.table_uuid == table_uuid))
        table = table.scalars().first()

        if (not table):
            return DBTransactionStatus.NOT_EXIST
        
        table.block_start = None
        table.block_end = None

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Block time of the table entity with uuid {table_uuid} has been nullified"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while nullifying the block time of a table entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_by_storey_and_bar_id(self, storey: int, bar_id: int) -> Optional[List[Table]]:
        result = await self.db_session.execute(select(Table).where(and_(
            Table.storey == storey,
            Table.bar_id == bar_id
        )))
        return result.scalars().all()

if __name__ == "__main__":
    async def main():
        async with async_session() as session:
            td = TableDAL(session)

            result = await td.create(
                bar_id=1,
                storey=1,
                table_id=1,
                table_uuid=str(uuid4()),
                terminal_group_uuid=str(uuid4()),
                capacity=4
            )
            print(result)
    asyncio.run(main())
