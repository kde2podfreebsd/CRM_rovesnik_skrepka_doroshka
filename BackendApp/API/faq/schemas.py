from pydantic import BaseModel

class FAQForCreating(BaseModel):
    bar_id: int
    text: str

class FAQForUpdating(BaseModel):
    faq_id: int
    text: str

class FAQForReturn(BaseModel):
    faq_id: int
    bar_id: int
    text: str