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
                data = json.load(f)
                return data
            except:
                pass
    if "list" in filename:
        return []  # Kino yoki multfilm ro'yxati
    else:
        return {}  # Holat (state) fayllari uchun

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
    from_peer=event.chat_id  # bu joyda PeerUser bo‘lyapti
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
    # MULTI komandasi — rejimni yoqish
    @bot.on(events.NewMessage(pattern="^multi$"))
    async def activate_multi(event):
        user_id = event.sender_id
        username = (await event.get_sender()).username or str(user_id)

        mode = "admin" if is_admin(user_id) else "user"

        save_data({
            "active": True,
            "type": mode,
            "user_id": user_id,
            "username": username
        }, MULTI_STATE_FILE)

        if mode == "admin":
            msg = (
                "🎞 <b>Multfilm yuklash rejimi yoqildi.</b>\n"
                "Video yuboring va bot avtomatik kod beradi."
            )
        else:
            msg = (
                "🍿 <b>Multfilm izlash rejimi yoqildi.</b>\n"
                "Iltimos, <code>00045</code> kabi kod yuboring."
            )

        await event.respond(
            msg,
            parse_mode="html",
            buttons=[[Button.inline("❌ Chiqish", b"exit_multi")]]
        )

    # Multfilm kodi kiritilganda (faqat userlar)
    @bot.on(events.NewMessage(pattern=r"^0{3}\d{1,3}$"))
    async def handle_multi_code(event):
        data = load_data(MULTI_STATE_FILE)
        if not data.get("active") or data.get("type") != "user":
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
                        event.chat_id,
                        msg.media,
                        caption="🍿 Siz so‘ragan multfilm:",
                        buttons=[[Button.inline("❌ Chiqish", b"exit_multi")]]
                    )
                else:
                    await event.reply("⚠️ Bu multfilm emas!")
            except Exception as e:
                await event.reply(f"❌ Xatolik: {str(e)}")
        else:
            await event.reply("❌ Bunday kodli multfilm topilmadi.")

    # Admin video tashlasa — kod biriktiriladi
    @bot.on(events.NewMessage(
        func=lambda e: (e.video or 
                       (e.document and e.document.mime_type and 
                        e.document.mime_type.startswith("video/")))))
    async def admin_upload_multi(event):
        data = load_data(MULTI_STATE_FILE)
        if not data.get("active") or data.get("type") != "admin":
            return
        if event.sender_id != data.get("user_id"):
            return

        try:
            fwd = await bot.forward_messages(STORAGE_CHANNEL_MULTI, event.chat_id, event.id)
            msg_id = fwd.id

            multi_list = load_data(MULTI_LIST_FILE)
            if msg_id not in multi_list:
                multi_list.append(msg_id)
                save_data(multi_list, MULTI_LIST_FILE)

            await event.reply(f"✅ Multfilm yuklandi!\n🎬 Kod: <code>{msg_id}</code>", parse_mode="html")
        except Exception as e:
            await event.reply(f"❌ Xatolik: {str(e)}")

    # Rejimdan chiqish
    @bot.on(events.CallbackQuery(data=b"exit_multi"))
    async def exit_multi(event):
        if os.path.exists(MULTI_STATE_FILE):
            os.remove(MULTI_STATE_FILE)
        await event.edit("❌ Multfilm rejimidan chiqildi.", buttons=None)

    # Rejim ichida boshqa matnlar yozilmasin
    @bot.on(events.NewMessage())
    async def filter_other_texts(event):
        data = load_data(MULTI_STATE_FILE)
        if not data.get("active"):
            return
        if event.sender_id != data.get("user_id"):
            return

        if not event.raw_text.startswith("000") and data.get("type") == "user":
            await event.reply(
                "⚠️ Faqat <code>00012</code> kabi kod yuboring!",
                parse_mode="html",
                buttons=[[Button.inline("❌ Chiqish", b"exit_multi")]]
            )
print("🎬 movie ishladi")