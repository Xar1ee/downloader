import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BotCommand
import yt_dlp
from dotenv import load_dotenv

# --- SOZLAMALAR ---

load_dotenv()
TOKEN = os.getenv("TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()


# 1. Menyu ro'yxatini shakllantirish
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command = "start", description="Botni ishga tushirish 🚀"),
        BotCommand(command = "insta", description="Instagram-dan yuklash bo'yicha yordam"),
        BotCommand(command = "tiktok", description="TikTok-dan yuklash bo'yicha yordam"),
        BotCommand(command = "youtube", description="YouTube-dan yuklash bo'yicha yordam"),
        BotCommand(command = "help", description = "Yordamchi informatsiyalar")
    ]
    await bot.set_my_commands(commands)


# 2. Yuklab olish funksiyasi
def download_media(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
    }
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


# --- HANDLERLAR ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Salom {message.from_user.first_name}! Menyu orqali imkoniyatlarni ko'rishingiz yoki to'g'ridan-to'g'ri link yuborishingiz mumkin.")


@dp.message(Command("insta"))
async def cmd_insta(message: types.Message):
    await message.answer("📱 Instagram Reels yoki Video linkini yuboring, men uni reklamasiz yuklab beraman.")


@dp.message(Command("tiktok"))
async def cmd_tiktok(message: types.Message):
    await message.answer("🎵 TikTok videosi linkini yuboring. Men uni sizga taqdim etaman.")


@dp.message(Command("youtube"))
async def cmd_youtube(message: types.Message):
    await message.answer("🎥 YouTube Shorts yoki Video linkini yuboring. (Hajmi 50MB dan kam bo'lishi tavsiya etiladi)")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Agar sizda videoingiz yuklamnmasa bu Bot yomon degani emas, kodlar yozilgan kompyuter yoki noutbookdagi Wi-Fi yomonligini yoki umuman yoqligini ")


# 2. Yuklab olish o'rniga video URL manzilini olish funksiyasi
def get_video_url(url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)  # download=False - yuklamaydi, faqat ma'lumot oladi
        return info.get('url'), info.get('title', 'Video')


# Link kelganda ishlovchi handler
@dp.message(F.text.regexp(r'(https?://[^\s]+)'))
async def handle_download(message: types.Message):
    url = message.text
    if any(site in url for site in ["instagram.com", "tiktok.com", "youtube.com", "youtu.be"]):
        status = await message.answer("🔍 Video tayyorlanmoqda...")

        try:
            # Videoni yuklab olmaymiz, shunchaki to'g'ridan-to'g'ri linkini olamiz
            video_url, title = await asyncio.to_thread(get_video_url, url)

            if video_url:
                # Telegramga videoni URL orqali yuboramiz
                # Bunda Telegram o'z serveriga videoni sizning serveringizsiz tortib oladi
                await message.answer_video(
                    video=video_url,
                    caption=f"🎥 {title}\n\n✅ @sizning_botingiz"
                )
            else:
                await message.answer("❌ Video manzilini aniqlab bo'lmadi.")

        except Exception as e:
            logging.error(f"Xatolik: {e}")
            await message.answer("❌ Xatolik! Video yopiq yoki format botga mos kelmadi.")

        finally:
            await status.delete()# --- ISHGA TUSHIRISH ---
async def main():
    logging.basicConfig(level=logging.INFO)

    # Menyu buyruqlarini o'rnatish
    await set_bot_commands(bot)

    print("Bot menyusi bilan birga ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO,
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers = [
            logging.FileHandler("bot-log"),
            logging.StreamHandler(sys.stdout)
        ])
    asyncio.run(main())