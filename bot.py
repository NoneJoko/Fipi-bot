import os
import telebot
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

# Список всех предметов
subjects = [
    'Математика', 'Русский язык', 'Физика', 'Обществознание',
    'Информатика', 'История', 'Литература', 'География',
    'Английский', 'Биология', 'Химия'
]

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

# Функция для показа клавиатуры с выбором предметов
def send_subjects_keyboard(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(subjects), 2):
        markup.row(*subjects[i:i+2])
    bot.send_message(
        message.chat.id,
        "Выберите предмет для тренировки:",
        reply_markup=markup
    )

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Сгенерировать вариант', 'Выбрать из существующих')
    bot.send_message(
        message.chat.id,
        "Привет! 👋\n\n"
        "Это бот для подготовки к ОГЭ.\n\n"
        "Сначала выберите, хотите ли вы сгенерировать новый вариант или выбрать из существующих:",
        reply_markup=markup
    )

# Обработчик выбора "Сгенерировать вариант" или "Выбрать из существующих"
@bot.message_handler(func=lambda m: m.text in ['Сгенерировать вариант', 'Выбрать из существующих'])
def handle_mode_choice(message):
    send_subjects_keyboard(message)

# Обработчик выбора предмета
@bot.message_handler(func=lambda m: m.text in subjects)
def handle_subject(message):
    send_tasks_keyboard(message, message.text)

# Обработчик выбора номера задания
@bot.message_handler(func=lambda m: m.text.isdigit() and 1 <= int(m.text) <= 30)
def handle_number(message):
    bot.send_message(message.chat.id, f"Задание №{message.text}")

# Обработчик кнопки "Назад"
@bot.message_handler(func=lambda m: m.text == 'Назад')
def go_back(message):
    send_subjects_keyboard(message)

if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
