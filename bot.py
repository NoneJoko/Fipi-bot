import os
import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

user_state = {}

variants = {
    'Русский язык': {
        'Вариант 1': {
            '1': {'question': 'Прослушайте текст и напишите сжатое изложение.', 
                  'solution': 'Пример изложения с микротемами.', 'answer': 'сделано'},
            '2': {'question': 'Почему Серёжа сначала решил, что нашёл янтарь? Выберите 1–4\n1. Камень был похож на смолу и блестел\n2. Отец был экспертом\n3. Камень лежал среди обычной гальки\n4. Мальчик давно мечтал найти янтарь',
                  'solution': 'В предложении 5 камень блестел на солнце.', 'answer': '1'},
            '3': {'question': 'Укажите вариант со сравнением (1–4)\n1. День клонился к вечеру\n2. Он был тёмным\n3. Они положили камень в карман\n4. Он, как верный друг', 
                  'solution': 'Вариант 4: "как верный друг"', 'answer': '4'},
            '4': {'question': 'В каком слове приставка перед глухим согласным? 1–4\n1. расстроился\n2. внимательно\n3. отполировать\n4. вспыхивали', 
                  'solution': 'Расстроился — приставка РАС- перед глухим согласным', 'answer': '1'},
            '5': {'question': 'В каком слове наречие с приставкой ИЗ-, ДО-, С-? 1–4\n1. задумавшись\n2. издалека\n3. внимательно\n4. по-прежнему', 
                  'solution': 'Издалека — приставка ИЗ-, суффикс -А', 'answer': '2'},
            '6': {'question': 'Замените «ахнул» стилистически нейтральным синонимом', 
                  'solution': 'воскликнул или удивился', 'answer': 'воскликнул'},
            '7': {'question': 'Замените «морской смольё» на управление', 
                  'solution': 'смольё моря', 'answer': 'смольё моря'},
            '8': {'question': 'Выпишите грамматическую основу предложения 13', 
                  'solution': 'Серёжа расстроился, разглядел отблеск', 'answer': 'Серёжа расстроился, разглядел отблеск'},
            '9': {'question': 'Найдите предложение с обособленным обстоятельством (7–12)', 
                  'solution': 'Обособленных обстоятельств нет', 'answer': 'нет'}
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

def send_tasks_keyboard(chat_id, subject, variant):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for t in variants[subject][variant].keys():
        markup.row(str(t))
    markup.row('Назад')
    bot.send_message(chat_id, f"{subject} - {variant}: выберите задание", reply_markup=markup)

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
    user_state[chat_id]['variant'] = variant
    user_state[chat_id]['awaiting_answer'] = False
    send_tasks_keyboard(chat_id, user_state[chat_id]['subject'], variant)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id, {})

    # Если ожидается ответ, проверяем его
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
        # После проверки возвращаемся к списку заданий
        send_tasks_keyboard(chat_id, subject, variant)
        return

    # Если сообщение — "Назад"
    if message.text.lower() == 'назад':
        if 'variant' in state:
            send_tasks_keyboard(chat_id, state['subject'], state['variant'])
        else:
            send_subjects_keyboard(chat_id)
        state['awaiting_answer'] = False
        return

    # Если сообщение — номер задания, и мы не ожидаем ответ
    if message.text.isdigit() and not state.get('awaiting_answer', False):
        task_num = message.text
        subject = state['subject']
        variant = state['variant']
        if task_num in variants[subject][variant]:
            state['task_num'] = task_num
            state['awaiting_answer'] = True
            task = variants[subject][variant][task_num]
            bot.send_message(chat_id, f"Задание {task_num}:\n{task['question']}", reply_markup=ReplyKeyboardRemove())
            bot.send_message(chat_id, "Введите ваш ответ:")
        else:
            bot.send_message(chat_id, "Такого задания нет.")
        return

    # Любое другое сообщение игнорируем или подсказка
    bot.send_message(chat_id, "Пожалуйста, выберите задание через кнопки или введите ответ на текущее задание.")
    
if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
