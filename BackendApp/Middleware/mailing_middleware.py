from BackendApp.Database.DAL.mailing_dal import MailingDAL
from BackendApp.Database.DAL.client_dal import ClientDAL
from BackendApp.Database.Models.mailing_model import Mailing
from BackendApp.Database.session import async_session
from BackendApp.Database.DAL.db_presets_dal import *
from BackendApp.Database.session import DBTransactionStatus

from BackendApp.TelegramBots.HeadBot.Config import bot
from telebot import types
from typing import Union, Optional
import asyncio
import os
import math

URL = 0
BUTTON_TEXT = 1

class MailingMiddleware:

    @staticmethod
    async def send_msg(
        chat_id: int,
        mailing_name: str
    ):
        input_media = []
        async with async_session() as session:
            client_dal = ClientDAL(session)
            mailing_dal = MailingDAL(session)
            existing_client = await client_dal.get_client(chat_id=chat_id)
            if (isinstance(existing_client, Client)):
                mailing = await mailing_dal.get_mailing(mailing_name=mailing_name)
                if (mailing == DBTransactionStatus.NOT_EXIST):
                    return mailing
            else:
                return existing_client

        # despite being directly stated in documentation, that .send_media_group
        # requires at least 2 InputMedia objects, it works fine with only one
        if (mailing.photo_paths):
            for photo_path in mailing.photo_paths:
                file = open(photo_path, "rb")
                input_file = types.InputFile(file=file)
                input_media.append(
                    types.InputMediaPhoto(
                        media=input_file
                    )
                )
        if (mailing.video_paths):
            for video_path in mailing.video_paths:
                file = open(video_path, "rb")
                input_file = types.InputFile(file=file)
                input_media.append(
                    types.InputMediaVideo(
                        media=input_file
                    )
                )
        try:
            if (len(input_media) >= 1):
                await bot.send_media_group(
                    chat_id=chat_id,
                    media=input_media
                )
        except Exception as e:
            return e
        
        keyboard = []
        if (mailing.url_buttons):
            for button in mailing.url_buttons:
                keyboard.append(
                    [
                        types.InlineKeyboardButton(
                            text=button[BUTTON_TEXT],
                            url=button[URL],
                        )
                    ]
                )
        
        await bot.send_message(
            chat_id=chat_id,
            text=mailing.text,
            reply_markup=types.InlineKeyboardMarkup(
                keyboard=keyboard,
                row_width=2
            ),
            parse_mode="HTML"
        )

        # InputMediaPhoto and InputMediaVideo cannot be mixed with InputMediaDocument, 
        # therefore they are sent in two parts, which are devided by input_media.clear()

        input_media.clear()
        if (mailing.document_paths):
            for document_path in mailing.document_paths:
                file = open(document_path, "rb")
                try:
                    await bot.send_document(
                        chat_id=chat_id,
                        document=file
                    )
                except Exception as e:
                    return e
        
        return DBTransactionStatus.SUCCESS
    
    """
    +------------------------------------------------------------------------------+
    All methods connected with Mailing interactions:
    - launch aplha-beta mailing: launch_mailing_alpha, launch_mailing_beta
    - create mailing with all fields filled: create_full_mailing
    - create empty mailing only with text, preset and mailing_name: create_mailing
    - update all mailing fields: update_mailing
    - get mailing: get_mailing
    - get all mailing: get_all_mailing
    - delete mailing and all documents realted to it: delete_mailing
    +------------------------------------------------------------------------------+
    """

    @staticmethod
    async def launch_mailing_alpha(
            mailing_name: str, 
        ) -> None:
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            mailing = await mailing_dal.get_mailing(mailing_name=mailing_name)

        if (mailing == DBTransactionStatus.NOT_EXIST):
            return mailing
        
        alpha_sent = 0
        alpha_delivered = 0

        # implement the logic, how you want to find clients for mailing 
        command = f"{mailing.preset}.preset_enabled()"
        clients = await eval(command) 
        if (not clients):
            return "There is no such preset"
        clients_pool_size = len(clients)
        clients_alpha_pool = int(clients_pool_size * mailing.alpha/100)

        clients = clients[:clients_alpha_pool]

        for client in clients:
            result = await MailingMiddleware.send_msg(
                chat_id=client.chat_id,
                mailing_name=mailing_name
            )

            alpha_sent += 1
            if (result == DBTransactionStatus.SUCCESS):
                alpha_delivered += 1

        await MailingMiddleware.update_alpha_sent(
            mailing_name=mailing_name,
            new_alpha_sent=alpha_sent
        )
        await MailingMiddleware.update_alpha_delivered(
            mailing_name=mailing_name,
            new_alpha_delivered=alpha_delivered
        )
        
    @staticmethod
    async def launch_mailing_beta(
            mailing_name: str, 
        ) -> None:
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            mailing = await mailing_dal.get_mailing(mailing_name=mailing_name)

        if (mailing == DBTransactionStatus.NOT_EXIST):
            return mailing

        beta_sent = 0
        beta_delivered = 0
        
        # implement the logic, how you want to find clients for mailing 
        command = f"{mailing.preset}.preset_enabled()"
        clients = await eval(command)
        if (not clients):
            return "There is no such preset"
        
        clients_pool_size = len(clients)
        clients_alpha_pool = int(clients_pool_size * mailing.alpha/100)

        clients = clients[clients_alpha_pool:]

        for client in clients:
            result = await MailingMiddleware.send_msg(
                chat_id=client.chat_id,
                mailing_name=mailing_name
            )
            
            beta_sent += 1
            if (result == DBTransactionStatus.SUCCESS):
                beta_delivered += 1
        
        await MailingMiddleware.update_beta_sent(
            mailing_name=mailing_name,
            new_beta_sent=beta_sent
        )
        await MailingMiddleware.update_beta_delivered(
            mailing_name=mailing_name,
            new_beta_delivered=beta_delivered
        )

    @staticmethod 
    async def create_full_mailing(
        mailing_name: str,
        text: str,
        preset: str,
        photo_paths: list = None,
        video_paths: list = None,
        document_paths: list = None,
        url_buttons: list = None,
        alpha: int = None,
        beta: int = None
    ) -> Union[DBTransactionStatus.SUCCESS, Exception]:
        async with async_session() as session:
            result = None
            try:
                mailing_dal = MailingDAL(session)
                result = await mailing_dal.create_mailing(
                    mailing_name=mailing_name,
                    text=text,
                    preset=preset
                )
                if (result == DBTransactionStatus.SUCCESS):
                    if (photo_paths):
                        for photo_path in photo_paths:
                            photo_name = photo_path.split("/")[-1]
                            await mailing_dal.add_photo_path(
                                mailing_name=mailing_name,
                                photo_name=photo_name
                            )
                    if (video_paths):
                        for video_path in video_paths:
                            video_name = video_path.split("/")[-1]
                            await mailing_dal.add_video_path(
                                mailing_name=mailing_name,
                                video_name=video_name
                            )
                    if (document_paths):
                        for document_path in document_paths:
                            document_name = document_path.split("/")[-1]
                            await mailing_dal.add_document_path(
                                mailing_name=mailing_name,
                                document_name=document_name
                            )
                    if (url_buttons):
                        for url_button in url_buttons:
                            await mailing_dal.add_url_button(
                                mailing_name=mailing_name,
                                url=url_button[URL],
                                button_text=url_button[BUTTON_TEXT]
                            )
                    if (alpha):
                        await mailing_dal.update_alpha(
                            mailing_name=mailing_name,
                            new_alpha=alpha
                        )
                    if (beta):
                        await mailing_dal.update_beta(
                            mailing_name=mailing_name,
                            new_beta=beta
                        )
            except Exception as e:
                result = e

            return result
    
    @staticmethod 
    async def update_mailing(
        mailing_name: str,
        new_mailing_name: str = None,
        new_text: str = None,
        new_photo_name: str = None,
        new_video_name: str = None,
        new_document_name: str = None,
        new_url_button: list = None,
        new_preset: str = None,
        alpha: int = None,
        beta: int = None
    ) -> Optional[Exception]:
        async with async_session() as session:
            md = MailingDAL(session)
            if (new_mailing_name):
                result = await md.update_mailing_name(
                    mailing_name=mailing_name,
                    new_mailing_name=new_mailing_name
                )
                if (not isinstance(result, Mailing)):
                    return result
                else:
                    mailing_name = new_mailing_name
                
            if (new_text):
                result = await md.update_text(
                    mailing_name=mailing_name,
                    new_text=new_text
                )
                if (not isinstance(result, Mailing)):
                    return result
                
            if (new_preset):
                result = await md.update_preset(
                    mailing_name=mailing_name,
                    new_preset=new_preset
                )    
                if (not isinstance(result, Mailing)):
                    return result
                
            if (new_photo_name):
                result = await md.add_photo_path(
                    mailing_name=mailing_name,
                    photo_name=new_photo_name
                )
                if (not isinstance(result, Mailing)):
                    return result
            if (new_video_name):
                result = await md.add_video_path(
                    mailing_name=mailing_name,
                    video_name=new_video_name
                )
                if (not isinstance(result, Mailing)):
                    return result
                
            if (new_document_name):
                result = await md.add_document_path(
                    mailing_name=mailing_name,
                    document_name=new_document_name
                )
                if (not isinstance(result, Mailing)):
                    return result
                
            if (new_url_button):
                result = await md.add_url_button(
                    mailing_name=mailing_name,
                    url=new_url_button[URL],
                    button_text=new_url_button[BUTTON_TEXT]
                )
                if (not isinstance(result, Mailing)):
                    return result
            if (alpha):
                result = await md.update_alpha(
                    mailing_name=mailing_name,
                    new_alpha=alpha
                )
                if (not isinstance(result, Mailing)):
                    return result
            if (beta):
                result = await md.update_beta(
                    mailing_name=mailing_name,
                    new_beta=beta
                )
                if (not isinstance(result, Mailing)):
                    return result
            return result 
            

    @staticmethod
    async def create_mailing(
        mailing_name: str,
        text: str,
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.create_mailing(
                mailing_name=mailing_name,
                text=text,
            )
            return result

    @staticmethod
    async def get_mailing(
        mailing_name: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.get_mailing(
                mailing_name=mailing_name
            )
            return result
    
    @staticmethod
    async def get_all_mailings():
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.get_all_mailings()
            return result

    @staticmethod
    async def delete_mailing(
        mailing_name: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.delete_mailing(
                mailing_name=mailing_name
            )
            return result
    
    @staticmethod
    async def get_mailing_stats(mailing_name: str) -> dict:
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            mailing = await mailing_dal.get_mailing(
                mailing_name=mailing_name
            )
            if (mailing != DBTransactionStatus.NOT_EXIST):
                stats = {
                    "alpha": mailing.alpha,
                    "alpha_sent": mailing.alpha_sent,
                    "alpha_delivered": mailing.alpha_delivered,
                    "beta": mailing.beta,
                    "beta_sent": mailing.beta_sent,
                    "beta_delivered": mailing.beta_delivered,
                }
            else:
                return mailing
            
            return stats
    """
    +------------------------------------------------------------------------------+
    """
    @staticmethod
    async def add_photo_path(
        mailing_name: str,
        photo_name: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.add_photo_path(
                mailing_name=mailing_name,
                photo_name=photo_name
            )
            return result
    
    @staticmethod
    async def delete_photo_path(
        mailing_name: str,
        photo_name: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.delete_photo_path(
                mailing_name=mailing_name,
                photo_name=photo_name
            )
            return result

    @staticmethod
    async def get_photo_paths(
        mailing_name: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.get_photo_paths(
                mailing_name=mailing_name
            )
            return result
    
    @staticmethod
    async def add_video_path(
        mailing_name: str,
        video_name: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.add_video_path(
                mailing_name=mailing_name,
                video_name=video_name
            )
            return result
    
    @staticmethod
    async def delete_video_path(
        mailing_name: str,
        video_name: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.delete_video_path(
                mailing_name=mailing_name,
                video_name=video_name
            )
            return result

    @staticmethod
    async def get_video_paths(
        mailing_name: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.get_video_paths(
                mailing_name=mailing_name
            )
            return result
    
    @staticmethod
    async def add_document_path(
        mailing_name: str,
        document_name: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.add_document_path(
                mailing_name=mailing_name,
                document_name=document_name
            )
            return result
    
    @staticmethod
    async def delete_document_path(
        mailing_name: str,
        document_name: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.delete_document_path(
                mailing_name=mailing_name,
                document_name=document_name
            )
            return result

    @staticmethod
    async def get_document_paths(
        mailing_name: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.get_document_paths(
                mailing_name=mailing_name
            )
            return result
    @staticmethod
    async def add_url_button(
        mailing_name: str,
        url: str,
        button_text: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.add_url_button(
                mailing_name=mailing_name,
                url=url,
                button_text=button_text
            )
            return result
    
    @staticmethod
    async def get_url_button(
        mailing_name: str,
        url: str,
        button_text: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.get_url_button(
                mailing_name=mailing_name,
                url=url,
                button_text=button_text
            )
            return result
        
    @staticmethod
    async def delete_url_button(
        mailing_name: str,
        url: str,
        button_text: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.delete_url_button(
                mailing_name=mailing_name,
                url=url,
                button_text=button_text
            )
            return result
    
    @staticmethod
    async def update_text(
        mailing_name: str,
        new_text: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.update_text(
                mailing_name=mailing_name,
                new_text=new_text
            )
            return result
    
    @staticmethod
    async def update_url_button(
        mailing_name: str,
        new_url_button: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.update_url_button(
                mailing_name=mailing_name,
                new_url_button=new_url_button
            )
            return result
    
    @staticmethod
    async def update_alpha(
        mailing_name: str,
        new_alpha: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.update_alpha(
                mailing_name=mailing_name,
                new_alpha=new_alpha
            )
            return result

    @staticmethod
    async def update_alpha_sent(
        mailing_name: str,
        new_alpha_sent: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.update_alpha_sent(
                mailing_name=mailing_name,
                new_alpha_sent=new_alpha_sent
            )
            return result

    @staticmethod
    async def update_alpha_delivered(
        mailing_name: str,
        new_alpha_delivered: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.update_alpha_delivered(
                mailing_name=mailing_name,
                new_alpha_delivered=new_alpha_delivered
            )
            return result
    
    @staticmethod
    async def update_beta(
        mailing_name: str,
        new_beta: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.update_beta(
                mailing_name=mailing_name,
                new_beta=new_beta
            )
            return result
    
    @staticmethod
    async def update_beta_sent(
        mailing_name: str,
        new_beta_sent: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.update_beta_sent(
                mailing_name=mailing_name,
                new_beta_sent=new_beta_sent
            )
            return result
    
    @staticmethod
    async def update_beta_delivered(
        mailing_name: str,
        new_beta_delivered: str
    ):
        async with async_session() as session:
            mailing_dal = MailingDAL(session)
            result = await mailing_dal.update_beta_delivered(
                mailing_name=mailing_name,
                new_beta_delivered=new_beta_delivered
            )
            return result


# @bot.message_handler(commands=["start"])
# async def main(message):
#     mailing_name = "first"
#     mailing = await MailingMiddleware.get_mailing(
#         mailing_name=mailing_name
#     )
#     print(message.chat.id)
#     # result = await MailingMiddleware.send_msg(
#     #     chat_id = message.chat.id,
#     #     mailing=mailing
#     # )
#     print("STATS: ", await MailingMiddleware.get_mailing_stats(mailing_name))
#     result = await MailingMiddleware.launch_mailing_beta(
#         mailing=mailing,
#     )
#     print(result)
#     result = await MailingMiddleware.launch_mailing_alpha(
#         mailing=mailing,
#     )
#     print(result)


# async def _polling():
#     await bot.polling()

# if __name__ == "__main__":
#     asyncio.run(_polling())