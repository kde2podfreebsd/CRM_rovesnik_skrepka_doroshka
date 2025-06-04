from BackendApp.API.client_action_log.schemas import *
from BackendApp.Database.Models.client_log_model import ClientActionLog

def parse_log_into_format(log: ClientActionLog):
    return LogForReturn(
        action=log.action,
        created_at=log.created_at
    )