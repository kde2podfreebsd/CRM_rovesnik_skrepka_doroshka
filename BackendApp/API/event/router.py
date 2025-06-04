from typing import Union, List
from fastapi import APIRouter, File, UploadFile
from starlette.responses import FileResponse
from BackendApp.Middleware.event_middleware import EventMiddleware
from BackendApp.API.event.utils import *
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Middleware.artist_event_relationship_middleware import ArtistEventRelationshipMiddleware
from BackendApp.Logger import logger, LogLevel
import os

router = APIRouter()

@router.get("/event/{event_id}/", tags=["Events"])
async def get_event_by_id(event_id: int) -> Union[EventForReturn, dict]:
    try:
        event = await EventMiddleware.get_event_by_id(event_id)
        if event:
            return parse_event_into_format(event)
        return {"message" : "Event not found"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /event/: {e}",
            module_name="API"
        )

@router.get("/{bar_id}/events/", tags=["Events"])
async def get_all_events(bar_id: int) -> Union[List[EventForReturn], dict]:
    try:
        events = await EventMiddleware.get_all_events_by_id(bar_id)
        if events:
            return parse_events_into_format(events)
        return {"message" : "Event doesn't exists"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /bar_id/events/: {e}",
            module_name="API"
        )

@router.get("/{bar_id}/upcoming_events/", tags=["Events"])
async def get_all_events(bar_id: int) -> Union[List[EventForReturn], dict]:
    try:
        events = await EventMiddleware.get_upcoming_events_by_bar_id(bar_id=bar_id)
        if events:
            return {
                "status": "Success",
                "message": parse_events_into_format(events)
            }
        return {
            "status": "Failed",
            "message": f"There are no upcoming events in the bar with bar_id {bar_id}"
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /bar_id/upcoming_events/: {e}",
            module_name="API"
        )

@router.post("/event/create/", tags=["Events"])
async def create_event(event: EventForCreating) -> dict:
    try:
        status = await EventMiddleware.create_event(**event.model_dump())
        if status == DBTransactionStatus.SUCCESS:
            id = await EventMiddleware.get_entity_id(**event.model_dump())
            return {
                "status" : "Success",
                "message": f"Event enitty with id {id} has been successfully created"
            }
        return {
            "status" : "Failed",
            "message": "An error occured while interacting with the data base"
        }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /event/create/: {e}",
            module_name="API"
        )

@router.patch("/event/update/", tags=["Events"])
async def update_event(event: EventForUpdating) -> dict:
    try:
        dct = event.model_dump()
        status = await EventMiddleware.update_event(
            short_name=dct['short_name'],
            event_id=dct['event_id'],
            description=dct['description'],
            img_path=dct['img_path'],
            datetime=dct['dateandtime'],
            end_datetime=dct['end_datetime'],
            bar_id=dct['bar_id'],
            place=dct['place'],
            age_restriction=dct['age_restriction'],
            event_type=dct['event_type'],
            price=dct['price'],
            notification_time=dct['notification_time'],
            motto=dct['motto']
        )
        if status == DBTransactionStatus.SUCCESS:
            return {"status" : "Success"}
        return {"status" : "Something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /event/update/: {e}",
            module_name="API"
        )

@router.delete("/event/delete/", tags=["Events"])
async def delete_event(event_id: int) -> dict:
    try:
        status = await EventMiddleware.delete_event(event_id)
        if status == DBTransactionStatus.SUCCESS:
            return {"status" : "Success"}
        return {"status" : "Something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /event/delete/: {e}",
            module_name="API"
        )

@router.get("/event/get_related_artists", tags=["Events"])
async def get_related_artists_for_event(event_id: int) -> Union[List[EventArtistRelationshipResponse], dict]:
    try:
        relationships = await ArtistEventRelationshipMiddleware.get_all_artists_for_event(event_id=event_id)
        if relationships:
            return parse_relationships_into_format(relationships)
        else:
            return []
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /event/get_related_artists: {e}",
            module_name="API"
        )
