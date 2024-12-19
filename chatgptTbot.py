import logging
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Настройки API ключей
TELEGRAM_BOT_TOKEN = "7687315559:AAFDp1K9p81sTnmgohUmoK6fn8oYMtBerqo"
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Главное меню
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("💬 Чат с ChatGPT"))
    keyboard.add(KeyboardButton("💰 Проверить баланс"), KeyboardButton("🔄 Пополнить баланс"))
    return keyboard

# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я G_p_t_Chat бот.\n\n"
        "Я могу:\n"
        "1️⃣ Общаться с ChatGPT.\n"
        "2️⃣ Проверять баланс токенов (скоро).\n"
        "3️⃣ Пополнять баланс и оплачивать подписку (скоро).\n\n"
        "Выберите действие ниже:",
        reply_markup=main_menu(),
    )

# Обработчик кнопки "Чат с ChatGPT"
@dp.message_handler(lambda message: message.text == "💬 Чат с ChatGPT")
async def chat_with_gpt(message: types.Message):
    await message.answer("💬 Напишите ваш вопрос, и я передам его ChatGPT!")

# Обработчик сообщений для общения с ChatGPT
@dp.message_handler()
async def gpt_chat(message: types.Message):
    try:
        # Отправляем запрос в OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Или "gpt-4"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message.text}
            ]
        )
        gpt_response = response["choices"][0]["message"]["content"]
        await message.answer(gpt_response)
    except Exception as e:
        await message.answer("⚠️ Ошибка при обращении к ChatGPT. Попробуйте позже.")
        logging.error(f"Ошибка ChatGPT: {e}")

# Обработчик кнопки "Проверить баланс"
@dp.message_handler(lambda message: message.text == "💰 Проверить баланс")
async def check_balance(message: types.Message):
    await message.answer("⚙️ Функция проверки баланса находится в разработке.")

# Обработчик кнопки "Пополнить баланс"
@dp.message_handler(lambda message: message.text == "🔄 Пополнить баланс")
async def refill_balance(message: types.Message):
    await message.answer("⚙️ Функция пополнения баланса находится в разработке.")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
