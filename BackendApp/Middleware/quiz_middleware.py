from BackendApp.Database.DAL.quiz_dal import QuizDAL
from BackendApp.Database.DAL.test_dal import TestDAL
from BackendApp.Database.Models.promocode_types import _PromocodeType
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Database.DAL.test_result_dal import TestResultDAL
from BackendApp.Database.Models.test_result_model import TestResult
from BackendApp.Database.session import async_session
from BackendApp.Middleware.classes import *
import asyncio
import pickle
import json
import pprint


'''
    - Создание теста. +++
    - получение Список всех тестов.  +++++
    - получение теста по имени  ++++++++=
    - По chat id и test_id отправлять тест. + Писать резы.
    - Просто по одному новому сообщению.

    - Получить все quiz по test_name +++
'''

async def create_test_without_quizes(
    name: str,
    correct_cnt: int,
    total_cnt: int,
    description: int,
    test_id: int,
    promocode_type: _PromocodeType,
    bar_id: int
):
    async with async_session() as session:
        test_dal = TestDAL(session)

        test_create_status = await test_dal.create(
            name=name,
            correct_cnt=correct_cnt,
            total_cnt=total_cnt,
            description=description,
            test_id=test_id,
            promocode_type=promocode_type,
            bar_id=bar_id
        )
        return test_create_status
    
async def create_quiz_without_test(
    quiz: Quiz
):
    async with async_session() as session:
        quiz_dal = QuizDAL(session)
        
        quiz_create_status = await quiz_dal.create(
            header=quiz.header,
            answers=quiz.answers,
            answer_count=quiz.answer_cnt,
            correct_ans_id=quiz.correct_ans_id,
            test_id=quiz.test_id
        )
        
        return quiz_create_status

async def create_test(
        test: Test,
        quizes: List[Quiz]
):

    await create_test_without_quizes(test)

    async with async_session() as session:
        quiz_dal = QuizDAL(session)

        quiz_number = 1

        for quiz in quizes:
            quiz_create_status = await quiz_dal.create(
                header=quiz.header,
                answers=quiz.answers,
                answer_count=quiz.answer_cnt,
                correct_ans_id=quiz.correct_ans_id,
                test_id=quiz.test_id
            )

            quiz_number += 1


async def get_all_test_names() -> List[str]:
    async with async_session() as session:
        test_dal = TestDAL(session)

        all_tests = await test_dal.get_all()
        return [test.name for test in all_tests]
    
async def get_all_test_results() -> List[TestResult]:
    async with async_session() as session:
        test_result_dal = TestResultDAL(session)
        return await test_result_dal.get_all()
    
async def get_all_test_results_by_chat_id(chat_id: int) -> List[TestResult]:
    async with async_session() as session:
        test_result_dal = TestResultDAL(session)
        return await test_result_dal.get_results_by_chat_id(chat_id=chat_id)
    

async def get_test_by_name(test_name: str) -> Test:
    async with async_session() as session:
        test_dal = TestDAL(session)
        test_obj = await test_dal.get_by_name(test_name)

        if test_obj is None:
            raise Exception("Нет такого теста")

        return Test(
            name=test_obj.name,
            correct_cnt=test_obj.correct_cnt,
            description=test_obj.description,
            test_id=test_obj.test_id,
            total_cnt=test_obj.total_cnt,
            promocode_type=test_obj.promocode_type,
            bar_id=test_obj.bar_id
        )

async def get_all_quizes_for_test(test_name: str) -> List[Quiz]:
    test_id = None
    async with async_session() as session:
        test_dal = TestDAL(session)
        test_obj = await test_dal.get_by_name(test_name)

        if test_obj is None:
            raise Exception("Нет такого теста")

        test_id = test_obj.test_id

    async with async_session() as session:
        quiz_dal = QuizDAL(session)

        model_quiz_objs = await quiz_dal.get_all_by_test_id(test_id=test_id)
        dataclass_quiz_objs = [Quiz(
            header=quiz.header,
            answer_cnt=quiz.answer_count,
            correct_ans_id=quiz.correct_ans_id,
            test_id=test_id,
            answers=json.loads(pickle.loads(quiz.answers).decode())
        ) for quiz in model_quiz_objs]

        return dataclass_quiz_objs

async def get_all_quizzes() -> List[Quiz]:
    async with async_session() as session:
        quiz_dal = QuizDAL(session)

        model_quiz_objs = await quiz_dal.get_all()
        dataclass_quiz_objs = [QuizForAPI(
            id=quiz.id,
            header=quiz.header,
            answer_cnt=quiz.answer_count,
            correct_ans_id=quiz.correct_ans_id,
            test_id=quiz.test_id,
            answers=json.loads(pickle.loads(quiz.answers).decode())
        ) for quiz in model_quiz_objs]

        return dataclass_quiz_objs



async def add_test_result(test_name: str, number_correct_user_answers: int, chat_id: int):
    test_obj = None
    async with async_session() as session:
        test_dal = TestDAL(session)
        test_obj = await test_dal.get_by_name(test_name)

        if test_obj is None:
            raise Exception("Нет такого теста")

    async with async_session() as session:
        test_result_dal = TestResultDAL(session)

        # Если уже запись с этим пользователем есть - значит это не первая попытка.
        test_id = test_obj.test_id
        is_first_try = True

        if await test_result_dal.get_by_chat_id_and_test_id(chat_id=chat_id, test_id=test_id):
            is_first_try = False

        correct_cnt = test_obj.correct_cnt
        total_cnt = test_obj.total_cnt
        get_reward = False


        if is_first_try and number_correct_user_answers >= correct_cnt:
            get_reward = True

        test_result_create_status = await test_result_dal.create(
            chat_id=chat_id,
            test_id=test_id,
            correct_cnt=number_correct_user_answers,
            total_cnt=total_cnt,
            get_reward=get_reward,
            is_first_try=is_first_try
        )
        
