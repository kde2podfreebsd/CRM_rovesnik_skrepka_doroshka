from BackendApp.API.mailing.schemas import *
from BackendApp.API.mailing.utils import *
from BackendApp.Database.Models.mailing_model import Mailing

def parse_mailing_into_format(mailing: Mailing):
    return MailingForReturn(
        mailing_name=mailing.mailing_name,
        text=mailing.text,
        preset=mailing.preset,
        photo_paths=mailing.photo_paths,
        video_paths=mailing.video_paths,
        document_paths=mailing.document_paths,
        url_buttons=mailing.url_buttons,
        alpha=mailing.alpha,
        alpha_sent=mailing.alpha_sent,
        alpha_delivered=mailing.alpha_delivered,
        beta=mailing.beta,
        beta_sent=mailing.beta_sent,
        beta_delivered=mailing.beta_delivered
    )