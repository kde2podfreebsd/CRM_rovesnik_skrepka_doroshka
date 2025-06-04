from sqlalchemy.future import select
from sqlalchemy import and_
from BackendApp.Database.Models.quiz_model import Quiz
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Logger import logger, LogLevel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
import asyncio
import json
import pickle


class QuizDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
            self,
            header: str,
            answers: list,
            answer_count: int,
            correct_ans_id: int,
            test_id: int
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST]:

        answers_bytes = pickle.dumps(json.dumps(answers).encode())

        new_quiz = Quiz(
            header=header,
            answers=answers_bytes,
            answer_count=answer_count,
            correct_ans_id=correct_ans_id,
            test_id=test_id
        )

        self.db_session.add(new_quiz)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Quiz entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Quiz entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def update(
            self,
            quiz_id: int,
            header: str = None,
            answers: list = None,
            answer_count: int = None,
            correct_ans_id: int = None,
            test_id: int = None
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        quiz = await self.db_session.execute(
            select(Quiz).where(Quiz.id == quiz_id)
        )

        quiz = quiz.scalars().first()

        if not quiz:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Quiz with id {quiz_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if header is not None:
            quiz.header = header
        if answers is not None:
            answers_bytes = pickle.dumps(json.dumps(answers).encode())
            quiz.answers = answers_bytes
        if answer_count is not None:
            quiz.answer_count = answer_count
        if correct_ans_id is not None:
            quiz.correct_ans_id = correct_ans_id
        if test_id is not None:
            quiz.test_id = test_id

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Quiz entity with id {quiz_id} has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating Quiz entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def delete(self, quiz_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        quiz = await self.db_session.execute(
            select(Quiz).where(Quiz.id == quiz_id)
        )

        quiz = quiz.scalars().first()

        if not quiz:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Quiz with id {quiz_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(quiz)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Quiz entity with id {quiz_id} has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting Quiz entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_all(self):
        result = await self.db_session.execute(select(Quiz))
        return result.scalars().all()

    async def get_all_by_test_id(self, test_id: int):
        result = await self.db_session.execute(select(Quiz).where(Quiz.test_id == test_id))
        return result.scalars().all()

    async def get_by_id(self, quiz_id: int):
        result = await self.db_session.execute(select(Quiz).where(Quiz.id == quiz_id))
        return result.scalars().first()

    async def get_by_header(self, header: str):
        result = await self.db_session.execute(select(Quiz).where(Quiz.header == header))
        return result.scalars().first()

    async def get_entity_id(
        self,
        header: str,
        answers: list,
        answer_count: int,
        correct_ans_id: int,
        test_id: int
    ):
        result = await self.db_session.execute(select(Quiz).where(and_(
            Quiz.header == header,
            Quiz.answers == answers,
            Quiz.answer_count == answer_count,
            Quiz.correct_ans_id == correct_ans_id,
            Quiz.test_id == test_id
        )))
        result = result.scalars().first()
        if (result):
            return result.id
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Quiz with the given parameters: {header, answer_count, answers, correct_ans_id, test_id} does not exist in the data base"
            )
            return None

if __name__ == "__main__":
    async def quiz_test():
        from BackendApp.Database.session import async_session

        async with async_session() as session:
            quiz_dal = QuizDAL(session)

            # Вызовы функций
            # quiz_create_status = await quiz_dal.create(header="quiz1", answers=["Option A", "Option B"], answer_count=2, correct_ans_id=1, test_id=1)
            # print("Quiz Create Status:", quiz_create_status)
            #
            # quiz_update_status = await quiz_dal.update(quiz_id=2, header="updated quiz")
            # print("Quiz Update Status:", quiz_update_status)
            #
            # quiz_delete_status = await quiz_dal.delete(quiz_id=7)
            # print("Quiz Delete Status:", quiz_delete_status)
            #
            # all_quizzes = await quiz_dal.get_all()
            # print("All Quizzes:", [quiz.header for quiz in all_quizzes])
            #
            # quiz_by_id = await quiz_dal.get_by_id(quiz_id=8)
            # print("Quiz By ID:", quiz_by_id.id if quiz_by_id else None)
            # answers_json_bytes = pickle.loads(quiz_by_id.answers)
            # answers_list = json.loads(answers_json_bytes.decode())
            # print(answers_list)
            #
            # quiz_by_header = await quiz_dal.get_by_header(header="updated quiz")
            # print("Quiz By Header:", quiz_by_header.id if quiz_by_header else None)


    asyncio.run(quiz_test())