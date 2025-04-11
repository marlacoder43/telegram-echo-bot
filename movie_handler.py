from telethon import events, Button
from config import ADMIN_IDS, STORAGE_CHANNEL, MOVIE_CHANNEL, STORAGE_CHANNEL_MULTI
import os, json

MULTI_STATE_FILE = "multi_state.json"
MOVIE_LIST_FILE = "movie_list.json"
MULTI_LIST_FILE = "multi_list.json"

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_data(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def is_admin(user_id):
    return user_id in ADMIN_IDS

def register_movie_handlers(bot):

    @bot.on(events.NewMessage(func=lambda e: (e.video or (e.document and e.document.mime_type and e.document.mime_type.startswith("video/")))))
    async def admin_upload_movie(event):
        if not is_admin(event.sender_id):
            return

        try:
            multi_data = load_data(MULTI_STATE_FILE)
            is_multi = multi_data.get("active") if isinstance(multi_data, dict) else False

            target_channel = STORAGE_CHANNEL_MULTI if is_multi else STORAGE_CHANNEL
            target_file = MULTI_LIST_FILE if is_multi else MOVIE_LIST_FILE
            mode = "Multfilm" if is_multi else "Kino"

            forwarded = await bot.forward_messages(
                entity=target_channel,
                messages=event.id,
                from_peer=event.chat_id
            )

            msg_id = forwarded.id
            movie_list = load_data(target_file)

            if msg_id not in movie_list:
                movie_list.append(msg_id)
                save_data(movie_list, target_file)

            await event.reply(
                f"✅ {mode} yuklandi!\n🔢 Kod: <code>{msg_id}</code>",
                parse_mode="html"
            )

        except Exception as e:
            await event.reply(f"❌ Xatolik: {str(e)}")

    @bot.on(events.NewMessage(pattern=r"^\d+$"))
    async def user_requests_movie(event):
        if os.path.exists(MULTI_STATE_FILE):
            data = load_data(MULTI_STATE_FILE)
            if isinstance(data, dict) and data.get("active"):
                return

        code = int(event.raw_text.strip())
        movie_list = load_data(MOVIE_LIST_FILE)

        if code in movie_list:
            try:
                msg = await bot.get_messages(MOVIE_CHANNEL, ids=code)
                if msg.video or (msg.document and msg.document.mime_type.startswith("video/")):
                    await bot.send_file(
                        event.chat_id,
                        msg.media,
                        caption="🎬 Siz so‘ragan kino topildi!\n@Archive_channel1"
                    )
                else:
                    await event.reply("❌ Bu kino emas!")
            except Exception as e:
                await event.reply(f"❌ Xatolik: {str(e)}")
        else:
            await event.reply("❌ Bunday kino kodi mavjud emas.")

    @bot.on(events.NewMessage(func=lambda e: (e.video or (e.document and e.document.mime_type and e.document.mime_type.startswith("video/")))))
    async def block_user_videos(event):
        if not is_admin(event.sender_id):
            await event.delete()
            await event.respond("❌ Siz video yubora olmaysiz!")
            
def register_multi_handlers(bot):
    """Register multi-film mode handlers"""

    @bot.on(events.NewMessage(pattern="^multi$"))
    async def activate_multi(event):
        if not is_admin(event.sender_id):
            return

        save_data({
            "active": True,
            "user_id": event.sender_id,
            "username": event.sender.username or str(event.sender_id)
        }, MULTI_STATE_FILE)

        await event.respond(
            "🎞 Multfilm rejimi yoqildi!\n"
            "000 bilan boshlangan kodlarni kiriting.\n\n"
            "Misol: <code>00045</code>",
            buttons=[[Button.inline("❌ Chiqish", b"exit_multi")]],
            parse_mode="html"
        )

    @bot.on(events.NewMessage(pattern=r"^0{3}\d{1,3}$"))
    async def handle_multi_code(event):
        data = load_data(MULTI_STATE_FILE)
        if not data or not data.get("active"):
            return

        if event.sender_id != data.get("user_id"):
            return

        code = int(event.raw_text.strip())
        multi_list = load_data(MULTI_LIST_FILE)

        if code in multi_list:
            try:
                msg = await bot.get_messages(STORAGE_CHANNEL_MULTI, ids=code)
                if msg.video or (msg.document and msg.document.mime_type.startswith("video/")):
                    await bot.send_file(
                        entity=event.chat_id,
                        file=msg.media,
                        caption="🍿 Multfilm topildi!",
                        buttons=[[Button.inline("❌ Chiqish", b"exit_multi")]]
                    )
                else:
                    await event.reply("⚠️ Bu multfilm emas!")
            except Exception as e:
                await event.reply(f"❌ Xatolik: {str(e)}")
        else:
            await event.reply("❌ Bunday kodli multfilm yo‘q!")

    @bot.on(events.CallbackQuery(data=b"exit_multi"))
    async def exit_multi(event):
        if os.path.exists(MULTI_STATE_FILE):
            os.remove(MULTI_STATE_FILE)
        await event.edit("❌ Multfilm rejimidan chiqildi.", buttons=None)

    @bot.on(events.NewMessage())
    async def filter_non_multi(event):
        data = load_data(MULTI_STATE_FILE)
        if not data or not data.get("active"):
            return
        if event.sender_id != data.get("user_id"):
            return
        if not event.raw_text.startswith("000") and event.raw_text != "multi":
            await event.reply(
                "❗ Iltimos, faqat multfilm kodlarini kiriting!",
                buttons=[[Button.inline("❌ Chiqish", b"exit_multi")]]
            )
print("🎬 movie ishladi")                    