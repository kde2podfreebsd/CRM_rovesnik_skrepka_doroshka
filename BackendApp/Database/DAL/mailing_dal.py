from psycopg2 import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from BackendApp.Logger import logger, LogLevel
from BackendApp.Database.Models.mailing_model import Mailing
from BackendApp.Database.session import DBTransactionStatus
from typing import Union, Optional, List
from BackendApp.Database.session import async_session

import os
import asyncio 

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
photo_path_folder = os.path.join(basedir, "static", "photo")
video_path_folder = os.path.join(basedir, "static", "video")
document_path_folder = os.path.join(basedir, "static", "document")

MAXIMUM_BUTTONS = 5
MAXIMUM_INPUT_MEDIA = 10

class MailingDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    # photo name, video name and document name: file format should be written with the file name
    async def create_mailing(
            self,
            mailing_name: str,
            text: str,
            preset: str
    ) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.ALREADY_EXIST
    ]:
        existing_mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        existing_mailing = existing_mailing.scalars().first()

        if existing_mailing:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with the given parameters: {mailing_name, text, preset}, - already exists in the data base"
            )
            return DBTransactionStatus.ALREADY_EXIST
        
        new_mailing = Mailing(
            mailing_name=mailing_name,
            text=text,
            preset=preset
        )
        # initialization of arrays by lists
        new_mailing.photo_paths = []
        new_mailing.video_paths = []
        new_mailing.url_buttons = []
        new_mailing.document_paths = []

        self.db_session.add(new_mailing)

        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Mailing entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Mailing entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK
    
    async def get_mailing(self, mailing_name: str) -> Union[
        Mailing, DBTransactionStatus.NOT_EXIST
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )
        mailing = mailing.scalars().first()
        if mailing:
            logger.log(
                level=LogLevel.INFO,
                message=f"Mailing entity with name {mailing_name} has been successfully retrieved"
            )
            return mailing
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def get_all_mailings(self) -> Union[
        List, DBTransactionStatus.NOT_EXIST
    ]:
        mailings_db = await self.db_session.execute(
            select(Mailing)
        )
        mailings = mailings_db.scalars().all()
        if mailings:
            logger.log(
                level=LogLevel.INFO,
                message=f"Mailing entities have been successfully retrieved"
            )
            return mailings
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"There are no Mailing entities in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def delete_mailing(self, mailing_name: str) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.NOT_EXIST
    ]:  
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )
        mailing = mailing.scalars().first()

        if (not mailing):
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

        for photo_path in mailing.photo_paths:
            if (os.path.exists(photo_path)):
                os.remove(photo_path)
        for video_path in mailing.video_paths:
            if (os.path.exists(video_path)):
                os.remove(video_path)
        for document_path in mailing.document_paths:
            if (os.path.exists(document_path)):
                os.remove(document_path)
        
        await self.db_session.delete(mailing)
        try:
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"A Mailing with name {mailing_name} has been successfully deleted from the data base"
            )
            return DBTransactionStatus.SUCCESS

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while deleting Mailing entity with name {mailing_name}: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def add_photo_path(self, mailing_name: str, photo_name: str) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.NOT_EXIST,
        Exception
    ]:  
        photo_path = os.path.join(photo_path_folder, photo_name)
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            try:
                if (photo_path in mailing.photo_paths):
                    raise PhotoNameOccupiedError(name=photo_name)
                if (
                    len(mailing.video_paths) + 
                    len(mailing.photo_paths) >= 
                    MAXIMUM_INPUT_MEDIA
                ):
                    raise MaximumInputMediaExceededError
            except Exception as e:
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while adding photo_path to Mailing entity with name {mailing_name}: {e}"
                )
                return e 
            try:
                mailing.photo_paths.append(photo_path)
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"A photo_path has been successfully added to Mailing with name {mailing_name}"
                )
                return DBTransactionStatus.SUCCESS
            
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while adding photo_path to Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def delete_photo_path(self, mailing_name: str, photo_name: str) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.NOT_EXIST
    ]:  
        photo_path = os.path.join(photo_path_folder, photo_name)
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            try:
                mailing.photo_paths.remove(photo_path)
                os.remove(photo_path)
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"A photo_path has been successfully deleted from Mailing with name {mailing_name}"
                )
                return DBTransactionStatus.SUCCESS
            
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while deleting photo_path from Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def add_video_path(self, mailing_name: str, video_name: str) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.NOT_EXIST,
        Exception
    ]:  
        video_path = os.path.join(video_path_folder, video_name)
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            try:
                if (video_path in mailing.video_paths):
                    raise VideoNameOccupiedError(name=video_path)
                if (
                    len(mailing.video_paths) + 
                    len(mailing.photo_paths) >= 
                    MAXIMUM_INPUT_MEDIA
                ):
                    raise MaximumInputMediaExceededError
            except Exception as e:
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while adding video_path to Mailing entity with name {mailing_name}: {e}"
                )
                return e
            try:
                
                mailing.video_paths.append(video_path)
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"A video_path has been successfully added to Mailing with name {mailing_name}"
                )
                return DBTransactionStatus.SUCCESS
            
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while adding video_path to Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def delete_video_path(self, mailing_name: str, video_name: str) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.NOT_EXIST
    ]:  
        video_path = os.path.join(video_path_folder, video_name)
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            try:
                mailing.video_paths.remove(video_path)
                os.remove(video_path)
                logger.log(
                    level=LogLevel.INFO,
                    message=f"A video_path has been successfully deleted from Mailing with name {mailing_name}"
                )
                await self.db_session.commit()
                return DBTransactionStatus.SUCCESS
            
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while deleting video_path from Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def add_document_path(self, mailing_name: str, document_name: str) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.NOT_EXIST,
        Exception
    ]:  
        document_path = os.path.join(document_path_folder, document_name)
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            try:
                if (document_path in mailing.document_paths):
                    raise DocumentNameOccupiedError(name=document_name)
                if (
                    len(mailing.document_paths) >= MAXIMUM_INPUT_MEDIA
                ):
                    raise MaximumInputMediaExceededError
            except Exception as e:
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while adding document_path to Mailing entity with name {mailing_name}: {e}"
                )
                return e
            try:
                
                mailing.document_paths.append(document_path)
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"A document_path has been successfully added to Mailing with name {mailing_name}"
                )
                return DBTransactionStatus.SUCCESS
            
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while adding document_path to Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def delete_document_path(self, mailing_name: str, document_name: str) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.NOT_EXIST
    ]:  
        document_path = os.path.join(document_path_folder, document_name)
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            try:
                mailing.document_paths.remove(document_path)
                os.remove(document_path)
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"A document_path has been successfully deleted from Mailing with name {mailing_name}"
                )
                return DBTransactionStatus.SUCCESS
            
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while deleting document_path from Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def get_photo_paths(self, mailing_name: str) -> Union[
        List, DBTransactionStatus.NOT_EXIST
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            return mailing.photo_paths
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def get_video_paths(self, mailing_name: str) -> Union[
        List, DBTransactionStatus.NOT_EXIST
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            return mailing.video_paths
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def get_document_paths(self, mailing_name: str) -> Union[
        List, DBTransactionStatus.NOT_EXIST
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            return mailing.document_paths
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def add_url_button(self, mailing_name: str, url: str, button_text: str) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.NOT_EXIST,
        Exception
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            url_buttons = mailing.url_buttons
            try:
                if (len(url_buttons) >= MAXIMUM_BUTTONS):
                    raise MaximumButtonsExceededError
                
                if (await URLButtonsMethods.check_if_button_created(
                        url=url,
                        button_text=button_text,
                        url_buttons=url_buttons
                    ) 
                ):
                    raise ButtonCreatedError(
                        url=url,
                        button_text=button_text
                    )
            except Exception as e:
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while adding url_button to Mailing entity with name {mailing_name}: {e}"
                )
                return e
            url_buttons.append([url, button_text])
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"A url_button has been successfully added to Mailing with name {mailing_name}"
                )
                return DBTransactionStatus.SUCCESS
            except Exception:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while adding url_button to Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        
    
    async def get_url_button(self, mailing_name: str, url: str, button_text: str) -> Union[
        List, DBTransactionStatus.NOT_EXIST
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()
        
        if mailing:
            return await URLButtonsMethods.check_if_button_created(
                url=url, 
                button_text=button_text, 
                url_buttons=mailing.url_buttons
            )
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def delete_url_button(self, mailing_name: str, url: str, button_text: str) -> Union[
        DBTransactionStatus.SUCCESS,
        DBTransactionStatus.ROLLBACK,
        DBTransactionStatus.NOT_EXIST
    ]:  
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            try:
                mailing.url_buttons.remove(
                    await URLButtonsMethods.check_if_button_created(
                        url=url,
                        button_text=button_text,
                        url_buttons=mailing.url_buttons
                    )
                )
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"A url_button has been successfully deleted from Mailing with name {mailing_name}"
                )
                return DBTransactionStatus.SUCCESS
            
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while deleting url_button from Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def update_mailing_name(self, mailing_name: str, new_mailing_name: str) -> Union[
        Mailing,
        DBTransactionStatus.NOT_EXIST, 
        DBTransactionStatus.ROLLBACK
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            mailing.mailing_name = new_mailing_name
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Mailing with name {mailing_name} has successfully changed its' name to {new_mailing_name}"
                )
                return mailing
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating mailing_name in Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def update_text(self, mailing_name: str, new_text: str) -> Union[
        Mailing, 
        DBTransactionStatus.NOT_EXIST, 
        DBTransactionStatus.ROLLBACK
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            mailing.text = new_text
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Mailing with name {mailing_name} text has been successfully updated"
                )
                return mailing
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating text in Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def update_preset(self, mailing_name: str, new_preset: str) -> Union[
        Mailing, 
        DBTransactionStatus.NOT_EXIST, 
        DBTransactionStatus.ROLLBACK
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            mailing.preset = new_preset
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Mailing with name {mailing_name} preset has been successfully updated"
                )
                return mailing
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating preset in Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def update_alpha(self, mailing_name: str, new_alpha: int) -> Union[
        Mailing, 
        DBTransactionStatus.NOT_EXIST, 
        DBTransactionStatus.ROLLBACK
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            mailing.alpha = new_alpha
            mailing.beta = 100 - new_alpha
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Mailing with name {mailing_name} alpha has been successfully updated"
                )
                return mailing
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating alpha in Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def update_alpha_sent(self, mailing_name: str, new_alpha_sent: int) -> Union[
        Mailing, 
        DBTransactionStatus.NOT_EXIST, 
        DBTransactionStatus.ROLLBACK
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            mailing.alpha_sent = new_alpha_sent
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Mailing with name {mailing_name} alpha_sent has been successfully updated"
                )
                return mailing
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating alpha_sent in Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

    async def update_alpha_delivered(self, mailing_name: str, new_alpha_delivered: int) -> Union[
        Mailing, 
        DBTransactionStatus.NOT_EXIST, 
        DBTransactionStatus.ROLLBACK
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            mailing.alpha_delivered  = new_alpha_delivered
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Mailing with name {mailing_name} alpha_delivered has been successfully updated"
                )
                return mailing
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating alpha_delivered in Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def update_beta(self, mailing_name: str, new_beta: int) -> Union[
        Mailing, 
        DBTransactionStatus.NOT_EXIST, 
        DBTransactionStatus.ROLLBACK
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            mailing.beta = new_beta
            mailing.alpha = 100 - new_beta
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Mailing with name {mailing_name} beta has been successfully updated"
                )
                return mailing
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating beta in Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
        
    async def update_beta_sent(self, mailing_name: str, new_beta_sent: int) -> Union[
        Mailing, 
        DBTransactionStatus.NOT_EXIST, 
        DBTransactionStatus.ROLLBACK
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            mailing.beta_sent = new_beta_sent
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Mailing with name {mailing_name} beta_sent has been successfully updated"
                )
                return mailing
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating beta_sent in Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST
    
    async def update_beta_delivered(self, mailing_name: str, new_beta_delivered: int) -> Union[
        Mailing, 
        DBTransactionStatus.NOT_EXIST, 
        DBTransactionStatus.ROLLBACK
    ]:
        mailing = await self.db_session.execute(
            select(Mailing).where(and_(Mailing.mailing_name == mailing_name))
        )

        mailing = mailing.scalars().first()

        if mailing:
            mailing.beta_delivered = new_beta_delivered
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Mailing with name {mailing_name} beta_delivered has been successfully updated"
                )
                return mailing
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating beta_sent in Mailing entity with name {mailing_name}: {e}"
                )
                return DBTransactionStatus.ROLLBACK
        else:
            logger.log(
                level=LogLevel.WARNING,
                message=f"A Mailing with name {mailing_name} does not exist in the data base"
            )
            return DBTransactionStatus.NOT_EXIST

