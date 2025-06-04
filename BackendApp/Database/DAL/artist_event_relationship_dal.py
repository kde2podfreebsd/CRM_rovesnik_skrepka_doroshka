from sqlalchemy.future import select
from BackendApp.Database.Models.atrist_event_relationship_model import ArtistEventRelationship
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from BackendApp.Logger import logger, LogLevel
from typing import Union, Optional
import asyncio


class ArtistEventRelationshipDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
            self,
            artist_id: int,
            event_id: int
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST]:

        existing_relationship = await self.db_session.execute(
            select(ArtistEventRelationship).where(
                ArtistEventRelationship.artist_id == artist_id,
                ArtistEventRelationship.event_id == event_id
            )
        )

        existing_relationship = existing_relationship.scalars().first()

        if existing_relationship:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An ArtistEventRelationship with the given parameters: {artist_id, event_id}, - already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST

        new_relationship = ArtistEventRelationship(
            artist_id=artist_id,
            event_id=event_id
        )

        self.db_session.add(new_relationship)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"ArtistEventRelationship entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating ArtistEventRelationship entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def delete(self, relationship_id: int) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        relationship = await self.db_session.execute(
            select(ArtistEventRelationship).where(ArtistEventRelationship.id == relationship_id)
        )

        relationship = relationship.scalars().first()

        if not relationship:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An ArtistEventRelationship with id {relationship_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(relationship)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"ArtistEventRelationship entity has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting ArtistEventRelationship entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def get_all(self):
        result = await self.db_session.execute(select(ArtistEventRelationship))
        return result.scalars().all()

    async def get_by_id(self, relationship_id: int) -> Optional[ArtistEventRelationship]:
        result = await self.db_session.execute(
            select(ArtistEventRelationship).where(ArtistEventRelationship.id == relationship_id))
        return result.scalars().first()

    async def get_by_artist_id(self, artist_id: int):
        result = await self.db_session.execute(
            select(ArtistEventRelationship).where(ArtistEventRelationship.artist_id == artist_id))
        return result.scalars().all()

    async def get_by_event_id(self, event_id: int):
        result = await self.db_session.execute(
            select(ArtistEventRelationship).where(ArtistEventRelationship.event_id == event_id))
        return result.scalars().all()


if __name__ == "__main__":
    async def artist_event_relationship_test():
        from BackendApp.Database.session import async_session

        async with async_session() as session:
            relationship_dal = ArtistEventRelationshipDAL(session)

            # Тестирование CRUD функций

            # Создание отношения артист-событие
            # relationship_create_status = await relationship_dal.create(artist_id=2, event_id=3)
            # print("Relationship Create Status:", relationship_create_status)

            # Удаление отношения артист-событие
            # relationship_delete_status = await relationship_dal.delete(relationship_id=3)
            # print("Relationship Delete Status:", relationship_delete_status)

            # Получение всех отношений артист-событие
            # all_relationships = await relationship_dal.get_all()
            # print("All Relationships:", [(relationship.artist_id, relationship.event_id) for relationship in all_relationships])

            # Получение отношения артист-событие по идентификатору
            # relationship_by_id = await relationship_dal.get_by_id(relationship_id=1)
            # print("Relationship By ID:", (relationship_by_id.artist_id, relationship_by_id.event_id) if relationship_by_id else None)

            # Получение всех отношений артист-событие по идентификатору артиста
            # relationships_by_artist_id = await relationship_dal.get_by_artist_id(artist_id=1)
            # print("Relationships By Artist ID:", [(relationship.artist_id, relationship.event_id) for relationship in relationships_by_artist_id])

            # Получение всех отношений артист-событие по идентификатору события
            # relationships_by_event_id = await relationship_dal.get_by_event_id(event_id=1)
            # print("Relationships By Event ID:", [(relationship.artist_id, relationship.event_id) for relationship in relationships_by_event_id])

    asyncio.run(artist_event_relationship_test())
