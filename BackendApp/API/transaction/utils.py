from BackendApp.Database.Models.transaction_model import Transaction
from BackendApp.API.transaction.schemas import TransactionForReturn

def parse_tx_into_format(tx: Transaction):
    return TransactionForReturn(
        id=tx.id,
        client_chat_id=tx.client_chat_id,
        bar_id=tx.bar_id,
        amount=tx.amount,
        final_amount=tx.final_amount,
        tx_type=tx.tx_type
    )