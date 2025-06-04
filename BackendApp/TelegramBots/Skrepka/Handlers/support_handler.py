import asyncio
import os
import random
import sys
import traceback

import telebot
from telebot import apihelper
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage

from BackendApp.Database.DAL.SupportBot.agent_dal import AgentDAL
from BackendApp.Database.DAL.SupportBot.file_dal import FileDAL
from BackendApp.Database.DAL.SupportBot.message_model import MessageDAL
from BackendApp.Database.DAL.SupportBot.password_dal import PasswordDAL
from BackendApp.Database.DAL.SupportBot.requests_dal import RequestDAL
from BackendApp.Database.session import DBTransactionStatus, async_session
from BackendApp.Logger import LogLevel, logger
from BackendApp.TelegramBots.Skrepka.Config.bot import bot
from BackendApp.TelegramBots.Skrepka.Middlewares.message_context_middleware import (
    message_context_manager,
)
from BackendApp.TelegramBots.SupportBot import config, core
from BackendApp.TelegramBots.SupportBot.inline_markup import InlineMarkup
from BackendApp.TelegramBots.utils.handler_loggining import handler_logging

if config.PROXY_URL:
    apihelper.proxy = {"https": config.PROXY_URL}


class MyStates(StatesGroup):
    get_password_message = State()
    get_additional_message = State()
    get_agent_id_message = State()
    get_new_request = State()

@handler_logging
@bot.message_handler(
    state=MyStates.get_new_request,
    content_types=["text", "document", "photo", "video", "audio", "file"],
)
async def get_new_request(message):
    request = message.text
    user_id = message.from_user.id
    check_file = core.get_file(message)

    message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=message.message_id
    )
    await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
    try:
        # Если пользователь отправляет файл
        if check_file != None:
            file_id = check_file["file_id"]
            file_name = check_file["file_name"]
            type = check_file["type"]
            request = check_file["text"]

            if str(request) == "None":
                msg = await bot.send_message(
                    message.chat.id,
                    "⚠️ Вы не ввели ваш запрос. Попробуйте ещё раз, отправив текст вместе с файлом.",
                    reply_markup=InlineMarkup.support_back_to_main_menu(),
                )

            else:
                async with async_session() as session:
                    request_dal = RequestDAL(session)
                    req_id = await request_dal.new_req(user_id, request)
                    file_dal = FileDAL(session)
                    await file_dal.add_file(req_id, file_id, file_name, type)

                msg = await bot.send_message(
                    message.chat.id,
                    f"✅ Ваш запрос под ID {req_id} создан. Посмотреть текущие запросы можно нажав кнопку <b>Мои текущие запросы</b>",
                    parse_mode="html",
                    reply_markup=InlineMarkup.support_back_to_main_menu(),
                )
                await bot.delete_state(message.from_user.id, message.chat.id)

        # Если пользователь отправляет только текст
        else:
            if request == None:
                msg = await bot.send_message(
                    message.chat.id,
                    "⚠️ Отправляемый вами тип данных не поддерживается в боте. Попробуйте еще раз отправить ваш запрос, использовав один из доступных типов данных (текст, файлы, фото, видео, аудио).",
                    reply_markup=InlineMarkup.support_back_to_main_menu(),
                )
            else:
                async with async_session() as session:
                    request_dal = RequestDAL(session)
                    req_id = await request_dal.new_req(user_id, request)
                msg = await bot.send_message(
                    message.chat.id,
                    f"✅ Ваш запрос под ID {req_id} создан. Посмотреть текущие запросы можно нажав кнопку <b>Мои текущие запросы</b>",
                    parse_mode="html",
                    reply_markup=InlineMarkup.support_back_to_main_menu(),
                )
                await bot.delete_state(message.from_user.id, message.chat.id)

        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id, msgId=msg.message_id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in get_new_request: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )


