from telethon import events, Button
from config import ADMIN_IDS
import os

def register_help_handler(bot):
    def is_admin(user_id):
        return user_id in ADMIN_IDS

    @bot.on(events.NewMessage(pattern='/help'))
    async def help_command(event):
        user_id = event.sender_id
        image_path = "media/start_photo.jpg"

        if is_admin(user_id):
            help_text = (
                "🛠 <b>Admin Yordam Menyusi</b>\n\n"
                "📌 <b>Asosiy Komandalar:</b>\n"
                "/broadcast - Xabar yuborish\n"
                "/stats - Statistika\n"
                "/kanal - Kanal boshqaruvi\n\n"
                "🎬 <b>Kino:</b> Video yuboring - avtomatik saqlanadi\n"
                "Yana bir sirli komanda bor... | aytmayman |!"
            )
            buttons = [
                [Button.inline("⚙️ Admin Panel", b"admin_panel")],
                [Button.url("📂 Bot Kodlari", "https://github.com/marlacoder43")]
            ]
        else:
            help_text = (
                "🤖 <b>Botdan foydalanish qo'llanmasi</b>\n\n"
                "🎬 Kino izlash uchun kod yuboring.\n"
                "📝 Misol: <code>153</code>\n\n"
                "🎥 Kinolar arxiv kanalidan olinadi.\n"
                "Agar muammo bo'lsa: @mehrsizlikda"
            )
            buttons = [
                [Button.inline("ℹ️ Qo'shimcha ma'lumot", b"more_info")]
            ]

        if os.path.exists(image_path):
            await bot.send_file(event.chat_id, image_path, caption=help_text, buttons=buttons, parse_mode='html')
        else:
            await event.respond(help_text, buttons=buttons, parse_mode='html')

    @bot.on(events.CallbackQuery(data=b"more_info"))
    async def more_info(event):
        await event.edit(
            "📚 <b>Qo'shimcha Ma'lumot</b>\n\n"
            "• Kodlar 2-5 raqamdan iborat bo'ladi\n"
            "• Har bir kodga kino biriktirilgan\n"
            "• Maxfiy kod kiritish: <code>000</code> bilan yozasiz kodni misol 00064\n\n"
            "• Dasturchi: @killerfurqat",
            parse_mode='html'
        )

    @bot.on(events.CallbackQuery(data=b"admin_panel"))
    async def admin_panel(event):
        if not is_admin(event.sender_id):
            await event.answer("❌ Siz admin emassiz!", alert=True)
            return

        await event.edit(
            "⚙️ <b>Admin Panel</b>\n\n"
            "👤 Foydalanuvchilar: /stats\n"
            "📢 Xabar yuborish: /broadcast\n"
            "🎬 Kino yuklash: video tashlang\n"
            "📡 Kanal boshqaruvi: /kanal\n\n"
            "🔐 Sirli buyruq: | Yashirin |",
            buttons=[[Button.inline("⏪ Orqaga", b"back_to_help")]],
            parse_mode='html'
        )

    @bot.on(events.CallbackQuery(data=b"back_to_help"))
    async def back_to_help(event):
        await help_command(event)
print("💡 help ishladi")                