from pydantic import BaseModel
from typing import Optional, List

class NewUrlButton(BaseModel):
    url: str
    button_text: str

class MailingForCreating(BaseModel):
    mailing_name: str
    text: str
    preset: str
    photo_paths: Optional[List] = None
    video_paths: Optional[List] = None
    document_paths: Optional[List] = None
    url_buttons: Optional[List[NewUrlButton]] = None
    alpha: Optional[int] = None
    beta: Optional[int] = None

class MailingForUpdating(BaseModel):
    mailing_name: str
    new_mailing_name: Optional[str] = None
    new_text: Optional[str] = None
    new_photo_name: Optional[str] = None
    new_video_name: Optional[str] = None
    new_document_name: Optional[str] = None
    new_url_button: Optional[NewUrlButton] = None
    new_preset: Optional[str] = None
    alpha: Optional[int] = None
    beta: Optional[int] = None

class MailingForReturn(BaseModel):
    mailing_name: str
    text: str
    preset: str
    photo_paths: Optional[List] = None
    video_paths: Optional[List] = None
    document_paths: Optional[List] = None
    url_buttons: Optional[List] = None
    alpha: int
    alpha_sent: Optional[int] = None
    alpha_delivered: Optional[int] = None
    beta: int
    beta_sent: Optional[int] = None
    beta_delivered: Optional[int] = None

class MailingStats(BaseModel):
    mailing_name: str
    alpha: int
    alpha_sent: Optional[int] = None
    alpha_delivered: Optional[int] = None
    beta: int
    beta_sent: Optional[int] = None
    beta_delivered: Optional[int] = None

class SendMessageRequest(BaseModel):
    chat_id: int
    mailing_name: str

class DeletePhotoPathRequest(BaseModel):
    mailing_name: str
    photo_name: str

class DeleteVideoPathRequest(BaseModel):
    mailing_name: str
    video_name: str

class DeleteDocumentPathRequest(BaseModel):
    mailing_name: str
    document_name: str

class DeleteUrlButtonRequest(BaseModel):
    mailing_name: str
    url: str
    button_text: str

class DeleteUrlButtonRequest(BaseModel):
    mailing_name: str
    url: str
    button_text: str