@handler_logging
@bot.message_handler(state=MyStates.get_password_message, content_types=["text"])
async def get_password_message(message):
    password = message.text
    user_id = message.from_user.id
    try:
        async with async_session() as session:
            password_dal = PasswordDAL(session)
            valid_password = await password_dal.valid_password(password)

        if password == None:
            msg = send_message = bot.send_message(
                message.chat.id,
                "⚠️ Вы отправляете не текст. Попробуйте еще раз.",
                reply_markup=InlineMarkup.back_to_main_menu(),
            )

            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )
            await bot.set_state(send_message, get_password_message)

        elif password.lower() == "отмена":
            msg = await bot.send_message(
                message.chat.id, "Отменено.", reply_markup=InlineMarkup.support_back_to_main_menu()
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )
            await bot.delete_state(message.from_user.id)

        elif valid_password == True:
            async with async_session() as session:
                password_dal = PasswordDAL(session)
                agent_dal = AgentDAL(session)
                await password_dal.delete_password(password)
                await agent_dal.add_agent(user_id)

            msg = await bot.send_message(
                message.chat.id,
                "Выберите раздел технической панели:",
                parse_mode="html",
                reply_markup=InlineMarkup.markup_agent(),
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )

        else:
            msg = await bot.send_message(
                message.chat.id,
                "⚠️ Неверный пароль. Попробуй ещё раз.",
                reply_markup=InlineMarkup.support_back_to_main_menu(),
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )

            await bot.set_state(message.from_user.id, MyStates.get_password_message)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in get_password_message: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )


@handler_logging
@bot.message_handler(commands=["admin"])
async def admin(message):
    user_id = message.from_user.id
    message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=message.message_id
    )
    try:
        await bot.delete_state(user_id)

        if str(user_id) == config.ADMIN_ID:
            msg = await bot.send_message(
                message.chat.id,
                "🔑 Вы авторизованы как Админ",
                reply_markup=InlineMarkup.markup_admin(),
            )
        else:
            msg = await bot.send_message(
                message.chat.id, "🚫 Эта команда доступна только администратору."
            )
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        message_context_manager.add_msgId_to_help_menu_dict(chat_id=message.chat.id, msgId=msg.message_id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in admin: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
@bot.message_handler(commands=["agent"])
async def agent(message):
    try:
        user_id = message.from_user.id
        async with async_session() as session:
            agent_dal = AgentDAL(session)
        if await agent_dal.check_agent_status(user_id) == True:
            msg = await bot.send_message(
                message.chat.id,
                "🔑 Вы авторизованы как Агент поддержки",
                parse_mode="html",
                reply_markup=InlineMarkup.markup_agent(),
            )

        else:
            msg = await bot.send_message(
                message.chat.id,
                "⚠️ Тебя нет в базе. Отправь одноразовый пароль доступа.",
                reply_markup=InlineMarkup.support_back_to_main_menu(),
            )

            await bot.delete_state(user_id)
            await bot.set_state(user_id, MyStates.get_password_message)
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id, msgId=msg.message_id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in agent: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
@bot.message_handler(state=MyStates.get_agent_id_message, content_types=["text"])
async def get_agent_id_message(message):
    message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=message.message_id
    )
    try:
        agent_id = message.text
        if agent_id == None:
            take_agent_id_message = await bot.send_message(
                message.chat.id,
                "⚠️ Вы отправляете не текст. Попробуйте еще раз.",
                reply_markup=InlineMarkup.support_back_to_main_menu(),
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=take_agent_id_message.message_id
            )
            await bot.set_state(message.from_user.id, MyStates.get_agent_id_message)

        elif agent_id.lower() == "отмена":
            msg = await bot.send_message(
                message.chat.id, "Отменено.", reply_markup=InlineMarkup.support_back_to_main_menu()
            )
            await bot.delete_state(message.from_user.id)
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )
            return

        elif not agent_id.isdigit():
            msg = await bot.send_message(
                message.chat.id,
                "⚠️ Неверный айди. Попробуйте ещё раз.",
                reply_markup=InlineMarkup.support_back_admin(),
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )
            await bot.set_state(message.from_user.id, MyStates.get_agent_id_message)

        else:
            async with async_session() as session:
                agent_dal = AgentDAL(session)
                rusult = await agent_dal.add_agent(agent_id)
                if rusult != DBTransactionStatus.SUCCESS:
                    msg = await bot.send_message(
                        message.chat.id,
                        "⚠️ Ошибка при добавление агента! Попробуйте снова.",
                        reply_markup=InlineMarkup.support_back_to_main_menu(),
                    )
                else:
                    msg = await bot.send_message(
                        message.chat.id,
                        "Выберите раздел админ панели:",
                        reply_markup=InlineMarkup.markup_admin(),
                    )

            await bot.delete_state(message.from_user.id)
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in get_agent_id_message: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
def generate_passwords(number, length):
    chars = "abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    passwords = []
    for _ in range(number):
        password = "".join(random.choice(chars) for _ in range(length))
        passwords.append(password)

    return passwords

