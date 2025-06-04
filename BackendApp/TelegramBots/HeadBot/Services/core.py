import datetime
import random


def get_file(message):
    types = ["document", "video", "audio", "voice"]
    dt = datetime.datetime.now()
    date_now = dt.strftime("%d.%m.%Y %H:%M:%S")
    print()

    try:
        return {
            "file_id": message.photo[-1].file_id,
            "file_name": date_now,
            "type": "photo",
            "text": str(message.caption),
        }
    except:
        try:
            if message.content_type in types:
                file_name = message.__dict__.get("document").__dict__["file_name"]
                return {
                    "file_id": message.__dict__[message.content_type].__dict__["file_id"],
                    "file_name": file_name,
                    "type": message.content_type,
                    "text": str(message.__dict__.get("caption")),
                }
        except Exception as e:
            print(e)

    return None


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
