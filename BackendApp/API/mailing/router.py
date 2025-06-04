from BackendApp.Middleware.mailing_middleware import MailingMiddleware
from BackendApp.Database.DAL.mailing_dal import (
    PhotoNameOccupiedError,
    VideoNameOccupiedError,
    DocumentNameOccupiedError,
    ButtonCreatedError,
    MaximumButtonsExceededError
)
from BackendApp.Middleware.client_middleware import ClientMiddleware
from BackendApp.Database.session import DBTransactionStatus
from BackendApp.Database.Models.mailing_model import Mailing
from BackendApp.API.mailing.schemas import *
from BackendApp.API.mailing.utils import *
from BackendApp.Logger import logger, LogLevel

from fastapi import APIRouter

router = APIRouter()

@router.post(path="/mailing/create/", tags=["Mailing"])
async def create(request: MailingForCreating):
    try:
        dump = request.model_dump()
        url_buttons = []
        url_buttons_dumped = dump['url_buttons']
        if (url_buttons_dumped):
            for url_button in url_buttons_dumped:
                url_button_formed = []
                url_button_formed.append(url_button['url'])
                url_button_formed.append(url_button['button_text'])
                url_buttons.append(url_button_formed)
        
        result = await MailingMiddleware.create_full_mailing(
            mailing_name=dump['mailing_name'],
            text=dump['text'],
            preset=dump['preset'],
            photo_paths=dump['photo_paths'],
            video_paths=dump['video_paths'],
            document_paths=dump['document_paths'],
            url_buttons=url_buttons,
            alpha=dump['alpha'],
            beta=dump['beta']
        )
        if (result == DBTransactionStatus.SUCCESS):
            mailing = await MailingMiddleware.get_mailing(mailing_name=request.mailing_name)
            return {
                "status": "Success",
                "message": parse_mailing_into_format(mailing=mailing)
            }
        elif (isinstance(result, PhotoNameOccupiedError)):
            return {
                "status": "Failed",
                "message": "You have given two identical photo_names. The entity creation stopped."
            }
        elif (isinstance(result, VideoNameOccupiedError)):
            return {
                "status": "Failed",
                "message": "You have given two identical video_names. The entity creation stopped."
            }
        elif (isinstance(result, DocumentNameOccupiedError)):
            return {
                "status": "Failed",
                "message": "You have given two identical document_names. The entity creation stopped."
            }
        elif (isinstance(result, ButtonCreatedError)):
            return {
                "status": "Failed",
                "message": "You have given two identical buttons. The entity creation stopped."
            }
        elif (isinstance(result, MaximumButtonsExceededError)):
            return {
                "status": "Failed",
                "message": "The maximum amount of buttons is five. It has been exceeded."
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/create/: {e}",
            module_name="API"
        )

@router.post(path="/mailing/update/", tags=["Mailing"])
async def update(request: MailingForUpdating):
    try:
        dump = request.model_dump()
        new_url_button = []
        if (dump['new_url_button']):
            new_url_button.append(dump['new_url_button']['url'])
            new_url_button.append(dump['new_url_button']['button_text'])
        
        result = await MailingMiddleware.update_mailing(
            mailing_name=dump['mailing_name'],
            new_mailing_name=dump['new_mailing_name'],
            new_text=dump['new_text'],
            new_photo_name=dump['new_photo_name'],
            new_video_name=dump['new_video_name'],
            new_document_name=dump['new_document_name'],
            new_url_button=new_url_button,
            new_preset=dump['new_preset'],
            alpha=dump['alpha'],
            beta=dump['beta']
        )

        if (result == DBTransactionStatus.ROLLBACK):
            return {
                "status": "Failed",
                "message": "An error occurred while communicating with the data base"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"The mailing with the name {request.mailing_name} does not exist"
            }
        elif (isinstance(result, PhotoNameOccupiedError)):
            return {
                "status": "Failed",
                "message": "You have given two identical photo_names. The entity update stopped."
            }
        elif (isinstance(result, VideoNameOccupiedError)):
            return {
                "status": "Failed",
                "message": "You have given two identical video_names. The entity update stopped."
            }
        elif (isinstance(result, DocumentNameOccupiedError)):
            return {
                "status": "Failed",
                "message": "You have given two identical document_names. The entity update stopped."
            }
        elif (isinstance(result, ButtonCreatedError)):
            return {
                "status": "Failed",
                "message": "You have given two identical buttons. The entity update stopped."
            }
        elif (isinstance(result, MaximumButtonsExceededError)):
            return {
                "status": "Failed",
                "message": "The maximum amount of buttons is five. It has been exceeded."
            }
        else:
            mailing = await MailingMiddleware.get_mailing(mailing_name=request.mailing_name)
            return {
                "status": "Success",
                "message": parse_mailing_into_format(mailing=mailing)
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/update/: {e}",
            module_name="API"
        )

@router.delete(path="/mailing/delete/", tags=["Mailing"])
async def delete(mailing_name: str):
    try:
        result = await MailingMiddleware.delete_mailing(mailing_name=mailing_name)
        if (result == DBTransactionStatus.SUCCESS):
            return {
                "status": "Success",
                "message": f"The mailing with the name {mailing_name} has been successfully deleted"
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"The mailing with the name {mailing_name} does not exist"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/delete/: {e}",
            module_name="API"
        )

@router.post(path="/mailing/send_message/", tags=["Mailing"])
async def send_message(request: SendMessageRequest):
    try:
        result = await MailingMiddleware.send_msg(**request.model_dump())
        if (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"Either client with chat_id {request.chat_id} or mailing with mailing_name {request.mailing_name} does not exist"
            }
        else:
            return {
                "status": "Success",
                "message": f"A message has been successfully sent to the client with chat_id {request.chat_id}"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/send_message/: {e}",
            module_name="API"
        )

