from typing import List
from fastapi import APIRouter
from BackendApp.API.affilate_promotions.scheme import *
from BackendApp.API.affilate_promotions.utils import *
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Middleware.affilate_promotions_middleware import *
from BackendApp.Logger import logger, LogLevel


router = APIRouter()

@router.get("/affilate_promotion/{promotion_id}/", tags=["Promotions"])
async def get_affilate_promotion_by_id(promotion_id: int) -> PromotionResponse:
    try:
        promotion = await get_promotion_by_id(promotion_id)
        return parse_promotion_into_format(promotion)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /affiliate_promotion/: {e}",
            module_name="API"
        )

@router.get("/affilate_promotions/", tags=["Promotions"])
async def get_affilate_promotions() -> List[PromotionResponse]:
    try:
        promotions = await get_all_promotions()
        return parse_promotions_into_format(promotions)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /affiliate_promotions/: {e}",
            module_name="API"
        )

@router.post("/affilate_promotion/create/", tags=["Promotions"])
async def create_affilate_promotion(promotion_info: CreatePromotionRequest) -> dict:
    try:
        status = await create_promotion(**promotion_info.model_dump())
        if status == DBTransactionStatus.SUCCESS:
            id = await get_entity_id(**promotion_info.model_dump())
            return {
                "status" : "Success",
                "message": f"Affiliate promotion enitty with id {id} has been successfully created"
            }
        return {
            "status" : "Failed",
            "message": "An error occured while interacting with the data base"
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /affiliate_promotion/create/: {e}",
            module_name="API"
        )


@router.patch("/affilate_promotion/update/", tags=["Promotions"])
async def update_affilate_promotion(promotion_info: UpdatePromotionRequest) -> dict:
    try:
        status = await update_promotion(**promotion_info.model_dump())
        if status == DBTransactionStatus.SUCCESS:
            return {"status" : "Success"}
        return {"status" : "Something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /affiliate_promotion/update/: {e}",
            module_name="API"
        )

@router.delete("/affilate_promotion/delete/", tags=["Promotions"])
async def delete_affilate_promotion(promotion_id: int) -> dict:
    try:
        status = await delete_promotion(promotion_id)
        if status == DBTransactionStatus.SUCCESS:
            return {"status" : "Success"}
        return {"status" : "Something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /affiliate_promotion/delete/: {e}",
            module_name="API"
        )
