from BackendApp.acquiring.tinkoff_api import MerchantService
from enum import Enum

class CalculationSubject(Enum):
    """Calculation subjects"""

    COMMODITY = "commodity"
    EXCISE = "excise"
    JOB = "job"
    SERVICE = "service"
    GAMBLING_BET = "gambling_bet"
    GAMBLING_PRIZE = "gambling_prize"
    LOTTERY = "lottery"
    LOTTERY_PRIZE = "lottery_prize"
    INTELLECTUAL_ACTIVITY = "intellectual_activity"
    PAYMENT = "payment"
    AGENT_COMMISSION = "agent_commission"
    COMPOSITE = "composite"
    ANOTHER = "another"


class EntityProcessor:
    
    @staticmethod
    # we have to ensure that email or phone is present in client's info 
    async def form_receipt(
        ffd_ver: str, 
        tax: str, 
        email: str | None, 
        phone: str | None,
        items: dict
    ) -> dict:
        return {
            "FfdVersion": ffd_ver,
            "Taxation": tax, 
            "Phone": phone,
            "Email": email,
            "Items": items
        }

    @staticmethod
    # method forms a single item with all fields required by the API, but in order to send a ticket to a customer with
    # multiple items, they should be put into list

    # price: inputted as string in format as follows: price as integer = 123, price as integer in API = 12300

    # measurement_unit: input "шт" as default, otherwise address api docs
    async def form_item(
        name: str, 
        price: int, 
        quantity: int,
        tax: str,
        payment_method: str,
        payment_obj: str,
        measurement_unit: str 
    ) -> dict:
        amount = quantity * price 

        return {
            "Name": name,
            "Price": price,
            "Quantity": quantity,
            "Amount": amount,
            "Tax": tax,
            "PaymentMethod": payment_method,
            "PaymentObject": payment_obj,
            "MeasurementUnit": measurement_unit 
        }

    @staticmethod
    async def form_payment_data(
        amount: int,
        order_id: str,
        description: str,
        data: dict
    ) -> dict:
        return {
            "TerminalKey": MerchantService.terminal_name,
            "Amount": amount,
            "OrderId": order_id,
            "Description": description,
            "DATA": data
        }

    @staticmethod
    # payment_info: payment_info is a list containing of two values: InfoEmail - email of the buyer - and 
    # PaymentData: info about the payment: TerminalKey, Amount (in copecs), OrderId, Description, DATA, Receipt
    async def form_payment_info(
        payment_info: list, 
        payment_data: dict
    ) -> dict:
        INFO_EMAIL = 0
        PAYMENT_DATA = 1

        info_email = payment_info[INFO_EMAIL]
        payment_data = payment_info[PAYMENT_DATA]

        return {
            "payemnetInfo": {
                "InfoEmail": info_email,
                "PaymentData": payment_data 
            }
        }