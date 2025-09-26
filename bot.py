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
voice_timers = {}

# --- Текст и задания ---
text_part2 = (
    "(1)Серёжа и его отец шли берегом моря, усыпанным крупной галькой. "
    "(2)День клонился к вечеру, и длинные тени падали от скал на песок. "
    "(3)Отец шёл молча, задумавшись, а Серёжа бросал в воду плоские камешки, стараясь пустить их по воде как можно дальше. "
    "(4)Вдруг он заметил необычный камень. "
    "(5)Он был тёмным, почти чёрным, но там, где его касались лучи заходящего солнца, вспыхивали яркие искры. "
    "(6)Мальчик поднял его и ахнул от удивления. "
    "(7)«Папа, смотри, янтарь!» — крикнул он. "
    "(8)Отец взял находку и улыбнулся. "
    "(9)«Нет, сынок, это не янтарь...» "
    "(10)Это морской смольё, или гагат. "
    "(11)Его иногда называют чёрным янтарём."
)

variants = {
    'Русский язык': {
        'Вариант 1': {
            '1': {
                'voice_text': (
                    "У каждого из нас есть места, которые становятся особенными, "
                    "наполняясь глубоким личным смыслом. Для кого-то это родной дом, "
                    "для другого — старая улица, хранящая память о важных встречах. "
                    "Такие места обладают удивительной силой, возвращают нас в прошлое, "
                    "заставляют задуматься о будущем."
                ),
                'solution': 'Пример изложения с микротемами.',
                'answer': 'сделано'
            },
            '2': {'question': f'{text_part2}\n\nЗадание 2. Почему Серёжа сначала решил, что нашёл янтарь?\n1. Камень был похож на смолу и блестел на солнце.\n2. Отец был экспертом.\n3. Камень лежал среди гальки.\n4. Мальчик давно мечтал найти янтарь.', 'solution': 'В предложении 5 камень блестел на солнце.', 'answer': '1'},
            '3': {'question': f'{text_part2}\n\nЗадание 3. Укажите вариант со сравнением (1–4)\n1. День клонился к вечеру.\n2. Он был тёмным.\n3. Они положили камень в карман.\n4. Он, как верный друг, был готов дать чувство защищённости.', 'solution': 'Вариант 4 содержит сравнение.', 'answer': '4'}
            # ... можно добавить остальные задания 4–9
        }
    }
}

subjects = list(variants.keys())

# --- Функции клавиатур ---
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

# --- Функции TTS ---
def send_voice_memory(chat_id, delay=300):
    tts = gTTS(variants['Русский язык']['Вариант 1']['1']['voice_text'], lang='ru')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    bot.send_voice(chat_id, mp3_fp)
    t = threading.Timer(delay, lambda: send_voice_memory(chat_id, delay))
    t.start()
    voice_timers[chat_id] = t

# --- Обработчики ---
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
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Задание 1')
    markup.row('Часть 2')
    bot.send_message(chat_id, "Выберите Задание 1 или Часть 2 (задания 2–9):", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id, {})

    # Остановка повторов
    if message.text.lower() == 'остановить повтор':
        timer = voice_timers.get(chat_id)
        if timer:
            timer.cancel()
            del voice_timers[chat_id]
            bot.send_message(chat_id, "Повтор остановлен.")
        else:
            bot.send_message(chat_id, "Повтор не был активен.")
        return

    # Выбор Задание 1
    if message.text == 'Задание 1':
        state['task_num'] = '1'
        state['awaiting_answer'] = True
        send_voice_memory(chat_id, delay=300)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Остановить повтор')
        bot.send_message(chat_id, "Задание 1: прослушайте изложение. После прослушивания введите ответ.", reply_markup=markup)
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

    # Проверка ответа
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

    bot.send_message(chat_id, "Выберите задание через кнопки или введите ответ на текущее задание.")

if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
