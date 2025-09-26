import os
import telebot
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

# Состояния пользователей
user_state = {}

# Полный словарь с 12 предметами и 30 заданиями для каждого
variants = {
    'Русский язык': {'Вариант 1': {str(i): {'question': f'Русский язык, задание {i}',
                                             'solution': f'Решение задания {i}',
                                             'answer': f'Ответ {i}'} for i in range(1, 31)}},
    'Математика': {'Вариант 1': {str(i): {'question': f'Математика, задание {i}',
                                           'solution': f'Решение задания {i}',
                                           'answer': f'Ответ {i}'} for i in range(1, 31)}},
    'Физика': {'Вариант 1': {str(i): {'question': f'Физика, задание {i}',
                                      'solution': f'Решение задания {i}',
                                      'answer': f'Ответ {i}'} for i in range(1, 31)}},
    'Обществознание': {'Вариант 1': {str(i): {'question': f'Обществознание, задание {i}',
                                              'solution': f'Решение задания {i}',
                                              'answer': f'Ответ {i}'} for i in range(1, 31)}},
    'Информатика': {'Вариант 1': {str(i): {'question': f'Информатика, задание {i}',
                                           'solution': f'Решение задания {i}',
                                           'answer': f'Ответ {i}'} for i in range(1, 31)}},
    'История': {'Вариант 1': {str(i): {'question': f'История, задание {i}',
                                       'solution': f'Решение задания {i}',
                                       'answer': f'Ответ {i}'} for i in range(1, 31)}},
    'Литература': {'Вариант 1': {str(i): {'question': f'Литература, задание {i}',
                                          'solution': f'Решение задания {i}',
                                          'answer': f'Ответ {i}'} for i in range(1, 31)}},
    'География': {'Вариант 1': {str(i): {'question': f'География, задание {i}',
                                         'solution': f'Решение задания {i}',
                                         'answer': f'Ответ {i}'} for i in range(1, 31)}},
    'Английский': {'Вариант 1': {str(i): {'question': f'Английский, задание {i}',
                                          'solution': f'Решение задания {i}',
                                          'answer': f'Ответ {i}'} for i in range(1, 31)}},
    'Биология': {'Вариант 1': {str(i): {'question': f'Биология, задание {i}',
                                        'solution': f'Решение задания {i}',
                                        'answer': f'Ответ {i}'} for i in range(1, 31)}},
    'Химия': {'Вариант 1': {str(i): {'question': f'Химия, задание {i}',
                                     'solution': f'Решение задания {i}',
                                     'answer': f'Ответ {i}'} for i in range(1, 31)}},
}

subjects = list(variants.keys())

# Функция для отображения предметов
def send_subjects_keyboard(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(subjects), 2):
        markup.row(*subjects[i:i+2])
    bot.send_message(chat_id, "Выберите предмет:", reply_markup=markup)

# Функция для отображения вариантов (все предметы имеют Вариант 1)
def send_variants_keyboard(chat_id, subject):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Вариант 1')
    bot.send_message(chat_id, f"Выберите вариант для {subject}:", reply_markup=markup)

# Функция для отображения заданий
def send_tasks_keyboard(chat_id, subject, variant):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    nums = [str(i) for i in variants[subject][variant].keys()]
    for i in range(0, len(nums), 5):
        markup.row(*nums[i:i+5])
    markup.row('Назад')
    bot.send_message(chat_id, f"{subject} - {variant}: выберите задание", reply_markup=markup)

# Старт бота
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    send_subjects_keyboard(chat_id)

# Выбор предмета
@bot.message_handler(func=lambda m: m.text in subjects)
def handle_subject(message):
    chat_id = message.chat.id
    subject = message.text
    user_state[chat_id] = {'subject': subject}
    send_variants_keyboard(chat_id, subject)

# Выбор варианта
@bot.message_handler(func=lambda m: m.text.startswith('Вариант'))
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
    if chat_id not in user_state:
        bot.send_message(chat_id, "Сначала выберите предмет и вариант.")
        return
    task_num = message.text
    user_state[chat_id]['task_num'] = task_num
    subject = user_state[chat_id]['subject']
    variant = user_state[chat_id]['variant']
    task = variants[subject][variant].get(task_num)
    if task:
        bot.send_message(chat_id, f"Задание {task_num}:\n{task['question']}")
        bot.send_message(chat_id, "Введите ваш ответ:")
    else:
        bot.send_message(chat_id, f"Задание №{task_num} пока не готово.")

# Кнопка "Назад"
@bot.message_handler(func=lambda m: m.text == 'Назад')
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

# Проверка ответа пользователя
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
            bot.send_message(chat_id, "✅ Верно!")
        else:
            bot.send_message(chat_id, f"❌ Неверно. Правильный ответ: {task['answer']}")
        bot.send_message(chat_id, f"Решение:\n{task['solution']}")
        del user_state[chat_id]['task_num']

# Запуск бота
if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
