import asyncio
import os
from typing import Literal

from BackendApp.Database.DAL.client_dal import ClientDAL
from BackendApp.Database.session import async_session
from BackendApp.IIKO.api import Client as ClientIIKO
from BackendApp.IIKO.api.customer import Customer
from BackendApp.IIKO.promocodes.get_promocodes import generate_promo_code

podpiska = "bd3c8b28-1d50-4118-bc22-c426aaa85972"

from dotenv import load_dotenv

load_dotenv()

API_LOGIN = os.getenv("API_LOGIN")


class NextLevelNotExistException(Exception):
    pass


class LoyaltyMiddleware:

    @classmethod
    async def check_client_level(self, chat_id):
        async with async_session() as session:
            client_dal = ClientDAL(session)
            client = await client_dal.get_client(chat_id=chat_id)
            client_iiko = await ClientIIKO.create(API_LOGIN, "Rovesnik")

            all_loyalties = await client_iiko.get_full_customer_categories()
            user_loyalties = await client_iiko.get_customer_loyalty_info(client.iiko_id)

            # Добавляем дефолтные лояльности, если их нет
            for loyalty in all_loyalties:
                if (
                    loyalty.isDefaultForNewGuests == True
                    and loyalty not in user_loyalties
                    and loyalty.level != 1
                ):
                    await client_iiko.add_category_to_customer(
                        customer_id=client.iiko_id, category_id=loyalty.id
                    )
            # Получаем текущий уровень лояльности
            for loyalty in user_loyalties:
                if loyalty.category == "level":
                    user_level_loyalty = loyalty
                    break

            next_level_loyalty = await self.get_next_level(all_loyalties, user_level_loyalty)
            if not next_level_loyalty:
                return "Next level not exist"

            # Получаем следующий уровень лояльности
            # Проверяем достижение следующего уровня и заменяем, если да
            while next_level_loyalty.spend_money_amount <= client.spent_amount:
                await client_iiko.remove_category_from_customer(
                    customer_id=client.iiko_id, category_id=user_level_loyalty.id
                )
                await client_iiko.add_category_to_customer(
                    customer_id=client.iiko_id, category_id=next_level_loyalty.id
                )
                user_level_loyalty = next_level_loyalty
                next_level_loyalty = await self.get_next_level(all_loyalties, user_level_loyalty)
                if not next_level_loyalty:
                    return "Next level not exist"

    @classmethod
    async def get_next_level(self, all_loyalties, user_level_loyalty):
        # Получаем следующий уровень лояльности
        next_level_loyalty = None
        for loyalty in all_loyalties:
            if loyalty.category == "level" and loyalty.level - user_level_loyalty.level == 1:
                next_level_loyalty = loyalty
        if next_level_loyalty is None:  # Если нет следующего уровня
            return None

        return next_level_loyalty


if __name__ == "__main__":

    async def main():
        await LoyaltyMiddleware.check_client_level(chat_id=445756820)
        iiko_client = await ClientIIKO.create(API_LOGIN, "Rovesnik")

        print(await iiko_client.get_customer_loyalty_info("01330000-6bec-ac1f-9ef5-08dc5cd18d94"))

    asyncio.run(main())
