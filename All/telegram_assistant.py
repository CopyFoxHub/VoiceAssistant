# Импорт необходимых модулей
from aiogram import Bot, Dispatcher, executor, types

with open("Resources/Files/teleid.txt", "r") as file:
    TELEGRAM_ID = int(file.read())

# Функция для отправки сообщений
def my_answer_send():
    # Токен для бота
    with open("Resources/Files/TeleToken", "r") as file:
        TOKEN = file.read()
    # Интеграция бота
    bot = Bot(TOKEN)
    # Диспетчер для бота
    disp = Dispatcher(bot)
    # Функция запуска
    async def on_startup(_):
        # Текст, который нужно отправить
        with open("Resources/Files/Answer.txt", "r", encoding="utf-8") as file:
            text = file.read()
        await bot.send_message(chat_id=TELEGRAM_ID, text=text)
        exit()

    # Запуск
    executor.start_polling(disp, on_startup=on_startup)