@handler_logging
async def start_support(message):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        await bot.delete_state(
            message.chat.id,
        )
        message = await bot.send_message(
            message.chat.id,
            "👋🏻 Привет! Это бот для технической поддержки пользователей.\nЕсли у тебя есть какой-либо вопрос или проблема - нажми на кнопку <b>Написать запрос</b> и наши сотрудники в скором времени тебе ответят!",
            parse_mode="html",
            reply_markup=InlineMarkup.support_markup_main(),
        )
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id, msgId=message.message_id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in start_support: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
async def take_new_request(message):
    try: 
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        msg = await bot.send_message(
            message.chat.id,
            "Введите свой запрос и наши сотрудники скоро с вами свяжутся.",
            reply_markup=InlineMarkup.back_to_main_menu(),
        )
        await bot.set_state(
            message.chat.id,
            MyStates.get_new_request,
        )
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id, msgId=msg.message_id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"Error in take_new_request: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )
        
@handler_logging
async def my_requests(call, value, markup_req):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)
        agents_callback = ["answered_reqs", "confirm_reqs", "waiting_reqs"]
        is_agent = call.data.split(":")[0] in agents_callback
        if value == 0:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="⚠️ Запросы не обнаружены.",
                reply_markup=InlineMarkup.support_back_to_main_menu(
                    ) if not is_agent else InlineMarkup.support_back_to_agent_menu(),
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=call.message.chat.id, msgId=msg.message_id
            )
            return
        try:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="Нажмите на запрос, чтобы посмотреть историю переписки, либо добавить сообщение:",
                reply_markup=markup_req,
            )
        except:
            msg = await bot.send_message(
                chat_id=call.message.chat.id, text="Ваши запросы:", reply_markup=markup_req
            )

        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id, msgId=msg.message_id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in my_requests: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )


