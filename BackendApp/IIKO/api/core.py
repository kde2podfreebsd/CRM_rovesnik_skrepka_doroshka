import asyncio
import json
import pprint
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

import aiohttp
import requests

from BackendApp.IIKO.classes import OrganizationData
from BackendApp.Logger import LogLevel, logger


class TokenException(Exception):
    pass


def token_required(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.token or datetime.now() > self.token_expiry:
            await self.get_access_token()  # Обновляем токен асинхронно, если он отсутствует или истек
        return await func(self, *args, **kwargs)

    return wrapper


class Client:
    name_id_orgranization = {"Rovesnik": "9cb23610-e67b-4b76-af30-75bd8a1785f4"}

    def __init__(self, api_login, org_name: Literal["Rovesnik"]):
        self.api_login = api_login
        self.base_url = "https://api-ru.iiko.services"
        self.org_name = org_name
        self.organization_id = self.name_id_orgranization[org_name]
        self.session_s = None
        self.token = None
        self.token_expiry = None
        self.auto_update_token_in = 1800  # Обновляем раз в пол часа.

    @classmethod
    async def create(cls, api_login, org_name: Literal["Rovesnik"]):
        self = cls(api_login, org_name)
        self.session_s = aiohttp.ClientSession()

        return self

    async def close_session(self):
        if self.session_s:
            await self.session_s.close()

    async def __set_token(self, token, token_expiry):
        self.token = token
        self.token_expiry = token_expiry

    def check_status_code_token(self, status_code):
        if status_code != 200:
            raise TokenException(f"Unexpected status code: {status_code}")

    async def get_access_token(self):
        """Получить token"""
        data = {"apiLogin": self.api_login}
        _response = None
        try:
            async with self.session_s.post(
                url=f"{self.base_url}/api/1/access_token", json=data
            ) as _response:

                response_data = await _response.json()

                if "errorDescription" in response_data:
                    raise TokenException(f"Error: {response_data['errorDescription']}")

                if "token" in response_data:
                    self.check_status_code_token(_response.status)
                    token_expiry = datetime.now() + timedelta(seconds=self.auto_update_token_in)
                    await self.__set_token(response_data["token"], token_expiry)

        except (aiohttp.ClientError, TokenException) as err:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Failed to get access token: {err}", 
                module_name="BackendApp.IIKO.api.core"
                )
            raise TokenException(f"Failed to get access token: {err}")

    @token_required
    async def get_organizations(
        self,
        organization_ids: Optional[List[str]] = None,
        return_external_data: Optional[List[str]] = None,
        return_additional_info: Optional[bool] = False,
        include_disabled: Optional[bool] = True,
    ):
        """
        Получить организации.

        Args:
            organization_ids (Optional[List[str]]): Список идентификаторов организации.
            return_external_data (Optional[List[str]]): Внешние ключи данных, которые должны быть возвращены.
            return_additional_info (Optional[bool]): Знак того, должна ли быть возвращена дополнительная информация об организации (версия RMS, страна, адрес ресторана и т. д.), или должна быть возвращена только минимальная информация (идентификационный идентификатор и имя).
            include_disabled (Optional[bool]): Атрибут, который показывает, что ответ содержит отключенные организации.

        Returns:
            dict: JSON-ответ, содержащий данные об организациях.

        Raises:
            TokenException: Если не удалось получить организации.
        """

        data = {
            "organizationIds": organization_ids,
            "returnAdditionalInfo": return_additional_info,
            "includeDisabled": include_disabled,
            "returnExternalData": return_external_data,
        }
        headers = {"Authorization": f"Bearer {self.token}"}

        json_data = None
        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/organizations", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return OrganizationData(**json_data)
        except (aiohttp.ClientError, ValueError) as err:
            pprint.pprint(json_data)
            raise TokenException(f"Failed to get organizations: {err}")

    @token_required
    async def get_programs(
        self, without_marketing_campaigns: Optional[bool] = True, organization_id: UUID = None
    ):
        """
        Получите все программы лояльности для организации.

        Args:
            organization_id (str): Идентификатор организации.
            without_marketing_campaigns (bool, optional): Определяет, не требуются ли маркетинговые кампании. По умолчанию - True.

        Returns:
            dict: JSON-ответ, содержащий программы.

        Raises:
            TokenException: Если возникла проблема с получением программ.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "withoutMarketingCampaigns": without_marketing_campaigns,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }
        json_data = None
        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/program", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, ValueError) as err:
            pprint.pprint(json_data)
            raise TokenException(f"Failed to get programs: {err}")

    @token_required
    def get_menu_by_id(
        self,
        external_menu_id: str,
        price_category_id: Optional[str] = None,
        version: Optional[int] = 0,
        language: Optional[str] = "ru",
        start_revision: Optional[int] = 0,
        organization_ids: Optional[List[UUID]] = None,
    ):
        """Получить меню"""
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "externalMenuId": external_menu_id,
            "organizationIds": [self.organization_id] if not organization_ids else organization_ids,
            "priceCategoryId": price_category_id,
            "version": version,
            "language": language,
            "startRevision": start_revision,
        }

        try:
            result = self.session_s.post(
                f"{self.base_url}/api/2/menu/by_id", headers=headers, json=data
            )
            result.raise_for_status()
            return result.json()
        except (requests.exceptions.RequestException, ValueError) as err:
            raise TokenException(f"Failed to get menu: {err}, {result.text}")

    @token_required
    async def terminal_groups(self, organization_id: Optional[UUID] = None):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "organizationIds": [self.organization_id] if not organization_id else organization_id,
            "includeDisabled": True,
        }
        try:
            result = await self.session_s.post(
                f"{self.base_url}/api/1/terminal_groups", headers=headers, json=data
            )
            # print(await result.json())
            # await result.raise_for_status()
            return await result.json()
        except (requests.exceptions.RequestException, ValueError) as err:
            raise TokenException(f"Failed to get terminal groups: {err}, {result.text}")
        
    @token_required
    async def awake_terminal_groups(
        self, 
        organization_ids: Optional[List[UUID]] = None, 
        terminal_group_ids: Optional[List[UUID]] = None, 
    ):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "organizationIds": [self.organization_id] if not organization_ids else organization_ids,
            "terminalGroupIds": terminal_group_ids
        }
        try:
            result = await self.session_s.post(
                f"{self.base_url}/api/1/terminal_groups/awake", headers=headers, json=data
        )
            return await result.json()
        except (requests.exceptions.RequestException, ValueError) as err:
            raise TokenException(f"Failed to get terminal groups: {err}, {result.text}")
        


if __name__ == "__main__":

    api_login = "a061da2d-0f0"
    #     menu_id = "21653"
    #     organization_id = "9cb23610-e67b-4b76-af30-75bd8a1785f4"
    #     terminal_group_id = "c4923c8b-1747-b52f-016d-f7c0c79c00cd"
    #     customer_id = "01330000-6bec-ac1f-823d-08dc36ceec35"
    #     phone = "89000000001"
    #     program_id = "01330000-6bec-ac1f-c574-08dc36d8330b"
    #     user_wallet = "01330000-6bec-ac1f-fe19-08dc36d8330c"
    #     card_track = "8641560005487957"
    #     card_number = "05487957"
    #     item = {
    #         "type": "Product",
    #         "amount": 1,
    #         "productId": "ed184eed-8b89-47ec-0184-082fe03a289e",
    #         "comment": "string",
    #     }

    #     client = Client(api_login)

    #     try:

    # print(client.create_order(organization_id, terminal_group_id, [item]))
    # print(
    #     client.retrieve_orders_by_ids([organization_id], ["03650000-6bec-ac1f-9318-08dc38499a54"])
    # )
    # pprint.pprint(client.get_menu_by_id(menu_id, [organization_id]))
    async def main():
        client = await Client.create(api_login, "Rovesnik")

        print(await client.terminal_groups())

    asyncio.run(main())
# print(client.get_or_create_customer(name="test test", phone=phone, organization_id=organization_id))
# print(client.delete_card(organization_id, customer_id, card_track))
# print(
#     client.hold_money(
#         None,
#         organization_id,
#         customer_id,
#         user_wallet,
#         40,
#     )
# )
# print(client.cancel_hold_money(organization_id, "03650000-6bec-ac1f-9318-08dc38499a54"))
# print(client.withdraw_balance(organization_id, customer_id, user_wallet, 40))
# print(client.get_customer_info(organization_id=organization_id, phone="89000000001"))
# print(client.add_card(organization_id, customer_id, card_track, card_number))
# print(client.get_programs(organization_id=organization_id))
# print(client.add_customer_to_program(organization_id, customer_id, program_id))
# print(client.refill_customer_balance(organization_id, customer_id, user_wallet, 100))
# sleep(10)

# menu = auth_client.get_menu()
# print("Menu:", menu)
# print("Token:", auth_client.token)

# sleep(10)
# menu = auth_client.get_menu()
# print("Menu:", menu)
# print("Token:", auth_client.token)

# except TokenException as e:
#     print("Error:", e)
