from telebot import types
from BackendApp.TelegramBots.Skrepka.Config import bot
from BackendApp.TelegramBots.Skrepka.Middlewares.message_context_middleware import message_context_manager
from BackendApp.TelegramBots.Skrepka.Markups.message_text import MessageText
from BackendApp.TelegramBots.Skrepka.Markups.inline_markup import InlineMarkup
from BackendApp.Middleware.promocodes_middleware import PromocodesMiddleware
from BackendApp.Middleware.quiz_middleware import *
from BackendApp.TelegramBots.Skrepka.Handlers.main_menu_handler import main_menu

from collections import defaultdict
from math import ceil

from BackendApp.TelegramBots.utils.handler_loggining import handler_logging
from BackendApp.Logger import logger, LogLevel

selected_quiz_by_user = defaultdict(str)
user_state = defaultdict(lambda: {"quiz_index": 0, "correct_answers": 0})
user_quiz = dict()

BAR_ID = 2
BTNS_PER_PAGE = 10

@handler_logging
async def test(message, page):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(chat_id=message.chat.id)
        keyboard = types.InlineKeyboardMarkup(row_width=3)

        test_entities = await get_all_by_bar_id(bar_id=BAR_ID)
        tests = [test.name for test in test_entities]

        if (len(tests) > 0):
            amount_of_pages = ceil(len(tests)/BTNS_PER_PAGE)
            chunks = []
            i = 0
            while i < len(tests):
                chunks.append(tests[i:i + BTNS_PER_PAGE])
                i += BTNS_PER_PAGE

            data_to_display = chunks[page - 1]
            for data in data_to_display:
                button = types.InlineKeyboardButton(text=data, callback_data=data + "_test_promoactions")
                keyboard.add(button)

            InlineMarkup.quiz_slider(
                page=page,
                amount_of_pages=amount_of_pages,
                keyboard=keyboard
            )
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text="📋 Выберите тест, чтобы\nузнать подробную информацию:",
                reply_markup=keyboard
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id,
                msgId=msg.id
            )

        else:
            keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data=f"back_to_promo_menu"))
            msg = await bot.send_message(
                message.chat.id, 
                "🍃 Пока что нет никаких квизов...", 
                reply_markup=keyboard
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id,
                msgId=msg.id
            )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in test_handler.py in test function: {e}",
            module_name="skrepka_bot"
        )

@handler_logging
async def back_to_tests(message, page):    
    try:
        keyboard = types.InlineKeyboardMarkup(row_width=3)

        tests = await get_all_test_names()

        if (len(tests) > 0):
            amount_of_pages = ceil(len(tests)/BTNS_PER_PAGE)
            chunks = []
            i = 0
            while i < len(tests):
                chunks.append(tests[i:i + BTNS_PER_PAGE])
                i += BTNS_PER_PAGE

            data_to_display = chunks[page - 1]
            for data in data_to_display:
                button = types.InlineKeyboardButton(text=data, callback_data=data + "_test_promoactions")
                keyboard.add(button)

            InlineMarkup.quiz_slider(
                page=page,
                amount_of_pages=amount_of_pages,
                keyboard=keyboard
            )
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text="📋 Выберите тест, чтобы\nузнать подробную информацию:",
                reply_markup=keyboard
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id,
                msgId=msg.id
            )

        else:
            keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data=f"back_to_promo_menu"))
            msg = await bot.send_message(
                message.chat.id, 
                "🍃 Пока что нет никаких квизов...", 
                reply_markup=keyboard
            )

            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id,
                msgId=msg.id
            )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in test_handler.py in back_to_tests function: {e}",
            module_name="skrepka_bot"
        )

def get_test_text(test: Test) -> str:
    return f"""📋 {test.name}

✍ {test.description}
        
✅ Вам необходимо верно ответить на {test.correct_cnt} из {test.total_cnt}.
        
🎁 В случае успеха вы получите промокод!!!

❗ У вас есть всего одна попытка получить его, но не ограниченное колчество попыток на прохождение теста!!!
"""


async def get_result_text(correct_answers: int, selected_quiz: str, user_id) -> str:
    try:
        test_obj = None
        async with async_session() as session:
            test_dal = TestDAL(session)
            test_obj = await test_dal.get_by_name(selected_quiz)

            if test_obj is None:
                raise Exception("Нет такого теста")
        participant_test_info = await get_first_try(chat_id=user_id, test_id=test_obj.test_id)
        if (correct_answers >= test_obj.correct_cnt):
            if (not participant_test_info.claimed_reward):
                return f"🎉 Поздравляем! Вы ответили верно на {correct_answers} из {test_obj.total_cnt} вопросов! Вы еще не получили награду, она находится в области теста."
            else:
                return f"🎉 Поздравляем! Вы ответили верно на {correct_answers} из {test_obj.total_cnt} вопросов!"
        else:
            return f"❌ К сожалению, Вы ответили верно только на {correct_answers} из {test_obj.total_cnt} вопросов."    
        
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in test_handler.py in get_result_text function: {e}",
            module_name="skrepka_bot"
        )


