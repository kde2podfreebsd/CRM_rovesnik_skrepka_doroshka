import requests
import os
import json
import hashlib
import asyncio
from BackendApp.acquiring.tinkoff_api import MerchantService

INIT_PAYMENTS_URL = 'https://securepay.tinkoff.ru/v2/InitPayments'
GET_QR_URL = 'https://securepay.tinkoff.ru/v2/GetQr'
QR_MEMBERS_LIST_URL = 'https://securepay.tinkoff.ru/v2/QrMembersList'
GET_QR_STATE_URL = 'https://securepay.tinkoff.ru/v2/GetQRState'
GET_ACCOUNT_QR_LIST_URL = 'https://securepay.tinkoff.ru/v2/GetAccountQrList'
GET_ADD_ACCOUNT_QR_STATE_URL = 'https://securepay.tinkoff.ru/v2/GetAddAccountQrState'

class MerchantServiceSpb(MerchantService):

    @staticmethod
    # initializaing transaction for spb qr payment in widget

    #payment_info: list as it contains InfoEmail - the user's email where notification will be sent - and PaymentData - dict
    async def init_widget_transaction(
        data: dict
    ):
        # token = await MerchantService.auth(data=data)
        # data.update(
        #     {
        #         "Token": token
        #     }
        # )
        # print(token)
        print(data) 
        response = await MerchantService.send_request(
            data=data,
            api=INIT_PAYMENTS_URL
        )
        
        return response

    @staticmethod
    async def get_qr(payment_id: int):
        data = {
            "TerminalKey": MerchantService.terminal_name,
            "PaymentId": payment_id
        }
        token = await MerchantService.auth(data=data)
        data["Token"] = token

        response = await MerchantService.send_request(
            data=data,
            api=GET_QR_URL
        )

        return response

    @staticmethod
    async def get_users_bank_qr(payment_id: int):
        data = {
            "TerminalKey": MerchantService.terminal_name,
            "PaymentId": payment_id
        }
        token = await MerchantService.auth(data=data)
        data["Token"] = token

        response = await MerchantService.send_request(
            data = data,
            api=QR_MEMBERS_LIST_URL
        )

        return response
    
    @staticmethod
    async def get_qr_state(payment_id: int):
        data = {
            "TerminalKey": MerchantService.terminal_name,
            "PaymentId": payment_id
        }
        token = await MerchantService.auth(data=data)
        data["Token"] = token

        response = await MerchantService.send_request(
            data=data,
            api=GET_QR_STATE_URL
        )

        return response
    
    @staticmethod
    async def get_account_qr_list():
        data = {
            "TerminalKey": MerchantService.terminal_name
        }
        token = await MerchantService.auth(data=data)
        data["Token"] = token

        response = await MerchantService.send_request(
            data=data,
            api=GET_ACCOUNT_QR_LIST_URL
        )

        return response
    
    @staticmethod
    async def get_add_account_qr_state(request_key: str):
        data = {
            "TerminalKey": MerchantService.terminal_name,
            "RequestKey": request_key
        }
        token = await MerchantService.auth(data=data)
        data["Token"] = token

        response = await MerchantService.send_request(
            data=data,
            api=GET_ADD_ACCOUNT_QR_STATE_URL
        )

        return response

async def main():
    with open("init_widget_tran.json", "r") as js:
        data = json.load(js)
    response = await MerchantServiceSpb.init_widget_transaction(data=data)
    print(response, type(response))


    # rd = response.json()
    # order_id = rd["PaymentId"]
    # print(order_id)
    # response = await MerchantService.get_order_status(
    #     order_id=order_id, x
    # )
    # print(response, type(response))
    # print(response.json())

if __name__ == "__main__":
    asyncio.run(main())