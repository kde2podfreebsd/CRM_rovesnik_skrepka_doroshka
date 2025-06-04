import asyncio
import dataclasses
import pprint
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID
from BackendApp.Logger import LogLevel, logger

import aiohttp
from BackendApp.IIKO.classes import (
    ChequeAdditionalInfo,
    Combo,
    CustomerInfo,
    Order,
    OrderCreateResponse,
    OrderItem,
    OrderResponse,
    Payments,
    Tip,
    addOrderItemsSettings,
    createOrderSettings,
    orderInfo,
)
from BackendApp.IIKO.api.core import Client, TokenException, token_required


class CoreOrder(Client):

    @token_required
    async def create_order(
        self,
        terminal_group_id: UUID,
        order: Order,
        createOrderSettings: Optional[createOrderSettings] = None,
        organization_id: Optional[UUID] = None,
    ):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "terminalGroupId": terminal_group_id,
            "organizationId": self.organization_id if not organization_id else organization_id,
            "order": dataclasses.asdict(order, dict_factory=dict),
            "createOrderSettings": createOrderSettings,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/order/create", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()

                return OrderCreateResponse(**json_data)
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при создании заказа. Подробности: {err}"
                "BackendApp.IIKO.api.order.CoreOrder.create_order"
                )
            raise TokenException(f"Failed to get menu: {err}")

    @token_required
    async def retrieve_orders_by_ids(
        self,
        order_ids: List[UUID],
        source_keys: Optional[List[str]] = None,
        pos_order_ids: Optional[List[UUID]] = None,
        return_external_data_keys: Optional[List[str]] = None,
        organization_ids: Optional[List[UUID]] = None,
    ):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "sourceKeys": source_keys,
            "organizationIds": [self.organization_id] if not organization_ids else organization_ids,
            "orderIds": order_ids,
            "posOrderIds": pos_order_ids,
            "returnExternalDataKeys": return_external_data_keys,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/order/by_id", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return OrderResponse(**json_data)
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при получении заказов. Подробности: {err}"
                "BackendApp.IIKO.api.order.CoreOrder.retrieve_orders_by_ids"
                )
            raise TokenException(f"Failed to retrieve orders: {err}, {response.text}")

    @token_required
    async def retrive_orders_by_tables(
        self,
        table_ids: List[UUID],
        source_keys: Optional[List[str]] = None,
        statuses: Optional[Literal["New", "Bill", "Closed", "Deleted"]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        organization_ids: Optional[List[UUID]] = None,
    ):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "sourceKeys": source_keys,
            "organizationIds": [self.organization_id] if not organization_ids else organization_ids,
            "tableIds": table_ids,
            "statuses": statuses,
            "dateFrom": date_from.strftime("%Y-%m-%d %H:%m:%s.%f") if date_from else None,
            "dateTo": date_to.strftime("%Y-%m-%d %H:%m:%s.%f") if date_to else None,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/order/by_table", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return OrderResponse(**json_data)
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при получении заказов. Подробности: {err}"
                "BackendApp.IIKO.api.order.CoreOrder.retrive_orders_by_tables"
                )
            raise TokenException(f"Failed to retrieve order by table: {err}")

    @token_required
    async def add_order_items(
        self,
        order_id: UUID,
        items: List[OrderItem],
        add_order_items_settings: addOrderItemsSettings = None,
        combos: Optional[List[Combo]] = None,
        organization_id: Optional[UUID] = None,
    ):

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "addOrderItemsSettings": add_order_items_settings,
            "orderId": order_id,
            "organizationId": self.organization_id if not organization_id else organization_id,
            "items": ([dataclasses.asdict(item, dict_factory=dict) for item in items]),
            "combos": (
                [dataclasses.asdict(combo, dict_factory=dict) for combo in combos]
                if combos
                else None
            ),
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/order/add_items", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return json_data["correlationId"]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при добавлении заказа. Подробности: {err}"
                "BackendApp.IIKO.api.order.CoreOrder.add_order_items"
                )
            raise TokenException(f"Failed to add order items: {err}")

    @token_required
    async def close_order(
        self,
        order_id: UUID,
        cheque_additional_info: Optional[ChequeAdditionalInfo] = None,
        organization_id: Optional[UUID] = None,
    ):

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "chequeAdditionalInfo": (
                dataclasses.asdict(cheque_additional_info, dict_factory=dict)
                if cheque_additional_info
                else None
            ),
            "organizationId": self.organization_id if not organization_id else organization_id,
            "orderId": order_id,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/order/close", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return json_data["correlationId"]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при закрытии заказа. Подробности: {err}"
                "BackendApp.IIKO.api.order.CoreOrder.close_order"
                )
            raise TokenException(f"Failed to close order: {err}")

    @token_required
    async def change_table_orders_payment(
        self,
        order_id: UUID,
        payments: List[Payments],
        organization_id: Optional[UUID] = None,
        tips: Optional[List[Tip]] = None,
    ):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "organizationId": self.organization_id if not organization_id else organization_id,
            "orderId": order_id,
            "payments": [dataclasses.asdict(payment, dict_factory=dict) for payment in payments],
            "tips": [dataclasses.asdict(tip, dict_factory=dict) for tip in tips] if tips else None,
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/order/change_payments", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return json_data["correlationId"]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при изменении оплаты. Подробности: {err}"
                "BackendApp.IIKO.api.order.CoreOrder.change_table_orders_payment"
                )
            raise TokenException(f"Failed to change payments: {err}")

    @token_required
    async def add_customer_to_order(
        self,
        order_id: UUID,
        customer: CustomerInfo,
        organization_id: Optional[UUID] = None,
    ):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "organizationId": self.organization_id if not organization_id else organization_id,
            "orderId": order_id,
            "customer": dataclasses.asdict(customer, dict_factory=dict),
        }
        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/order/add_customer", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return json_data["correlationId"]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при добавлении клиента. Подробности: {err}"
                "BackendApp.IIKO.api.order.CoreOrder.add_customer_to_order"
                )
            raise TokenException(f"Failed to add customer: {err}")

    @token_required
    async def add_order_payments(
        self,
        order_id: UUID,
        payments: List[Payments],
        tips: Optional[List[Tip]] = None,
        organization_id: Optional[UUID] = None,
    ):

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "orderId": order_id,
            "tips": [dataclasses.asdict(tip, dict_factory=dict) for tip in tips] if tips else None,
            "organizationId": self.organization_id if not organization_id else organization_id,
            "payments": [dataclasses.asdict(payment, dict_factory=dict) for payment in payments],
        }

        json_data = None

        try:
            async with self.session_s.post(
                f"{self.base_url}/api/1/order/add_payments", headers=headers, json=data
            ) as response:
                json_data = await response.json()
                response.raise_for_status()
                return json_data["correlationId"]
        except (aiohttp.ClientError, ValueError) as err:
            logger.log(
                LogLevel.ERROR, 
                f"Произошла ошибка при добавлении оплат. Подробности: {err}"
                "BackendApp.IIKO.api.order.CoreOrder.add_order_payments"
                )
            raise TokenException(f"Failed to add payments: {err}")


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
        order_id = "484c4ca1-7726-403d-8bbb-8de6c474c39c"

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
        order_item = OrderItem(
            productId="42425143-8ef7-4fe9-854e-6a53e27fefba",
            type="Product",
            amount=1,
        )

        client = await CoreOrder.create(api_login, "Rovesnik")

        try:
            # print(
            #     await client.create_order(
            #         terminal_group_id,
            #         organization_id,
            #         Order(
            #             items=[
            #                 OrderItem(
            #                     productId="42425143-8ef7-4fe9-854e-6a53e27fefba",
            #                     type="Product",
            #                     amount=1,
            #                 )
            #             ],
            #         ),
            #         createOrderSettings=None,
            #     )
            # )

            # print(await client.retrieve_orders_by_ids([organization_id], [order_id]))
            # print(await client.retrive_orders_by_tables([organization_id], tables))
            print(await client.add_order_items(order_id, organization_id, items=[order_item]))

        except TokenException as e:
            print("Error:", e)

        await client.close_session()

    asyncio.run(main())
