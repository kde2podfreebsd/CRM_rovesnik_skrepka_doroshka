from BackendApp.Database.DAL.client_log_dal import ClientLogDAL
from BackendApp.Database.session import async_session
from BackendApp.Middleware.client_middleware import ClientMiddleware


def handler_logging(func):
    async def handler(*args, **kwargs):
        try: 
            data = args[0]
        except IndexError:
            try:
                data = kwargs["message"]
            except KeyError:
                data = kwargs["call"]
        action = (
            f"{func.__module__}.{func.__name__}"
        )
        try: 
            user_id = data.chat.id
        except:
            user_id = data.message.chat.id
        async with async_session() as session:
            dal = ClientLogDAL(session)
            await dal.create(
                client_chat_id=user_id,
                action=action
            )
        return await func(*args, **kwargs)

    return handler