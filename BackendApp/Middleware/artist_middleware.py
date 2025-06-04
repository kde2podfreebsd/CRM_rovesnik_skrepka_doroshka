from BackendApp.Database.session import async_session
from BackendApp.Database.DAL.artist_dal import ArtistDAL
import asyncio

class ArtistMiddleware:

    @staticmethod
    async def create_artist(
            name: str,
            description: str,
            img_path: str,
    ):
        async with async_session() as session:
            artist_dal = ArtistDAL(session)
            status = await artist_dal.create(
                name=name,
                description=description,
                img_path=img_path
            )
            return status

    @staticmethod
    async def get_artist_by_id(artist_id: int):
        async with async_session() as session:
            artist_dal = ArtistDAL(session)
            artist_by_id = await artist_dal.get_by_id(artist_id=artist_id)
            return artist_by_id

    @staticmethod
    async def get_all_artists():
        async with async_session() as session:
            artist_dal = ArtistDAL(session)
            artists = await artist_dal.get_all()
            return artists
        
    @staticmethod
    async def update_artist(
        artist_id: int,
        name: str = None,
        description: str = None,
        img_path: str = None
    ):
        async with async_session() as session:
            return await ArtistDAL(session).update(
                artist_id=artist_id,
                name=name,
                description=description,
                img_path=img_path
            )
            
    @staticmethod
    async def delete_artist(artist_id: int):
        async with async_session() as session:
            return await ArtistDAL(session).delete(artist_id)

    @staticmethod
    async def get_entity_id(
        name: str,
        description: str,
        img_path: str
    ):
        async with async_session() as session:
            dal = ArtistDAL(session)
            result = await dal.get_entity_id(
                name=name,
                description=description,
                img_path=img_path
            )
            return result
if __name__ == "__main__":
    
    async def main():
        
        artist = await ArtistMiddleware.get_all_artists()
        print(artist)
    
    asyncio.run(main())
    