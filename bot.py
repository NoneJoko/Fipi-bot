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

# --- Тексты и ключевые слова для проверки изложения ---
voice_text_template = "У каждого человека есть особенные места, которые становятся значимыми..."
keywords_template = ["места", "значимыми", "родной", "улица", "смысл", "воспоминания"]

text_part2_template = "(1)Серёжа и его отец шли по берегу..."

# --- Генерация 30 вариантов ---
variants = {'Русский язык': {}}
for v_num in range(1, 31):
    var_name = f'Вариант {v_num}'
    variants['Русский язык'][var_name] = {}
    # Задание 1
    variants['Русский язык'][var_name]['1'] = {
        'voice_text': voice_text_template + f" Вариант {v_num}.",
        'solution': 'Пример изложения с микротемами.',
        'answer': 'сделано'
    }
    # Задания 2–9 (аналогично)
    for t_num in range(2, 10):
        variants['Русский язык'][var_name][str(t_num)] = {
            'question': f'{text_part2_template} Задание {t_num} Вариант {v_num}.',
            'solution': f'Решение задания {t_num} Вариант {v_num}.',
            'answer': '1'  # для примера, можно настроить разные правильные ответы
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
def send_voice_once(chat_id, text):
    tts = gTTS(text, lang='ru')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    bot.send_voice(chat_id, mp3_fp)

def task1_playback(chat_id, voice_text):
    send_voice_once(chat_id, voice_text)
    bot.send_message(chat_id, "Голосовое сообщение 1/2. Прослушайте полностью.")

    def second_playback():
        send_voice_once(chat_id, voice_text)
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

    if message.text == 'Задание 1':
        state['awaiting_answer'] = False
        voice_text = variants[state['subject']][state['variant']]['1']['voice_text']
        task1_playback(chat_id, voice_text)
        return

    if message.text == 'Часть 2':
        send_part2_tasks_keyboard(chat_id, state['subject'], state['variant'])
        return

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

    if state.get('awaiting_answer') and 'task_num' not in state:
        answer = message.text.lower()
        matched = sum(1 for kw in keywords_template if kw.lower() in answer)
        if matched >= max(1, len(keywords_template)//2):
            bot.send_message(chat_id, f"✅ Хорошо! Ваше изложение содержит достаточное количество ключевых идей ({matched}/{len(keywords_template)}).")
        else:
            bot.send_message(chat_id, f"⚠️ В вашем изложении недостаточно ключевых идей ({matched}/{len(keywords_template)}). Попробуйте добавить важные детали.")
        state['awaiting_answer'] = False
        return

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
