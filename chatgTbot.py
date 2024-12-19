import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Загрузка данных из .env с явным указанием пути
dotenv_path = "/storage/emulated/0/Pydroid 3 bots/.env"  # Укажите полный путь к вашему .env файлу
load_dotenv(dotenv_path)

# Получение токенов из .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO)

# Проверка наличия токена
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден. Проверьте .env файл и путь к нему.")

# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Главное меню
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("💬 Чат с ChatGPT"),
        KeyboardButton("⚙️ Выбрать модель"),
    )
    keyboard.add(
        KeyboardButton("💰 Проверить баланс"),
        KeyboardButton("🔄 Пополнить баланс")
    )
    keyboard.add(
        KeyboardButton("💳 Оплатить подписку")
    )
    return keyboard

# Пример обработчика команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я G_p_t_Chat бот.\n\n"
        "Выберите действие ниже:",
        reply_markup=main_menu(),
    )

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
