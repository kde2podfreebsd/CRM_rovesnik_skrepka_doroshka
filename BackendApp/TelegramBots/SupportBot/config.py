"""
Для начала работы с ботом вам необходимо настроить конфигурационный файл бота - config.py
Обязательными переменными является TOKEN, ADMIN_ID и MySQL.
PROXY_URL вы можете оставить пустым.
"""

import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = "5975175083:AAHrVzSQEuaLKssbHzi2NxxGg2XJIjclfjY"
ADMIN_ID = os.getenv("SUPPORT_ADMIN_ID")
PROXY_URL = ""
