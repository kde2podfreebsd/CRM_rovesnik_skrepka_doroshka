from sqlalchemy.future import select
from sqlalchemy import and_
from BackendApp.Logger import LogLevel, logger
from BackendApp.Database.Models.test_model import Test
from BackendApp.Database.Models.promocode_types import _PromocodeType
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
import asyncio


class TestDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
            self,
            name: str,
            correct_cnt: int,
            total_cnt: int,
            description: str,
            test_id: int,
            promocode_type: _PromocodeType,
            bar_id: int
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST]:

        existing_test = await self.db_session.execute(
            select(Test).where(Test.test_id == test_id)
        )

        existing_test = existing_test.scalars().first()

        if existing_test:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Test with id {test_id} already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST

        new_test = Test(
            name=name,
            correct_cnt=correct_cnt,
            description=description,
            test_id=test_id,
            total_cnt=total_cnt,
            promocode_type=promocode_type,
            bar_id=bar_id
        )

        self.db_session.add(new_test)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Test entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Test entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def update(
            self,
            test_id: int,
            name: str = None,
            correct_cnt: int = None,
            total_cnt: int = None,
            description: str = None,
            promocode_type: _PromocodeType = None,
            bar_id: int = None
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        test = await self.db_session.execute(
            select(Test).where(Test.test_id == test_id)
        )

        test = test.scalars().first()

        if not test:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Test with id {test_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if name is not None:
            test.name = name
        if correct_cnt is not None:
            test.correct_cnt = correct_cnt
        if total_cnt is not None:
            test.total_cnt = total_cnt
        if description is not None:
            test.description = description
        if promocode_type is not None:
            test.promocode_type = promocode_type
        if bar_id is not None:
            test.bar_id = bar_id

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Test entity with id {test_id} has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating Test entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def delete(self, test_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        test = await self.db_session.execute(
            select(Test).where(Test.test_id == test_id)
        )

        test = test.scalars().first()

        if not test:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Test with id {test_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(test)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Test entity with id {test_id} has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting Test entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_all(self):
        result = await self.db_session.execute(select(Test))
        return result.scalars().all()

    async def get_by_name(self, name: str):
        result = await self.db_session.execute(select(Test).where(Test.name == name))
        return result.scalars().first()

    async def get_by_id(self, test_id: int):  # ЭТО PK, но Ваня, как ты сказал, здесь есть еще один типа PK
        result = await self.db_session.execute(select(Test).where(Test.id == test_id))
        return result.scalars().first()

    async def get_by_test_id(self, test_id: int):  # Это "типа PK"
        result = await self.db_session.execute(select(Test).where(Test.test_id == test_id))
        return result.scalars().first()

    async def get_by_bar_id(self, bar_id: int):  # Это "типа PK"
        result = await self.db_session.execute(select(Test).where(Test.bar_id == bar_id))
        return result.scalars().all()

    async def get_entity_id(
        self,
        name: str,
        correct_cnt: int,
        total_cnt: int,
        description: str,
        test_id: int,
        promocode_type: _PromocodeType,
        bar_id: int
    ):
        result = await self.db_session.execute(select(Test).where(and_(
            Test.name == name,
            Test.correct_cnt == correct_cnt,
            Test.total_cnt == total_cnt,
            Test.description == description,
            Test.test_id == test_id,
            Test.promocode_type == promocode_type,
            Test.bar_id == bar_id
        )))
        result = result.scalars().first()
        if (result):
            return result.id
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Test with id {test_id} does not exist in the data base"
            )
            return None

if __name__ == "__main__":
    async def test_test():
        from BackendApp.Database.session import async_session

        async with async_session() as session:
            test_dal = TestDAL(session)

            # test_create_status = await test_dal.create(name="test1", correct_cnt=0, description="abobababab", percent_to_add=0.5, test_id=3)
            # print("Test Create Status:", test_create_status)
            #
            # test_update_status = await test_dal.update(test_id=1, description="updated description")
            # print("Test Update Status:", test_update_status)
            #
            # test_delete_status = await test_dal.delete(test_id=1)
            # print("Test Delete Status:", test_delete_status)
            #
            # all_tests = await test_dal.get_all()
            # print("All Tests:", [test.name for test in all_tests])

            # test_by_id = await test_dal.get_by_id(test_id=1)
            # print("Test By ID:", test_by_id.id if test_by_id else None)

            # test_by_test_id = await test_dal.get_by_test_id(test_id=2)
            # print("Test By Test ID:", test_by_test_id.id if test_by_test_id else None)


    asyncio.run(test_test())