@handler_logging
async def open_request(call):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)
        await bot.delete_state(
            call.message.chat.id,
        )
        parts = call.data.split(":")
        req_id = parts[1]
        callback = parts[2]

        async with async_session() as session:
            request_dal = RequestDAL(session)
            req_status = await request_dal.get_req_status(req_id)
            request_data = await request_dal.get_request_data(req_id, callback)
        len_req_data = len(request_data)

        i = 1
        for data in request_data:
            if i == len_req_data:
                markup_req = InlineMarkup.markup_request_action(req_id, req_status, callback)
            else:
                markup_req = None
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text=data,
                parse_mode="html",
                reply_markup=markup_req,
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=call.message.chat.id, msgId=msg.message_id
            )
            i += 1

        await bot.answer_callback_query(call.id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in open_request: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
async def add_message(call):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)
        parts = call.data.split(":")
        req_id = parts[1]
        status_user = parts[2]

        take_additional_message = await bot.send_message(
            chat_id=call.message.chat.id,
            text="Отправьте ваше сообщение, использовав один из доступных типов данных (текст, файлы, фото, видео, аудио).",
            reply_markup=InlineMarkup.support_back_to_request(req_id, "open_request", 1),
        )

        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id, msgId=take_additional_message.message_id
        )
        await bot.set_state(call.from_user.id, MyStates.get_additional_message)
        async with bot.retrieve_data(call.from_user.id) as data:
            data["req_id"] = req_id
            data["status_user"] = status_user
        await bot.answer_callback_query(call.id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in add_message: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
async def confirm_req(call):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)

        parts = call.data.split(":")
        confirm_status = parts[1]
        req_id = parts[2]
        async with async_session() as session:
            request_dal = RequestDAL(session)
            req_status = await request_dal.get_req_status(req_id)
        if req_status == "confirm":
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="⚠️ Этот запрос уже завершен.",
                reply_markup=InlineMarkup.support_back_to_main_menu(),
            )
            await bot.answer_callback_query(call.id)

        # Запросить подтверждение завершения
        if confirm_status == "wait":
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="Для завершения запроса - нажмите кнопку <b>Подтвердить</b>",
                parse_mode="html",
                reply_markup=InlineMarkup.markup_confirm_req(req_id),
            )
            await bot.answer_callback_query(call.id)
        # Подтвердить завершение
        elif confirm_status == "true":
            async with async_session() as session:
                request_dal = RequestDAL(session)
                await request_dal.confirm_req(req_id)

            try:
                msg = await bot.send_message(
                    chat_id=call.message.chat.id,
                    text="✅ Запрос успешно завершён.",
                    reply_markup=InlineMarkup.support_back_to_main_menu(),
                )
            except:
                msg = await bot.send_message(
                    chat_id=call.message.chat.id,
                    text="✅ Запрос успешно завершён.",
                    reply_markup=InlineMarkup.support_back_to_main_menu(),
                )
            await bot.answer_callback_query(call.id)
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id, msgId=msg.message_id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in confirm_req: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
async def req_files(call):
    await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)
    try:
        parts = call.data.split(":")
        req_id = parts[1]
        callback = parts[2]
        number = parts[3]

        markup_and_value = await InlineMarkup.markup_files(number, req_id, callback)
        markup_files = markup_and_value[0]
        value = markup_and_value[1]

        if value == 0:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="⚠️ Файлы не обнаружены.",
                reply_markup=InlineMarkup.support_back_to_request(req_id, "my_reqs", 1),
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=call.message.chat.id, msgId=msg.message_id
            )
            return await bot.answer_callback_query(call.id)

        try:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="Нажмите на файл, чтобы получить его.",
                reply_markup=markup_files,
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=call.message.chat.id, msgId=msg.message_id
            )
        except:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="Нажмите на файл, чтобы получить его.",
                reply_markup=markup_files,
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=call.message.chat.id, msgId=msg.message_id
            )

        await bot.answer_callback_query(call.id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in req_files: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
async def send_file(call):
    parts = call.data.split(":")
    id = parts[1]
    type = parts[2]
    try:
        async with async_session() as session:
            file_dal = FileDAL(session)
            file_id = await file_dal.get_file_id(id)

        if type == "photo":
            msg = await bot.send_photo(
                call.message.chat.id,
                photo=file_id,
                reply_markup=InlineMarkup.support_back_to_main_menu(),
            )
        elif type == "document":
            msg = await bot.send_document(
                call.message.chat.id,
                document=file_id,
                reply_markup=InlineMarkup.support_back_to_main_menu(),
            )
        elif type == "video":
            msg = await bot.send_video(
                call.message.chat.id,
                video=file_id,
                reply_markup=InlineMarkup.support_back_to_main_menu(),
            )
        elif type == "audio":
            msg = await bot.send_audio(
                call.message.chat.id,
                audio=file_id,
                reply_markup=InlineMarkup.support_back_to_main_menu(),
            )
        elif type == "voice":
            msg = await bot.send_voice(
                call.message.chat.id,
                voice=file_id,
                reply_markup=InlineMarkup.support_back_to_main_menu(),
            )

        await bot.answer_callback_query(call.id)
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id, msgId=msg.message_id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in send_file: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
async def back_agent(call):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)

        try:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="🔑 Вы авторизованы как Агент поддержки",
                parse_mode="html",
                reply_markup=InlineMarkup.markup_agent(),
            )
        except:
            msg = await bot.send_message(
                call.message.chat.id,
                "🔑 Вы авторизованы как Агент поддержки",
                parse_mode="html",
                reply_markup=InlineMarkup.markup_agent(),
            )

        await bot.answer_callback_query(call.id)
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id, msgId=msg.message_id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in back_agent: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
async def back_admin(call):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)
        await bot.delete_state(call.message.chat.id)
        try:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="🔑 Вы авторизованы как Админ",
                parse_mode="html",
                reply_markup=InlineMarkup.markup_admin(),
            )
        except:
            msg = await bot.send_message(
                call.message.chat.id,
                "🔑 Вы авторизованы как Админ",
                parse_mode="html",
                reply_markup=InlineMarkup.markup_admin(),
            )

        await bot.answer_callback_query(call.id)
        message_context_manager.add_msgId_to_help_menu_dict(chat_id=call.message.chat.id, msgId=msg.message_id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in back_admin: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
async def add_agent(call):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)

        take_agent_id_message = await bot.send_message(
            chat_id=call.message.chat.id,
            text="Чтобы добавить агента поддержки - введите его ID Telegram.",
            reply_markup=InlineMarkup.support_back_admin(),
        )
        await bot.set_state(call.message.chat.id, MyStates.get_agent_id_message)
        await bot.answer_callback_query(call.id)
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id, msgId=take_agent_id_message.message_id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in add_agent: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
async def all_agents(call):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)
        number = call.data.split(":")[1]
        markup_and_value = await InlineMarkup.markup_agents(number)
        markup_agents = markup_and_value[0]
        len_agents = markup_and_value[1]

        if len_agents == 0:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="⚠️ Агенты не обнаружены.",
                reply_markup=InlineMarkup.support_back_admin(),
            )
            await bot.answer_callback_query(call.id)
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=call.message.chat.id, msgId=msg.message_id
            )
            return

        try:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Нажмите на агента поддержки, чтобы удалить его",
                parse_mode="html",
                reply_markup=markup_agents,
            )
        except:
            msg = await bot.send_message(
                call.message.chat.id,
                "Нажмите на агента поддержки, чтобы удалить его",
                parse_mode="html",
                reply_markup=markup_agents,
            )

        await bot.answer_callback_query(call.id)
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id, msgId=msg.message_id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in all_agents: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )


