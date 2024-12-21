import logging
import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
dotenv_path = "./.env"  # Укажите путь к .env файлу в директории Pydroid 3
load_dotenv(dotenv_path)

# Получение токенов
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка токенов
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден. Проверьте .env файл.")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не найден. Проверьте .env файл.")

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация приложения
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Хранилище данных пользователей
user_sessions = {}
MAX_HISTORY_LENGTH = 60
selected_model = "gpt-3.5-turbo"  # Модель по умолчанию

# Главное меню
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("💬 Чат с ChatGPT"),
        KeyboardButton("⚙️ Выбрать модель")
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
async def start(update: Update, context):
    user_id = update.message.from_user.id
    user_sessions[user_id] = [{"role": "system", "content": "Ты — помощник."}]
    await update.message.reply(
        "👋 Привет! Я G_p_t_Chat бот.\n\n"
        "Выберите действие ниже:",
        reply_markup=main_menu(),
    )

# Обработчик команды /reset
async def reset_history(update: Update, context):
    user_id = update.message.from_user.id
    if user_id in user_sessions:
        user_sessions.pop(user_id)
    await update.message.reply("✅ История сообщений очищена.")

# Обработчик "Проверить баланс"
async def check_balance(update: Update, context):
    balance_url = "https://platform.openai.com/account/usage"
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Перейти к балансу OpenAI", url=balance_url)
    )
    await update.message.reply(
        "💰 Чтобы проверить ваш текущий баланс, перейдите по ссылке ниже:",
        reply_markup=keyboard
    )

# Обработчик "Пополнить баланс"
async def refill_balance(update: Update, context):
    refill_url = "https://platform.openai.com/account/billing"
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Перейти к пополнению баланса", url=refill_url)
    )
    await update.message.reply(
        "💳 Чтобы пополнить баланс, перейдите по ссылке ниже:",
        reply_markup=keyboard
    )

# Обработчик "Оплатить подписку"
async def pay_subscription(update: Update, context):
    subscription_url = "https://chat.openai.com/#pricing"
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Перейти к оплате подписки", url=subscription_url)
    )
    await update.message.reply(
        "🔔 Чтобы оплатить подписку на ChatGPT, перейдите по ссылке ниже:",
        reply_markup=keyboard
    )

# Обработчик "Выбрать модель"
async def choose_model(update: Update, context):
    model_menu = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("GPT-3.5", callback_data="select_gpt-3.5-turbo"),
        InlineKeyboardButton("GPT-4", callback_data="select_gpt-4")
    )
    await update.message.reply("Выберите модель для общения:", reply_markup=model_menu)

# Обработчик выбора модели
async def select_model(update: Update, context):
    global selected_model
    selected_model = update.callback_query.data.split("_")[1]
    await update.callback_query.message.reply(f"✅ Вы выбрали модель: {selected_model}")
    await update.callback_query.answer()

# Обработчик "Чат с ChatGPT"
async def chat_with_gpt(update: Update, context):
    await update.message.reply(f"💬 Выбранная модель: {selected_model}. Напишите ваш вопрос, и я передам его в ChatGPT!")

# Обработчик текстовых сообщений для ChatGPT
async def gpt_chat(update: Update, context):
    user_id = update.message.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = [{"role": "system", "content": "Ты — помощник."}]

    user_sessions[user_id].append({"role": "user", "content": update.message.text})

    if len(user_sessions[user_id]) > MAX_HISTORY_LENGTH:
        user_sessions[user_id] = user_sessions[user_id][-MAX_HISTORY_LENGTH:]

    # Подготовка запроса
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": selected_model,
        "messages": user_sessions[user_id]
    }

    try:
        # Отправка POST запроса к OpenAI API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )

        # Проверка на успешность запроса
        if response.status_code == 200:
            gpt_response = response.json()["choices"][0]["message"]["content"]
            user_sessions[user_id].append({"role": "assistant", "content": gpt_response})
            await update.message.reply(gpt_response)
        else:
            await update.message.reply("⚠️ Ошибка при запросе к OpenAI API. Попробуйте позже.")
            logging.error(f"Ошибка OpenAI API: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        await update.message.reply("⚠️ Произошла ошибка при взаимодействии с API.")
        logging.error(f"Ошибка при отправке запроса: {e}")

def main():
    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset_history))

    # Обработчики кнопок (с заменой pattern на filters.Regex)
    application.add_handler(MessageHandler(filters.Regex("💰 Проверить баланс"), check_balance))
    application.add_handler(MessageHandler(filters.Regex("🔄 Пополнить баланс"), refill_balance))
    application.add_handler(MessageHandler(filters.Regex("💳 Оплатить подписку"), pay_subscription))
    application.add_handler(MessageHandler(filters.Regex("⚙️ Выбрать модель"), choose_model))
    application.add_handler(MessageHandler(filters.Regex("💬 Чат с ChatGPT"), chat_with_gpt))

    # Обработчик callback данных
    application.add_handler(CallbackQueryHandler(select_model, pattern="select_"))

    # Обработчик текстовых сообщений для ChatGPT
    application.add_handler(MessageHandler(filters.TEXT, gpt_chat))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
