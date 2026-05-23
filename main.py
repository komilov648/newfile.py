import os
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

import yt_dlp

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Linklarni saqlash
user_links = {}


# START
@dp.message(CommandStart())
async def start(message: Message):

    text = (
        "🔥 <b>SAQLA BOT</b>\n\n"
        "🎬 Video yuklash\n"
        "🎵 MP3 yuklash\n"
        "📥 Link yuboring"
    )

    await message.answer(text)


# LINK QABUL QILISH
@dp.message(F.text)
async def get_link(message: Message):

    url = message.text

    if "http" not in url:
        return await message.answer("❌ Link yuboring")

    user_links[message.from_user.id] = url

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 Video",
                    callback_data="video"
                ),
                InlineKeyboardButton(
                    text="🎵 MP3",
                    callback_data="mp3"
                )
            ]
        ]
    )

    await message.answer(
        "✅ Format tanlang",
        reply_markup=keyboard
    )


# VIDEO YUKLASH
@dp.callback_query(F.data == "video")
async def download_video(callback: CallbackQuery):

    user_id = callback.from_user.id
    url = user_links.get(user_id)

    if not url:
        return await callback.message.answer("❌ Link topilmadi")

    await callback.message.answer("⏳ Video yuklanmoqda...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s'
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_name = None

        for file in os.listdir():
            if file.startswith("video."):
                file_name = file
                break

        if file_name:

            await callback.message.answer_video(
                video=open(file_name, 'rb')
            )

            os.remove(file_name)

    except Exception as e:
        await callback.message.answer(f"❌ Xato:\n{e}")


# MP3 YUKLASH
@dp.callback_query(F.data == "mp3")
async def download_mp3(callback: CallbackQuery):

    user_id = callback.from_user.id
    url = user_links.get(user_id)

    if not url:
        return await callback.message.answer("❌ Link topilmadi")

    await callback.message.answer("⏳ MP3 yuklanmoqda...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_name = None

        for file in os.listdir():
            if file.endswith(".mp3"):
                file_name = file
                break

        if file_name:

            await callback.message.answer_audio(
                audio=open(file_name, 'rb')
            )

            os.remove(file_name)

    except Exception as e:
        await callback.message.answer(f"❌ Xato:\n{e}")


# BOTNI YOQISH
async def main():

    print("🔥 Saqla Bot ishga tushdi")

    await dp.start_polling(bot)


if name == "main":
    asyncio.run(main())