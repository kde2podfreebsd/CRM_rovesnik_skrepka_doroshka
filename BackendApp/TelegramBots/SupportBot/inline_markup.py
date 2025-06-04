import os
import traceback

from dotenv import load_dotenv
from telebot import formatting, types

from BackendApp.Database.DAL.SupportBot.agent_dal import AgentDAL
from BackendApp.Database.DAL.SupportBot.file_dal import FileDAL
from BackendApp.Database.DAL.SupportBot.password_dal import PasswordDAL
from BackendApp.Database.DAL.SupportBot.requests_dal import RequestDAL
from BackendApp.Database.session import async_session
from BackendApp.Logger import LogLevel, logger
from BackendApp.TelegramBots.SupportBot.core import get_file_text, get_icon_from_status

load_dotenv()


def page(markup, number, list, call, callback_cancel):
    if len(list) != 10:
        max_nums = number
    else:
        max_nums = "None"

    if str(number) == "1":
        item1 = types.InlineKeyboardButton(f"⏹", callback_data=f"None")
    else:
        item1 = types.InlineKeyboardButton(f"◀️", callback_data=f"{call}:{int(number) - 1}")

    if str(number) == str(max_nums):
        item2 = types.InlineKeyboardButton(f"⏹", callback_data=f"None")
    else:
        item2 = types.InlineKeyboardButton(f"▶️", callback_data=f"{call}:{int(number) + 1}")

    item3 = types.InlineKeyboardButton("Назад", callback_data=callback_cancel)

    if callback_cancel != "None":
        markup.add(item1, item3, item2)
    else:
        if str(number) == "1" and str(number) == str(max_nums):
            pass
        else:
            markup.add(item1, item2)

    return markup


