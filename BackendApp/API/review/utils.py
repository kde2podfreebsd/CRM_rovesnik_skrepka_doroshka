from BackendApp.API.review.schemas import *
from BackendApp.Database.Models.review_model import Review

def parse_review_into_format(review: Review):
    return ReviewMold(
        chat_id=review.chat_id,
        text=review.text,
        bar_id=review.bar_id,
        event_id=review.event_id
    )