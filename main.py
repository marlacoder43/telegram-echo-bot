from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from keep_alive import keep_alive
keep_alive()
import os
import json

# ✅ Bot API credentials
API_ID = 22225255
API_HASH = "6cb04f39cc07170b75d1ce675eeb65b8"
BOT_TOKEN = "7618049070:AAGvuAektEiRIPJQcIHQt8lbtTyKb-ziCaM"
ADMIN_ID = 5732326881

# ✅ Storage Channel (ID ko‘rinishida)
STORAGE_CHANNEL = -1002625959955  
MOVIE_CHANNEL = "Archive_channel1"

# ✅ Start bot
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ Majburiy obuna saqlash fayli
FORCE_SUB_FILE = "force_subs.json"

# 🔹 JSON mavjudligini tekshirish
if not os.path.exists(FORCE_SUB_FILE):
    with open(FORCE_SUB_FILE, "w") as f:
        json.dump([], f)

# ✅ Majburiy obuna kanallarini yuklash
def load_forced_subs():
    with open(FORCE_SUB_FILE, "r") as f:
        return json.load(f)

# ✅ Majburiy obuna kanallarini saqlash
def save_forced_subs(channels):
    with open(FORCE_SUB_FILE, "w") as f:
        json.dump(channels, f, indent=4)

# ✅ Obuna tekshirish (bir nechta kanal uchun)
def is_subscribed(user_id):
    channels = load_forced_subs()
    for channel in channels:
        try:
            chat_member = bot.get_chat_member(channel, user_id)
            if chat_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return False
        except Exception:
            return False
    return True

