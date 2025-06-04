from typing import Union, List
from fastapi import APIRouter
from BackendApp.Middleware.event_middleware import EventMiddleware
from BackendApp.Middleware.artist_middleware import ArtistMiddleware
from BackendApp.Middleware.artist_event_relationship_middleware import ArtistEventRelationshipMiddleware
from BackendApp.API.lineup.utils import *
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Logger import logger, LogLevel
from BackendApp.API.lineup.scheme import *

router = APIRouter()

@router.post("/artist/create/", tags=["Artists"])
async def create_artist(artist: ArtistRequest) -> dict:
    try:
        status = await ArtistMiddleware.create_artist(**artist.model_dump())
        if status == DBTransactionStatus.SUCCESS:
            id = await ArtistMiddleware.get_entity_id(**artist.model_dump())
            return {
                "status" : "Success",
                "entity_id": id
            }
        return {"status" : "something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /artist/create/: {e}",
            module_name="API"
        )

@router.get("/artist/{artist_id}/", tags=["Artists"])
async def get_artist_by_id(artist_id: int) -> Union[ArtistResponse, dict]:
    try:
        artist = await ArtistMiddleware.get_artist_by_id(artist_id)
        if artist:
            return parse_artist_into_format(artist)
        return {"message" : "Artist not found"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /artist/: {e}",
            module_name="API"
        )

@router.get("/artists/get_all/", tags=["Artists"])
async def get_all_artists() -> Union[List[ArtistResponse], dict]:
    try:
        artists = await ArtistMiddleware.get_all_artists()
        if artists:
            return parse_artists_into_format(artists)
        return {"Message" : "Artists doesn't exists"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /artists/get_all/: {e}",
            module_name="API"
        )


@router.patch("/artist/update/", tags=["Artists"])
async def update_artist(artist: ArtistToUpdate) -> dict:
    try:
        status = await ArtistMiddleware.update_artist(**artist.model_dump())
        if status == DBTransactionStatus.SUCCESS:
            return {"status" : "Success"}
        return {"status" : "something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /artist/update/: {e}",
            module_name="API"
        )

@router.delete("/artist/delete/", tags=["Artists"])
async def delete_artist(artist_id: int) -> dict:
    try:
        status = await ArtistMiddleware.delete_artist(artist_id)
        if status == DBTransactionStatus.SUCCESS:
            return {"status" : "Success"}
        return {"status" : "something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /artist/delete/: {e}",
            module_name="API"
        )


@router.post("/artist/create_relationship/", tags=["Artists"])
async def create_relationship(artist_id: int, event_id: int) -> dict:
    try:
        status = await ArtistEventRelationshipMiddleware.create_relationship(event_id=event_id, artist_id=artist_id)
        if status == DBTransactionStatus.SUCCESS:
            return {"status" : "Success"}
        return {"status" : "something went wrong"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /artist/create_relationship/: {e}",
            module_name="API"
        )

@router.delete("/artist/delete_relationship/{relationship_id}", tags=["Artists"])
async def delete_relationship(relationship_id: int) -> dict:
    try:
        relationship = await ArtistEventRelationshipMiddleware.get_relationship_by_id(relationship_id=relationship_id)
        artist = await ArtistMiddleware.get_artist_by_id(artist_id=relationship.artist_id)
        event = await EventMiddleware.get_event_by_id(event_id=relationship.event_id)
        status = await ArtistEventRelationshipMiddleware.delete_relationship(relationship_id=relationship_id)
        if status == DBTransactionStatus.SUCCESS:
            return {
                "status" : "Success",
                "message": f"The relationship between artist {artist.name}, id {artist.id} and event {event.short_name}, id {event.id} has been broken"
            }
        return {"status" : "Failed"}
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /artist/delete_relationship/: {e}",
            module_name="API"
        )
