from BackendApp.Database.session import async_session
from BackendApp.Database.DAL.faq_dal import FAQDAL

class FAQMiddleware:

    @staticmethod
    async def create(
        text: str,
        bar_id: int
    ):
        async with async_session() as session:
            faq_dal = FAQDAL(session)
            result = await faq_dal.create(
                text=text,
                bar_id=bar_id
            )
            return result


    @staticmethod
    async def update(
        faq_id: int,
        text: int
    ):
        async with async_session() as session:
            faq_dal = FAQDAL(session)
            result = await faq_dal.update(
                faq_id = faq_id,
                text=text
            )
            return result

    @staticmethod
    async def delete(faq_id: int):
        async with async_session() as session:
            faq_dal = FAQDAL(session)
            result = await faq_dal.delete(faq_id=faq_id)
            return result

    @staticmethod
    async def get_all():
        async with async_session() as session:
            faq_dal = FAQDAL(session)
            result = await faq_dal.get_all()
            return result

    @staticmethod
    async def get_by_id(faq_id: int):
        async with async_session() as session:
            faq_dal = FAQDAL(session)
            result = await faq_dal.get_by_id(faq_id=faq_id)
            return result
    
    @staticmethod
    async def get_by_bar_id(bar_id: int):
        async with async_session() as session:
            faq_dal = FAQDAL(session)
            result = await faq_dal.get_by_bar_id(bar_id=bar_id)
            return result

    @staticmethod
    async def get_entity_id(bar_id: int, text: str):
        async with async_session() as session:
            faq_dal = FAQDAL(session)
            result = await faq_dal.get_entity_id(bar_id=bar_id, text=text)
            return result
    
    @staticmethod
    def escape_json(string: str):
        res_string = ""
        for char in string:
            if (char == '\n'):
                res_string += "\\n"
            elif (char == '\\'):
                res_string += "\\\\"
            elif (char == '\b'):
                res_string += "\\b"
            elif (char == '\t'):
                res_string += "\\t"
            elif (char == '\f'):
                res_string += "\\f"
            elif (char == '\r'):
                res_string += "\\r"
            else:
                res_string += char
        return res_string




