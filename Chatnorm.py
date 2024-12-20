import logging
import openai
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Загрузка данных из .env файла
dotenv_path = "/storage/emulated/0/Pydroid 3 bots/.env"
load_dotenv(dotenv_path)

# Получение токенов из .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка токенов
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден. Проверьте .env файл и путь к нему.")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не найден. Проверьте .env файл и путь к нему.")

# Установка API-ключа OpenAI
openai.api_key = OPENAI_API_KEY

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Глобальная переменная для хранения выбранной модели
selected_model = "gpt-3.5-turbo"

# Словарь для хранения истории сообщений пользователей
user_sessions = {}

# Максимальное количество сообщений в истории
MAX_HISTORY_LENGTH = 60

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

# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    user_sessions[user_id] = [{"role": "system", "content": "Ты — помощник."}]
    await message.answer(
        "👋 Привет! Я G_p_t_Chat бот.\n\n"
        "Выберите действие ниже:",
        reply_markup=main_menu(),
    )

# Обработчик команды /reset
@dp.message_handler(commands=["reset"])
async def reset_history(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        user_sessions.pop(user_id)
    await message.answer("✅ История сообщений очищена.")

# Обработчик кнопки "Проверить баланс"
@dp.message_handler(lambda message: message.text == "💰 Проверить баланс")
async def check_balance(message: types.Message):
    balance_url = "https://platform.openai.com/account/usage"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Перейти к балансу OpenAI", url=balance_url))
    await message.answer(
        "💰 Чтобы проверить ваш текущий баланс, перейдите по ссылке ниже:",
        reply_markup=keyboard
    )

# Обработчик кнопки "Пополнить баланс"
@dp.message_handler(lambda message: message.text == "🔄 Пополнить баланс")
async def refill_balance(message: types.Message):
    refill_url = "https://platform.openai.com/account/billing"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Перейти к пополнению баланса", url=refill_url))
    await message.answer(
        "💳 Чтобы пополнить баланс, перейдите по ссылке ниже:",
        reply_markup=keyboard
    )

# Обработчик кнопки "Оплатить подписку"
@dp.message_handler(lambda message: message.text == "💳 Оплатить подписку")
async def pay_subscription(message: types.Message):
    subscription_url = "https://chat.openai.com/#pricing"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Перейти к оплате подписки", url=subscription_url))
    await message.answer(
        "🔔 Чтобы оплатить подписку на ChatGPT, перейдите по ссылке ниже:",
        reply_markup=keyboard
    )

# Обработчик кнопки "Выбрать модель"
@dp.message_handler(lambda message: message.text == "⚙️ Выбрать модель")
async def choose_model(message: types.Message):
    model_menu = InlineKeyboardMarkup(row_width=2)
    model_menu.add(
        InlineKeyboardButton("GPT-3.5", callback_data="select_gpt-3.5-turbo"),
        InlineKeyboardButton("GPT-4", callback_data="select_gpt-4")
    )
    await message.answer("Выберите модель для общения:", reply_markup=model_menu)

# Обработчик выбора модели
@dp.callback_query_handler(lambda c: c.data.startswith("select_"))
async def select_model(callback_query: types.CallbackQuery):
    global selected_model
    selected_model = callback_query.data.split("_")[1]
    await callback_query.message.answer(f"✅ Вы выбрали модель: {selected_model}")
    await callback_query.answer()

# Обработчик кнопки "Чат с ChatGPT"
@dp.message_handler(lambda message: message.text == "💬 Чат с ChatGPT")
async def chat_with_gpt(message: types.Message):
    await message.answer(f"💬 Выбранная модель: {selected_model}. Напишите ваш вопрос, и я передам его в ChatGPT!")

# Обработчик текстовых сообщений для ChatGPT
@dp.message_handler()
async def gpt_chat(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = [{"role": "system", "content": "Ты — помощник."}]

    # Добавляем сообщение пользователя в историю
    user_sessions[user_id].append({"role": "user", "content": message.text})

    # Ограничиваем длину истории
    if len(user_sessions[user_id]) > MAX_HISTORY_LENGTH:
        user_sessions[user_id] = user_sessions[user_id][-MAX_HISTORY_LENGTH:]

    try:
        # Отправляем запрос в OpenAI API
        response = openai.ChatCompletion.create(
            model=selected_model,
            messages=user_sessions[user_id]
        )
        # Получаем текст ответа
        gpt_response = response["choices"][0]["message"]["content"]

        # Добавляем ответ бота в историю
        user_sessions[user_id].append({"role": "assistant", "content": gpt_response})

        await message.answer(gpt_response)
    except openai.error.AuthenticationError:
        await message.answer("⚠️ Ошибка аутентификации API. Проверьте ваш API-ключ.")
    except openai.error.InvalidRequestError as e:
        await message.answer(f"⚠️ Неправильный запрос: {e}")
    except openai.error.RateLimitError:
        await message.answer("⚠️ Превышен лимит запросов. Попробуйте позже.")
    except Exception as e:
        await message.answer("⚠️ Произошла ошибка при взаимодействии с ChatGPT.")
        logging.error(f"Ошибка ChatGPT: {e}")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
