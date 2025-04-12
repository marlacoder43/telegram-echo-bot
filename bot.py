from telethon import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN, STORAGE_CHANNEL, MOVIE_CHANNEL
import asyncio
import requests

bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

from commands import register_commands
register_commands(bot)
from movie_handler import register_movie_handlers
register_movie_handlers(bot)
from movie_handler import register_multi_handlers
register_multi_handlers(bot)
from broadcast_handler import register_broadcast_handler
register_broadcast_handler(bot)
from stats_handler import register_stats_handler
register_stats_handler(bot)
from start_handler import register_start_handler
register_start_handler(bot)
from help_handler import register_help_handler
register_help_handler(bot)

def set_bot_commands():
    commands = [
        {"command": "start", "description": "Botni ishga tushirish"},
        {"command": "help", "description": "Yordam"},
        {"command": "kanal", "description": "Obuna kanallarini boshqarish (ADMIN)"},
        {"command": "broadcast", "description": "Xabar yuborish (ADMIN)"},
        {"command": "stats", "description": "Statistika (ADMIN)"}
    ]

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    response = requests.post(url, json={"commands": commands})

    if response.status_code == 200 and response.json().get("ok"):
        print("✅ Bot komandalar o‘rnatildi.")
    else:
        print("❌ Komanda sozlashda xatolik:", response.text)

# Ishga tushirishda bir marta chaqiramiz
set_bot_commands()


print("✅ Bot ishga tushdi")    
bot.run_until_disconnected()