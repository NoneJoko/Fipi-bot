import io
import threading
import os
import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from gtts import gTTS

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)
user_state = {}

# --- Тексты и задания ---
voice_text = (
    "У каждого из нас есть места, которые становятся особенными, "
    "наполняясь глубоким личным смыслом. Для кого-то это родной дом, "
    "для другого — старая улица, хранящая память о важных встречах. "
    "Такие места обладают удивительной силой, возвращают нас в прошлое, "
    "заставляют задуматься о будущем. Часто именно с этими уголками связаны наши самые тёплые воспоминания."
)
keywords = ["места", "особенными", "родной дом", "улица", "смыслом", "сила", "воспоминания"]

text_part2 = (
    "(1)Серёжа и его отец шли берегом моря, усыпанным крупной галькой. "
    "(2)День клонился к вечеру, и длинные тени падали от скал на песок. "
    "(3)Отец шёл молча, задумавшись, а Серёжа бросал в воду плоские камешки. "
    "(4)Вдруг он заметил необычный камень. "
    "(5)Он был тёмным, почти чёрным, но там, где его касались лучи заходящего солнца, вспыхивали яркие искры. "
    "(6)Мальчик поднял его и ахнул от удивления. "
    "(7)«Папа, смотри, янтарь!» — крикнул он. "
    "(8)Отец взял находку и улыбнулся. "
    "(9)«Нет, сынок, это не янтарь...» "
    "(10)Это морской смольё, или гагат. "
    "(11)Его иногда называют чёрным янтарём."
)

# --- Вариант с заданиями 1–9 ---
variants = {
    'Русский язык': {
        'Вариант 1': {
            '1': {'voice_text': voice_text, 'solution': 'Пример изложения с микротемами.', 'answer': 'сделано'},
            '2': {'question': f'{text_part2}\n\nЗадание 2. Почему Серёжа сначала решил, что нашёл янтарь?\n1. Камень был похож на смолу и блестел на солнце.\n2. Отец был экспертом.\n3. Камень лежал среди гальки.\n4. Мальчик давно мечтал найти янтарь.', 'solution': 'В предложении 5 камень блестел на солнце.', 'answer': '1'},
            '3': {'question': f'{text_part2}\n\nЗадание 3. Укажите вариант со сравнением (1–4)\n1. День клонился к вечеру.\n2. Он был тёмным.\n3. Они положили камень в карман.\n4. Он, как верный друг, был готов дать чувство защищённости.', 'solution': 'Вариант 4 содержит сравнение.', 'answer': '4'},
            '4': {'question': 'Задание 4. В каком слове правописание приставки определяется правилом «Если после приставки следует глухой согласный, то на конце пишется -С»?\n1. расстроился\n2. внимательно\n3. отполировать\n4. вспыхивали', 'solution': 'Приставка РАС- перед глухим согласным: расстроился.', 'answer': '1'},
            '5': {'question': 'Задание 5. В каком слове правописание суффикса определяется правилом «В наречиях с приставками ИЗ-, ДО-, С- пишется суффикс -А»?\n1. задумавшись\n2. издалека\n3. внимательно\n4. по-прежнему', 'solution': 'Правильный вариант: издалека.', 'answer': '2'},
            '6': {'question': 'Задание 6. Замените разговорное слово «ахнул» стилистически нейтральным синонимом. Напишите синоним.', 'solution': 'Стилистически нейтральный синоним — воскликнул или удивился.', 'answer': 'воскликнул'},
            '7': {'question': 'Задание 7. Замените словосочетание «морской смольё» с согласованием на синонимичное со связью управление.', 'solution': 'смольё моря', 'answer': 'смольё моря'},
            '8': {'question': 'Задание 8. Выпишите грамматическую основу предложения 13: «Серёжа немного расстроился, но потом разглядел в глубине камня какой-то отблеск».', 'solution': 'Серёжа расстроился, (он) разглядел отблеск.', 'answer': 'Серёжа расстроился, разглядел отблеск'},
            '9': {'question': 'Задание 9. Среди предложений 7–12 найдите предложение с обособленным обстоятельством. Напишите номер предложения.', 'solution': 'В данном тексте обособленных обстоятельств нет.', 'answer': 'нет'}
        }
    }
}

