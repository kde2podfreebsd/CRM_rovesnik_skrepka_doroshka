from BackendApp.TelegramBots.HeadBot.Config import bot
from datetime import datetime, timedelta


class MessageContextManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.help_menu_msgId_to_delete = {}

    def add_msgId_to_help_menu_dict(self, chat_id, msgId):
        if (chat_id in self.help_menu_msgId_to_delete.keys()):
            self.help_menu_msgId_to_delete[chat_id].append((msgId, datetime.now() + timedelta(hours=3)))
        else:
            self.help_menu_msgId_to_delete[chat_id] = [(msgId, datetime.now() + timedelta(hours=3))]

    async def delete_msgId_from_help_menu_dict(self, chat_id):
        if self.help_menu_msgId_to_delete.get(chat_id) is not None:
            if self.help_menu_msgId_to_delete[chat_id] is not None:
                for msgId in self.help_menu_msgId_to_delete[chat_id]:
                    try:
                        await bot.delete_message(chat_id, msgId[0])
                    except Exception as e:
                        # 48 hours have passed and message cannot be deleted due to telegram api restrictions
                        pass
                self.help_menu_msgId_to_delete[chat_id] = []


message_context_manager = MessageContextManager()
