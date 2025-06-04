from sqlalchemy.future import select
from sqlalchemy import and_
from BackendApp.Database.Models.artist_model import Artist
from BackendApp.Database.Models.atrist_event_relationship_model import ArtistEventRelationship
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional
from BackendApp.Logger import logger, LogLevel
import asyncio


class ArtistDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
            self,
            name: str,
            description: str,
            img_path: str
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST]:

        existing_artist = await self.db_session.execute(
            select(Artist).where(Artist.name == name)
        )

        existing_artist = existing_artist.scalars().first()

        if existing_artist:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An Artist with the given parameters: {name, description, img_path}, - already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST

        new_artist = Artist(
            name=name,
            description=description,
            img_path=img_path
        )

        self.db_session.add(new_artist)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Artist entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Artist entity: {e}"
            )
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def update(
            self,
            artist_id: int,
            name: str = None,
            description: str = None,
            img_path: str = None
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        artist = await self.db_session.execute(
            select(Artist).where(Artist.id == artist_id)
        )

        artist = artist.scalars().first()

        if not artist:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An Artist with id {artist_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        if name is not None:
            artist.name = name
        if description is not None:
            artist.description = description
        if img_path is not None:
            artist.img_path = img_path

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Artist entity with id {artist_id} has been successfully updated"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while updating Artist entity: {e}"
            )
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def delete(self, artist_id: int) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.NOT_EXIST]:

        artist = await self.db_session.execute(
            select(Artist).where(Artist.id == artist_id)
        )
        artist = artist.scalars().first()
        if (not artist):
            logger.log(
                level=LogLevel.WARNING,
                message=f"An Artist with id {artist_id} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        artist_event_reltionships = await self.db_session.execute(
            select(ArtistEventRelationship).where(ArtistEventRelationship.artist_id == artist_id)
        )
        artist_event_reltionships = artist_event_reltionships.scalars().all()

        if (artist_event_reltionships):
            for relationship in artist_event_reltionships:
                await self.db_session.delete(relationship)

        await self.db_session.delete(artist)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Artist entity with id {artist_id} has been successfully deleted"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting Artist entity: {e}"
            )
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def get_all(self):
        result = await self.db_session.execute(select(Artist))
        return result.scalars().all()

    async def get_by_id(self, artist_id: int) -> Optional[Artist]:
        result = await self.db_session.execute(select(Artist).where(Artist.id == artist_id))
        return result.scalars().first()

    async def get_by_name(self, name: str):
        result = await self.db_session.execute(select(Artist).where(Artist.name == name))
        return result.scalars().first()

    async def get_entity_id(
        self,
        name: str,
        description: str,
        img_path: str
    ):
        result = await self.db_session.execute(select(Artist).where(and_(
            Artist.name == name,
            Artist.description == description,
            Artist.img_path == img_path
        )))
        result = result.scalars().first()
        if (result):
            return result.id
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"An Artist with the given parameters: {name, description, img_path} does not exist in the data base"
            )
            return None


if __name__ == "__main__":
    async def artist_test():
        from BackendApp.Database.session import async_session

        async with async_session() as session:
            artist_dal = ArtistDAL(session)

            # Тестирование CRUD функций

            # Создание артиста
            # artist_create_status = await artist_dal.create(
            #     name="Some Artistaaa",
            #     description="Some Description",
            #     img_path="some_img.jpg"
            # )
            # print("Artist Create Status:", artist_create_status)

            # Обновление артиста
            # artist_update_status = await artist_dal.update(artist_id=1, description="Updated Description")
            # print("Artist Update Status:", artist_update_status)

            # Удаление артиста
            # artist_delete_status = await artist_dal.delete(artist_id=1)
            # print("Artist Delete Status:", artist_delete_status)

            # Получение всех артистов
            # all_artists = await artist_dal.get_all()
            # print("All Artists:", [artist.name for artist in all_artists])

            # Получение артиста по идентификатору
            # artist_by_id = await artist_dal.get_by_id(artist_id=2)
            # print("Artist By ID:", artist_by_id.id if artist_by_id else None)

            # Получение артиста по имени
            # artist_by_name = await artist_dal.get_by_name(name="Some Artist")
            # print("Artist By Name:", artist_by_name.id if artist_by_name else None)

    asyncio.run(artist_test())
