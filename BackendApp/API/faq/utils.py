from BackendApp.Database.Models.faq_model import FAQ
from BackendApp.API.faq.schemas import *

def parse_faq_into_format(request: FAQ):
    return FAQForReturn(
        faq_id=request.id,
        bar_id=request.bar_id,
        text=request.text
    )