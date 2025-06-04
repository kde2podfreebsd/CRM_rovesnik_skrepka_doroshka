from fastapi import APIRouter
from BackendApp.API.quiz.scheme import *
from BackendApp.Middleware.quiz_middleware import *
from BackendApp.API.quiz.utils import *

import BackendApp.Middleware.classes as mw
from BackendApp.Logger import logger, LogLevel

router = APIRouter()

@router.get("/quizzes/", tags=["Quizzes"])
async def _get_all_quizes() -> List[QuizResponse]:
    try:
        quizzes = await get_all_quizzes()
        return [QuizResponse(
            id=quiz.id,
            header=quiz.header,
            answer_count=quiz.answer_cnt,
            correct_ans_id=quiz.correct_ans_id,
            test_id=quiz.test_id,
            answers=quiz.answers
        ) for quiz in quizzes]
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /quizzes/: {e}",
            module_name="API"
        )
    
    
@router.post("/quiz/create/", tags=["Quizzes"])
async def _create_quiz(quiz: CreateQuizRequest) -> dict:
    try:
        status = await create_quiz_without_test(mw.Quiz(**quiz.model_dump()))
        if status == DBTransactionStatus.SUCCESS:
            return {
                "status": "Success",
                "message": f"Quiz enitty has been successfully created"
            }
        return {
            "status" : "Failed",
            "message": "An error occured while interacting with the data base"
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /quiz/create/: {e}",
            module_name="API"
        )


@router.patch("/quiz/update/", tags=["Quizzes"])
async def _update_quiz(quiz: UpdateQuizRequest) -> dict:
    try:
        status = await update_quiz(**quiz.model_dump())
        if status == DBTransactionStatus.SUCCESS:
            return {"status" : "Success"}
        return {"status" : "Something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /quiz/update/: {e}",
            module_name="API"
        )


@router.delete("/quiz/delete/", tags=["Quizzes"])
async def _delete_quiz(quiz_id: int) -> dict:
    try:
        status = await delete_quiz(quiz_id)
        if status == DBTransactionStatus.SUCCESS:
            return {"status" : "Success"}
        return {"status" : "Something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /quiz/delete/: {e}",
            module_name="API"
        )
    