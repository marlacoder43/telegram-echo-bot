from telethon import events, Button
from config import ADMIN_IDS
from utils import load_users
import os, json

BROADCAST_STATE = "broadcast_state.json"

def register_broadcast_handler(bot):

    @bot.on(events.NewMessage(pattern="/broadcast"))
    async def start_broadcast(event):
        if event.sender_id not in ADMIN_IDS:
            return

        if os.path.exists(BROADCAST_STATE):
            await event.reply("⚠️ Siz allaqachon broadcast holatidasiz.\n❌ Bekor qilish uchun 'Bekor qilish' tugmasini bosing.")
            return

        await event.respond(
            "📝 Iltimos, yubormoqchi bo‘lgan xabaringizni yuboring.",
            buttons=[[Button.inline("❌ Bekor qilish", b"cancel_broadcast")]]
        )

        with open(BROADCAST_STATE, "w") as f:
            json.dump({"step": "awaiting_message"}, f)

    @bot.on(events.NewMessage())
    async def handle_admin_input(event):
        if not os.path.exists(BROADCAST_STATE):
            return
        if event.sender_id not in ADMIN_IDS:
            return
        if event.raw_text and event.raw_text.startswith("/"):
            return

        with open(BROADCAST_STATE, "r") as f:
            data = json.load(f)

        step = data.get("step")

        if step == "awaiting_message":
            data = {
                "text": event.raw_text if event.raw_text else "",
                "media": None,
                "is_forward": bool(event.fwd_from),
                "fwd_msg_id": event.id if event.fwd_from else None,
                "step": "preview"
            }

            if event.photo or (event.document and event.document.mime_type.startswith("image/")):
                path = await event.download_media(file="media/broadcast.jpg")
                data["media"] = path

            with open(BROADCAST_STATE, "w") as f:
                json.dump(data, f)

            if data["is_forward"]:
                await event.reply("🚀 Forward qilingan xabar tayyor. Jo‘natish tugmasini bosing.",
                    buttons=[
                        [Button.inline("🚀 Yuborish", b"send_now")],
                        [Button.inline("❌ Bekor qilish", b"cancel_broadcast")]
                    ])
            else:
                buttons = [
                    [Button.inline("➕ Tugma qo‘shish", b"add_button")],
                    [Button.inline("🚀 Tugmasiz yuborish", b"send_now")],
                    [Button.inline("❌ Bekor qilish", b"cancel_broadcast")]
                ]

                if data["media"]:
                    await bot.send_file(event.chat_id, data["media"], caption=data["text"], buttons=buttons)
                else:
                    await bot.send_message(event.chat_id, data["text"], buttons=buttons)

        elif step == "awaiting_btn_text":
            data["btn_text"] = event.raw_text.strip()
            data["step"] = "awaiting_btn_url"
            with open(BROADCAST_STATE, "w") as f:
                json.dump(data, f)
            await event.reply("🔗 Endi tugmaga havolani yuboring. Masalan: https://t.me/example")

        elif step == "awaiting_btn_url":
            data["btn_url"] = event.raw_text.strip()
            data["step"] = "ready"
            with open(BROADCAST_STATE, "w") as f:
                json.dump(data, f)
            await event.reply("✅ Tugma saqlandi. Habar jo‘natilmoqda...")
            await send_broadcast(bot, data, event)

    @bot.on(events.CallbackQuery(data=b"add_button"))
    async def add_button(event):
        if event.sender_id not in ADMIN_IDS:
            return

        with open(BROADCAST_STATE, "r") as f:
            data = json.load(f)

        if data.get("is_forward"):
            return await event.answer("Forward qilingan xabarga tugma qo‘shib bo‘lmaydi!", alert=True)

        data["step"] = "awaiting_btn_text"
        with open(BROADCAST_STATE, "w") as f:
            json.dump(data, f)

        await event.respond("✍️ Tugma nomini yozing. Masalan: Ko‘rish")

    @bot.on(events.CallbackQuery(data=b"send_now"))
    async def send_now(event):
        if event.sender_id not in ADMIN_IDS:
            return

        with open(BROADCAST_STATE, "r") as f:
            data = json.load(f)

        await event.edit("✅ Habar jo‘natilmoqda...")
        await send_broadcast(bot, data, event)

    @bot.on(events.CallbackQuery(data=b"cancel_broadcast"))
    async def cancel_broadcast(event):
        if event.sender_id not in ADMIN_IDS:
            return

        if os.path.exists(BROADCAST_STATE):
            os.remove(BROADCAST_STATE)
        await event.edit("❌ Broadcast bekor qilindi.")

async def send_broadcast(bot, data, event):
    users = load_users()
    success = 0
    fail = 0

    btns = None
    if data.get("btn_text") and data.get("btn_url"):
        btns = [[Button.url(data["btn_text"], data["btn_url"])]]

    for user_id in users:
        try:
            if data.get("is_forward") and data.get("fwd_msg_id"):
                await bot.forward_messages(
                    entity=int(user_id),
                    messages=int(data["fwd_msg_id"]),
                    from_peer=event.chat_id
                )
            elif data["media"]:
                await bot.send_file(int(user_id), file=data["media"], caption=data["text"], buttons=btns)
            else:
                await bot.send_message(int(user_id), data["text"], buttons=btns)
            success += 1
        except:
            fail += 1

    if os.path.exists(BROADCAST_STATE):
        os.remove(BROADCAST_STATE)

    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, f"✅ Yuborildi: {success} ta\n❌ Xatolik: {fail} ta")
print("📬 Broadcast ishladi")