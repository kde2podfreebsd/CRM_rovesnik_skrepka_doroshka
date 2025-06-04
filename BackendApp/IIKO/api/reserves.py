import asyncio
import json
import pprint
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import aiohttp
import dacite

from BackendApp.IIKO.api.core import Client, TokenException, token_required

# from classes import Organization, RestaurantSection, Table, Reservation, ReserveInfo, CreatingReservationCustomer
from BackendApp.IIKO.classes import *
from BackendApp.Logger import LogLevel, logger

# ad-hoc полиморфизм
# iiko_reserves + iiko_custore = iiko_interface, наши ветки в old_versions, удалить ветки.


class Reserves(Client):

    @token_required
    async def get_organizations_with_booking(
        self,
        organization_ids: Optional[List[UUID]] = None,
        return_additional_info: bool = True,
        include_disabled: bool = False,
        return_external_data: Optional[List[str]] = None,
    ) -> Tuple[UUID, List[Organization]]:
        """
        Получите список организаций с учетом указанных параметров.

        Args:
            organization_ids (List[str], optional): Список идентификаторов организаций, которые необходимо вернуть. По умолчанию - все организации из apiLogin.
            return_additional_info (bool): Показывает, нужна ли дополнительная информация об организациях. По умолчанию - True.
            include_disabled (bool): Показывает, должны ли в ответе быть отключенные организации. По умолчанию - False.
            return_external_data (List[str], optional): Список ключей внешних данных, которые необходимо вернуть. По умолчанию - None.

        Returns:
            tuple: Номер операции и список организаций

        Raises:
            TokenException: Если не удалось получить список организаций.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "organizationIds": organization_ids,
            "returnAdditionalInfo": return_additional_info,
            "includeDisabled": include_disabled,
            "returnExternalData": return_external_data,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/reserve/available_organizations", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()

                correlation_id = json_data["correlationId"]

                organizations = [
                    dacite.from_dict(
                        data_class=Organization,
                        data=organization,
                        config=dacite.Config(type_hooks={UUID: UUID}),
                    )
                    for organization in json_data["organizations"]
                ]

                return UUID(correlation_id), organizations

        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при получении организаций. Подробности: {err}"
                "BackendApp.IIKO.api.reserves.Reserves.get_organizations_with_booking"
                )
            raise TokenException(f"Failed to get organizations with bookeng: {err}")

    @token_required
    async def get_terminal_groups_with_booking(self, organization_ids: List[UUID]):
        """
        Получите все терминальные группы указанных организаций, для которых доступно бронирование.

        Args:
            organization_ids (List[str]): Список идентификаторов организаций, для которых запрашивается информация.

        Returns:
            dict: JSON-ответ, содержащий терминальные группы с бронированием.

        Raises:
            TokenException: Если не удалось получить терминальные группы.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"organizationIds": organization_ids}

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/reserve/available_terminal_groups",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()

                return await response.json()
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при получении терминальных групп. Подробности: {err}"
                "BackendApp.IIKO.api.reserves.Reserves.get_terminal_groups_with_booking"
                )
            raise TokenException(f"Failed to get terminal groups with booking: {err}")

    @token_required
    async def get_restaurant_sections_with_booking(
        self, terminal_group_ids: List[UUID], revision: Optional[int] = None
    ) -> Tuple[UUID, List[RestaurantSection], int]:
        """
        Получите все ресторанные разделы указанных терминальных групп, для которых доступно бронирование.
        Тут так же будут все доступные для бронирования столы.

        Args:
            terminal_group_ids (List[UUID]): Список идентификаторов терминальных групп.
            return_schema (bool, optional): Показывает, нужно ли возвращать информацию о расположении столов. По умолчанию - False. Этот аргумент пока что игнорируется. Я спросил у фронтендеров, нужно ли им расположение столов, они (Ваня Фомин), сказал не нужно.
            revision (int, optional): Время последнего изменения. По умолчанию - None.

        Returns:
            Tuple:
                - id операции
                - List[RestaurantSection] - список секций ресторана. Тут же расположены и столы
                - revision (int)



        Raises:
            TokenException: Если не удалось получить ресторанные разделы.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "terminalGroupIds": terminal_group_ids,
            "returnSchema": False,  # Не возвращаем схему ресторана.
            "revision": revision,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/reserve/available_restaurant_sections",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()

                correlation_id = json_data["correlationId"]
                revision = json_data["revision"]
                sections = [
                    dacite.from_dict(
                        data_class=RestaurantSection,
                        data=section,
                        config=dacite.Config(type_hooks={UUID: UUID}),
                    )
                    for section in json_data["restaurantSections"]
                ]

                return UUID(correlation_id), sections, revision
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при получении ресторанных раздел. Подробности: {err}"
                "BackendApp.IIKO.api.reserves.Reserves.get_restaurant_sections_with_booking"
                )
            raise TokenException(f"Failed to get restaurant sections with booking: {err}")

    @token_required
    async def get_reservations_for_sections(
        self, restaurant_section_ids: List[UUID], date_from: str, date_to: Optional[str] = None
    ) -> Tuple[UUID, List[Reservation]]:
        """
        Получите все резервации для указанных ресторанных разделов в заданный временной период.

        Args:
            restaurant_section_ids (List[str]): Список идентификаторов ресторанных разделов.
            date_from (str): Начальное время (локальное для терминала) в формате "yyyy-MM-dd HH:mm:ss.fff".
            date_to (str, optional): Верхняя граница временного интервала (локальное для терминала) в формате "yyyy-MM-dd HH:mm:ss.fff". По умолчанию - None.

        Returns:
            Tuple:
                - correlationId: Id операции
                - reserves (List[Reservation]): - Список броней

        Raises:
            TokenException: Если не удалось получить резервации.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "restaurantSectionIds": restaurant_section_ids,
            "dateFrom": date_from,
            "dateTo": date_to,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/reserve/restaurant_sections_workload",
                headers=headers,
                json=data,
            ) as response:
                json_data = await response.json()
                response.raise_for_status()

                correlation_id = json_data["correlationId"]

                reserves = [
                    dacite.from_dict(
                        data_class=Reservation,
                        data=reservation,
                        config=dacite.Config(type_hooks={UUID: UUID}),
                    )
                    for reservation in json_data["reserves"]
                ]

                return UUID(correlation_id), reserves
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при получении резервации. Подробности: {err}"
                "BackendApp.IIKO.api.reserves.Reserves.get_reservations_for_sections"
                )
            raise TokenException(f"Failed to get reservations for sections: {err}")

    @token_required
    async def create_banquet_or_reservation(
        self, info: InformationForCreatingReservation
    ) -> Tuple[UUID, ReserveInfo]:
        """
        Создайте банкет или резервацию с указанными параметрами.

        Args:
            organization_id (str): Идентификатор организации.
            terminal_group_id (str): Идентификатор терминальной группы.
            customer_phone (str): Телефонный номер клиента.
            duration_in_minutes (int): Продолжительность банкета/резервации в минутах.
            should_remind (bool): Нужно ли напомнить персоналу о подготовке стола заранее.
            table_ids (List[str]): Список идентификаторов зарезервированных столов.
            estimated_start_time (str): Предполагаемое время начала банкета/резервации в формате "yyyy-MM-dd HH:mm:ss.fff".
            external_number (str, optional): Внешний номер банкета/резервации. По умолчанию - None.
            order_id (str, optional): Идентификатор заказа (используется только для банкета). По умолчанию - None.
            guests_count (int, optional): Количество гостей. Устаревший параметр. По умолчанию - None.
            comment (str, optional): Комментарий к банкету/резервации. По умолчанию - None.
            transport_to_front_timeout (int, optional): Таймаут для передачи в iikoFront (устаревший параметр). По умолчанию - None.
            event_type (str, optional): Тип события. По умолчанию - None.
            create_reserve_settings (dict, optional): Параметры создания резервации. По умолчанию - None.

        Returns:
            Tuple:
                - UUID - id операции
                - ReserveInfo - вся информация о бронирование

        Raises:
            TokenException: Если не удалось создать банкет/резервацию.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = asdict(info)
        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/reserve/create", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()

                correlation_id = json_data["correlationId"]

                reserveInfo = [
                    dacite.from_dict(
                        data_class=ReserveInfo,
                        data=json_data["reserveInfo"],
                        config=dacite.Config(type_hooks={UUID: UUID}),
                    )
                ]

                return correlation_id, reserveInfo
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при создании банкета. Подробности: {err}"
                "BackendApp.IIKO.api.reserves.Reserves.create_banquet_or_reservation"
                )
            raise TokenException(f"Failed to create banquet/reservation: {err}")

    @token_required
    async def get_reservation_info(
        self, organization_id: str, reserve_ids: List[str], source_keys: Optional[List[str]] = None
    ) -> Tuple[UUID, List[ReserveInfo]]:
        """
        Получите информацию о бронированиях/резервациях по указанным идентификаторам.

        Args:
            organization_id (str): Идентификатор организации, для которой будет выполнен поиск заказа.
            reserve_ids (List[str]): Список идентификаторов бронирований/резерваций.
            source_keys (List[str], optional): Ключи источника. По умолчанию - None.

        Returns:
            Tuple:
                - Operation ID
                - List[ReserveInfo]

        Raises:
            TokenException: Если не удалось получить информацию о бронированиях/резервациях.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "organizationId": organization_id,
            "reserveIds": reserve_ids,
            "sourceKeys": source_keys,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/reserve/status_by_id", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()

                correlation_id = json_data["correlationId"]

                reserves = [
                    dacite.from_dict(
                        data_class=ReserveInfo,
                        data=reserve,
                        config=dacite.Config(type_hooks={UUID: UUID}),
                    )
                    for reserve in json_data["reserves"]
                ]

                return correlation_id, reserves

        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при получении информации о бронированиях/резервациях. Подробности: {err}"
                "BackendApp.IIKO.api.reserves.Reserves.get_reservation_info"
                )
            raise TokenException(f"Failed to get reservation info: {err}")

    @token_required
    async def add_items_to_order(self, info: AdditionalItemsToReservation) -> UUID:
        """
        Добавьте товары к заказу.

        Args:
            reserve_id (str): Идентификатор банкета/резервации.
            organization_id (str): Идентификатор организации.
            items (List[dict]): Список товаров для добавления к заказу.
            combos (List[dict], optional): Список комбо. По умолчанию - None.

        Returns:
            UUID - id операции

        Raises:
            TokenException: Если не удалось выполнить добавление товаров.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = asdict(info)

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/reserve/add_items", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()

                correlation_id = json_data["correlationId"]

                return correlation_id
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при добавлении товаров. Подробности: {err}"
                "BackendApp.IIKO.api.reserves.Reserves.add_items_to_order"
                )
            raise TokenException(f"Failed to add items to order: {err}")

    @token_required
    async def cancel_reservation(
        self,
        organization_id: str,
        reserve_id: str,
        cancel_reason: Literal["ClientNotAppeared", "ClientRefused", "Other"],
    ) -> UUID:
        """
        Отменить заказ.

        Args:
            organization_id (str): Идентификатор организации, для которой нужно отменить заказ.
            reserve_id (str): Идентификатор заказа, который требуется отменить.
            cancel_reason (str): Причина отмены заказа. Возможные значения: "ClientNotAppeared", "ClientRefused", "Other".

        Returns:
            UUID - id операции

        Raises:
            TokenException: Если не удалось выполнить отмену заказа.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "organizationId": organization_id,
            "reserveId": reserve_id,
            "cancelReason": cancel_reason,
        }

        json_data = None
        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/reserve/cancel", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return json_data["correlationId"]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при отмене заказа. Подробности: {err}"
                "BackendApp.IIKO.api.reserves.Reserves.cancel_reservation"
                )
            raise TokenException(f"Failed to cancel reservation: {err}")

    @token_required
    async def add_payment_to_order(
        self, reserve_id: UUID, organization_id: UUID, payments: List[Payments]
    ) -> UUID:
        """
        Добавить способ оплаты к заказу.

        Args:
            reserve_id (UUID): Идентификатор банкета/резервации.
            organization_id (UUID): Идентификатор организации.
            payments (List[Payments]): Список способов оплаты для добавления к заказу.

        Returns:
            UUID: - id операции

        Raises:
            TokenException: Если не удалось выполнить добавление способа оплаты.
        """

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "reserveId": reserve_id,
            "organizationId": organization_id,
            "payments": [asdict(payment) for payment in payments],
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/reserve/add_payments", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return json_data["correlationId"]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при добавлении способа оплаты. Подробности: {err}"
                "BackendApp.IIKO.api.reserves.Reserves.add_payment_to_order"
                )
            raise TokenException(f"Failed to add payment to order: {err}")