# ✅ Obunaga majbur qilish xabarini yuborish
def send_force_sub_message(user_id):
    channels = load_forced_subs()
    buttons = [[InlineKeyboardButton(f"📢 Kanal {i+1}", url=f"https://t.me/{channel[1:]}")] for i, channel in enumerate(channels)]
    buttons.append([InlineKeyboardButton("🔄 Tekshirish", callback_data="check_sub")])

    bot.send_message(
        chat_id=user_id,
        text="❌ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


#start bot buyrug'ri
@bot.on_message(filters.command("start"))
def start(client, message):
    user_id = message.chat.id

    if not is_subscribed(user_id):
        send_force_sub_message(user_id)
        return  

    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    try:
        # 🎬 Storage kanalidan 8-ID li rasmni olish
        msg = bot.get_messages(
            chat_id=STORAGE_CHANNEL,  # 📂 Storage kanali ID
            message_ids=4  # 📸 Rasm ID
        )

        # 📩 Faqat bitta xabar yuborish
        bot.send_photo(
            chat_id=user_id,
            photo=msg.photo.file_id,
            caption=f"<b>👑 Assalomu alaykum hurmatli botimizning foydalanuvchisi >> {user_name} <<. Kino izlash botimizga hush kelibsiz. </b>\n\n"
                "🔎 Iltimos kino kodini kiriting,va biz sizga yuboramiz.\n",
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        bot.send_message(
            chat_id=user_id,
            text="⚠️ Rasm topilmadi yoki xatolik yuz berdi!",
            parse_mode=ParseMode.HTML
        )

# ✅ /kanal buyrug‘i - Adminlar uchun
@bot.on_message(filters.command("kanal") & filters.user(ADMIN_ID))
def manage_channels(client, message):
    channels = load_forced_subs()
    buttons = [[InlineKeyboardButton(f"🚫 O‘chirish - {channel}", callback_data=f"del_{channel}")] for channel in channels]

    if len(channels) < 6:
        buttons.append([InlineKeyboardButton("+ Kanal qo‘shish", callback_data="add_channel")])

    bot.send_message(
        chat_id=ADMIN_ID,
        text="📢 <b>Majburiy ulanish kanallarini boshqarish</b>\n\n"
             "Yangi kanal qo‘shish yoki mavjudini o‘chirish uchun tugmalarni bosing.",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ✅ Yangi kanal qo‘shish so‘rovini qabul qilish
@bot.on_callback_query(filters.regex("add_channel"))
def request_channel_id(client, callback_query):
    bot.send_message(
        chat_id=ADMIN_ID,
        text="🔹 <b>Yangi kanal qo‘shish:</b>\n\n"
             "1️⃣ Iltimos, kanalga admin qilib qo‘ying.\n"
             "2️⃣ Kanal username (@kanal_nomi) ni botga yuboring.",
        parse_mode=ParseMode.HTML
    )

# ✅ Kanal qo‘shish
@bot.on_message(filters.user(ADMIN_ID) & filters.text)
def add_channel(client, message: Message):
    channel = message.text.strip()
    channels = load_forced_subs()

    if channel.startswith("@") or channel.startswith("-100"):
        if channel in channels:
            message.reply_text("⚠️ Bu kanal allaqachon majburiy ulanish ro‘yxatida!")
        elif len(channels) >= 6:
            message.reply_text("⚠️ 6 tadan ortiq kanal qo‘shib bo‘lmaydi!")
        else:
            channels.append(channel)
            save_forced_subs(channels)
            message.reply_text(f"✅ <b>{channel}</b> kanal majburiy ulanishga qo‘shildi!")
    else:
        message.reply_text("⚠️ Noto‘g‘ri format! Iltimos, kanal ID yoki @username shaklida yuboring.")

# ✅ Kanalni olib tashlash
@bot.on_callback_query(filters.regex(r"del_(.+)"))
def remove_channel(client, callback_query):
    channel = callback_query.data.split("_", 1)[1]
    channels = load_forced_subs()

    if channel in channels:
        channels.remove(channel)
        save_forced_subs(channels)
        callback_query.message.edit_text(f"✅ <b>{channel}</b> majburiy ulanishdan olib tashlandi.")
    else:
        callback_query.answer("⚠️ Kanal topilmadi!")

# ✅ Obuna tekshirish tugmasi
@bot.on_callback_query(filters.regex("check_sub"))
def check_subscription_callback(client, callback_query):
    user_id = callback_query.message.chat.id

    if is_subscribed(user_id):
        callback_query.message.edit_text("✅ <b>Rahmat! Siz kanal(lar)ga obuna bo‘ldingiz.</b>\n\n"
                                         "🎬 Endi botdan foydalanishingiz mumkin.",
                                         parse_mode=ParseMode.HTML)
    else:
        callback_query.answer("❌ Hali ham barcha kanallarga obuna bo‘lmagansiz!", show_alert=True)


#---------------------------------------------------------

# 🔹 STATS COMMAND (ONLY FOR ADMIN)
@bot.on_message(filters.command("stats"))
def bot_stats(client, message):
    user_id = message.chat.id

    # If non-admin user tries to use /stats → Show warning
    if user_id != ADMIN_ID:
        bot.send_message(
            user_id,
            "🚫 <b>Ushbu buyruq faqat admin uchun!</b>",
            parse_mode=ParseMode.HTML
        )
        return  # ⛔ Stop here, don’t run the rest

    # Load users
    with open("users.json", "r") as f:
        users = json.load(f)

    # Get usernames
    user_list = []
    for user_id in users:
        try:
            user = bot.get_users(user_id)
            username = f"@{user.username}" if user.username else user.first_name
            user_list.append(username)
        except Exception:
            continue  # Ignore users who left the bot

    user_text = "\n".join(user_list) if user_list else "🚫 Hech kim yo‘q!"
    
    # Send stats to admin
    bot.send_message(
        ADMIN_ID,
        f"📊 <b>Bot a’zolari soni:</b> {len(user_list)} ta\n\n"
        f"🧑‍💻 <b>Foydalanuvchilar:</b>\n{user_text}",
        parse_mode=ParseMode.HTML
    )

# 🔹 HELP COMMAND (FOR EVERYONE) - With "Contact Admin" Button
@bot.on_message(filters.command("help"))
def help_message(client, message):
    bot.send_message(
        message.chat.id,
        "<b>ℹ️ Botdan foydalanish qo‘llanmasi:</b>\n\n"
        "🎬 Kino izlash uchun kino kodini yuboring.\n"
        "📢 Yangiliklar uchun admin bilan bog‘laning.\n\n"
        "👨‍💻 Dasturchi: @mexirsiz_bro",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Admin bilan bog‘lanish", url="https://t.me/killerfurqat")]
        ])
    )

###########################


# 🔹 BROADCAST COMMAND (ONLY FOR ADMIN)
@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
def broadcast_message(client, message):
    bot.send_message(
        ADMIN_ID,
        "<b>📨 Yangi xabarni yozing va botga yuboring.</b>\n\n"
        "✏️ Bot barcha foydalanuvchilarga shu xabarni jo‘natadi.\n\n"
        "❌ Yoki \"🚫 Bekor qilish\" tugmasini bosing.",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 Bekor qilish", callback_data="cancel_broadcast")]
        ])
    )

    with open("step.txt", "w") as f:
        f.write("broadcast")

# 🔹 CANCEL BROADCAST
@bot.on_callback_query(filters.regex("cancel_broadcast"))
def cancel_broadcast(client, callback_query):
    if os.path.exists("step.txt"):
        os.remove("step.txt")  # Reset step file

    callback_query.message.edit_text(
        "❌ <b>Broadcast bekor qilindi.</b>",
        parse_mode=ParseMode.HTML
    )

# 🔹 HANDLE BROADCASTING (NOW CHECKS IF ACTIVE)
@bot.on_message(filters.text & filters.user(ADMIN_ID))
def handle_broadcast(client, message):
    try:
        if not os.path.exists("step.txt"):
            return  # ⛔ If no broadcast is active, do nothing (let other handlers process)

        with open("step.txt", "r") as f:
            step = f.read().strip()

        if step == "broadcast":
            with open("users.json", "r") as f:
                users = json.load(f)

            sent_count = 0
            failed_count = 0

            for user_id in users:
                try:
                    bot.send_message(user_id, message.text, parse_mode=ParseMode.HTML)
                    sent_count += 1
                except Exception:
                    failed_count += 1  # Ignore blocked users

            bot.send_message(
                ADMIN_ID,
                f"✅ Xabar {sent_count} ta foydalanuvchiga yuborildi!\n"
                f"❌ {failed_count} ta foydalanuvchi bloklagan yoki xatolik yuz berdi.",
                parse_mode=ParseMode.HTML
            )

            os.remove("step.txt")  # Reset step file

    except FileNotFoundError:
        pass  # If step.txt doesn't exist, do nothing

