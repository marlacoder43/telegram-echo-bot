from telethon import events, Button
from config import ADMIN_IDS  # Changed from ADMIN_ID to ADMIN_IDS
from utils import load_start, save_start, load_users, save_users, is_subscribed, send_force_sub_message
from datetime import datetime
import os
import json

EDIT_STATE_FILE = "edit_start_mode.txt"

def register_start_handler(bot):
    
    # Helper function to check admin status
    def is_admin(user_id):
        return user_id in ADMIN_IDS

    @bot.on(events.NewMessage(pattern="/start"))
    async def start(event):
        user = await event.get_sender()
        user_id = user.id

        # Save user data
        users = load_users()
        if str(user_id) not in users:
            users[str(user_id)] = {
                "first_name": user.first_name,
                "username": user.username or None,
                "registered": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_users(users)

        # Check subscription
        if not await is_subscribed(bot, user_id):
            await send_force_sub_message(bot, user_id)
            return

        # Load and send start message
        start_data = load_start()
        text = start_data["text"].format(first_name=user.first_name)

        # Show edit buttons only for admins
        buttons = [
            [Button.inline("✏️ Start xabarini o'zgartirish", b"edit_start_text")],
            [Button.inline("🖼 Start rasmini o'zgartirish", b"edit_start_photo")]
        ] if is_admin(user_id) else None

        if start_data["photo"] and os.path.exists(start_data["photo"]):
            await bot.send_file(
                user_id, 
                start_data["photo"], 
                caption=text, 
                buttons=buttons
            )
        else:
            await bot.send_message(user_id, text, buttons=buttons)

    @bot.on(events.CallbackQuery(data=b"edit_start_text"))
    async def edit_text_prompt(event):
        if not is_admin(event.sender_id):
            await event.answer("❌ Siz admin emassiz!", alert=True)
            return
            
        await event.delete()
        await event.respond(
            "✍️ Yangi start xabarini yuboring.\n\n"
            "Quyidagi o'zgaruvchilarni ishlatishingiz mumkin:\n"
            "• {first_name} - Foydalanuvchi ismi\n"
            "• {username} - Foydalanuvchi nomi\n"
            "• {date} - Sana",
            buttons=[[Button.inline("❌ Bekor qilish", b"cancel_edit")]]
        )
        with open(EDIT_STATE_FILE, "w") as f:
            f.write(f"text:{event.sender_id}")  # Store which admin is editing

    @bot.on(events.CallbackQuery(data=b"edit_start_photo"))
    async def edit_photo_prompt(event):
        if not is_admin(event.sender_id):
            await event.answer("❌ Siz admin emassiz!", alert=True)
            return
            
        await event.delete()
        await event.respond(
            "🖼 Yangi start rasmni yuboring (foto sifatida).",
            buttons=[[Button.inline("❌ Bekor qilish", b"cancel_edit")]]
        )
        with open(EDIT_STATE_FILE, "w") as f:
            f.write(f"photo:{event.sender_id}")  # Store which admin is editing

    @bot.on(events.CallbackQuery(data=b"cancel_edit"))
    async def cancel_edit(event):
        if os.path.exists(EDIT_STATE_FILE):
            os.remove(EDIT_STATE_FILE)
        await event.delete()
        await start(event)

    @bot.on(events.NewMessage(func=lambda e: os.path.exists(EDIT_STATE_FILE)))
    async def handle_edit_input(event):
        with open(EDIT_STATE_FILE, "r") as f:
            content = f.read().strip()
            mode, admin_id = content.split(":", 1)
            admin_id = int(admin_id)

        # Only the admin who started editing can complete it
        if event.sender_id != admin_id:
            return

        if mode == "text":
            save_start(text=event.raw_text)
            await event.reply("✅ Start matni saqlandi.")
        elif mode == "photo" and event.photo:
            os.makedirs("media", exist_ok=True)
            path = await event.download_media(file="media/start_photo.jpg")
            save_start(photo=path)
            await event.reply("✅ Start rasmi saqlandi.")

        os.remove(EDIT_STATE_FILE)
        await start(event)
print("📡 start ishladi")                