class MailingDALErrors(Exception):
    """The parent class of exceptions which can be envoked while working with MailingDAL"""

class MaximumButtonsExceededError(MailingDALErrors):
    def __init__(self, message = "A mailing must consist only of 5 buttons"):
        self.message = message
        super().__init__(message)

class MaximumInputMediaExceededError(MailingDALErrors):
    """Telebot's .send_media_group supports only 2-10 InputMedia objects"""

    def __init__(self, message = "The sum of sizes of the mailing photo_paths, video_paths and document_paths cannot exceed 10"):
        self.message = message
        super().__init__(message)

class PhotoNameOccupiedError(MailingDALErrors):
    def __init__(self, name: str):
        self.message = f"The photo with the name \"{name}\" has already been added to database. You must change change its' name to upload it"
        super().__init__(self.message)

class VideoNameOccupiedError(MailingDALErrors):
    def __init__(self, name: str):
        self.message = f"The video with the name \"{name}\" has already been added to database. You must change change its' name to upload it"
        super().__init__(self.message)

class DocumentNameOccupiedError(MailingDALErrors):
    def __init__(self, name: str):
        self.message = f"The document with the name \"{name}\" has already been added to database. You must change change its' name to upload it"
        super().__init__(self.message)

class ButtonCreatedError(MailingDALErrors):
    def __init__(self, url: str, button_text: str):
        self.message = f"""
        The button with url: \"{url}\" and button_text: \"{button_text}\" has already been added to database. You must use another URL or change button_text to make a button
        """
        super().__init__(self.message)