@handler_logging
async def send_test_detail_info(call, test_name: str):
    try:    
        test = await get_test_by_name(test_name)

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button_select_another = types.InlineKeyboardButton(text="◀️ Назад", callback_data="select_another_test_promoactions")
        button_start = types.InlineKeyboardButton(text="▶️ Начать", callback_data="start_test_promoactions")

        selected_quiz_by_user[call.message.chat.id] = test_name
        participant_test_info = await get_first_try(chat_id=call.message.chat.id, test_id=test.test_id)

        if (participant_test_info):
            if (participant_test_info.is_first_try and participant_test_info.get_reward and not(participant_test_info.claimed_reward)):
                keyboard.add(
                    types.InlineKeyboardButton(
                        text="🎟 Получи промокод за победу в тесте",
                        callback_data=f"get_award_for_test#{participant_test_info.id}#{test_name}"
                    )
                )
        
        keyboard.add(button_select_another, button_start)
        msg = await bot.send_message(
            chat_id=call.message.chat.id,
            text=get_test_text(test),
            reply_markup=keyboard
        )
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=call.message.chat.id,
            msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in test_handler.py in send_test_detail_info function: {e}",
            module_name="skrepka_bot"
        )

@handler_logging
async def get_award_for_test(message, result_id, test_name):
    try:
        await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)
        test = await get_test_by_name(test_name)
        free_promocodes = await PromocodesMiddleware.get_free_promocodes_by_type(type=test.promocode_type)
        if (free_promocodes != DBTransactionStatus.NOT_EXIST):
            result = await PromocodesMiddleware.add_client_to_promocode(
                number=free_promocodes[0].number, 
                client_chat_id=message.chat.id
            )
            if (result == DBTransactionStatus.SUCCESS):
                await update_test_result(result_id=result_id, claimed_reward=True)
                msg_text = "Вам был успешно добавлен случайный новый промокод 🥳 Вы можете посмотреть его наличие в вкладке профиля \"🎟 Мои промокоды\""
            else:
                msg_text = "Произошла ошибка при взаимодействии с базой данных, попробуйте еще раз позже 😔"

        else:
            msg_text = "К сожалению, сейчас нет доступных промокодов в базе данных 😔"
        
        mp = types.InlineKeyboardMarkup(row_width=1)
        mp.add(
            types.InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="select_another_test_promoactions"
            )
        )
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=mp
        )

        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id, msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in test_handler.py in get_award_for_test function: {e}",
            module_name="skrepka_bot"
        )


async def back_to_main_menu(user_id):
    msg = await bot.send_message(
        user_id,
        MessageText.menu_text(),
        reply_markup=InlineMarkup.main_menu(),
        parse_mode="html"
    )

    message_context_manager.add_msgId_to_help_menu_dict(chat_id=user_id, msgId=msg.message_id)

@handler_logging
@bot.poll_answer_handler()
async def handle_poll_answer(poll_answer):
    try:
        user_id = poll_answer.user.id
        quiz_index = user_state[user_id]["quiz_index"]
        correct_answers = user_state[user_id]["correct_answers"]
        quizes = user_quiz[user_id]

        if poll_answer.option_ids[0] == quizes[quiz_index].correct_ans_id:
            correct_answers += 1

        quiz_index += 1
        user_state[user_id]["quiz_index"] = quiz_index
        user_state[user_id]["correct_answers"] = correct_answers

        if quiz_index >= len(quizes):
            await add_test_result(selected_quiz_by_user[user_id], correct_answers, user_id)
            msg = await bot.send_message(
                chat_id=user_id, 
                text=(await get_result_text(correct_answers, selected_quiz_by_user[user_id], user_id)),
                reply_markup=types.InlineKeyboardMarkup(
                    row_width=1,
                    keyboard=[
                        [
                            types.InlineKeyboardButton(
                                text="🔙 Назад",
                                callback_data="quiz"
                            )
                        ]
                    ]
                )
            )
            message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=user_id,
                msgId=msg.id
            )

            del user_state[user_id]
        else:
            await send_next_quiz(user_id, quiz_index)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in test_handler.py in handle_poll_answer function: {e}",
            module_name="skrepka_bot"
        )


async def send_next_quiz(user_id, quiz_index):
    try:
        if quiz_index == 0:
            test_name = selected_quiz_by_user[user_id]
            quizes = await get_all_quizes_for_test(test_name)
            user_quiz[user_id] = quizes

        quizes = user_quiz[user_id]

        next_quiz = quizes[quiz_index]
        header = next_quiz.header
        answer_cnt = next_quiz.answer_cnt
        answers = next_quiz.answers
        correct_ans_id = next_quiz.correct_ans_id

        msg = await bot.send_poll(
            chat_id=user_id,
            type="quiz",
            is_anonymous=False,
            question=header,
            options=answers,
            correct_option_id=correct_ans_id,
        )
        message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=user_id,
            msgId=msg.id
        )
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"An error occurred in test_handler.py in send_next_quiz function: {e}",
            module_name="skrepka_bot"
        )    


@bot.callback_query_handler(func=lambda call: "_test_promoactions" in call.data)
async def handle_callback_query(call):    
    if call.data == "select_another_test_promoactions":
        await test(call.message, 1)

    elif call.data == "start_test_promoactions":
        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=call.message.chat.id,
        )
        test_name = selected_quiz_by_user[call.message.chat.id]
        user_id = call.from_user.id
        await send_next_quiz(user_id, 0)

    else:
        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=call.message.chat.id,
        )
        test_name = call.data[:-len("_test_promoactions")]
        await send_test_detail_info(call, test_name)
