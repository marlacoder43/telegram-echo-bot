from telethon import Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError, ChannelPrivateError
import os
import json

START_FILE = "start_message.json"
FORCE_SUB_FILE = "force_subs.json"
EDIT_FORCE_SUB_FILE = "edit_force_state.txt"
LIST_FILE = "list.json"
USERS_FILE = "users.json"

def load_admins():
    try:
        with open("admins.json", "r") as f:
            return json.load(f)
    except:
        return []

ADMIN_IDS = load_admins()

def load_start():
    if os.path.exists(START_FILE):
        with open(START_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    return {"text": "👋 Salom {first_name}!", "photo": None}

def save_start(text=None, photo=None):
    data = load_start()
    if text:
        data["text"] = text
    if photo:
        data["photo"] = photo
    with open(START_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_list():
    if not os.path.exists(LIST_FILE):
        with open(LIST_FILE, "w") as f:
            json.dump([], f)
    with open(LIST_FILE, "r") as f:
        return json.load(f)

def save_list(data):
    with open(LIST_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4, ensure_ascii=False) 


# Fayl mavjudligini tekshirish
if not os.path.exists(FORCE_SUB_FILE):
    with open(FORCE_SUB_FILE, "w") as f:
        json.dump([], f)

# Kanallarni yuklash
def load_forced_subs():
    with open(FORCE_SUB_FILE, "r") as f:
        return json.load(f)

# Kanallarni saqlash
def save_forced_subs(channels):
    with open(FORCE_SUB_FILE, "w") as f:
        json.dump(channels, f, indent=4)

async def is_subscribed(bot, user_id):
    from config import ADMIN_IDS
    if user_id == ADMIN_IDS:
        return True

    channels = load_forced_subs()
    for ch in channels:
        try:
            # Normalize channel format
            channel = ch.lstrip('@')
            
            # Get the input peer for the channel
            channel_entity = await bot.get_input_entity(channel)
            
            # Get the input peer for the user
            user_entity = await bot.get_input_entity(user_id)
            
            # Make the request with correct parameters
            await bot(GetParticipantRequest(
                channel=channel_entity,
                participant=user_entity
            ))
            
        except UserNotParticipantError:
            return False
        except ChannelPrivateError:
            print(f"Bot doesn't have access to channel {ch}")
            continue
        except Exception as e:
            print(f"[ERROR is_subscribed] Channel: {ch}, Error: {e}")
            return False
    return True

async def send_force_sub_message(bot, user_id):
    channels = load_forced_subs()
    buttons = []
    for ch in channels:
        username = ch.lstrip('@')
        buttons.append([Button.url(f"📢 {username}", f"https://t.me/{username}")])
    buttons.append([Button.inline("🔄 Tekshirish", b"check_sub")])

    await bot.send_message(
        user_id,
        "❌ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
        buttons=buttons
    )