from sqlalchemy.future import select
from sqlalchemy import and_, or_
from BackendApp.Database.Models.event_model import Event
from BackendApp.Database.Models.ticket_model import Ticket
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional
from datetime import datetime, timedelta
import time
from typing import List
from BackendApp.Database.session import async_session
from BackendApp.Logger import logger, LogLevel
import asyncio

class EventDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_event(
            self,
            short_name: str,
            description: str,
            img_path: str,
            event_datetime: datetime,
            end_datetime: datetime,
            bar_id: int,
            place: str,
            age_restriction: int,
            event_type: str,
            price: float,
            notification_time: list = [],
            motto: Optional[str] = None
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK]:
        
        new_event = Event(
            short_name=short_name,
            description=description,
            img_path=img_path,
            datetime=event_datetime,
            end_datetime=end_datetime,
            bar_id=bar_id,
            place=place,
            age_restriction=age_restriction,
            event_type=event_type,
            price=price,
            notification_time=notification_time,
            motto=motto
        )
        self.db_session.add(new_event)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Event entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Event entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
        
    async def update(
        self,
        event_id: int,
        short_name: str = None,
        description: str = None,
        img_path: str = None,
        event_datetime: datetime = None,
        end_datetime: datetime = None,
        bar_id: int = None,
        place: str = None,
        age_restriction: int = None,
        event_type: str = None,
        price: float = None,
        notification_time: list = None,
        motto: str = None
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:
        
        event = await self.db_session.execute(
            select(Event).where(Event.id == event_id)
        )
        
        event = event.scalars().first()
        
        if not event:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An Event with id {event_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if short_name:
            event.short_name = short_name
        if description:
            event.description = description
        if img_path:
            event.img_path = img_path
        if event_datetime:
            event.datetime = event_datetime
        if end_datetime:
            event.end_datetime = end_datetime
        if bar_id:
            event.bar_id = bar_id
        if place:
            event.place = place
        if age_restriction:
            event.age_restriction = age_restriction
        if event_type:
            event.event_type = event_type
        if price:
            event.price = price
        if notification_time:
            event.notification_time = notification_time
        if motto:
            event.motto = motto
         
        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Event entity with id {event_id} has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating Event entity with id {event_id}: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_event_by_id(self, event_id: int) -> Union[Event, None]:
        result = await self.db_session.execute(select(Event).where(Event.id == event_id))
        return result.scalars().first()

    async def get_all_events(self, bar_id: int) -> Union[List[Event], None]:
        try:
            result = await self.db_session.execute(select(Event).where(Event.bar_id == bar_id))
            events = result.scalars().all()
            logger.log(
                level=LogLevel.INFO,
                message=f"Event entities with bar_id {bar_id} have been successfully retrieved"
            )
            return events
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while retrieving Event entities with bar_id {bar_id}: {e}"
            )
            return None
    
    async def get_events_from_all_bars(self) -> Optional[List[Event]]:
        try:
            result = await self.db_session.execute(select(Event))
            events = result.scalars().all()
            logger.log(
                level=LogLevel.INFO,
                message=f"Event entities have been successfully retrieved"
            )
            return events
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while retrieving Event entities: {e}"
            )
            return None
    
    async def get_upcoming_events_from_all_bars(self) -> Optional[List[Event]]:
        try:
            now = datetime.now() + timedelta(hours=3)
            result = await self.db_session.execute(select(Event).where(
                Event.datetime > now
            ))
            events = result.scalars().all()
            logger.log(
                level=LogLevel.INFO,
                message=f"Upcoming Event entities have been successfully retrieved"
            )
            return events
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while retrieving upcoming Event entities: {e}"
            )
            return []
    
    async def get_upcoming_events_by_bar_id(self, bar_id: int) -> Optional[List[Event]]:
        try:
            now = datetime.now() + timedelta(hours=3)
            result = await self.db_session.execute(select(Event).where(
                Event.datetime > now,
                Event.bar_id == bar_id
            ))
            events = result.scalars().all()
            logger.log(
                level=LogLevel.INFO,
                message=f"Upcoming Event entities with bar_id {bar_id} have been successfully retrieved"
            )
            return events
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while retrieving upcoming Event entities with bar_id {bar_id}: {e}"
            )
            return []
    
    async def get_upcoming_deposit_and_free_events_from_all_bars(self) -> Optional[List[Event]]:
        try:
            now = datetime.now() + timedelta(hours=3)
            result = await self.db_session.execute(select(Event).where(
                Event.datetime > now,
                or_(
                    Event.event_type == "deposit",
                    Event.event_type == "free"
                )
            ))
            events = result.scalars().all()
            logger.log(
                level=LogLevel.INFO,
                message=f"Upcoming deposit and free Event entities have been successfully retrieved"
            )
            return events
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while retrieving upcoming deposit and free Event entities: {e}"
            )
            return []

    async def get_all_today_events(self) -> Optional[List[Event]]:
        try:
            now = datetime.now() + timedelta(hours=3)
            day_end = datetime.combine(datetime.now().date(), datetime.max.time())
            result = await self.db_session.execute(select(Event).where(
                    now < Event.datetime,
                    day_end > Event.datetime
                )
            )

            events = result.scalars().all()
            logger.log(
                level=LogLevel.INFO,
                message=f"Today Event entities have been successfully retrieved"
            )
            return events
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while retrieving today Event entities: {e}"
            )
            return None
    
    async def get_all_today_deposit_events(self) -> Optional[List[Event]]:
        try:
            now = datetime.now() + timedelta(hours=3)
            day_end = datetime.combine(datetime.now().date(), datetime.max.time())
            result = await self.db_session.execute(select(Event).where(
                    now < Event.datetime,
                    day_end > Event.datetime,
                    Event.event_type == "deposit"
                )
            )

            events = result.scalars().all()
            logger.log(
                level=LogLevel.INFO,
                message=f"Today deposit Event entities have been successfully retrieved"
            )
            return events
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while retrieving today deposit Event entities: {e}"
            )
            return None
    
    async def get_past_events_by_bar(self, bar_id: int) -> Optional[List[Event]]:
        try:
            now = datetime.now() + timedelta(hours=3)
            result = await self.db_session.execute(select(Event).where(
                    Event.datetime < now,
                    Event.bar_id == bar_id
                )
            )

            events = result.scalars().all()
            logger.log(
                level=LogLevel.INFO,
                message=f"Past Event entities with bar_id {bar_id} have been successfully retrieved"
            )
            return events
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while retrieving past Event entities with bar_id {bar_id}: {e}"
            )
            return None
        
    async def delete(self, event_id: int) ->  Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:
        
        event = await self.db_session.execute(
            select(Event).where(Event.id == event_id)
        )

        event = event.scalars().first()

        if not event:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An Event with id {event_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(event)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Event entity with id {event_id} has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting Event entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_entity_id(
        self,
        short_name: str,
        description: str,
        img_path: str,
        event_datetime: datetime,
        end_datetime: datetime,
        bar_id: int,
        place: str,
        age_restriction: int,
        event_type: str,
        price: float
    ):
        result = await self.db_session.execute(select(Event).where(and_(
            Event.short_name == short_name,
            Event.description == description,
            Event.img_path == img_path,
            Event.datetime == event_datetime,
            Event.end_datetime == end_datetime,
            Event.event_type == event_type,
            Event.bar_id == bar_id,
            Event.place == place,
            Event.age_restriction == age_restriction,
            Event.price == price
        )))
        result = result.scalars().first()
        if (result):
            return result.id
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An Event with the given parameters: {short_name, description, img_path, event_datetime, end_datetime, event_type, bar_id, place, age_restriction, price} does not exist in the data base"
            )
            return None

if __name__ == "__main__":
    async def test_dal():
        async with async_session() as session:
            event_dal = EventDAL(session)
            # print(await event_dal.get_all_today_events())
            # print((await event_dal.get_all_events(1))[0].id)
            # print(await event_dal.create_event(
            #     short_name="Test Event",
            #     description="Test description",
            #     img_path="test_img.jpg",
            #     event_datetime=datetime.now(),
            #     bar_id=1,
            #     place="Test place",
            #     age_restriction=18,
            #     event_type="Test type",
            #     price=10.0
            # ))

            # events = await event_dal.get_all_events(1)
            # print("All Events:", events)

            # event_by_id = await event_dal.get_event_by_id(event_id=1)
            # print("Event by ID:", event_by_id)

    asyncio.run(test_dal())
