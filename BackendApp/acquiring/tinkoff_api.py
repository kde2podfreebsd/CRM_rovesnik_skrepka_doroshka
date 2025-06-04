import requests
import os
import json
import hashlib
import asyncio
from dotenv import load_dotenv

# TINKOFF API ENDPOINTS
API_URL = 'https://securepay.tinkoff.ru/v2/'
INIT_URL = 'https://securepay.tinkoff.ru/v2/Init/'
CHARGE_URL = 'https://securepay.tinkoff.ru/v2/Charge/'
CANCEL_URL = 'https://securepay.tinkoff.ru/v2/Cancel'

GET_STATE_URL = 'https://securepay.tinkoff.ru/v2/GetState'
CHECK_ORDER_URL = 'https://securepay.tinkoff.ru/v2/CheckOrder'

SEND_CLOSING_RECEIPT_URL = 'https://securepay.tinkoff.ru/v2/SendClosingReceipt'

load_dotenv()

class MerchantService:

    """
    This class provides wrappers for interacting with Tinkoff API for merchants.

    It offers functionalities for:
        - Authentication: Generates a token using the terminal name and password stored in environment variables.
        - Transaction Initiation: Initializes a transaction by reading data from a JSON file, adding the generated token, and sending a request to the Tinkoff API.
        - Transaction Repetition: Repeats a previously initiated transaction using the same approach as transaction initiation.
        - Payment Status Retrieval: Gets the status of a specific payment by its ID.
        - Order Status Retrieval: Gets the status of a specific order by its ID.
        - Sending Requests: Sends a POST request with JSON data to a specified Tinkoff API URL.
        - Extracting Payment URL: Extracts the payment URL from a successful transaction initiation response.
        - Extracting Order Description, Email, and Phone: Retrieves these details from a provided JSON file (likely containing order information).
    """

    terminal_name = str(os.getenv("TERMINAL_NAME"))
    terminal_password = str(os.getenv("TERMINAL_PASSWORD"))

    @staticmethod
    async def auth(data: dict) -> str:
        """
        Method for generating token by :param data: for interaction with TinkoffAPI
        Args:
            data: dictionary containing mandatorily terminal name and password and other parameters which must be encoded
        Returns:
            token string in ssh256
        """
        t = [] # token

        t.append({"Password": MerchantService.terminal_password})
        for key, value in data.items():
            # embedded objects (dictionaries) and lists are not considered when calculating the token 
            if (not(
                    isinstance(value, dict) or 
                    isinstance(value, list)
                    )
                ):
                t.append(
                    {key: value}
                )

        t = sorted(t, key=lambda x: list(x.keys())[0])
        t = "".join(str(value) for item in t for value in item.values())
        sha256 = hashlib.sha256()
        sha256.update(t.encode('utf-8'))
        t = sha256.hexdigest()

        return t

    @staticmethod
    async def init_transaction(data: dict):
        """
        Method for initializing transaction by :param file: - the name of the json file consisting of the transaction info
        Args:
            file: name of the json file
        Returns:
            response from API, represented as dictionary 
        """
        token = await MerchantService.auth(data=data)
        data["Token"] = token
        
        response = await MerchantService.send_request(
            data=data,
            api=INIT_URL
        )

        return response
    
    @staticmethod
    async def cancel_transaction(data: dict):
        token = await MerchantService.auth(data=data)
        data["Token"] = token

        response = await MerchantService.send_request(
            data=data,
            api=CANCEL_URL
        )
        return response

    @staticmethod
    async def get_payment_status(payment_id: str):
        """
        Method for getting info about the trasaction with :param payment_id:
        Args:
            payemnt_id: payment id
        Returns:
            dictionary
        """
        data = {
            "TerminalKey": MerchantService.terminal_name,
            "PaymentId": payment_id
        }

        token = await MerchantService.auth(data=data)
        data["Token"] = token

        response = await MerchantService.send_request(
            data=data,
            api=GET_STATE_URL
        )

        return response

    @staticmethod
    async def get_order_status(order_id: str):
        """
        Method for getting info about the trasaction with :param order_id:
        Args:
            order_id: order id
        Returns:
            dictionary
        """
        data = {
            "TerminalKey": MerchantService.terminal_name,
            "OrderId": order_id
        }

        token = await MerchantService.auth(data=data)
        data["Token"] = token

        response = await MerchantService.send_request(
            data=data,
            api=CHECK_ORDER_URL
        )

        return response        

    @staticmethod
    # before envoking this method, payment status must be ensured to be CONFIRMED
    # items: list - list of dictionaries
    async def send_receipt(data: dict):

        token = await MerchantService.auth(data=data)
        data["Token"] = token
        

        response = await MerchantService.send_request(
            data=data,
            api=SEND_CLOSING_RECEIPT_URL
        )

        return response

    @staticmethod
    async def send_request(data: dict, api: str) -> requests.models.Response:
        response = requests.post(
            url=api,
            json=data,
            headers={
                'content-type': 'application/json'
            }
        )
        return response

async def main():
    with open("test.json", "r") as jf:
        js = json.load(jf)
    response = await MerchantService.init_transaction(js)
    print(response, type(response))
    data = response.json()
    print(data)
    # # payment_id = response["PaymentId"]
    # # print(payment_id)
    # # response = await MerchantService.get_payment_status(
    # #     payment_id=payment_id
    # # )
    # # print(response, type(response))
    # # print(response.json())
    # order_id = data["OrderId"]
    # print(order_id)
    # response = await MerchantService.get_order_status(
    #     order_id=order_id, 
    # )
    # print(response, type(response))
    # print(response.json())



    # with open("init_widget_tran.json", "r") as jf:
    #     data = json.load(jf)
    # token = await MerchantService.auth(data=data)
    # print(token)
if __name__ == "__main__":
    asyncio.run(main())
