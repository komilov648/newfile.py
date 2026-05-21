import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv
import yt_dlp

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎬 Saqla Bot\n\n"
        "Link yuboring."
    )


@dp.message(F.text)
async def downloader(message: Message):

    url = message.text

    if "http" not in url:
        return await message.answer("❌ Link yuboring")

    await message.answer("⏳ Yuklanmoqda...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video_file = None

        for file in os.listdir():
            if file.startswith("video."):
                video_file = file
                break

        if video_file:
            await message.answer_video(
                video=open(video_file, 'rb')
            )

            os.remove(video_file)

    except Exception as e:
        await message.answer(f"❌ Xato:\n{e}")


async def main():
    await dp.start_polling(bot)

if __name__ == "main":
    asyncio.run(main())