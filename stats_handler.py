from telethon import events, Button
from config import ADMIN_IDS  # Changed from ADMIN_ID to ADMIN_IDS
import json
import os
from datetime import datetime

USERS_FILE = "users.json"
LIST_FILE = "list.json"

def register_stats_handler(bot):
    
    # Helper function to check admin status
    def is_admin(user_id):
        return user_id in ADMIN_IDS

    @bot.on(events.NewMessage(pattern="/stats"))
    async def stats_handler(event):
        if not is_admin(event.sender_id):  # Updated admin check
            await event.respond("❌ Siz admin emassiz!")
            return

        # Load data
        users = load_users()
        user_count = len(users)
        movies = load_list()
        movie_count = len(movies)

        buttons = [
            [Button.inline("🗂️ Ko'proq ma'lumot", b"more_stats")]
        ]

        await event.respond(
            f"📊 <b>Bot statistikasi</b>\n\n"
            f"👥 Foydalanuvchilar: <b>{user_count}</b>\n"
            f"🎬 Kinolar: <b>{movie_count}</b>\n"
            f"🔄 Oxirgi yangilanish: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            buttons=buttons,
            parse_mode="html"
        )

    @bot.on(events.CallbackQuery(data=b"more_stats"))
    async def more_options(event):
        if not is_admin(event.sender_id):  # Admin check for callback
            await event.answer("❌ Siz admin emassiz!", alert=True)
            return

        await event.edit(
            "💾 Qo'shimcha ma'lumotlar:",
            buttons=[
                [Button.inline("🎬 Kinolar ro'yxati", b"show_movies")],
                [Button.inline("👥 Foydalanuvchilar", b"show_users")],
                [Button.inline("🔙 Orqaga", b"back_stats")]
            ]
        )

    @bot.on(events.CallbackQuery(data=b"show_movies"))
    async def show_movie_list(event):
        if not is_admin(event.sender_id):
            await event.answer("❌ Siz admin emassiz!", alert=True)
            return

        movies = load_list()
        if not movies:
            return await event.edit("🎥 Hozircha hech qanday kino mavjud emas.")

        movie_text = "\n".join([f"• {m}" for m in movies[:50]])  # Show first 50 to avoid message too long
        if len(movies) > 50:
            movie_text += f"\n\n...va yana {len(movies)-50} ta"

        await event.edit(
            f"<b>🎦 Kinolar ro'yxati (jami: {len(movies)})</b>\n\n{movie_text}",
            parse_mode="html",
            buttons=[[Button.inline("🔙 Orqaga", b"more_stats")]]
        )

    @bot.on(events.CallbackQuery(data=b"show_users"))
    async def show_users_list(event):
        if not is_admin(event.sender_id):
            await event.answer("❌ Siz admin emassiz!", alert=True)
            return

        users = load_users()
        if not users:
            return await event.edit("👤 Hozircha foydalanuvchilar mavjud emas.")

        text = ""
        for i, (uid, info) in enumerate(users.items(), 1):
            name = info.get("first_name", "Noma'lum")
            username = f"@{info['username']}" if info.get("username") else ""
            registered = info.get("registered", "Noma'lum vaqt")
            text += f"{i}. {name} {username}\n   🆔 <code>{uid}</code>\n   📅 {registered}\n\n"
            if i >= 20:  # Limit to 20 users per message
                text += f"...va yana {len(users)-20} ta foydalanuvchi"
                break

        await event.edit(
            f"<b>👤 Foydalanuvchilar (jami: {len(users)})</b>\n\n{text}",
            parse_mode="html",
            buttons=[[Button.inline("🔙 Orqaga", b"more_stats")]]
        )

    @bot.on(events.CallbackQuery(data=b"back_stats"))
    async def back_to_main_stats(event):
        if not is_admin(event.sender_id):
            await event.answer("❌ Siz admin emassiz!", alert=True)
            return

        users = load_users()
        movies = load_list()

        await event.edit(
            f"📊 <b>Umumiy statistika</b>\n\n"
            f"👥 Foydalanuvchilar: <b>{len(users)}</b>\n"
            f"🎬 Kinolar: <b>{len(movies)}</b>\n"
            f"🕒 Oxirgi yangilanish: {datetime.now().strftime('%H:%M:%S')}",
            buttons=[[Button.inline("🗂️ Ko'proq ma'lumot", b"more_stats")]],
            parse_mode="html"
        )

# Helper functions
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def load_list():
    if not os.path.exists(LIST_FILE):
        return []
    with open(LIST_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

print("📑 stats ishladi")                    