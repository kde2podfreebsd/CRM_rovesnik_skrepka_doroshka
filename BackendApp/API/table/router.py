from fastapi import APIRouter
from BackendApp.API.table.schemas import *
from BackendApp.API.table.utils import *
from BackendApp.API.event.utils import parse_event_into_format

from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Database.Models.table_model import Table
from BackendApp.Database.Models.event_model import Event
from BackendApp.Middleware.table_middleware import TableMiddleware
from BackendApp.Middleware.reservation_middleware import ReservationResponse
from BackendApp.Logger import logger, LogLevel

router = APIRouter()

@router.post("/table/create/", tags=["Table"])
async def create(request: TableForCreating):
    try:
        result = await TableMiddleware.create(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            id = await TableMiddleware.get_entity_id(
                bar_id=request.bar_id,
                storey=request.storey,
                table_id=request.table_id,
                table_uuid=request.table_uuid,
                terminal_group_uuid=request.terminal_group_uuid,
                capacity=request.capacity
            )
            return {
                "Status": "Success",
                "Message": f"Table with id {id} has been succesfully created in the data base"
            }
        elif (result == DBTransactionStatus.ALREADY_EXIST):
            return {
                "Status": "Failed",
                "Message": f"Table with the given parameters already exists"
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/create/: {e}",
            module_name="API"
        )

@router.post("/table/update/", tags=["Table"])
async def update(request: TableForUpdating):
    try:
        result = await TableMiddleware.update(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "Status": "Success",
                "Message": f"Table has been succesfully updated in the data base"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "Status": "Failed",
                "Message": f"Table with table_id {request.table_uuid} does not exist"
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/update/: {e}",
            module_name="API"
        )

@router.delete("/table/delete/{table_uuid}", tags=["Table"])
async def delete(table_uuid: str):
    try:
        result = await TableMiddleware.delete(table_uuid=table_uuid)
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "Status": "Success",
                "Message": f"Table has been succesfully deleted from the data base"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "Status": "Failed",
                "Message": f"Table with table_uuid {table_uuid} does not exist"
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/delete/: {e}",
            module_name="API"
        )

@router.get("/table/get_all/", tags=["Table"])
async def get_all():
    try:
        result = await TableMiddleware.get_all()
        return {
            "Status": "Success",
            "Message": [parse_table_into_format(table) for table in result]
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/get_all/: {e}",
            module_name="API"
        )

@router.get("/table/get_by_uuid/{table_uuid}/", tags=["Table"])
async def get_by_id(table_uuid: str):
    try:
        result = await TableMiddleware.get_by_uuid(table_uuid=table_uuid)
        return {
            "Status": "Success",
            "Message": parse_table_into_format(result)
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/get_by_uuid/: {e}",
            module_name="API"
        )

@router.get("/table/get_by_terminal_group/{terminal_group_uuid}/", tags=["Table"])
async def get_by_terminal_group(terminal_group_uuid: str):
    try:
        result = await TableMiddleware.get_by_terminal_group(terminal_group_uuid=terminal_group_uuid)
        return {
            "Status": "Success",
            "Message": [parse_table_into_format(table) for table in result]
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/get_by_terminal_group/: {e}",
            module_name="API"
        )

@router.post("/table/get_by_storey/", tags=["Table"])
async def get_by_storey(request: GetByStoreyRequest):
    try:
        result = await TableMiddleware.get_by_storey(**request.model_dump())
        return {
            "Status": "Success",
            "Message": [parse_table_into_format(table) for table in result]
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/get_by_storey/: {e}",
            module_name="API"
        )

@router.patch("/table/change_status_by_storey/", tags=["Table"])
async def change_status_by_storey(request: ChangeStatusRequest):
    try:
        result = await TableMiddleware.change_status_by_storey(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "Status": "Success",
                "Message": f"Tables statuses on the storey {request.storey} in the bar {request.bar_id} have been successfully changed"
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"An error occured while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/change_status_by_storey/: {e}",
            module_name="API"
        )

@router.post("/table/get_available_tables_by_capacity_and_time/", tags=["Table"])
async def get_available_tables_by_capacity_and_time(request: GetByCapacityAndTimeRequest):
    try:
        result = await TableMiddleware.get_available_tables_by_capacity_and_time(**request.model_dump())
        if (isinstance(result, list)):
            return {
                "Status": "Success",
                "Message": result
            }
        elif (isinstance(result, Event)):
            return {
                "Status": "Failed",
                "Message": f"The given time for booking intercepts with the ongoing event",
                "Entity": parse_event_into_format(result)
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There are not any tables with the capacity {request.capacity}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/get_available_tables_by_capacity_and_time/: {e}",
            module_name="API"
        )

@router.post("/table/check_availability/", tags=["Table"])
async def check_availability(request: CheckAvailabilityRequest):
    try:
        result = await TableMiddleware.check_availability(**request.model_dump())
        return {
            "Status": "Success",
            "Message": result
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/check_availability/: {e}",
            module_name="API"
        )

@router.get("/table/get_bowling/", tags=["Table"])
async def get_bowling():
    try:
        result = await TableMiddleware.get_bowling()
        if (result):
            return {
                "Status": "Success",
                "Message": result
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There are no bowling lines in all three bars"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/get_bowling/: {e}",
            module_name="API"
        )

@router.get("/table/get_pool/", tags=["Table"])
async def get_pool():
    try:
        result = await TableMiddleware.get_pool()
        if (result):
            return {
                "Status": "Success",
                "Message": result
            }
        else:
            return {
                "Status": "Failed",
                "Message": f"There are no pool tables in all three bars"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/get_pool/: {e}",
            module_name="API"
        )

@router.post("/table/block_by_time/", tags=["Table"])
async def block_by_time(request: BlockTablesRequest):
    try:
        tables = await TableMiddleware.get_by_storey_and_bar_id(
            bar_id=request.bar_id,
            storey=request.storey
        )
        if (tables):
            for table in tables:
                await TableMiddleware.update(
                    table_uuid=table.table_uuid,
                    block_start=request.block_start,
                    block_end=request.block_end
                )
        return {
            "status": "Success",
            "message": f"The tables' block_start and block_end fields on the {request.storey} storey in the bar with bar_id {request.bar_id} has been successfully updated"
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /table/get_pool/: {e}",
            module_name="API"
        )
