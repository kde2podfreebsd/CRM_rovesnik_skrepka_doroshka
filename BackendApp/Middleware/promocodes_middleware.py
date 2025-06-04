import datetime as dt
from typing import List, Union

from BackendApp import basedir
from BackendApp.Database.DAL.promocode_dal import PromocodeDAL
from BackendApp.Database.Models.promocode_model import Promocode
from BackendApp.Database.Models.promocode_types import _PromocodeType
from BackendApp.Database.session import async_session, DBTransactionStatus

import secrets
import hashlib
import qrcode

class PromocodesMiddleware:

    @staticmethod
    async def create(
        client_chat_id: int,
        number: int,
        name: str,
        operational_info: str,
        description: str,
        type: _PromocodeType,
        end_time: dt.datetime = None,
        is_activated: bool = False,
        weight: int = None
    ):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.create(
                client_chat_id=client_chat_id,
                number=number,
                name=name,
                operational_info=operational_info,
                description=description,
                type=type,
                end_time=end_time,
                is_activated=is_activated,
                weight=weight
            )
            return result

    @staticmethod
    async def update_promocode(
        number: int,
        name: str = None,
        operational_info: str = None,
        description: str = None,
        type: _PromocodeType = None,
        client_chat_id: int = None,
        is_activated: bool = None,
        weight: int = None
    ):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.update_promocode(
                number=number,
                name=name,
                operational_info=operational_info,
                description=description,
                type=type,
                client_chat_id=client_chat_id,
                is_activated=is_activated,
                weight=weight
            )
            return result

    @staticmethod
    async def delete_promocode(number: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.delete_promocode(number=number)
            return result

    @staticmethod
    async def check_promocodes_validity(client_chat_id: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.check_promocodes_validity(client_chat_id=client_chat_id)
            return result

    @staticmethod
    async def get_user_promocodes(client_chat_id: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.get_user_promocodes(client_chat_id=client_chat_id)
            return result

    @staticmethod
    async def get_all_promocodes():
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.get_all_promocodes()
            return result

    @staticmethod
    async def get_promocode_by_id(promocode_id: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.get_promocode_by_id(promocode_id=promocode_id)
            return result

    @staticmethod
    async def get_free_promocodes():
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.get_free_promocodes()
            return result

    @staticmethod
    def generate_random_hash(length=16):
        hash_code = secrets.token_hex(length)
        return hash_code

    @staticmethod
    def generate_qr_code(client_chat_id: int, hashcode: str) -> str:
        qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
        qr.add_data(hashcode)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        qr_path = rf'{basedir}/static/promocodes/{client_chat_id}_{hashcode}.png'
        qr_img.save(qr_path)
        return qr_path

    @staticmethod
    async def add_client_to_promocode(number: int, client_chat_id: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.add_client_to_promocode(number=number, client_chat_id=client_chat_id)
            if (result == DBTransactionStatus.SUCCESS):
                hashcode=PromocodesMiddleware.generate_random_hash()
                result = await pd.update_hashcode(
                    number=number, 
                    hashcode=hashcode
                )
                if (result == DBTransactionStatus.SUCCESS):
                    result = await pd.update_qr_path(
                        number=number,
                        qr_path=PromocodesMiddleware.generate_qr_code(
                            client_chat_id=client_chat_id, 
                            hashcode=hashcode
                        )
                    )
       
            return result

    @staticmethod
    async def activate_promocode(number: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.activate_promocode(number=number)
            return result
    
    @staticmethod
    async def activate_promocode_by_hashcode(hashcode: str):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.activate_promocode_by_hashcode(hashcode=hashcode)
            return result

    @staticmethod
    async def get_free_promocodes_by_type(type: _PromocodeType):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.get_free_promocodes_by_type(promocode_type=type)
            return result

    @staticmethod
    async def update_hashcode(number: int, hashcode: str):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.update_hashcode(number=number, hashcode=hashcode)
            return result
    
    @staticmethod
    async def update_qr_path(number: int, qr_path: str):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.update_qr_path(number=number, qr_path=qr_path)
            return result
    
    @staticmethod
    async def update_activation_time(number: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.update_activation_time(number=number)
            return result
    
    @staticmethod
    async def get_entity_id(number: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.get_entity_id(number=number)
            return result
    
    @staticmethod
    async def get_promocode_by_hashcode(hashcode: str):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.get_promocode_by_hashcode(hashcode=hashcode)
            return result
    
    @staticmethod
    async def get_activated_promocodes_for_client(chat_id: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.get_activated_promocodes_for_client(chat_id=chat_id)
            return result
    
    @staticmethod
    async def get_not_activated_promocodes_for_client(chat_id: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.get_not_activated_promocodes_for_client(chat_id=chat_id)
            return result
    
    @staticmethod
    async def get_by_number(number: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.get_by_number(number=number)
            return result
    
    @staticmethod
    async def validate_promocode_by_number(number: int):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.validate_promocode_by_number(number=number)
            return result
    
    @staticmethod
    async def validate_promocode_by_hashcode(hashcode: str):
        async with async_session() as session:
            pd = PromocodeDAL(session)
            result = await pd.validate_promocode_by_hashcode(hashcode=hashcode)
            return result

if __name__ == "__main__":
    print(len(PromocodesMiddleware.generate_random_hash()))