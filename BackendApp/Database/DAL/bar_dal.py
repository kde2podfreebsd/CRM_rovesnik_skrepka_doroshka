from sqlalchemy.future import select
from BackendApp.Database.Models.bar_model import Bar
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from BackendApp.Logger import logger, LogLevel
from typing import Union
import asyncio


class BarDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
            self,
            bar_id: int,
            bar_name: str
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST]:

        existing_bar = await self.db_session.execute(
            select(Bar).where(Bar.bar_id == bar_id)
        )

        existing_bar = existing_bar.scalars().first()

        if existing_bar:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Bar with the given parameters: {bar_id, bar_name}, - already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST

        new_bar = Bar(
            bar_id=bar_id,
            bar_name=bar_name
        )

        self.db_session.add(new_bar)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Bar entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Bar entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def update(
            self,
            bar_id: int,
            bar_name: str = None
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        bar = await self.db_session.execute(
            select(Bar).where(Bar.bar_id == bar_id)
        )

        bar = bar.scalars().first()

        if not bar:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Bar with id {bar_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if bar_name is not None:
            bar.bar_name = bar_name

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Bar entity with id {bar_id} has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Bar entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def delete(self, bar_id: int) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        bar = await self.db_session.execute(
            select(Bar).where(Bar.bar_id == bar_id)
        )

        bar = bar.scalars().first()

        if not bar:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Bar with id {bar_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(bar)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Bar entity with id {bar_id} has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Bar entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_all(self):
        result = await self.db_session.execute(select(Bar))
        return result.scalars().all()

    async def get_by_id(self, bar_id: int):
        result = await self.db_session.execute(select(Bar).where(Bar.bar_id == bar_id))
        return result.scalars().first()

    async def get_by_name(self, bar_name: str):
        result = await self.db_session.execute(select(Bar).where(Bar.bar_name == bar_name))
        return result.scalars().first()


if __name__ == "__main__":
    async def bar_test():
        from BackendApp.Database.session import async_session

        async with async_session() as session:
            bar_dal = BarDAL(session)

            # bar_create_status = await bar_dal.create(bar_id=1, bar_name="Rovesnik")
            # print("Bar Create Status:", bar_create_status)

            # bar_update_status = await bar_dal.update(bar_id=1, bar_name="Updated Bar 1")
            # print("Bar Update Status:", bar_update_status)

            # bar_delete_status = await bar_dal.delete(bar_id=1)
            # print("Bar Delete Status:", bar_delete_status)

            # all_bars = await bar_dal.get_all()
            # print("All Bars:", [bar.bar_name for bar in all_bars])

            # bar_by_id = await bar_dal.get_by_id(bar_id=1)
            # print("Bar By ID:", bar_by_id.id if bar_by_id else None)

            # bar_by_name = await bar_dal.get_by_name(bar_name="Bar 2")
            # print("Bar By Name:", bar_by_name.id if bar_by_name else None)

    asyncio.run(bar_test())
