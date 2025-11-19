import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен бота
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # твой Telegram ID
