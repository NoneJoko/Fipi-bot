import os
import telebot
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

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

@bot.message_handler(func=lambda m: m.text in
                     ['Математика', 'Русский язык', 'Физика', 'Обществознание'])
def handle_subject(message):
    if message.text == 'Русский язык':
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        nums = [str(i) for i in range(1, 31)]
        for i in range(0, 30, 5):
            markup.row(*nums[i:i+5])
        bot.send_message(
            message.chat.id,
            "Вы выбрали «Русский язык».\nВыберите номер задания (1–30):",
            reply_markup=markup
        )
    else:
        bot.send_message(message.chat.id, f"Вы выбрали {message.text}.")

@bot.message_handler(func=lambda m: m.text.isdigit() and 1 <= int(m.text) <= 30)
def handle_number(message):
    bot.send_message(message.chat.id, f"Задание №{message.text} по русскому языку.")

if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