class InlineMarkup(object):

    @classmethod
    async def markup_reqs(cls, user_id, callback, number):
        try:
            async with async_session() as session:
                request_dal = RequestDAL(session)
                if callback == "my_reqs":
                    reqs = await request_dal.my_reqs(number, user_id)
                    user_status = "user"
                    callback_cancel = "None"
                else:
                    reqs = await request_dal.get_reqs(number, callback)
                    user_status = "agent"
                    callback_cancel = "back_agent"

            markup_my_reqs = types.InlineKeyboardMarkup(row_width=3)
            for req in reqs:
                req_id = req.req_id
                req_status = req.req_status
                req_icon = get_icon_from_status(req_status, user_status)
                # ❗️, ⏳, ✅

                item = types.InlineKeyboardButton(
                    f"{req_icon} | ID: {req_id}", callback_data=f"open_req:{req_id}:{callback}-{number}"
                )
                markup_my_reqs.add(item)

            markup_my_reqs = page(markup_my_reqs, number, reqs, callback, callback_cancel)
            if callback == "my_reqs":
                markup_my_reqs.add(
                    types.InlineKeyboardButton("Назад", callback_data="support_back_to_main_menu")
                )

            return markup_my_reqs, len(reqs)
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Error in markup_reqs: {e}. StackTrace: {traceback.format_exc()}",
                module_name="TelegramBots.SupportBot.core"
            )

    @classmethod
    def support_back_to_main_menu(cls):
        return types.InlineKeyboardMarkup(
            row_width=1,
            keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data="support_back_to_main_menu"
                    )
                ]
            ],
        )

    @classmethod
    def support_back_to_agent_menu(cls):
        return types.InlineKeyboardMarkup(
            row_width=1,
            keyboard=[[types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_agent")]],
        )

    @classmethod
    def back_to_main_menu(cls):
        return types.InlineKeyboardMarkup(
            row_width=1,
            keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data="support_back_to_main_menu"
                    )
                ]
            ],
        )

    @classmethod
    def support_markup_main(cls):
        markup_main = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton("✏️ Написать запрос", callback_data="write_request")
        item2 = types.InlineKeyboardButton("✉️ Мои запросы", callback_data="my_reqs:")
        back_to_main_menu = types.InlineKeyboardButton(
            "🔙 Назад", callback_data="back_to_main_menu"
        )
        markup_main.add(item1)
        markup_main.add(item2)
        markup_main.add(back_to_main_menu)

        return markup_main

    @classmethod
    async def markup_reqs(cls, user_id, callback, number):
        try:
            async with async_session() as session:
                request_dal = RequestDAL(session)
                if callback == "my_reqs":
                    reqs = await request_dal.my_reqs(number, user_id)
                    user_status = "user"
                    callback_cancel = "None"
                else:
                    reqs = await request_dal.get_reqs(number, callback)
                    user_status = "agent"
                    callback_cancel = "back_agent"

            markup_my_reqs = types.InlineKeyboardMarkup(row_width=3)
            for req in reqs:
                req_id = req.req_id
                req_status = req.req_status
                req_icon = get_icon_from_status(req_status, user_status)
                # ❗️, ⏳, ✅

                item = types.InlineKeyboardButton(
                    f"{req_icon} | ID: {req_id}", callback_data=f"open_req:{req_id}:{callback}-{number}"
                )
                markup_my_reqs.add(item)

            markup_my_reqs = page(markup_my_reqs, number, reqs, callback, callback_cancel)
            if callback == "my_reqs":
                markup_my_reqs.add(
                    types.InlineKeyboardButton("Назад", callback_data="support_back_to_main_menu")
                )

            return markup_my_reqs, len(reqs)
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Error in markup_reqs: {e}. StackTrace: {traceback.format_exc()}",
                module_name="TelegramBots.SupportBot.core"
            )
    
    def support_back_to_request(req_id, callback, number):
        return types.InlineKeyboardMarkup(
            row_width=1,
            keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data=f"open_req:{req_id}:{callback}-{number}"
                    )
                ]
            ],
        )

    def markup_request_action(req_id, req_status, callback):
        formatted_callback = callback.replace("-", ":")

        markup_request_action = types.InlineKeyboardMarkup(row_width=1)

        print(formatted_callback)
        try:
            if req_status == "confirm":
                item1 = types.InlineKeyboardButton(
                    "🗂 Показать файлы", callback_data=f"req_files:{req_id}:{callback}:1"
                )
                item2 = types.InlineKeyboardButton("Назад", callback_data=formatted_callback)

                markup_request_action.add(item1, item2)

            elif req_status == "answered" or req_status == "waiting":
                if "my_reqs:" in formatted_callback:
                    status_user = "user"
                else:
                    status_user = "agent"

                item1 = types.InlineKeyboardButton(
                    "✏️ Добавить сообщение", callback_data=f"add_message:{req_id}:{status_user}"
                )
                item2 = types.InlineKeyboardButton(
                    "🗂 Показать файлы", callback_data=f"req_files:{req_id}:{callback}:1"
                )

                if status_user == "user":
                    item3 = types.InlineKeyboardButton(
                        "✅ Завершить запрос", callback_data=f"confirm_req:wait:{req_id}"
                    )

                item4 = types.InlineKeyboardButton("Назад", callback_data=formatted_callback)

                if status_user == "user":
                    markup_request_action.add(item1, item2, item3, item4)
                else:
                    markup_request_action.add(item1, item2, item4)

            return markup_request_action
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Error in markup_request_action: {e}. StackTrace: {traceback.format_exc()}",
                module_name="TelegramBots.SupportBot.core"
            )

    def markup_confirm_req(req_id):
        markup_confirm_req = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton(
            "✅ Подтвердить", callback_data=f"confirm_req:true:{req_id}"
        )
        item2 = types.InlineKeyboardButton(
            "❌ Отменить", callback_data=f"open_req:{req_id}:my_reqs-1"
        )
        markup_confirm_req.add(item1, item2)

        return markup_confirm_req

    async def markup_files(number, req_id, callback):
        try:
            async with async_session() as session:
                file_dal = FileDAL(session)
                files = await file_dal.get_files(number=number, req_id=req_id)

            markup_files = types.InlineKeyboardMarkup(row_width=3)
            for file in files:
                id = file.id
                file_name = file.file_name
                type = file.type

                file_text = get_file_text(file_name, type)
                # 📷 | Фото 27.12.2020 14:21:50

                item = types.InlineKeyboardButton(file_text, callback_data=f"send_file:{id}:{type}")
                markup_files.add(item)
            markup_files = page(
                markup_files,
                number,
                files,
                f"req_files:{req_id}:{callback}",
                f"open_req:{req_id}:{callback}",
            )

            return markup_files, len(files)
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Error in markup_files: {e}. StackTrace: {traceback.format_exc()}",
                module_name="TelegramBots.SupportBot.core"
            )

    def markup_agent():
        markup_agent = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton(
            "❗️ Ожидают ответа от поддержки", callback_data="waiting_reqs:1"
        )
        item2 = types.InlineKeyboardButton(
            "⏳ Ожидают ответа от пользователя", callback_data="answered_reqs:1"
        )
        item3 = types.InlineKeyboardButton("✅ Завершенные запросы", callback_data="confirm_reqs:1")
        back_to_agent = types.InlineKeyboardButton("Назад", callback_data="support_back_to_main_menu")
        markup_agent.add(item1, item2, item3, back_to_agent)

        return markup_agent

    def markup_admin():
        markup_admin = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton(
            "✅ Добавить агента поддержки", callback_data="add_agent"
        )
        item2 = types.InlineKeyboardButton("🧑‍💻 Агенты поддержки", callback_data="all_agents:1")
        item3 = types.InlineKeyboardButton("🔑 Одноразовые пароли", callback_data="all_passwords:1")
        item4 = types.InlineKeyboardButton(
            "🎲 Сгенерировать одноразовые пароли", callback_data="generate_passwords"
        )
        item5 = types.InlineKeyboardButton("Назад", callback_data="support_back_to_main_menu")
        markup_admin.add(item1, item2, item3, item4, item5)

        return markup_admin

    async def markup_agents(number):
        try:
            async with async_session() as session:
                agent_dal = AgentDAL(session)
                agents = await agent_dal.get_agents(int(number))

            markup_agents = types.InlineKeyboardMarkup(row_width=3)
            for agent in agents:
                agent_id = agent

                item = types.InlineKeyboardButton(
                    f"🧑‍💻 | {agent_id}", callback_data=f"delete_agent:{agent_id}"
                )
                markup_agents.add(item)

            markup_agents = page(markup_agents, number, agents, "all_agents", "back_admin")

            return markup_agents, len(agents)
        except Exception as e:
            logger.log(
                level=LogLevel.ERROR, 
                message=f"Error in markup_agents: {e}. StackTrace: {traceback.format_exc()}",
                module_name="TelegramBots.SupportBot.core"
            )

    async def markup_passwords(number):
        async with async_session() as session:
            password_dal = PasswordDAL(session)
            passwords = await password_dal.get_passwords(number)

        markup_passwords = types.InlineKeyboardMarkup(row_width=3)
        for password in passwords:
            password_value = password

            item = types.InlineKeyboardButton(
                password_value, callback_data=f"delete_password:{password_value}"
            )
            markup_passwords.add(item)

        markup_passwords = page(markup_passwords, number, passwords, "all_passwords", "back_admin")

        return markup_passwords, len(passwords)

    def markup_confirm_stop():
        markup_confirm_stop = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton("Да", callback_data="stop_bot:confirm")
        item2 = types.InlineKeyboardButton("Нет", callback_data="back_admin")
        markup_confirm_stop.add(item1, item2)

        return markup_confirm_stop

    def support_back_to_request(req_id, callback, number):
        return types.InlineKeyboardMarkup(
            row_width=1,
            keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data=f"open_req:{req_id}:{callback}-{number}"
                    )
                ]
            ],
        )
        
    def support_back_admin():
        return types.InlineKeyboardMarkup(
            row_width=1,
            keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data="back_admin"
                    )
                ]
            ],
        )
    
    def reservation_request_menu(capacity: int, reservation_time, action):
        mp = types.InlineKeyboardMarkup(row_width=2)
        
        yes = types.InlineKeyboardButton(
            text="✔️ Да",
            callback_data=f"reservation_request_confirmed#{capacity}#{reservation_time}#{action}"
        )
        no = types.InlineKeyboardButton(
            text="➖ Нет",
            callback_data="back_to_main_menu"
        )

        mp.add(yes, no)
        return mp
    
    def reservation_request_confirmed_menu():
        mp = types.InlineKeyboardMarkup(row_width=1)
        
        back_to_main_menu = types.InlineKeyboardButton(
            text="🔜 Вернуться в главное меню",
            callback_data="back_to_main_menu"
        )

        mp.add(back_to_main_menu)
        return mp
