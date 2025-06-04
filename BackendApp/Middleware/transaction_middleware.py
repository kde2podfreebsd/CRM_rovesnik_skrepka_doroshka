from BackendApp.Database.session import async_session
from BackendApp.Database.DAL.transaction_dal import TransactionDAL
import enum

class TX_TYPES(str, enum.Enum):
    INCREASE_BALANCE = 'increase_balance'
    REDUCE_BALANCE = 'reduce_balance'

class TransactionMiddleware:

    @staticmethod
    async def create_tx(bar_id, amount, final_amount, client_chat_id, tx_type):
        async with async_session() as session:
            transaction_dal = TransactionDAL(session)

            result = await transaction_dal.create(
                bar_id=bar_id,
                amount=amount,
                final_amount=final_amount,
                client_chat_id=client_chat_id,
                tx_type=tx_type
            )
            return result

    @staticmethod
    async def get_all_tx(client_chat_id):
        async with async_session() as session:
            transaction_dal = TransactionDAL(session)

            txs = await transaction_dal.get_by_client_chat_id(client_chat_id=client_chat_id)

            return txs

    @staticmethod
    async def get_by_id(transaction_id: int):
        async with async_session() as session:
            td = TransactionDAL(session)
            tx = await td.get_by_id(transaction_id=transaction_id)
            return tx
