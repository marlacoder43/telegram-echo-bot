from telethon import events, Button
from config import ADMIN_IDS  # Changed from ADMIN_ID to ADMIN_IDS
from utils import load_forced_subs, save_forced_subs, is_subscribed, send_force_sub_message, EDIT_FORCE_SUB_FILE
import os

def register_commands(bot):
    # Helper function to check admin status
    def is_admin(user_id):
        return user_id in ADMIN_IDS

    @bot.on(events.CallbackQuery(data=b"check_sub"))
    async def check_subscription(event):
        user_id = event.sender_id
        if await is_subscribed(bot, user_id):
            await event.edit("✅ Obuna tasdiqlandi. Endi botdan foydalanishingiz mumkin.")
        else:
            await event.answer("❌ Hali ham barcha kanallarga obuna bo'lmadingiz!", alert=True)

    @bot.on(events.NewMessage(pattern="/kanal"))
    async def manage_channels(event):
        if not is_admin(event.sender_id):  # Changed to use is_admin()
            return
            
        channels = load_forced_subs()
        buttons = [[Button.inline(f"🚫 O'chirish - {ch}", f"del_{ch}")] for ch in channels]
        if len(channels) < 6:
            buttons.append([Button.inline("➕ Kanal qo'shish", b"add_channel")])

        await bot.send_message(
            event.sender_id,  # Reply to whoever sent the command (admin)
            "📢 Majburiy obuna kanallarini boshqarish:",
            buttons=buttons
        )

    @bot.on(events.CallbackQuery(data=b"add_channel"))
    async def request_channel_id(event):
        if not is_admin(event.sender_id):  # Admin check
            await event.answer("❌ Siz admin emassiz!", alert=True)
            return
            
        await event.respond("🔹 Iltimos, kanal username yuboring (masalan: kanal_nomi yoki @kanal_nomi):")
        with open(EDIT_FORCE_SUB_FILE, "w") as f:
            f.write(str(event.sender_id))  # Store which admin is adding

    @bot.on(events.NewMessage(func=lambda e: os.path.exists(EDIT_FORCE_SUB_FILE)))
    async def add_channel_input(event):
        with open(EDIT_FORCE_SUB_FILE, "r") as f:
            admin_id = int(f.read().strip())
            
        if event.sender_id != admin_id:  # Only the admin who started can add
            return

        channel = event.raw_text.strip()
        channels = load_forced_subs()

        if channel.startswith("@") or channel.startswith("-100"):
            if channel in channels:
                await event.reply("⚠️ Bu kanal allaqachon ro'yxatda.")
            elif len(channels) >= 6:
                await event.reply("⚠️ 6 tadan ortiq kanal qo'shib bo'lmaydi!")
            else:
                channels.append(channel)
                save_forced_subs(channels)
                await event.reply(f"✅ {channel} kanal qo'shildi.")
        else:
            await event.reply("⚠️ Noto'g'ri format! Kanal ID yoki @username yuboring.")

        os.remove(EDIT_FORCE_SUB_FILE)

    @bot.on(events.CallbackQuery(data=lambda d: d.startswith(b"del_")))
    async def remove_channel(event):
        if not is_admin(event.sender_id):  # Admin check
            await event.answer("❌ Siz admin emassiz!", alert=True)
            return
            
        ch = event.data.decode().split("_", 1)[1]
        channels = load_forced_subs()
        if ch in channels:
            channels.remove(ch)
            save_forced_subs(channels)
            await event.edit(f"✅ {ch} o'chirildi.")
        else:
            await event.answer("⚠️ Kanal topilmadi!")

print("🎛️ kanal qoshish ishladi")                    