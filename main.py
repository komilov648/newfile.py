
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os


API_ID = 123456
API_HASH = "API_HASH"
TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "SaqlaBot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

user_links = {}

# START
@app.on_message(filters.command("start"))
async def start(client, message):

    text = """
🚀 Video Yuklovchi Bot

📥 Link yuboring:
• YouTube
• TikTok
• Instagram
• Facebook

Keyin format tanlaysiz.
"""

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 Video", callback_data="video"),
            InlineKeyboardButton("🎵 MP3", callback_data="music")
        ]
    ])

    await message.reply(text, reply_markup=buttons)


# LINK SAQLASH
@app.on_message(filters.text & ~filters.command("start"))
async def save_link(client, message):

    user_links[message.from_user.id] = message.text

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 Video", callback_data="video"),
            InlineKeyboardButton("🎵 MP3", callback_data="music")
        ]
    ])

    await message.reply(
        "📥 Yuklash turini tanlang:",
        reply_markup=buttons
    )


# CALLBACK
@app.on_callback_query()
async def callback(client, callback_query):

    user_id = callback_query.from_user.id

    if user_id not in user_links:
        return await callback_query.message.reply("❌ Avval link yuboring.")

    url = user_links[user_id]

    msg = await callback_query.message.reply("⏳ Yuklanmoqda...")

    try:

        # VIDEO
        if callback_query.data == "video":

            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'noplaylist': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            await callback_query.message.reply_video(
                video=file_path,
                caption="✅ Video tayyor"
            )

            os.remove(file_path)

        # MUSIC
        elif callback_query.data == "music":

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info['title']
                file_path = f"downloads/{title}.mp3"

            await callback_query.message.reply_audio(
                audio=file_path,
                caption="🎵 MP3 tayyor"
            )

            os.remove(file_path)

        await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ Xato:\n{e}")


# DOWNLOAD PAPKA
if not os.path.exists("downloads"):
    os.mkdir("downloads")

print("Bot ishga tushdi ✅")

app.run()