@router.post(path="/mailing/launch_mailing_alpha/{mailing_name}", tags=["Mailing"])
async def launch_mailing_alpha(mailing_name: str):
    try:
        result = await MailingMiddleware.launch_mailing_alpha(mailing_name=mailing_name)
        if (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"The mailing with name {mailing_name} does not exist"
            }
        elif (result == "There is no such preset"):
            mailing = await MailingMiddleware.get_mailing(mailing_name=mailing_name)
            return {
                "status": "Failed",
                "message": f"The preset {mailing.preset} does not exist"
            }
        else:
            mailing = await MailingMiddleware.get_mailing(mailing_name=mailing_name)
            clients = await ClientMiddleware.get_all_clients()
            amount_of_clients = int(len(clients) * (mailing.alpha/100))
            return {
                "status": "Success",
                "message": f"Mailing has been succesfully sent to {amount_of_clients} clients"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/lauch_mailing_alpha/: {e}",
            module_name="API"
        )

@router.post(path="/mailing/launch_mailing_beta/{mailing_name}", tags=["Mailing"])
async def launch_mailing_beta(mailing_name: str):
    try:
        result = await MailingMiddleware.launch_mailing_beta(mailing_name=mailing_name)
        if (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"The mailing with name {mailing_name} does not exist"
            }
        elif (result == "There is no such preset"):
            mailing = await MailingMiddleware.get_mailing(mailing_name=mailing_name)
            return {
                "status": "Failed",
                "message": f"The preset {mailing.preset} does not exist"
            }
        else:
            mailing = await MailingMiddleware.get_mailing(mailing_name=mailing_name)
            clients = await ClientMiddleware.get_all_clients()
            amount_of_clients = int(len(clients) * (mailing.beta/100))
            return {
                "status": "Success",
                "message": f"Mailing has been succesfully sent to {amount_of_clients} clients"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/launch_mailing_beta/: {e}",
            module_name="API"
        )

@router.patch(path="/mailing/delete_photo_path/", tags=["Mailing"])
async def delete_photo_path(request: DeletePhotoPathRequest):
    try:
        result = await MailingMiddleware.delete_photo_path(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            mailing = await MailingMiddleware.get_mailing(mailing_name=request.mailing_name)
            return {
                "status": "Success",
                "message": parse_mailing_into_format(mailing=mailing)
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"The mailing with name {request.mailing_name} does not exist"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/delete_photo_path/: {e}",
            module_name="API"
        )

@router.patch(path="/mailing/delete_video_path/", tags=["Mailing"])
async def delete_video_path(request: DeleteVideoPathRequest):
    try:
        result = await MailingMiddleware.delete_video_path(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            mailing = await MailingMiddleware.get_mailing(mailing_name=request.mailing_name)
            return {
                "status": "Success",
                "message": parse_mailing_into_format(mailing=mailing)
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"The mailing with name {request.mailing_name} does not exist"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/delete_video_path/: {e}",
            module_name="API"
        )

@router.patch(path="/mailing/delete_document_path/", tags=["Mailing"])
async def delete_document_path(request: DeleteDocumentPathRequest):
    try:
        result = await MailingMiddleware.delete_document_path(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            mailing = await MailingMiddleware.get_mailing(mailing_name=request.mailing_name)
            return {
                "status": "Success",
                "message": parse_mailing_into_format(mailing=mailing)
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"The mailing with name {request.mailing_name} does not exist"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/delete_document_path/: {e}",
            module_name="API"
        )

@router.patch(path="/mailing/delete_url_button/", tags=["Mailing"])
async def delete_url_button(request: DeleteUrlButtonRequest):
    try:
        result = await MailingMiddleware.delete_url_button(**request.model_dump())
        if (result == DBTransactionStatus.SUCCESS):
            mailing = await MailingMiddleware.get_mailing(mailing_name=request.mailing_name)
            return {
                "status": "Success",
                "message": parse_mailing_into_format(mailing=mailing)
            }
        elif (result == DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Failed",
                "message": f"The mailing with name {request.mailing_name} does not exist"
            }
        else:
            return {
                "status": "Failed",
                "message": "An error occurred while communicating with the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/delete_url_button/: {e}",
            module_name="API"
        )

@router.get(path="/mailing/get_by_name/{mailing_name}", tags=["Mailing"])
async def get_mailing(mailing_name: str):
    try:
        result = await MailingMiddleware.get_mailing(mailing_name=mailing_name)
        if (isinstance(result, Mailing)):
            return {
                "status": "Success",
                "message": parse_mailing_into_format(result)
            }
        else:
            return {
                "status": "Failed",
                "message": f"The mailing with name {mailing_name} does not exist"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/get_by_name/: {e}",
            module_name="API"
        )

@router.get(path="/mailing/get_all/", tags=["Mailing"])
async def get_all_mailings():
    try:
        mailings = await MailingMiddleware.get_all_mailings()
        if (mailings != DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Success",
                "message": [parse_mailing_into_format(mailing) for mailing in mailings]
            }
        else:
            return {
                "status": "Failed",
                "message": f"There are no mailings in the data base"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/get_all/: {e}",
            module_name="API"
        )

@router.get(path="/mailing/get_stats/{mailing_name}", tags=["Mailing"])
async def get_mailing_stats(mailing_name: str):
    try:
        stats = await MailingMiddleware.get_mailing_stats(mailing_name=mailing_name)
        if (stats != DBTransactionStatus.NOT_EXIST):
            return {
                "status": "Success",
                "message": stats
            }
        else:
            return {
                "status": "Failed",
                "message": f"The mailing with name {mailing_name} does not exist"
            }
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /mailing/get_stats/: {e}",
            module_name="API"
        )
