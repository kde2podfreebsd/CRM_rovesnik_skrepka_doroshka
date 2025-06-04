import datetime
import random
import traceback

from BackendApp.Logger import LogLevel, logger


def get_file(message):
    try:
        dt = datetime.datetime.now()
        date_now = dt.strftime("%d.%m.%Y %H:%M:%S")
        
        if message.content_type == "photo":
            return {
                "file_id": message.photo[-1].file_id,
                "file_name": date_now,
                "type": "photo",
                "text": str(message.caption),
            }

        if message.content_type == "document":
            file_name = message.__dict__.get("document").__dict__["file_name"]
            return {
                "file_id": message.__dict__[message.content_type].__dict__["file_id"],
                "file_name": file_name,
                "type": message.content_type,
                "text": str(message.__dict__.get("caption")),
            }
        if message.content_type == "video":
            file_name = message.__dict__.get("video").__dict__["file_name"]
            return {
                "file_id": message.__dict__[message.content_type].__dict__["file_id"],
                "file_name": file_name,
                "type": message.content_type,
                "text": str(message.__dict__.get("caption")),
            }
        if message.content_type == "audio":
            file_name = message.__dict__.get("audio").__dict__["file_name"]
            return {
                "file_id": message.__dict__[message.content_type].__dict__["file_id"],
                "file_name": file_name,
                "type": message.content_type,
                "text": str(message.__dict__.get("caption")),
            }
        if message.content_type == "voice":
            file_name = message.__dict__.get("voice").__dict__["file_name"]
            return {
                "file_id": message.__dict__[message.content_type].__dict__["file_id"],
                "file_name": file_name,
                "type": message.content_type,
            }
        return None
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR, 
            message=f"Error in get_file: {e}. StackTrace: {traceback.format_exc()}",
            module_name="TelegramBots.SupportBot.core"
        )

def get_icon_from_status(req_status, user_status):
    if req_status == "confirm":
        return "✅"
    elif req_status == "waiting":
        if user_status == "user":
            return "⏳"
        elif user_status == "agent":
            return "❗️"
    elif req_status == "answered":
        if user_status == "user":
            return "❗️"
        elif user_status == "agent":
            return "⏳"


def get_file_text(file_name, type):
    if type == "photo":
        return f"📷 | Фото {file_name}"
    elif type == "document":
        return f"📄 | Документ {file_name}"
    elif type == "video":
        return f"🎥 | Видео {file_name}"
    elif type == "audio":
        return f"🎵 | Аудио {file_name}"
    elif type == "voice":
        return f"🎧 | Голосовое сообщение {file_name}"


def generate_passwords(number, length):
    chars = "abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    passwords = []
    for _ in range(number):
        password = "".join(random.choice(chars) for _ in range(length))
        passwords.append(password)

    return passwords
