import asyncio
import pprint
from typing import List, Optional
from uuid import UUID

import aiohttp

from BackendApp.IIKO.api.core import Client, TokenException, token_required
from BackendApp.IIKO.classes import (
    CustomerInfo,
    NotActivatedCoupon,
    guestCategorie,
    rawGuestCategorie,
)
from BackendApp.IIKO.iiko_card.card_utils import pop_card_info
from BackendApp.Logger import LogLevel, logger


class Customer(Client):

    @token_required
    async def get_or_create_customer(
        self,
        id: Optional[UUID] = None,
        phone: Optional[str] = None,
        card_track: Optional[str] = None,
        card_number: Optional[str] = None,
        name: Optional[str] = None,
        middle_name: Optional[str] = None,
        sur_name: Optional[str] = None,
        birthday: Optional[str] = None,
        email: Optional[str] = None,
        sex: Optional[int] = 0,
        consent_status: Optional[int] = 0,
        receive_promo_actions_info: Optional[bool] = None,
        referrer_id: Optional[UUID] = None,
        user_data: Optional[str] = None,
        organization_id: Optional[UUID] = None,
    ):
        """
        Эта функция либо получает, либо создает клиента с заданными параметрами.

        Аргументы:
            id (Optional[str]): Идентификатор клиента.
            phone (Optional[str]): Номер телефона клиента.
            card_track (Optional[str]): Дорожка карты клиента.
            card_number (Optional[str]): Номер карты клиента.
            name (Optional[str]): Имя клиента.
            middle_name (Optional[str]): Отчество клиента.
            sur_name (Optional[str]): Фамилия клиента.
            birthday (Optional[str]): День рождения клиента.
            email (Optional[str]): Электронная почта клиента.
            sex (Optional[int]): Пол клиента.
            consent_status (Optional[int]): Статус согласия клиента.
            receive_promo_actions_info (Optional[bool]): Статус получения информации о промо-акциях.
            referrer_id (Optional[str]): Идентификатор реферера клиента.
            user_data (Optional[str]): Дополнительные данные пользователя.

        Возвращает:
            Возвращает id клиента.

        Вызывает:
            ValueError: Если card_track или card_number не указаны, когда указан другой.
            TokenException: Если происходит сбой при создании клиента.
        """

        if (card_track and not card_number) or (not card_track and card_number):
            logger.log(
                LogLevel.ERROR, 
                "card_track и card_number должны быть указаны одновременно."
                "BackendApp.IIKO.api.customer.Customer.get_or_create_customer"
                )
            raise ValueError(
                "Если указаны card_track или card_number, то оба этих аргумента должны быть указаны."
            )

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "id": id,
            "phone": phone,
            "cardTrack": card_track,
            "cardNumber": card_number,
            "name": name,
            "middleName": middle_name,
            "surName": sur_name,
            "birthday": birthday,
            "email": email,
            "sex": sex,
            "consentStatus": consent_status,
            "shouldReceivePromoActionsInfo": receive_promo_actions_info,
            "referrerId": referrer_id,
            "userData": user_data,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer/create_or_update",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return json_data["id"]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при создании клиента. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.get_or_create_customer"
                )
            raise TokenException(f"Failed to create customer: {err}")

    @token_required
    async def get_customer_info(
        self,
        phone: Optional[str] = None,
        id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
    ):
        """
        Получает информацию о клиенте на основе идентификатора организации, номера телефона или идентификатора клиента.

        Args:
            phone (Optional[str], optional): Номер телефона клиента. По умолчанию None.
            id (Optional[str], optional): Идентификатор клиента. По умолчанию None.

        Returns:
            dict: Информация о клиенте в классе CustomerInfo.

        Raises:
            ValueError: Если указаны и номер телефона, и идентификатор, или если не указан ни номер телефона, ни идентификатор.
            TokenException: Если произошла ошибка при получении информации о клиенте.
        """

        if (phone and id) or (not phone and not id):
            raise ValueError("Укажите только один из аргументов: phone или id")

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "phone": phone,
            "id": id,
            "type": "phone" if phone else "id",
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer/info", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return CustomerInfo(**json_data if json_data else {})
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при получении информации о клиента. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.get_customer_info"
                )
            raise TokenException(f"Failed to get customer info: {err}")

    @token_required
    async def add_customer_to_program(
        self, customer_id: UUID, program_id: UUID, organization_id: Optional[UUID] = None
    ):
        """
        Добавляет клиента в программу лояльности.

        Аргументы:
            organization_id (str): Идентификатор организации.
            customer_id (str): Идентификатор клиента.
            program_id (str): Идентификатор программы лояльности.

        Возвращает:
            dict: id воллета программы клиента.

        Вызывает:
            TokenException: В случае ошибки при добавлении клиента в программу.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "customerId": customer_id,
            "programId": program_id,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer/program/add",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return json_data["userWalletId"]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при добавлении клиента в программу лояльности. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.add_customer_to_program"
                )
            raise TokenException(f"Failed to add customer to the program: {err}")

    @token_required
    async def refill_customer_balance(
        self,
        customer_id: UUID,
        wallet_id: UUID,
        sum: float,
        comment: Optional[str] = None,
        organization_id: Optional[UUID] = None,
    ):
        """
        Пополняет баланс клиента.

        Аргументы:
            customer_id (str): Идентификатор клиента.
            wallet_id (str): Идентификатор кошелька.
            sum (float): Сумма, которая будет добавлена на кошелек.
            comment (Optional[str], optional): Комментарий к пополнению. По умолчанию None.

        Возвращает:
            None

        Вызывает:
            TokenException: Если возникла проблема с токеном или запросом API.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "customerId": customer_id,
            "walletId": wallet_id,
            "sum": sum,
            "comment": comment,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer/wallet/topup",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return None
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при пополнении баланса клиента. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.refill_customer_balance"
                )
            raise TokenException(f"Failed to add customer to the program: {err}")

    @token_required
    async def add_card(
        self, customer_id: UUID, card_track: str, card_number: str, organization_id: UUID = None
    ):
        """
        Добавляет карту для клиента в программу лояльности указанной организации.

        Args:
            customer_id (str): Идентификатор клиента.
            card_track (str): Данные трека карты.
            card_number (str): Номер карты.

        Returns:
            dict: JSON-ответ от вызова API.

        Raises:
            TokenException: Если происходит ошибка при деобавлении клиента в программу.
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "customerId": customer_id,
            "cardTrack": card_track,
            "cardNumber": card_number,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer/card/add", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при пополнении добавлении карты клиенту. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.add_card"
                )
            raise TokenException(f"Failed to add customer to the program: {err}")

    @token_required
    async def delete_card(self, customer_id: UUID, card_track: str, organization_id: UUID = None):
        """
        Функция для удаления карты для конкретного клиента в организации.

        Параметры:
            customer_id (str): Идентификатор клиента.
            card_track (str): Дорожка карты, которую нужно удалить.

        Возвращает:
            None

        Вызывает:
            TokenException: Если происходит сбой при удалении карты.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "customerId": customer_id,
            "cardTrack": card_track,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer/card/remove",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return None
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при пополнении удалении карты клиенту. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.delete_card"
                )
            raise TokenException(f"Failed to remove customer from the program: {err}")

    @token_required
    async def hold_money(
        self,
        transaction_id: Optional[UUID],
        customer_id: UUID,
        wallet_id: UUID,
        sum: float,
        comment: Optional[str] = None,
        organization_id: Optional[UUID] = None,
    ):
        """
        Функция для удержания денег в кошельке клиента для транзакции.

        Аргументы:
            transaction_id (Optional[str]): Идентификатор транзакции.
            customer_id (str): Идентификатор клиента.
            wallet_id (str): Идентификатор кошелька.
            sum (float): Сумма денег для удержания.
            comment (Optional[str], optional): Необязательный комментарий для транзакции. По умолчанию None.

        Возвращает:
            transactionId.

        Вызывает:
            TokenException: Если возникает ошибка при удержании денег в кошельке клиента.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "transactionId": transaction_id,
            "customerId": customer_id,
            "walletId": wallet_id,
            "sum": sum,
            "comment": comment,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer/wallet/hold",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return json_data["transactionId"]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при удержании денег в кошельке клиента. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.hold_money"
                )
            raise TokenException(f"Failed to add customer to the program: {err}")

    @token_required
    async def cancel_hold_money(self, transaction_id: UUID, organization_id: Optional[UUID] = None):
        """
        Функция для отмены блокировки средств с заданным идентификатором организации и идентификатором транзакции.

        Args:
            transaction_id (UUID): Идентификатор транзакции.

        Returns:
            None.

        Raises:
            TokenException: Если не удается отменить блокировку с заданным сообщением об ошибке.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "transactionId": transaction_id,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer/wallet/cancel_hold",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return None
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при отмене блокировки средств с заданным идентификатором организации и идентификатором транзакции. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.cancel_hold_money"
                )
            raise TokenException(f"Failed to add customer to the program: {err}")

    @token_required
    async def withdraw_balance(
        self,
        customer_id: UUID,
        wallet_id: UUID,
        sum: float,
        comment: Optional[str] = None,
        organization_id: Optional[UUID] = None,
    ):
        """
        Функция для снятия денег с баланса клиента.

        Аргументы:
            customer_id (str): Идентификатор клиента.
            wallet_id (str): Идентификатор кошелька.
            sum (float): Сумма для вывода.
            comment (Optional[str], optional): Дополнительный комментарий для вывода. По умолчанию None.

        Возвращает:
            None.

        Вызывает:
            TokenException: Если возникла проблема с токеном или запросом к API.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "customerId": customer_id,
            "walletId": wallet_id,
            "sum": sum,
            "comment": comment,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer/wallet/chargeoff",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return None
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при снятии денег с баланса клиента. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.withdraw_balance"
                )
            raise TokenException(f"Failed to add customer to the program: {err}")

    @token_required
    async def full_create_customer(
        self,
        program_id: Optional[UUID] = None,
        id: Optional[UUID] = None,
        phone: Optional[str] = None,
        name: Optional[str] = None,
        middle_name: Optional[str] = None,
        sur_name: Optional[str] = None,
        birthday: Optional[str] = None,
        email: Optional[str] = None,
        sex: Optional[int] = 0,
        consent_status: Optional[int] = 0,
        receive_promo_actions_info: Optional[bool] = None,
        referrer_id: Optional[UUID] = None,
        user_data: Optional[str] = None,
        organization_id: Optional[UUID] = None,
    ):
        """
        Эта функция создает нового клиента с заданными параметрами и добавляет его в программу. Затем она возвращает информацию о клиенте.
        Телефон или айди клиента обязательны.

        Аргументы:
            program_id: UUID программы.
            id: Необязательный UUID клиента.
            phone: Необязательный номер телефона клиента.
            name: Необязательное имя клиента.
            middle_name: Необязательное отчество клиента.
            sur_name: Необязательная фамилия клиента.
            birthday: Необязательная дата рождения клиента.
            email: Необязательная электронная почта клиента.
            sex: Необязательное целое число, представляющее пол клиента.
            consent_status: Необязательное целое число, представляющее статус согласия клиента.
            receive_promo_actions_info: Необязательное булево значение, представляющее, хочет ли клиент получать информацию о рекламных акциях.
            referrer_id: Необязательный UUID реферрера.
            user_data: Необязательные пользовательские данные.

        Возвращает:
            Информация о клиенте.
        """
        try:
            card_info = pop_card_info()
            customer_id = await self.get_or_create_customer(
                id,
                phone,
                card_info["Track"],
                card_info["Number"],
                name,
                middle_name,
                sur_name,
                birthday,
                email,
                sex,
                consent_status,
                receive_promo_actions_info,
                referrer_id,
                user_data,
                organization_id,
            )
            if program_id:
                await self.add_customer_to_program(customer_id, program_id, organization_id)
            return await self.get_customer_info(id=customer_id, organization_id=organization_id)
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при создании клиента. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.full_create_customer"
                )
            raise TokenException(f"Failed to create customer: {err}")

    @token_required
    async def get_raw_customer_categories(self, organization_id: Optional[UUID] = None):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer_category",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return [rawGuestCategorie(**i) for i in json_data["guestCategories"]]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при получении категорий. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.get_raw_customer_categories"
                )
            raise TokenException(f"Failed to add customer to the program: {err}")

    async def get_full_customer_categories(
        self, organization_id: Optional[UUID] = None
    ) -> List[guestCategorie]:
        raw_categories = await self.get_raw_customer_categories(organization_id)
        result = []
        for category in raw_categories:
            result.append(self.pack_raw_category(category))
        return result

    def pack_raw_category(self, category: rawGuestCategorie):
        sign = ", "
        if category.name.split(sign)[0] == "level":
            data = dict(
                id=category.id,
                category=category.name.split(sign)[0],
                level=int(category.name.split(sign)[1]),
                spend_money_amount=float(category.name.split(sign)[2]),
                name=category.name.split(sign)[3],
                cashback=float(category.name.split(sign)[4]),
                isActive=category.isActive,
                isDefaultForNewGuests=category.isDefaultForNewGuests,
            )
        elif category.name.split(sign)[0] == "additional":
            data = dict(
                id=category.id,
                category=category.name.split(sign)[0],
                name=category.name.split(sign)[1],
                cashback=float(category.name.split(sign)[2]),
                isActive=category.isActive,
                isDefaultForNewGuests=category.isDefaultForNewGuests,
            )
        return guestCategorie(**data)

    @token_required
    async def get_customer_loyalty_info(self, iiko_id: UUID):
        customer_info = await self.get_customer_info(id=iiko_id)
        return [self.pack_raw_category(rawGuestCategorie(**i)) for i in customer_info.categories]
    
    @token_required
    async def get_additional_categorie(self, organization_id: Optional[UUID] = None):
        categories = await self.get_full_customer_categories(self.organization_id if not organization_id else organization_id)
        return [category for category in categories if category.category == "additional"][0]
    
    @token_required
    async def add_addictional_categorie_to_user(
        self, 
        customer_id: UUID, 
        organization_id: Optional[UUID] = None
    ):
        category = await self.get_additional_categorie(
            self.organization_id if not organization_id else organization_id
        )
        return await self.add_category_to_customer(
            customer_id, 
            category.id, 
            organization_id if not organization_id else self.organization_id
        )
        
    @token_required
    async def remove_addictional_categorie_from_user(
        self, 
        customer_id: UUID, 
        organization_id: Optional[UUID] = None
    ):
        category = await self.get_additional_categorie(
            self.organization_id if not organization_id else organization_id
        )
        return await self.remove_category_from_customer(
            customer_id, 
            category.id,
            organization_id if not organization_id else self.organization_id
        )
        
    @token_required
    async def add_category_to_customer(
        self, customer_id: UUID, category_id: UUID, organization_id: Optional[UUID] = None
    ):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "customerId": customer_id,
            "categoryId": category_id,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer_category/add",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return None
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при добавлении клиента в программу. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.add_category_to_customer"
                )
            raise TokenException(f"Failed to add customer to the program: {err}")

    @token_required
    async def remove_category_from_customer(
        self, customer_id: UUID, category_id: UUID, organization_id: Optional[UUID] = None
    ):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "customerId": customer_id,
            "categoryId": category_id,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/customer_category/remove",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return None
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при удалении клиента из программы. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.remove_category_from_customer"
                )
            raise TokenException(f"Failed to add customer to the program: {err}")

    @token_required
    async def non_activated_promocodes(
        self,
        series: str = 1,
        pageSize: int = 1,
        page: int = 1,
        organization_id: Optional[UUID] = None,
    ):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "series": series,
            "pageSize": pageSize,
            "page": page,
            "organizationId": self.organization_id if not organization_id else organization_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/loyalty/iiko/coupons/by_series", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()

                return [NotActivatedCoupon(**i) for i in json_data["notActivatedCoupon"]]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при получении не активированных промокодов. Подробности: {err}"
                "BackendApp.IIKO.api.customer.Customer.non_activated_promocodes"
                )
            raise TokenException(f"Failed to get menu: {err}")


if __name__ == "__main__":

    async def main():

        menu_id = "21653"

        organization_id = "9cb23610-e67b-4b76-af30-75bd8a1785f4"

        terminal_group_id = "c4923c8b-1747-b52f-016d-f7c0c79c00cd"
        customer_id = "01330000-6bec-ac1f-739f-08dc53e7c5e2"
        phone = "89000000001"
        phone_number = "+79222222222"
        program_id = "01330000-6bec-ac1f-c574-08dc36d8330b"
        user_wallet = "01330000-6bec-ac1f-fe19-08dc36d8330c"
        card_track = "8641560005487957"
        card_number = "05487957"

        THIRD_restaurant_section = "5d444c0c-5f3f-408f-85f0-61e64ead0e03"

        customer = {
            "id": customer_id,
            "name": "ПРОВЕРКА",
            "surname": None,
            "comment": None,
            "birthdate": None,
            "email": None,
            "shouldReceiveOrderStatusNotifications": None,
            "gender": "Male",
            "type": "regular",
        }

        estimated_start_time = "2024-03-25 15:00:00.000"
        tables = ["b0eccba9-c414-46d6-a9db-724465e0ac75"]
        reserve_id = "c20817c0-d194-43bf-8fa9-ce632c67d74e"
        second_org_id = "647c7cf3-b841-45c9-8e07-35509675ec9b"

        level_1 = "ca93375f-e9c1-4943-87e2-4cd4abceeada"
        level_2 = "59537b23-dc2d-4719-80eb-864f616aea6b"
        level_3 = "d09bb468-837b-4dd5-aa57-e5770c180408"
        level_4 = "0685a167-5d90-483c-87af-f7b5bb15eaff"
        level_5 = "814a4adb-e965-4736-9b7b-e5ab39c28a9a"
        level_6 = "faa46f79-4c5e-427e-bcf2-5d34dd61d1cc"
        podpiska = "bd3c8b28-1d50-4118-bc22-c426aaa85972"
        client = ""

        # client = await Customer.create(api_login, "Rovesnik")

        try:
            pp = pprint.PrettyPrinter(indent=4)
            # print(await client.get_restaurant_sections_with_booking([terminal_group_id]))
            # print(
            #     await client.get_or_create_customer(
            #         name="TEST DANIL", phone="89000000011", organization_id=rovesnik_id
            #     )
            # )
            # print(await client.get_customer_info(id=customer_id))
            # print(
            #     await client.refill_customer_balance(
            #         customer_id=customer_id,
            #         wallet_id=user_wallet,
            #         sum=-500,
            #     )
            # )
            # print(await client.withdraw_balance(customer_id, user_wallet, 500))
            # print(await client.get_customer_categories(), "\n")
            # print(await client.add_category_to_customer(customer_id, level_1))
            # print(await client.add_category_to_customer(customer_id, podpiska))
            # print(await client.get_programs(organization_id=skrepka_id), "\n")
            # print(await client.get_programs(organization_id=dorozhka_id))
            # print("03650000-6bec-ac1f-4b0e-08dc47343911")
            # print(await client.get_organizations())
            # print(await client.get_full_customer_categories())
            # print(await client.get_full_customer_categorie())
            # print(pop_card_info())

        except TokenException as e:
            print("Error:", e)

        await client.close_session()

    asyncio.run(main())
