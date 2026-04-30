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


# Link kelganda yuklab olish qismi
@dp.message(F.text.regexp(r'(https?://[^\s]+)'))
async def handle_download(message: types.Message):
    url = message.text
    if any(site in url for site in ["instagram.com", "tiktok.com", "youtube.com", "youtu.be"]):
        status = await message.answer("⏳ Video yuklanmoqda (5-15 sekund)...")
        file_path = None  # Fayl yo'lini boshlang'ich qiymati

        try:
            # Videoni yuklab olish
            file_path = await asyncio.to_thread(download_media, url)

            # Videoni Telegramga yuborish
            video = types.FSInputFile(file_path)
            await message.answer_video(video, caption="Tayyor! ✅ @sizning_botingiz")

        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}")
            await message.answer("❌ Xatolik! Video yopiq profilda bo'lishi yoki juda katta bo'lishi mumkin.")

        finally:
            # VIDEO O'CHIRISH QISMI:
            # Fayl yuklangan bo'lsa va u kompyuterda mavjud bo'lsa - uni o'chiramiz
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"Fayl o'chirildi: {file_path}")

            # Status xabarini (⏳...) o'chirish
            await status.delete()
# --- ISHGA TUSHIRISH ---
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