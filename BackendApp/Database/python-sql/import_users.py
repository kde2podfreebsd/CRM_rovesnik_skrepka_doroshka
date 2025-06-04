import pandas as pd

from BackendApp.Middleware.client_middleware import ClientMiddleware


async def create_client_from_csv(file_path: str):
    df = pd.read_csv(file_path)
    batch = []
    for i, (_, row) in enumerate(df.iterrows()):
        chat_id = row.get('tg_id')
        batch.append(ClientMiddleware.create_client(chat_id=chat_id))
        if len(batch) >= 100:
            await asyncio.gather(*batch)
            batch = []
        
if __name__ == "__main__":
    import asyncio

    async def main():
        await create_client_from_csv("./data_dumps/r_users.csv")
        await create_client_from_csv("./data_dumps/d_users.csv")
        await create_client_from_csv("./data_dumps/s_users.csv")

    asyncio.run(main())
    