async def delete_agent(call):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)

        agent_id = call.data.split(":")[1]
        async with async_session() as session:
            agent_dal = AgentDAL(session)

            await agent_dal.delete_agent(agent_id)
        markup_agents = await InlineMarkup.markup_agents("1")
        try:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="Нажмите на агента поддержки, чтобы удалить его",
                parse_mode="html",
                reply_markup=markup_agents[0],
            )
        except:
            msg = await bot.send_message(
                call.message.chat.id,
                "Нажмите на агента поддержки, чтобы удалить его",
                parse_mode="html",
                reply_markup=markup_agents[0],
            )

        await bot.answer_callback_query(call.id)
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id, msgId=msg.message_id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in delete_agent: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

async def all_passwords(call):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)
        number = call.data.split(":")[1]
        markup_and_value = await InlineMarkup.markup_passwords(number)
        markup_passwords = markup_and_value[0]
        len_passwords = markup_and_value[1]

        if len_passwords == 0:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="⚠️ Пароли не обнаружены.",
                reply_markup=InlineMarkup.support_back_admin(),
            )
            await bot.answer_callback_query(call.id)
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=call.message.chat.id, msgId=msg.message_id
            )
            return

        try:
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="Нажмите на пароль, чтобы удалить его",
                parse_mode="html",
                reply_markup=markup_passwords,
            )
        except:
            msg = await bot.send_message(
                call.message.chat.id,
                "Нажмите на пароль, чтобы удалить его",
                parse_mode="html",
                reply_markup=markup_passwords,
            )
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id, msgId=msg.message_id
        )
        await bot.answer_callback_query(call.id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in all_passwords: {e}\n{traceback.format_exc()}",
            module_name="TelegramBots/Skrepka/Handlers/support_handler.py"
        )