async def update_test(
    test_id: int,
    name: str = None,
    correct_cnt: int = None,
    total_cnt: int = None,
    description: str = None,
    promocode_type: _PromocodeType = None,
    bar_id: int = None
) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:
    async with async_session() as session:
        test_dal = TestDAL(session)
        
        return await test_dal.update(
            test_id=test_id,
            name=name,
            promocode_type=promocode_type,
            correct_cnt=correct_cnt,
            total_cnt=total_cnt,
            description=description,
            bar_id=bar_id
        )
        
async def update_quiz(
    id: int,
    header: str = None,
    answers: List[str] = None,
    answer_count: int = None,
    correct_ans_id: int = None,
    test_id: int = None
) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:
    
    async with async_session() as session:
        quiz_dal = QuizDAL(session)
        
        return await quiz_dal.update(
            quiz_id=id,
            header=header,
            answer_count=answer_count,
            answers=answers,
            correct_ans_id=correct_ans_id,
            test_id=test_id
        )
        
async def delete_quiz(quiz_id: int):
    async with async_session() as session:
        quiz_dal = QuizDAL(session)
        
        return await quiz_dal.delete(quiz_id)
        
async def get_all_tests():
    async with async_session() as session:
        test_dal = TestDAL(session)
        return await test_dal.get_all()
    
    
async def delete_test(test_id: int) ->  Union[
    DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

    async with async_session() as session:
        test_dal = TestDAL(session)
        quiz_dal = QuizDAL(session)
        quizzes = await quiz_dal.get_all()
        ids = [entity.id for entity in quizzes if entity == test_id]
        for id in ids:
            await quiz_dal.delete(quiz_id=id)

        return await test_dal.delete(test_id)

async def get_entity_id(
    header: str,
    answers: list,
    answer_cnt: int,
    correct_ans_id: int,
    test_id: int
):
    async with async_session() as session:
        dal = QuizDAL(session)
        result = await dal.get_entity_id(
            header=header,
            answers=answers,
            answer_count=answer_cnt,
            correct_ans_id=correct_ans_id,
            test_id=test_id
        )
        return result

async def get_test_entity_id(
    name: str,
    correct_cnt: int,
    total_cnt: int,
    description: str,
    test_id: int,
    promocode_type: _PromocodeType,
    bar_id: int
):
    async with async_session() as session:
        dal = TestDAL(session)
        result = await dal.get_entity_id(
            name=name,
            correct_cnt=correct_cnt,
            total_cnt=total_cnt,
            description=description,
            test_id=test_id,
            promocode_type=promocode_type,
            bar_id=bar_id
        )
        return result

async def get_first_try(chat_id: int, test_id: int):
    async with async_session() as session:
        dal = TestResultDAL(session)
        result = await dal.get_first_try(
            chat_id=chat_id,
            test_id=test_id
        )
        return result

async def update_test_result(
    result_id: int,
    chat_id: int = None,
    test_id: int = None,
    correct_cnt: int = None,
    total_cnt: int = None,
    get_reward: bool = None,
    is_first_try: bool = None,
    claimed_reward: bool = None
):
    async with async_session() as session:
        trd = TestResultDAL(session)
        result = await trd.update(
            result_id=result_id,
            chat_id=chat_id,
            test_id=test_id,
            correct_cnt=correct_cnt,
            total_cnt=total_cnt,
            get_reward=get_reward,
            is_first_try=is_first_try,
            claimed_reward=claimed_reward
        )
        return result

async def get_all_by_bar_id(bar_id: int):
    async with async_session() as session:
        td = TestDAL(session)
        result = await td.get_by_bar_id(bar_id=bar_id)
        return result

if __name__ == "__main__":
    async def test():
        test = Test(
            "Yet another testaaa",
            3,
            5,
            "Это проверочный тест. Необходимо ответить верно на 3 из 5 вопросов.",
            5.5,
            19
        )

        quiz1 = Quiz(
            "Сколько будет 2 + 2???",
            5,
            ["1", "22", "228", "4", "5"],
            3,
            19
        )

        quiz2 = Quiz(
            "Сколько будет 3 + 2???",
            5,
            ["1", "22", "228", "4", "5"],
            4,
            19
        )

        quiz3 = Quiz(
            "1000 - 7???",
            5,
            ["1", "22", "993", "4", "5"],
            2,
            19
        )

        quiz4 = Quiz(
            "1000 + 7???",
            5,
            ["1", "1007", "993", "4", "5"],
            1,
            19
        )

        quiz5 = Quiz(
            "1000 - 7???",
            5,
            ["1", "22", "993", "4", "5"],
            2,
            19
        )

        quizes = [quiz1, quiz2, quiz3, quiz4, quiz5]

        await create_test(test, quizes)

        # print(await get_all_test_names())

        print("Я тут что ли?")

        # pprint.pprint(await get_test_by_name("Первый тест"))
        # pprint.pprint(await get_all_quizes_for_test("Первый тест"))


    asyncio.run(test())
