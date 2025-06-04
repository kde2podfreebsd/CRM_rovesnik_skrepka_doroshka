from BackendApp.Database.DAL.bar_dal import BarDAL
from BackendApp.Database.Models.bar_model import Bar
from BackendApp.Database.session import async_session, DBTransactionStatus

import asyncio

class BarMiddleware:

    @staticmethod
    async def get_by_id(bar_id: int):
        async with async_session() as session:
            bd = BarDAL(session)
            result = await bd.get_by_id(bar_id=bar_id)
            return result
    
    @staticmethod
    async def get_all():
        async with async_session() as session:
            bd = BarDAL(session)
            result = await bd.get_all()
            return result
        
    @staticmethod 
    async def get_by_name(bar_name: str):
        async with async_session as session:
            bd = BarDAL(session)
            result = await bd.get_by_name(bar_name=bar_name)
            return result