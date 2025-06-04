from BackendApp.Database.session import async_session
from BackendApp.Database.DAL.artist_event_relationship_dal import ArtistEventRelationshipDAL
import asyncio

class ArtistEventRelationshipMiddleware:

    @staticmethod
    async def create_relationship(
            event_id: int,
            artist_id: int
    ):
        async with async_session() as session:
            dal = ArtistEventRelationshipDAL(session)
            status = await dal.create(
                event_id=event_id,
                artist_id=artist_id
            )
            return status

    @staticmethod
    async def get_relationship_by_id(relationship_id: int):
        async with async_session() as session:
            dal = ArtistEventRelationshipDAL(session)
            relationship = await dal.get_by_id(relationship_id=relationship_id)
            return relationship

    @staticmethod
    async def get_all_relationships():
        async with async_session() as session:
            dal = ArtistEventRelationshipDAL(session)
            relationships = await dal.get_all()
            return relationships
        
    @staticmethod
    async def delete_relationship(
        relationship_id: int
    ):
        async with async_session() as session:
            return await ArtistEventRelationshipDAL(session).delete(
                relationship_id=relationship_id
            )
            
    @staticmethod
    async def get_all_artists_for_event(event_id: int):
        async with async_session() as session:
            return await ArtistEventRelationshipDAL(session).get_by_event_id(event_id)

if __name__ == "__main__":
    
    async def main():
        
        # print(await ArtistEventRelationshipMiddleware.create_relationship(3, 4))
        # print(await ArtistEventRelationshipMiddleware.get_all_relationships())
        print(await ArtistEventRelationshipMiddleware.get_all_artists_for_event(3))
        # print(artist)
    
    asyncio.run(main())
    