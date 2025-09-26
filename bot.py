import os
import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)
user_state = {}

# Задания Русский язык, Вариант 1
variants = {
    'Русский язык': {
        'Вариант 1': {
            '1': {
                'question': 'Часть 1. Изложение\n\nПрослушайте текст и напишите сжатое изложение:\n'
                            '«У каждого из нас есть места, которые становятся особенными...»',
                'solution': 'Пример изложения с микротемами.',
                'answer': 'сделано'
            },
            '2': {
                'question': 'Часть 2. Задание 2.\nВ каком варианте ответа содержится информация, необходимая для ответа на вопрос: «Почему Серёжа сначала решил, что нашёл янтарь?»\n\n'
                            '1. Камень был похож на смолу и блестел на солнце.\n'
                            '2. Отец мальчика был экспертом по минералам.\n'
                            '3. Камень лежал среди обычной гальки.\n'
                            '4. Мальчик давно мечтал найти именно янтарь.',
                'solution': 'В предложении 5 камень блестел на солнце, что вызвало ассоциацию с янтарём.',
                'answer': '1'
            },
            '3': {
                'question': 'Часть 2. Задание 3.\nУкажите вариант, в котором средством выразительности речи является сравнение.\n\n'
                            '1. День клонился к вечеру, и длинные тени падали от скал на песок.\n'
                            '2. Он был тёмным, почти чёрным, но там, где его касались лучи заходящего солнца, вспыхивали яркие искры.\n'
                            '3. Они положили камень в карман и пошли дальше, а море по-прежнему шумело, накатывая на берег волну за волной.\n'
                            '4. Он, как верный друг, всегда готов был подарить чувство защищённости.',
                'solution': 'Сравнение присутствует в варианте 4: "как верный друг".',
                'answer': '4'
            },
            '4': {
                'question': 'Часть 2. Задание 4.\nВ каком слове правописание приставки определяется правилом: «Если после приставки следует глухой согласный, то на конце её пишется -С»?\n\n'
                            '1. расстроился\n2. внимательно\n3. отполировать\n4. вспыхивали',
                'solution': 'Приставка РАС- пишется перед глухим согласным (слово «расстроился»).',
                'answer': '1'
            },
            '5': {
                'question': 'Часть 2. Задание 5.\nВ каком слове правописание суффикса определяется правилом: «В наречиях с приставками ИЗ-, ДО-, С- пишется суффикс -А»?\n\n'
                            '1. задумавшись\n2. издалека\n3. внимательно\n4. по-прежнему',
                'solution': 'В слове «издалека» есть приставка ИЗ- и суффикс -А.',
                'answer': '2'
            },
            '6': {
                'question': 'Часть 2. Задание 6.\nЗамените разговорное слово «ахнул» стилистически нейтральным синонимом.',
                'solution': 'воскликнул или удивился',
                'answer': 'воскликнул'
            },
            '7': {
                'question': 'Часть 2. Задание 7.\nЗамените словосочетание «морской смольё» с согласования на управление.',
                'solution': 'смольё моря',
                'answer': 'смольё моря'
            },
            '8': {
                'question': 'Часть 2. Задание 8.\nВыпишите грамматическую основу предложения 13.',
                'solution': 'Серёжа расстроился, разглядел отблеск',
                'answer': 'Серёжа расстроился, разглядел отблеск'
            },
            '9': {
                'question': 'Часть 2. Задание 9.\nСреди предложений 7–12 найдите предложение с обособленным обстоятельством.',
                'solution': 'Обособленных обстоятельств нет',
                'answer': 'нет'
            }
        }
    }
}

subjects = list(variants.keys())

def send_subjects_keyboard(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(subjects), 2):
        markup.row(*subjects[i:i+2])
    bot.send_message(chat_id, "Выберите предмет:", reply_markup=markup)

def send_variants_keyboard(chat_id, subject):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for v in variants[subject].keys():
        markup.row(v)
    bot.send_message(chat_id, f"Выберите вариант для {subject}:", reply_markup=markup)

def send_part2_tasks_keyboard(chat_id, subject, variant):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for t in range(2, 10):
        markup.row(str(t))
    markup.row('Назад')
    bot.send_message(chat_id, f"{subject} - {variant}: Часть 2, выберите задание", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    send_subjects_keyboard(message.chat.id)
    user_state[message.chat.id] = {'awaiting_answer': False}

@bot.message_handler(func=lambda m: m.text in subjects)
def handle_subject(message):
    chat_id = message.chat.id
    subject = message.text
    user_state[chat_id] = {'subject': subject, 'awaiting_answer': False}
    send_variants_keyboard(chat_id, subject)

@bot.message_handler(func=lambda m: any(m.text in variants[s].keys() for s in subjects))
def handle_variant(message):
    chat_id = message.chat.id
    variant = message.text
    state = user_state[chat_id]
    state['variant'] = variant
    state['awaiting_answer'] = False
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Задание 1')
    markup.row('Часть 2')
    bot.send_message(chat_id, "Выберите Задание 1 или Часть 2 (задания 2–9):", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id, {})

    # Если ожидаем ответ
    if state.get('awaiting_answer') and 'task_num' in state:
        subject = state['subject']
        variant = state['variant']
        task_num = state['task_num']
        task = variants[subject][variant][task_num]
        user_answer = message.text.strip().lower()
        correct_answer = task['answer'].strip().lower()
        if user_answer == correct_answer:
            bot.send_message(chat_id, f"✅ Верно!\nРешение:\n{task['solution']}")
        else:
            bot.send_message(chat_id, f"❌ Неверно.\nПравильный ответ: {task['answer']}\nРешение:\n{task['solution']}")
        state['awaiting_answer'] = False
        del state['task_num']
        # После проверки возвращаемся к выбору Задание 1 / Часть 2
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Задание 1')
        markup.row('Часть 2')
        bot.send_message(chat_id, "Выберите Задание 1 или Часть 2:", reply_markup=markup)
        return

    # Кнопка Назад
    if message.text.lower() == 'назад':
        if 'variant' in state:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Задание 1')
            markup.row('Часть 2')
            bot.send_message(chat_id, "Выберите Задание 1 или Часть 2:", reply_markup=markup)
        else:
            send_subjects_keyboard(chat_id)
        state['awaiting_answer'] = False
        return

    # Выбор Задание 1
    if message.text == 'Задание 1':
        state['task_num'] = '1'
        state['awaiting_answer'] = True
        task = variants[state['subject']][state['variant']]['1']
        bot.send_message(chat_id, f"Задание 1:\n{task['question']}", reply_markup=ReplyKeyboardRemove())
        bot.send_message(chat_id, "Введите ваш ответ:")
        return

    # Выбор Часть 2
    if message.text == 'Часть 2':
        send_part2_tasks_keyboard(chat_id, state['subject'], state['variant'])
        return

    # Выбор задания в Часть 2
    if message.text.isdigit() and not state.get('awaiting_answer', False):
        task_num = message.text
        if task_num in variants[state['subject']][state['variant']]:
            state['task_num'] = task_num
            state['awaiting_answer'] = True
            task = variants[state['subject']][state['variant']][task_num]
            bot.send_message(chat_id, f"Задание {task_num}:\n{task['question']}", reply_markup=ReplyKeyboardRemove())
            bot.send_message(chat_id, "Введите ваш ответ:")
        else:
            bot.send_message(chat_id, "Такого задания нет.")
        return

    bot.send_message(chat_id, "Пожалуйста, выберите задание через кнопки или введите ответ на текущее задание.")

if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
