from BackendApp.Database.session import async_session
from BackendApp.Database.DAL.event_dal import EventDAL
from BackendApp.Database.DAL.artist_event_relationship_dal import ArtistEventRelationshipDAL
from BackendApp import basedir
from typing import List, Optional
import enum
from datetime import datetime
import asyncio

class EVENT_TYPE(str, enum.Enum):
    FREE = 'free'
    DEPOSIT = 'deposit'
    EVENT = 'event'


class EventMiddleware:

    @staticmethod
    async def create_event(
            short_name: str,
            description: str,
            img_path: str,
            dateandtime: datetime,
            end_datetime: datetime,
            bar_id: int,
            place: str,
            age_restriction: int,
            event_type: EVENT_TYPE,
            price: float,
            notification_time: list = [],
            motto: str = None
    ):
        async with async_session() as session:
            event_dal = EventDAL(session)
            status = await event_dal.create_event(
                short_name=short_name,
                description=description,
                img_path=img_path,
                event_datetime=dateandtime,
                end_datetime=end_datetime,
                bar_id=bar_id,
                place=place,
                age_restriction=age_restriction,
                event_type=event_type,
                price=price,
                notification_time=notification_time,
                motto=motto
            )
            return status

    @staticmethod
    async def get_event_by_id(event_id: int):
        async with async_session() as session:
            event_dal = EventDAL(session)
            event_by_id = await event_dal.get_event_by_id(event_id=event_id)
            return event_by_id

    @staticmethod
    async def get_all_events_by_id(bar_id: int):
        async with async_session() as session:
            event_dal = EventDAL(session)
            events = await event_dal.get_all_events(bar_id=bar_id)
            return events
    
    @staticmethod
    async def get_all_today_events():
        async with async_session() as session:
            event_dal = EventDAL(session)
            events = await event_dal.get_all_today_events()
            return events
    
    @staticmethod
    async def get_all_today_deposit_events():
        async with async_session() as session:
            event_dal = EventDAL(session)
            events = await event_dal.get_all_today_deposit_events()
            return events
    
    @staticmethod
    async def get_events_from_all_bars():
        async with async_session() as session:
            event_dal = EventDAL(session)
            events = await event_dal.get_events_from_all_bars()
            return events
    
    @staticmethod
    async def get_upcoming_events_from_all_bars():
        async with async_session() as session:
            event_dal = EventDAL(session)
            events = await event_dal.get_upcoming_events_from_all_bars()
            return events
    
    @staticmethod
    async def get_upcoming_events_by_bar_id(bar_id: int):
        async with async_session() as session:
            event_dal = EventDAL(session)
            events = await event_dal.get_upcoming_events_by_bar_id(bar_id=bar_id)
            return events
    
    @staticmethod
    async def get_upcoming_deposit_and_free_events_from_all_bars():
        async with async_session() as session:
            event_dal = EventDAL(session)
            events = await event_dal.get_upcoming_deposit_and_free_events_from_all_bars()
            return events
    
    @staticmethod
    async def get_past_events_by_bar(bar_id: int):
        async with async_session() as session:
            event_dal = EventDAL(session)
            events = await event_dal.get_past_events_by_bar(bar_id=bar_id)
            return events
        
    @staticmethod
    async def update_event(
        event_id: int,
        short_name: str = None,
        description: str = None,
        img_path: str = None,
        datetime: datetime = None,
        end_datetime: datetime = None,
        bar_id: int = None,
        place: str = None,
        age_restriction: int = None,
        event_type: str = None,
        price: float = None,
        notification_time: list = None,
        motto: str = None
    ):
        async with async_session() as session:
            return await EventDAL(session).update(
                event_id=event_id,
                short_name=short_name,
                description=description,
                img_path=img_path,
                event_datetime=datetime,
                end_datetime=end_datetime,
                bar_id=bar_id,
                place=place,
                age_restriction=age_restriction,
                event_type=event_type,
                price=price,
                notification_time=notification_time,
                motto=motto
            )
            
    @staticmethod
    async def delete_event(event_id: int):
        async with async_session() as session:
            aerd = ArtistEventRelationshipDAL(session)
            artists = await aerd.get_by_event_id(event_id=event_id)
            artists_ids = [artist.id for artist in artists]
            if (artists):
                for id in artists_ids:
                    await aerd.delete(relationship_id=id)
                    
            return await EventDAL(session).delete(event_id)

    @staticmethod
    async def get_entity_id(
        short_name: str,
        description: str,
        img_path: str,
        dateandtime: datetime,
        end_datetime: datetime,
        bar_id: int,
        place: str,
        age_restriction: int,
        event_type: str,
        price: float,
        notification_time: Optional[List[str]] = None,
        motto: str = None

    ):
        async with async_session() as session:
            dal = EventDAL(session)
            result = await dal.get_entity_id(
                short_name=short_name,
                description=description,
                img_path=img_path,
                event_datetime=dateandtime,
                end_datetime=end_datetime,
                bar_id=bar_id,
                place=place,
                age_restriction=age_restriction,
                event_type=event_type,
                price=price
            )
            return result

if __name__ == "__main__":

    asyncio.run(EventMiddleware.create_event(
        short_name="Вечеринка 3",
        description="ROCKET — артист, который не нуждается в представлении. С каждым релизом его фан-база растёт в геометрической прогрессии. Его музыка — одна из самых вайбовых в отечественной индустрии. Пожалуй, каждый из нас слышал такие треки, как: «Город», «Everything Is Fine», «Monday» и, конечно же, «Инкассатор».",
        img_path="/home/donqhomo/Desktop/orders/CRM-Rovesnik-Doroshka-Screpka/BackendApp/static/event3.jpg",
        event_datetime=datetime(2024, 3, 20, 18, 0),
        bar_id=1,
        place="2ой этаж Ровесник / адрес: abcdef",
        age_restriction=18,
        event_type=EVENT_TYPE.FREE,
        price=0
    ))