@handler_logging
async def delete_password(call):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)

        password = call.data.split(":")[1]
        async with async_session() as session:
            password_dal = PasswordDAL(session)
            await password_dal.delete_password(password)

        try:
            markup_passwords_delete = await InlineMarkup.markup_passwords("1")
            msg = await bot.send_message(
                chat_id=call.message.chat.id,
                text="Нажмите на пароль, чтобы удалить его",
                parse_mode="html",
                reply_markup=markup_passwords_delete[0],
            )
        except:
            msg = await bot.send_message(
                call.message.chat.id,
                "Нажмите на пароль, чтобы удалить его",
                parse_mode="html",
                reply_markup=markup_passwords_delete[0],
            )
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id, msgId=msg.message_id
        )
        await bot.answer_callback_query(call.id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in delete_password: {e}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )
        
@handler_logging
async def generate_passwords_and_send(call):
    try: 
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)
        # 10 - количество паролей, 16 - длина пароля
        passwords = generate_passwords(1, 16)
        async with async_session() as session:
            password_dal = PasswordDAL(session)
            await password_dal.add_passwords(passwords)

        text_passwords = ""
        i = 1
        for password in passwords:
            text_passwords += f"{i}. {password}\n"
            i += 1

        msg = await bot.send_message(
            call.message.chat.id,
            f"✅ Сгенерировано {i-1} паролей:\n\n{text_passwords}",
            parse_mode="html",
            reply_markup=InlineMarkup.support_back_to_main_menu(),
        )
        markup_passwords_delete = await InlineMarkup.markup_passwords("1")
        msg = await bot.send_message(
            call.message.chat.id,
            "Нажмите на пароль, чтобы удалить его",
            parse_mode="html",
            reply_markup=markup_passwords_delete[0],
        )

        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id, msgId=msg.message_id
        )
        await bot.answer_callback_query(call.id)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"Error while sending generate_passwords_and_send: {e}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )

@handler_logging
async def stop_bot(call):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=call.message.chat.id)

        status = call.data.split(":")[1]

        # Запросить подтверждение на отключение
        if status == "wait":
            try:
                msg = await bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"Вы точно хотите отключить бота?",
                    parse_mode="html",
                    reply_markup=InlineMarkup.markup_confirm_stop(),
                )
            except:
                msg = await bot.send_message(
                    call.message.chat.id,
                    f"Вы точно хотите отключить бота?",
                    parse_mode="html",
                    reply_markup=InlineMarkup.markup_confirm_stop(),
                )
            await bot.answer_callback_query(call.id)
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=call.message.chat.id, msgId=msg.message_id
            )

        # Подтверждение получено
        elif status == "confirm":
            try:
                msg = await bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="✅ Бот оключен.",
                )
            except:
                msg = await bot.send_message(chat_id=call.message.chat.id, text="✅ Бот оключен.")

            await bot.answer_callback_query(call.id)
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=call.message.chat.id, msgId=msg.message_id
            )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in send_file: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )


