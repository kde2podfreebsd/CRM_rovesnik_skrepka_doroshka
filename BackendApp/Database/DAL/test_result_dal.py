from sqlalchemy.future import select
from BackendApp.Logger import logger, LogLevel
from BackendApp.Database.Models.test_result_model import TestResult
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
import asyncio


class TestResultDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
            self,
            chat_id: int,
            test_id: int,
            correct_cnt: int,
            total_cnt: int,
            get_reward: bool,
            is_first_try: bool
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST]:

        new_test_result = TestResult(
            chat_id=chat_id,
            test_id=test_id,
            correct_cnt=correct_cnt,
            total_cnt=total_cnt,
            get_reward=get_reward,
            is_first_try=is_first_try
        )

        self.db_session.add(new_test_result)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"TestResult entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating TestResult entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def update(
            self,
            result_id: int,
            chat_id: int = None,
            test_id: int = None,
            correct_cnt: int = None,
            total_cnt: int = None,
            get_reward: bool = None,
            is_first_try: bool = None,
            claimed_reward: bool = None
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        result = await self.db_session.execute(
            select(TestResult).where(TestResult.id == result_id)
        )

        result = result.scalars().first()

        if not result:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A TestResult with id {result_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if chat_id is not None:
            result.chat_id = chat_id
        if test_id is not None:
            result.test_id = test_id
        if correct_cnt is not None:
            result.correct_cnt = correct_cnt
        if total_cnt is not None:
            result.total_cnt = total_cnt
        if get_reward is not None:
            result.get_reward = get_reward
        if is_first_try is not None:
            result.is_first_try = is_first_try
        if claimed_reward is not None:
            result.claimed_reward = claimed_reward
            
        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"TestResult entity with id {result_id} has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:

            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating TestResult entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def delete(self, result_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        result = await self.db_session.execute(
            select(TestResult).where(TestResult.id == result_id)
        )

        result = result.scalars().first()

        if not result:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A TestResult with id {result_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(result)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"TestResult entity with id {result_id} has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting TestResult entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_all(self):
        result = await self.db_session.execute(select(TestResult))
        return result.scalars().all()

    async def get_by_id(self, result_id: int):
        result = await self.db_session.execute(select(TestResult).where(TestResult.id == result_id))
        return result.scalars().first()

    async def get_by_chat_id_and_test_id(self, chat_id: int, test_id: int):
        result = await self.db_session.execute(
            select(TestResult).where(TestResult.chat_id == chat_id, TestResult.test_id == test_id)
        )
        return result.scalars().first()
    
    async def get_first_try(self, chat_id: int, test_id: int):
        result = await self.db_session.execute(
            select(TestResult).where(TestResult.chat_id == chat_id, TestResult.test_id == test_id, TestResult.is_first_try == True)
        )
        return result.scalars().first()
    
    async def get_results_by_chat_id(self, chat_id: int):
        result = await self.db_session.execute(
            select(TestResult).where(TestResult.chat_id == chat_id)
        )
        return result.scalars().all()


if __name__ == "__main__":
    async def test_result_test():
        from BackendApp.Database.session import async_session

        async with async_session() as session:
            test_result_dal = TestResultDAL(session)

            # Тестирование CRUD функций

            test_result_dal = TestResultDAL(session)

            # Создание результата теста
            # test_result_create_status = await test_result_dal.create(
            #     chat_id=123,
            #     test_id=1,
            #     correct_cnt=8,
            #     total_cnt=10,
            #     get_reward=True,
            #     promo=0.5
            # )
            # print("Test Result Create Status:", test_result_create_status)

            # Обновление результата теста
            # test_result_update_status = await test_result_dal.update(result_id=3, correct_cnt=900)
            # print("Test Result Update Status:", test_result_update_status)

            # Удаление результата теста
            # test_result_delete_status = await test_result_dal.delete(result_id=4)
            # print("Test Result Delete Status:", test_result_delete_status)

            # Получение всех результатов тестов
            # all_test_results = await test_result_dal.get_all()
            # print("All Test Results:", [result.chat_id for result in all_test_results])

            # Получение результата теста по идентификатору
            # test_result_by_id = await test_result_dal.get_by_id(result_id=3)
            # print("Test Result By ID:", test_result_by_id.id if test_result_by_id else None)

            # Получение результата теста по chat_id и test_id
            test_result_by_char_and_test = await test_result_dal.get_by_chat_id_and_test_id(chat_id=123, test_id=1)
            print("Test Result By Char ID and Test ID:",
                  test_result_by_char_and_test.correct_cnt if test_result_by_char_and_test else None)


    asyncio.run(test_result_test())