if __name__ == "__main__":

    async def main():

        api_login = "a061da2d-0f0"
        menu_id = "21653"
        organization_id = "9cb23610-e67b-4b76-af30-75bd8a1785f4"
        terminal_group_id = "c4923c8b-1747-b52f-016d-f7c0c79c00cd"
        customer_id = "01330000-6bec-ac1f-823d-08dc36ceec35"
        phone = "89000000001"
        phone_number = "+79222222222"
        program_id = "01330000-6bec-ac1f-c574-08dc36d8330b"
        user_wallet = "01330000-6bec-ac1f-fe19-08dc36d8330c"
        card_track = "8641560005487957"
        card_number = "05487957"

        THIRD_restaurant_section = "5d444c0c-5f3f-408f-85f0-61e64ead0e03"

        customer = CreatingReservationCustomer(
            id=customer_id,
            name="Евгений",
            surname="Пупкин",
            comment="Какой-то комментарий",
            birthdate="2000-10-10 00:00:00.000",
            email="test_mail@mail.ru",
            gender="Male",
            type="regular",
        )

        order = CreatingReservationOrder(
            items=[
                CreatingReservationItem(
                    productId="16ec26a4-7ad6-460a-babc-1ac252cfc293", type="Product", amount=5
                ),
            ]
        )
        estimated_start_time = "2024-04-25 15:00:00.000"
        tables = ["b0eccba9-c414-46d6-a9db-724465e0ac75"]
        reserve_id = "e4e9d436-68cf-4a40-8da9-66a8b40323fe"

        info_for_reservation = InformationForCreatingReservation(
            organizationId=organization_id,
            terminalGroupId=terminal_group_id,
            phone=phone_number,
            tableIds=tables,
            estimatedStartTime=estimated_start_time,
            shouldRemind=True,
            order=order,
            customer=customer,
        )

        additionalReservationItems = AdditionalItemsToReservation(
            reserveId=reserve_id,
            organizationId=organization_id,
            items=[
                CreatingReservationItem(
                    productId="16ec26a4-7ad6-460a-babc-1ac252cfc293", type="Product", amount=2
                ),
            ],
        )

        payment = Payments(
            paymentTypeKind="Cash",
            sum=0,
            paymentTypeId="a681b746-24d1-4f1c-aa71-6af3f1e19567",
            isFiscalizedExternally=True,
            isProcessedExternally=True,
            isPrepay=True,
        )

        client = await Reserves.create(api_login, "Rovesnik")

        try:
            pp = pprint.PrettyPrinter(indent=4)

            # data = await client.get_organizations_with_booking()
            # pp.pprint(data)

            # data = await client.get_terminal_groups_with_booking([organization_id])
            # pp.pprint(data)

            # data = await client.get_restaurant_sections_with_booking([terminal_group_id])
            # pp.pprint(data)

            # data = await client.get_reservations_for_sections(
            #     [THIRD_restaurant_section],
            #     "2024-02-29 19:00:00.000"
            # )
            # pp.pprint(data)

            # Создание заказа
            # data = await client.create_banquet_or_reservation(info_for_reservation)
            # pp.pprint(data)

            # data = await client.add_items_to_order(additionalReservationItems)
            # pp.pprint(data)

            data = await client.get_reservation_info(
                organization_id=organization_id,
                reserve_ids=[reserve_id]
            )
            pp.pprint(data)

            # Банкеты нельзя отменить!!!
            # data = await client.cancel_reservation(
            #     organization_id=organization_id,
            #     reserve_id=reserve_id,
            #     cancel_reason="ClientRefused"
            # )
            # pp.pprint(data)

            # data = await client.add_payment_to_order(
            #     reserve_id=reserve_id, organization_id=organization_id, payments=[payment]
            # )
            # pp.pprint(data)

        except TokenException as e:
            print("Error:", e)

        await client.close_session()

    asyncio.run(main())
