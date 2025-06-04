from sqlalchemy.future import select
from BackendApp.Database.session import DBTransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
import asyncio
from BackendApp.Database.Models.transaction_model import Transaction
from datetime import datetime, timedelta
from BackendApp.Logger import logger, LogLevel

class TransactionDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
        self, 
        bar_id: int, 
        amount: float, 
        final_amount: float, 
        client_chat_id: int, 
        tx_type
    ) -> Union[DBTransactionStatus.SUCCESS, DBTransactionStatus.ROLLBACK]:

        new_transaction = Transaction(
            bar_id=bar_id,
            amount=amount,
            final_amount=final_amount,
            client_chat_id=client_chat_id,
            tx_type=tx_type,
            time_stamp=(datetime.now() + timedelta(hours=3))
        )
        try:
            self.db_session.add(new_transaction)
            await self.db_session.commit()
            logger.log(
                level=LogLevel.INFO,
                message=f"Transaction entity has been successfully created"
            )
            return DBTransactionStatus.SUCCESS
        except Exception as e:
            await self.db_session.rollback()
            logger.log(
                level=LogLevel.ERROR,
                message=f"An error occurred while creating Transaction entity: {e}"
            )
            return DBTransactionStatus.ROLLBACK

    async def update_final_amount(self, transaction_id: int, final_amount: float):
        transaction = await self.db_session.get(Transaction, transaction_id)
        if transaction:
            transaction.final_amount = final_amount
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Transaction entity with id {transaction_id} final_amount has been successfully updated"
                )
                return True
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while updating final_amount of the Transaction entity with id {transaction_id}: {e}"
                )
                raise e
        else:
            return False

    async def delete(self, transaction_id: int):
        transaction = await self.db_session.get(Transaction, transaction_id)
        if transaction:
            self.db_session.delete(transaction)
            try:
                await self.db_session.commit()
                logger.log(
                    level=LogLevel.INFO,
                    message=f"Transaction entity with id {transaction_id} has been successfully deleted"
                )
                return True
            except Exception as e:
                await self.db_session.rollback()
                logger.log(
                    level=LogLevel.ERROR,
                    message=f"An error occurred while deleting Transaction entity with id {transaction_id}: {e}"
                )
                raise e
        else:
            return False

    async def get_all(self):
        return await self.db_session.execute(select(Transaction)).scalars().all()

    async def get_by_id(self, transaction_id: int):
        return await self.db_session.get(Transaction, transaction_id)

    async def get_by_client_chat_id(self, client_chat_id: int):
        txs = await self.db_session.execute(select(Transaction).where(Transaction.client_chat_id == client_chat_id))
        txs = txs.scalars().all()
        return txs


if __name__ == "__main__":
    async def transaction_test():
        from BackendApp.Database.session import async_session

        async with async_session() as session:
            transaction_dal = TransactionDAL(session)

            transaction_id = await transaction_dal.create(bar_id=1, amount=50.0, final_amount=40.0, client_chat_id=123456789)
            print("Transaction Created with ID:", transaction_id)

            update_result = await transaction_dal.update_final_amount(transaction_id=transaction_id, final_amount=35.0)
            print("Transaction Final Amount Updated:", update_result)

            all_transactions = await transaction_dal.get_all()
            print("All Transactions:", [transaction.id for transaction in all_transactions])

            transaction_by_id = await transaction_dal.get_by_id(transaction_id=transaction_id)
            print("Transaction By ID:", transaction_by_id.id if transaction_by_id else None)

            transactions_by_client = await transaction_dal.get_by_client_chat_id(client_chat_id=123456789)
            print("Transactions By Client Chat ID:", [transaction.id for transaction in transactions_by_client])

    asyncio.run(transaction_test())
