import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import replicate

# 1. ВСТАВЬТЕ СЮДА ВАШИ ДАННЫЕ
TOKEN = '8803947784:AAHhPpPT24IATdYgzYqJkVWYAYwTwMUgxbw'
replicate_api_token = os.environ.get("REPLICATE_API_TOKEN")

# Настройка бота
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот-генератор.\n\n"
        "Пиши мне команды в таком формате:\n"
        "📸 **фото: [описание на англ]**\n"
        "🎥 **видео: [описание на англ]**\n\n"
        "Пример: `фото: futuristic car in cyberpunk city`"
    )
@dp.message()
async def handle_media(message: types.Message):
    text = message.text.lower()
    
    # ЛОГИКА ФОТО
    if text.startswith("фото:"):
        prompt = text.replace("фото:", "").strip()
        status_msg = await message.answer("🎨 Генерирую фото, подожди...")
        
        try:
            # Генерация фото
            output = replicate.run(
                "bytedance/sdxl-lightning-4step:6f7a773af6fc3e8de9d5a3c00be77c17308914bf67772726aff83496ba1e3bbe",
                input={"prompt": prompt}
            )
            
            # --- ВАЖНОЕ ИСПРАВЛЕНИЕ ЗДЕСЬ ---
            # output от этой модели — это список [FileOutput(...)]. 
            # Нам нужно взять первый элемент и получить из него URL.
            image_url = str(output[0]) if isinstance(output, list) else str(output)
            
            # Теперь отправляем боту чистую ссылку-строку
            await bot.send_photo(message.chat.id, photo=image_url)
            # ---------------------------------
            
        except Exception as e:
            await message.answer(f"Ошибка при генерации фото: {e}")
        finally:
            await status_msg.delete()

    # ЛОГИКА ВИДЕО
    elif text.startswith("видео:"):
        prompt = text.replace("видео:", "").strip()
        status_msg = await message.answer("🎬 Генерирую видео, это займет около минуты...")
        
        try:
            # Используем актуальную модель для видео
            output = replicate.run(
                "wan-video/wan-2.1-14b:17112026", # Если эта версия устареет, возьмите новую с сайта Replicate
                input={
                    "prompt": prompt,
                    "aspect_ratio": "16:9"
                }
            )
            
            # Превращаем результат в ссылку для Telegram
            # Если это список, берем первый элемент и переводим в строку
            video_url = str(output[0]) if isinstance(output, list) else str(output)
            
            await bot.send_video(message.chat.id, video=video_url)
            
        except Exception as e:
            await message.answer(f"Ошибка при генерации видео: {e}")
        finally:
            await status_msg.delete()
    
    else:
        await message.answer("Не понял команду. Используй формат: 'фото: текст' или 'видео: текст'")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
#6f7a773af6fc3e8de9d5a3c00be77c17308914bf67772726aff83496ba1e3bbe
#5b14e2c2c648efecc8d36c6353576552f8a124e690587212f8e8bb17ecda3d8c