@bot.message_handler(
    state=MyStates.get_additional_message,
    content_types=["text", "document", "photo", "video", "audio", "file", "voice"],
)
async def get_additional_message(message):
    try:
        async with bot.retrieve_data(message.from_user.id) as data:
            req_id = data["req_id"]
            status = data["status_user"]

        if message.content_type == "voice":
            return await bot.send_message(
                message.chat.id, 
                "⚠️ Голосовые сообщения не поддерживаются. Напишите текстом или пришлите файл, видео или аудио.", 
                reply_markup=InlineMarkup.support_back_to_request(req_id, "my_reqs", 1)
            )
                
        additional_message = message.text
        check_file = core.get_file(message)

        # Если пользователь отправляет файл
        if check_file != None:
            file_id = check_file["file_id"]
            file_name = check_file["file_name"]
            type = check_file["type"]
            additional_message = check_file["text"]
            async with async_session() as session:
                file_dal = FileDAL(session)
                await file_dal.add_file(req_id, file_id, file_name, type)

            await bot.delete_state(message.from_user.id, message.chat.id)
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=message.message_id
            )

        if additional_message == None:
            take_additional_message = await bot.send_message(
                chat_id=message.chat.id,
                text="⚠️ Отправляемый вами тип данных не поддерживается в боте. Попробуйте еще раз отправить ваше сообщение, использовав один из доступных типов данных (текст, файлы, фото, видео, аудио).",
                reply_markup=InlineMarkup.support_back_to_main_menu(),
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=take_additional_message.message_id
            )

        else:
            await bot.delete_state(message.from_user.id, message.chat.id)
            if additional_message != None:
                async with async_session() as session:
                    message_dal = MessageDAL(session)
                    await message_dal.add_message(req_id, additional_message, status)

            if check_file != None:
                if additional_message != "None":
                    text = "✅ Ваш файл и сообщение успешно отправлены!"
                else:
                    text = "✅ Ваш файл успешно отправлен!"
            else:
                text = "✅ Ваше сообщение успешно отправлено!"

            msg = await bot.send_message(
                message.chat.id, 
                text, 
                reply_markup=InlineMarkup.support_back_to_agent_menu(
                    ) if status == "agent" else InlineMarkup.support_back_to_main_menu()
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )

            if status == "agent":
                async with async_session() as session:
                    request_dal = RequestDAL(session)
                    user_id = await request_dal.get_user_id_of_req(req_id=req_id)
                try:
                    if additional_message == "None":
                        additional_message = ""

                    msg = await bot.send_message(
                        user_id,
                        f"⚠️ Получен новый ответ на ваш запрос ID {req_id}!\n\n🧑‍💻 Ответ агента поддержки:\n{additional_message}",
                        reply_markup=InlineMarkup.support_back_to_main_menu(),
                    )
                    message_context_manager.add_msgId_to_help_menu_dict(
                        chat_id=message.chat.id, msgId=msg.message_id
                    )

                    if type == "photo":
                        msg = await bot.send_photo(
                            user_id,
                            photo=file_id,
                            reply_markup=InlineMarkup.support_back_to_main_menu(),
                        )
                    elif type == "document":
                        msg = await bot.send_document(
                            user_id,
                            document=file_id,
                            reply_markup=InlineMarkup.support_back_to_main_menu(),
                        )
                    elif type == "video":
                        msg = await bot.send_video(
                            user_id,
                            video=file_id,
                            reply_markup=InlineMarkup.support_back_to_main_menu(),
                        )
                    elif type == "audio":
                        msg = await bot.send_audio(
                            user_id,
                            audio=file_id,
                            reply_markup=InlineMarkup.support_back_to_main_menu(),
                        )
                    elif type == "voice":
                        msg = await bot.send_voice(
                            user_id,
                            voice=file_id,
                            reply_markup=InlineMarkup.support_back_to_main_menu(),
                        )
                    else:
                        msg = await bot.send_message(
                            user_id,
                            additional_message,
                            reply_markup=InlineMarkup.support_back_to_main_menu(),
                        )
                        message_context_manager.add_msgId_to_help_menu_dict(
                            chat_id=message.chat.id, msgId=msg.message_id
                        )
                except:
                    pass
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in send_file: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.Skrepka.Handlers.support_handler"
        )