############################



# 🔹 INLINE TUGMA ORQALI TEKSHIRISH (CALLBACK HANDLER)
@bot.on_callback_query(filters.regex("check_sub"))
def check_subscription_callback(client, callback_query):
    user_id = callback_query.message.chat.id

    if is_subscribed(user_id):
        callback_query.message.edit_caption("✅ <b>Rahmat! Siz kanalga obuna bo‘ldingiz.</b>\n\n"
                                            "🎬 Endi botdan foydalanishingiz mumkin.",
                                            parse_mode=ParseMode.HTML)
    else:
        callback_query.answer("❌ Hali ham obuna bo‘lmagansiz!", show_alert=True)


# 🔹 SEND MOVIE (Hides sender's name + Adds custom caption)
@bot.on_message(filters.text & filters.private & ~filters.user(ADMIN_ID))
def send_movie(client, message):
    user_id = message.chat.id
    movie_code = message.text.strip()

    # ✅ Check subscription
    if not is_subscribed(user_id):
        send_force_sub_message(user_id)
        return  # ⛔ If not subscribed, stop

    # ✅ Ensure only numbers are allowed
    if not movie_code.isdigit():
        message.reply_text(
            "❌ <b>Siz faqat kino kodlarini yuborishingiz mumkin.</b>\n\n"
            "📩 Agar muammo bo‘lsa, pastdagi tugma orqali admin bilan bog‘laning.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 Admin bilan bog‘lanish", url="https://t.me/mexirsiz_bro")]
            ])
        )
        return

    try:
        # ✅ Try to copy the message (If the movie exists)
        bot.copy_message(
            chat_id=user_id,
            from_chat_id="@Archive_channel1",  # Movie storage channel
            message_id=int(movie_code),
            caption="<b>🎬 Siz so‘ragan kino topildi!</b>\n\n"
                    "<i>@ozbefilmlar - Ko‘proq kinolar uchun!</i>",
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        # ❌ If movie is not found or error happens
        message.reply_text("❌ Xatolik: Kino topilmadi yoki noto‘g‘ri kod kiritildi!")


# 🔹 BLOCK NON-ADMINS FROM SENDING VIDEOS
@bot.on_message(filters.video & ~filters.user(ADMIN_ID))
def restrict_videos(client, message):
    message.reply_text(
        "❌ <b>Siz botga to‘g‘ridan-to‘g‘ri video yubora olmaysiz!</b>\n\n"
        "📩 Agar sizda film bor bo‘lsa, admin bilan bog‘laning.",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Admin bilan bog‘lanish", url="https://t.me/mexirsiz_bro")]
        ])
    )

# 🔹 ALLOW ONLY ADMIN TO UPLOAD VIDEOS
@bot.on_message(filters.video & filters.user(ADMIN_ID))
def upload_movie(client, message):
    user_id = message.chat.id

    if message.video:
        forwarded_messages = bot.forward_messages(
            chat_id=STORAGE_CHANNEL,  # Send to storage channel
            from_chat_id=user_id,
            message_ids=message.id
        )

        forwarded_message_id = forwarded_messages[0].id if isinstance(forwarded_messages, list) else forwarded_messages.id

        message.reply_text(f"🚀 Yangi kino yuklandi!\n\n#️⃣ Kino kodi: {forwarded_message_id}")

        with open("last.txt", "w") as f:
            f.write(str(forwarded_message_id))


# Handle video uploads
# 🔹 ALLOW ONLY ADMIN TO UPLOAD VIDEOS & MOVIE FILES
@bot.on_message((filters.video | filters.document) & filters.user(ADMIN_ID))
def upload_movie(client, message):
    user_id = message.chat.id

    # Ensure it's a valid video file (MP4, MKV, etc.)
    if message.video or (message.document and message.document.mime_type.startswith("video/")):
        forwarded_messages = bot.forward_messages(
            chat_id=STORAGE_CHANNEL,  # Send to storage channel
            from_chat_id=user_id,
            message_ids=message.id
        )

        forwarded_message_id = forwarded_messages[0].id if isinstance(forwarded_messages, list) else forwarded_messages.id

        message.reply_text(
            f"🚀 Yangi kino yuklandi!\n\n#️⃣ Kino kodi: {forwarded_message_id}",
            parse_mode=ParseMode.HTML
        )

        with open("last.txt", "w") as f:
            f.write(str(forwarded_message_id))

# ✅ Botni ishga tushirish
bot.run()
