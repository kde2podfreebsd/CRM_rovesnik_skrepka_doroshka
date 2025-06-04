from BackendApp.Middleware.table_middleware import TableMiddleware
from BackendApp.scheduler.core import Scheduler 

from datetime import datetime, timedelta
import asyncio

class TableManager:
    
    def __init__(
            self, 
            checking_delay: int, 
            scheduler: Scheduler
        ):
        self.checking_delay = checking_delay
        self.scheduler = scheduler
    
    @staticmethod
    async def manage_tables():
        tables = await TableMiddleware.get_all()
        for table in tables:
            now = datetime.now() + timedelta(hours=3)
            if (table.block_start):
                if (table.block_start < now):
                    await TableMiddleware.update(
                        table_uuid=table.table_uuid,
                        reserved=True
                    )
            if (table.block_end):
                if (table.block_end < now):
                    await TableMiddleware.update(
                        table_uuid=table.table_uuid,
                        reserved=False
                    )
                    await TableMiddleware.nullify_block_time(
                        table_uuid=table.table_uuid
                    )

async def table_managing_thread():
    table_manager = TableManager(
        checking_delay=1,
        scheduler=Scheduler(5)
    )

    table_manager.scheduler.create_job(
        TableManager.manage_tables,
        "every",
        "minutes",
        delay=1 
    )
   
    print(f"Delay is {table_manager.checking_delay} minutes")
    while True:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - TableManager envoked") 
        await table_manager.scheduler.pending()

if __name__ == "__main__":
    asyncio.run(table_managing_thread())