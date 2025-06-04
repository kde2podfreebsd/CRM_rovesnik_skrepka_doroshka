from fastapi import APIRouter
from BackendApp.API.test.scheme import *
from BackendApp.Middleware.quiz_middleware import *
from BackendApp.API.test.utils import *

from BackendApp.Middleware.classes import Test
from BackendApp.Logger import logger, LogLevel

router = APIRouter()

@router.get("/test/results/", tags=["Tests"])
async def get_all_test_result() -> List[TestResultResponse]:
    try:
        results = await get_all_test_results()
        return parse_test_results_into_format(results)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /test/results/: {e}",
            module_name="API"
        )

@router.get("/test/result_by_chat_id/{chat_id}", tags=["Tests"])
async def get_results_by_chat_id(chat_id: int) -> List[TestResultResponse]:
    try:
        results = await get_all_test_results_by_chat_id(chat_id)
        return parse_test_results_into_format(results)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /test/result_by_chat_id/: {e}",
            module_name="API"
        )

@router.post("/test/create/", tags=["Tests"])
async def _create_test(test_info: TestRequest) -> dict:
    try:
        status = await create_test_without_quizes(**test_info.model_dump())
        if status == DBTransactionStatus.SUCCESS:
            id = await get_test_entity_id(**test_info.model_dump())
            return {
                "status" : "Success",
                "message": f"Test enitty with id {id} has been successfully created"
            }
        return {
            "status" : "Failed",
            "message": "An error occured while interacting with the data base"
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /test/create/: {e}",
            module_name="API"
        )

@router.patch("/test/update/", tags=["Tests"])
async def _update_test(test_info: TestUpdateRequest) -> dict:
    try:
        status = await update_test(**test_info.model_dump())
        if status == DBTransactionStatus.SUCCESS:
            return {"status" : "Success"}
        return {"status" : "Something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /test/update/: {e}",
            module_name="API"
        )

@router.get("/tests/get_all/", tags=["Tests"])
async def _get_all_tests() -> List[TestResponse]:
    try:
        return parse_tests_into_format(await get_all_tests())
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /test/get_all/: {e}",
            module_name="API"
        )

@router.delete("/test/delete/", tags=["Tests"])
async def _delete_test(test_id: int) -> dict:
    try:
        status = await delete_test(test_id)
        if status == DBTransactionStatus.SUCCESS:
            return {"status" : "Success"}
        return {"status" : "Something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /test/delete/: {e}",
            module_name="API"
        )
