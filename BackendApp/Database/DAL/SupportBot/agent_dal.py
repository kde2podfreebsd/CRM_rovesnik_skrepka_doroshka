import asyncio
from typing import Union
import traceback

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from BackendApp.Database.Models.SupportBot.agent_model import Agent
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Logger import LogLevel, logger


class AgentDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add_agent(
        self,
        agent_id: int,
    ) -> Union[
        DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK, DBTransactionStatus.ALREADY_EXIST
    ]:

        existing_agent = await self.db_session.execute(
            select(Agent).where(Agent.agent_id == int(agent_id))
        )

        existing_agent = existing_agent.scalars().first()

        if existing_agent:
            return DBTransactionStatus.ALREADY_EXIST

        new_agent = Agent(
            agent_id=int(agent_id),
        )

        self.db_session.add(new_agent)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO, 
                message=f"Agent {agent_id} added successfully",
                module_name="BackendApp.Database.DAL.SupportBot.agent_dal"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Error in add_agent: {e}. StackTrace: {traceback.format_exc()}",
                module_name="BackendApp.Database.DAL.SupportBot.agent_dal"
            )
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def check_agent_status(self, agent_id):
        existing_agent = await self.db_session.execute(
            select(Agent).where(Agent.agent_id == agent_id)
        )

        existing_agent = existing_agent.scalars().first()

        if existing_agent:
            return True

        return False

    async def delete_agent(self, agent_id):
        agent = await self.db_session.execute(select(Agent).where(Agent.agent_id == int(agent_id)))
        agent = agent.scalars().first()
        if not agent:
            return DBTransactionStatus.NOT_EXIST

        await self.db_session.delete(agent)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO, 
                message=f"Agent {agent_id} deleted successfully",
                module_name="BackendApp.Database.DAL.SupportBot.agent_dal"
            )
            return DBTransactionStatus.SUCCESS

        except Exception as e:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Error in delete_agent: {e}. StackTrace: {traceback.format_exc()}",
                module_name="BackendApp.Database.DAL.SupportBot.agent_dal"
            )
            await self.db_session.rollback()
            return DBTransactionStatus.ROLLBACK

    async def get_agent(self, number):
        limit = (int(number) * 10) - 10

        agents = await self.db_session.execute(select(Agent).limit(10).offset(limit))
        agents = agents.scalars().all()

        return agents

    async def get_agents(self, number):
        limit = (int(number) * 10) - 10

        agents = await self.db_session.execute(select(Agent.agent_id).limit(10).offset(limit))
        agents = agents.scalars().all()
        return agents
