from BackendApp.Database.session import async_session, DBTransactionStatus
from BackendApp.Database.Models.client_log_model import ClientActionLog
from BackendApp.Database.DAL.client_log_dal import ClientLogDAL

class ClientLogMiddleware:
    @staticmethod
    async def get_by_chat_id(chat_id: int):
        async with async_session() as session:
            cld = ClientLogDAL(session)
            result = await cld.get_logs_for_client(client_chat_id=chat_id)
            return result