subjects = list(variants.keys())

# --- Кнопки ---
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

# --- TTS ---
def send_voice_once(chat_id):
    tts = gTTS(voice_text, lang='ru')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    bot.send_voice(chat_id, mp3_fp)  # отправляется как voice note, нельзя поставить на паузу

def task1_playback(chat_id):
    send_voice_once(chat_id)
    bot.send_message(chat_id, "Голосовое сообщение 1/2. Прослушайте полностью.")

    def second_playback():
        send_voice_once(chat_id)
        bot.send_message(chat_id, "Голосовое сообщение 2/2. После прослушивания можете ввести изложение.")
        user_state[chat_id]['awaiting_answer'] = True

    threading.Timer(300, second_playback).start()  # 5 минут

# --- Обработчики ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_state[chat_id] = {'awaiting_answer': False}
    send_subjects_keyboard(chat_id)

@bot.message_handler(func=lambda m: m.text in subjects)
def handle_subject(message):
    chat_id = message.chat.id
    subject = message.text
    user_state[chat_id].update({'subject': subject, 'awaiting_answer': False})
    send_variants_keyboard(chat_id, subject)

@bot.message_handler(func=lambda m: any(m.text in variants[s].keys() for s in subjects))
def handle_variant(message):
    chat_id = message.chat.id
    variant = message.text
    state = user_state[chat_id]
    state['variant'] = variant
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Задание 1')
    markup.row('Часть 2')
    bot.send_message(chat_id, "Выберите Задание 1 или Часть 2 (задания 2–9):", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id, {})

    # Задание 1
    if message.text == 'Задание 1':
        state['awaiting_answer'] = False
        task1_playback(chat_id)
        return

    # Часть 2
    if message.text == 'Часть 2':
        send_part2_tasks_keyboard(chat_id, state['subject'], state['variant'])
        return

    # Выбор задания в части 2
    if message.text.isdigit() and not state.get('awaiting_answer', False):
        task_num = message.text
        if task_num in variants[state['subject']][state['variant']]:
            state['task_num'] = task_num
            state['awaiting_answer'] = True
            task = variants[state['subject']][state['variant']][task_num]
            bot.send_message(chat_id, f"Задание {task_num}:\n{task.get('question', '')}", reply_markup=ReplyKeyboardRemove())
            bot.send_message(chat_id, "Введите ваш ответ:")
        else:
            bot.send_message(chat_id, "Такого задания нет.")
        return

    # Проверка ответа Задания 1
    if state.get('awaiting_answer') and 'task_num' not in state:
        answer = message.text.lower()
        matched = sum(1 for kw in keywords if kw.lower() in answer)
        if matched >= max(1, len(keywords)//2):
            bot.send_message(chat_id, f"✅ Хорошо! Ваше изложение содержит достаточное количество ключевых идей ({matched}/{len(keywords)}).")
        else:
            bot.send_message(chat_id, f"⚠️ В вашем изложении недостаточно ключевых идей ({matched}/{len(keywords)}). Попробуйте добавить важные детали.")
        state['awaiting_answer'] = False
        return

    # Проверка ответа части 2
    if state.get('awaiting_answer') and 'task_num' in state:
        task_num = state['task_num']
        task = variants[state['subject']][state['variant']][task_num]
        user_answer = message.text.strip().lower()
        correct_answer = task.get('answer', '').strip().lower()
        if user_answer == correct_answer:
            bot.send_message(chat_id, f"✅ Верно!\nРешение:\n{task['solution']}")
        else:
            bot.send_message(chat_id, f"❌ Неверно.\nПравильный ответ: {task['answer']}\nРешение:\n{task['solution']}")
        state['awaiting_answer'] = False
        del state['task_num']
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Задание 1')
        markup.row('Часть 2')
        bot.send_message(chat_id, "Выберите Задание 1 или Часть 2:", reply_markup=markup)
        return

    bot.send_message(chat_id, "Выберите задание через кнопки или дождитесь завершения прослушивания.")

if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
