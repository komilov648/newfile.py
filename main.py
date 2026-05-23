import os
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import CommandStart

import yt_dlp

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_links = {}


# START
@dp.message(CommandStart())
async def start(message: Message):

    text = (
        "🔥 SAQLA BOT\n\n"
        "🎬 Video yuklash\n"
        "🎵 MP3 yuklash\n"
        "🔍 Music qidirish\n\n"
        "📥 Link yoki music nomi yuboring"
    )

    await message.answer(text)


# LINK yoki MUSIC
@dp.message(F.text)
async def get_message(message: Message):

    text = message.text

    # AGAR LINK BO'LSA
    if "http" in text:

        user_links[message.from_user.id] = text

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

        return await message.answer(
            "✅ Format tanlang",
            reply_markup=keyboard
        )

    # AGAR MUSIC NOMI BO'LSA
    await message.answer("🔍 Music qidirilmoqda...")

    query = f"ytsearch1:{text} official audio"

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "outtmpl": "music.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)

        file_name = None

        for file in os.listdir():
            if file.endswith(".mp3"):
                file_name = file
                break

        if file_name:

            await message.answer_audio(
                audio=open(file_name, "rb"),
                title=text
            )

            os.remove(file_name)

    except Exception as e:
        await message.answer(f"❌ Xato:\n{e}")


# VIDEO
@dp.callback_query(F.data == "video")
async def video_download(callback: CallbackQuery):

    url = user_links.get(callback.from_user.id)

    if not url:
        return await callback.message.answer("❌ Link topilmadi")

    await callback.message.answer("⏳ Video yuklanmoqda...")

    ydl_opts = {
        "format": "best",
        "quiet": True,
        "outtmpl": "video.%(ext)s"
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
                video=open(file_name, "rb")
            )

            os.remove(file_name)

    except Exception as e:
        await callback.message.answer(f"❌ Xato:\n{e}")


# MP3
@dp.callback_query(F.data == "mp3")
async def mp3_download(callback: CallbackQuery):

    url = user_links.get(callback.from_user.id)

    if not url:
        return await callback.message.answer("❌ Link topilmadi")

    await callback.message.answer("⏳ MP3 yuklanmoqda...")

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "outtmpl": "music.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
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
                audio=open(file_name, "rb")
            )

            os.remove(file_name)

    except Exception as e:
        await callback.message.answer(f"❌ Xato:\n{e}")


# MAIN
async def main():

    print("🔥 Saqla Bot ishga tushdi")

    await dp.start_polling(bot)


if os.name == "main":
    asyncio.run(main())