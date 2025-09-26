import os
import telebot
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

# Функция для отправки клавиатуры с заданиями и кнопкой "Назад"
def send_tasks_keyboard(message, subject):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    nums = [str(i) for i in range(1, 31)]
    for i in range(0, 30, 5):
        markup.row(*nums[i:i+5])
    markup.row('Назад')  # кнопка "Назад" как 31-я
    bot.send_message(
        message.chat.id,
        f"Вы выбрали «{subject}».\nВыберите номер задания (1–30) или нажмите 'Назад' для возврата:",
        reply_markup=markup
    )

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "Привет! 👋\n\n"
        "Это бот для подготовки к ОГЭ.\n\n"
        "📚 Доступные предметы:\n"
        "- Математика\n- Русский язык\n- Физика\n- Обществознание\n\n"
        "Выберите предмет для тренировки:"
    )
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Математика', 'Русский язык')
    markup.row('Физика', 'Обществознание')
    bot.send_message(message.chat.id, text, reply_markup=markup)

# Обработчик выбора предмета
@bot.message_handler(func=lambda m: m.text in ['Математика', 'Русский язык', 'Физика', 'Обществознание'])
def handle_subject(message):
    send_tasks_keyboard(message, message.text)

# Обработчик выбора номера задания
@bot.message_handler(func=lambda m: m.text.isdigit() and 1 <= int(m.text) <= 30)
def handle_number(message):
    bot.send_message(message.chat.id, f"Задание №{message.text}")

# Обработчик кнопки "Назад"
@bot.message_handler(func=lambda m: m.text == 'Назад')
def go_back(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Математика', 'Русский язык')
    markup.row('Физика', 'Обществознание')
    bot.send_message(
        message.chat.id,
        "Вы вернулись к выбору предмета. Выберите предмет для тренировки:",
        reply_markup=markup
    )

if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