class URLButtonsMethods:
    @staticmethod
    async def check_if_button_created(url: str, button_text: str, url_buttons: list) -> Optional[List]:
        result = None
        for button in url_buttons:
            if (url in button and button_text in button):
                result = button
                break
        return result
    
    @staticmethod
    async def check_if_url_occupied(url: str, url_buttons: list) -> bool:
        result = False
        for button in url_buttons:
            if (url in button):
                result = True
                break
        return result
    
    @staticmethod
    async def check_if_button_text_is_occupied(button_text: str, url_buttons: list) -> bool:
        result = False
        for button in url_buttons:
            if (button_text in button):
                result = True
                break
        return result

# async def main():
#     async with async_session() as session:
#         mailing_name1 = "first"
#         mailing_name2 = "second"
#         dal = MailingDAL(session)
#         # result = await dal.create_mailing(
#         #     mailing_name=mailing_name2,
#         #     text="world",
#         #     preset="PresetN1"
#         # )
#         # print(result)
#         # result = await dal.get_all_mailings()
#         # print(result)
#         # result = await dal.add_document_path(mailing_name=mailing_name1, document_name="10.docx")
#         # print(result)
#         result = await dal.add_url_button(mailing_name=mailing_name2, url="yandex.ru", button_text="FART FART FART")
#         print(result)
#         result = await dal.add_video_path(mailing_name=mailing_name2, video_name="1.mp4")
#         print(result)
#         # result = await dal.add_photo_path(mailing_name=mailing_name1, photo_name="1.jpeg")
#         # print(result)
#         # result = await dal.delete_mailing(mailing_name=mailing_name1)
#         # print(result)
       


# if __name__ == "__main__":
#     asyncio.run(main())





