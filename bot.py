import os
import telebot
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

# Хранение состояния пользователей
user_state = {}

# Задания по Русскому языку, Вариант 1
variants = {
    'Русский язык': {
        'Вариант 1': {
            '1': {'question': 'Прослушайте текст и напишите сжатое изложение.',
                  'solution': 'Пример изложения с микротемами, около 80 слов.',
                  'answer': 'сделано'},
            '2': {'question': 'Почему Серёжа сначала решил, что нашёл янтарь? Выберите 1–4',
                  'solution': 'Камень блестел на солнце, что вызвало ассоциацию с янтарём.',
                  'answer': '1'},
            '3': {'question': 'Где есть сравнение? Выберите 1–4',
                  'solution': 'Вариант 4: "как верный друг".',
                  'answer': '4'},
            '4': {'question': 'В каком слове приставка перед глухим согласным? 1–4',
                  'solution': 'Расстроился — приставка РАС- перед глухим согласным.',
                  'answer': '1'},
            '5': {'question': 'В каком слове наречие с приставкой ИЗ-, ДО-, С-? 1–4',
                  'solution': 'Издалека — приставка ИЗ-, суффикс -А.',
                  'answer': '2'},
            '6': {'question': 'Замените «ахнул» стилистически нейтральным синонимом',
                  'solution': 'воскликнул или удивился',
                  'answer': 'воскликнул'},
            '7': {'question': 'Замените «морской смольё» с согласования на управление',
                  'solution': 'смольё моря',
                  'answer': 'смольё моря'},
            '8': {'question': 'Выпишите грамматическую основу предложения 13',
                  'solution': 'Серёжа расстроился, разглядел отблеск',
                  'answer': 'Серёжа расстроился, разглядел отблеск'},
            '9': {'question': 'Найдите предложение с обособленным обстоятельством (7–12)',
                  'solution': 'В данных предложениях обособленных обстоятельств нет.',
                  'answer': 'нет'}
        }
    }
}

subjects = list(variants.keys())

# Отправка кнопок предметов
def send_subjects_keyboard(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(subjects), 2):
        markup.row(*subjects[i:i+2])
    bot.send_message(chat_id, "Выберите предмет:", reply_markup=markup)

# Отправка кнопок вариантов
def send_variants_keyboard(chat_id, subject):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for v in variants[subject].keys():
        markup.row(v)
    bot.send_message(chat_id, f"Выберите вариант для {subject}:", reply_markup=markup)

# Отправка кнопок заданий
def send_tasks_keyboard(chat_id, subject, variant):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for t in variants[subject][variant].keys():
        markup.row(t)
    markup.row('Назад')
    bot.send_message(chat_id, f"{subject} - {variant}: выберите задание", reply_markup=markup)

# Старт бота
@bot.message_handler(commands=['start'])
def start(message):
    send_subjects_keyboard(message.chat.id)

# Выбор предмета
@bot.message_handler(func=lambda m: m.text in subjects)
def handle_subject(message):
    chat_id = message.chat.id
    subject = message.text
    user_state[chat_id] = {'subject': subject}
    send_variants_keyboard(chat_id, subject)

# Выбор варианта
@bot.message_handler(func=lambda m: any(m.text in variants[s].keys() for s in subjects))
def handle_variant(message):
    chat_id = message.chat.id
    variant = message.text
    subject = user_state[chat_id]['subject']
    user_state[chat_id]['variant'] = variant
    send_tasks_keyboard(chat_id, subject, variant)

# Выбор задания
@bot.message_handler(func=lambda m: m.text.isdigit())
def handle_task(message):
    chat_id = message.chat.id
    if chat_id not in user_state or 'subject' not in user_state[chat_id] or 'variant' not in user_state[chat_id]:
        bot.send_message(chat_id, "Сначала выберите предмет и вариант.")
        return
    task_num = message.text
    subject = user_state[chat_id]['subject']
    variant = user_state[chat_id]['variant']
    if task_num in variants[subject][variant]:
        user_state[chat_id]['task_num'] = task_num
        task = variants[subject][variant][task_num]
        bot.send_message(chat_id, f"Задание {task_num}:\n{task['question']}")
        bot.send_message(chat_id, "Введите ваш ответ:")
    else:
        bot.send_message(chat_id, f"Задание №{task_num} отсутствует.")

# Кнопка Назад
@bot.message_handler(func=lambda m: m.text.lower() == 'назад')
def handle_back(message):
    chat_id = message.chat.id
    if chat_id in user_state and 'subject' in user_state[chat_id] and 'variant' in user_state[chat_id]:
        subject = user_state[chat_id]['subject']
        variant = user_state[chat_id]['variant']
        send_tasks_keyboard(chat_id, subject, variant)
        if 'task_num' in user_state[chat_id]:
            del user_state[chat_id]['task_num']
    else:
        send_subjects_keyboard(chat_id)

# Проверка ответа
@bot.message_handler(func=lambda m: True)
def check_answer(message):
    chat_id = message.chat.id
    if chat_id in user_state and 'task_num' in user_state[chat_id]:
        task_num = user_state[chat_id]['task_num']
        subject = user_state[chat_id]['subject']
        variant = user_state[chat_id]['variant']
        task = variants[subject][variant][task_num]
        user_answer = message.text.strip().lower()
        correct_answer = task['answer'].strip().lower()
        if user_answer == correct_answer:
            bot.send_message(chat_id, f"✅ Верно!\nРешение:\n{task['solution']}")
        else:
            bot.send_message(chat_id, f"❌ Неверно. Правильный ответ: {task['answer']}\nРешение:\n{task['solution']}")
        del user_state[chat_id]['task_num']

# Запуск
if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
