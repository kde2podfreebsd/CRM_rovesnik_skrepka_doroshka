from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import registry

Base = declarative_base()

from BackendApp.Database.Models.affilate_promotions_model import *
from BackendApp.Database.Models.artist_model import *
from BackendApp.Database.Models.atrist_event_relationship_model import *
from BackendApp.Database.Models.bar_model import *
from BackendApp.Database.Models.client_model import *
from BackendApp.Database.Models.event_model import *
from BackendApp.Database.Models.faq_model import *
from BackendApp.Database.Models.mailing_model import *
from BackendApp.Database.Models.promocode_model import *
from BackendApp.Database.Models.quiz_model import *
from BackendApp.Database.Models.referrals_model import *
from BackendApp.Database.Models.subscriptions_model import *
from BackendApp.Database.Models.SupportBot.agent_model import *
from BackendApp.Database.Models.SupportBot.file_model import *
from BackendApp.Database.Models.SupportBot.message_model import *
from BackendApp.Database.Models.SupportBot.password_model import *
from BackendApp.Database.Models.SupportBot.requests_model import *
from BackendApp.Database.Models.test_model import *
from BackendApp.Database.Models.test_result_model import *
from BackendApp.Database.Models.ticket_model import *
from BackendApp.Database.Models.transaction_model import *
from BackendApp.Database.Models.partner_gift_model import *
from BackendApp.Database.Models.reservation_model import *
from BackendApp.Database.Models.table_model import *
from BackendApp.Database.Models.client_log_model import *
from BackendApp.Database.Models.review_model import *


mapper_registry = registry()
