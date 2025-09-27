import os
import io
import threading
import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from gtts import gTTS

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

# --- Состояние пользователя ---
user_state = {}

# --- Словарь с одним вариантом ---
variants = {
    'Русский язык': {
        'Вариант 1': {
            '1': {
                'voice_text': (
                    "У каждого из нас есть места, которые становятся особенными, "
                    "наполняясь глубоким личным смыслом. Для кого-то это родной дом, "
                    "для другого — старая улица, хранящая память о важных встречах. "
                    "Такие места обладают удивительной силой, возвращают нас в прошлое, "
                    "заставляют задуматься о будущем. Часто именно с этими уголками связаны наши самые тёплые воспоминания."
                ),
                'solution': 'Пример сжатого изложения с выделением микротем.',
                'answer': 'сделано'
            },
            '2': {
                'question': (
                    "(1)Серёжа и его отец шли берегом моря, усыпанным крупной галькой. "
                    "(2)День клонился к вечеру, и длинные тени падали от скал на песок. "
                    "(3)Отец шёл молча, задумавшись, а Серёжа бросал в воду плоские камешки, стараясь пустить их по воде как можно дальше. "
                    "(4)Вдруг он заметил необычный камень. "
                    "(5)Он был тёмным, почти чёрным, но там, где его касались лучи заходящего солнца, вспыхивали яркие искры. "
                    "(6)Мальчик поднял его и ахнул от удивления. "
                    "(7)«Папа, смотри, янтарь!» — крикнул он. "
                    "(8)Отец взял находку и улыбнулся. "
                    "(9)«Нет, сынок, это не янтарь. "
                    "(10)Это морской смольё, или гагат. "
                    "(11)Его иногда называют чёрным янтарём, но это совсем другой минерал. "
                    "(12)Он тоже тёплый на ощупь и очень красив, если его отполировать. "
                    "(13)Серёжа немного расстроился, но потом разглядел в глубине камня какой-то отблеск. "
                    "(14)«А можно мы его заберём с собой?» — спросил он. "
                    "(15)«Конечно, — ответил отец. "
                    "(16)— Из него может получиться отличный талисман на память о сегодняшнем дне». "
                    "(17)Они положили камень в карман и пошли дальше, а море по-прежнему шумело, накатывая на берег волну за волной."
                    "\n\nЗадание 2. Почему Серёжа сначала решил, что нашёл янтарь?\n"
                    "1. Камень был похож на смолу и блестел на солнце.\n"
                    "2. Отец был экспертом по минералам.\n"
                    "3. Камень лежал среди обычной гальки.\n"
                    "4. Мальчик давно мечтал найти именно янтарь."
                ),
                'solution': "В предложении 5 камень блестел на солнце и выглядел как янтарь. Ответ: 1",
                'answer': '1'
            },
            '3': {
                'question': (
                    "(Тот же текст)\n\nЗадание 3. Укажите вариант, в котором есть сравнение:\n"
                    "1. День клонился к вечеру, и длинные тени падали от скал на песок.\n"
                    "2. Он был тёмным, почти чёрным, но там, где его касались лучи заходящего солнца, вспыхивали яркие искры.\n"
                    "3. Они положили камень в карман и пошли дальше, а море по-прежнему шумело, накатывая на берег волну за волной.\n"
                    "4. Он, как верный друг, всегда готов был подарить чувство защищённости."
                ),
                'solution': "Сравнение есть в варианте 4: 'Он, как верный друг…'. Ответ: 4",
                'answer': '4'
            },
            '4': {
                'question': (
                    "Задание 4. В каком слове правописание приставки определяется правилом: "
                    "«Если после приставки следует глухой согласный, то на конце её пишется -С»?\n"
                    "1. расстроился\n2. внимательно\n3. отполировать\n4. вспыхивали"
                ),
                'solution': "Правильный вариант: расстроился (приставка РАС- перед глухим согласным).",
                'answer': '1'
            },
            '5': {
                'question': (
                    "Задание 5. В каком слове правописание суффикса определяется правилом: "
                    "«В наречиях, образованных от прилагательных с помощью приставок ИЗ-, ДО-, С-, пишется суффикс -А»?\n"
                    "1. задумавшись\n2. издалека\n3. внимательно\n4. по-прежнему"
                ),
                'solution': "Правильный вариант: издалека. Ответ: 2",
                'answer': '2'
            },
            '6': {
                'question': (
                    "Задание 6. Замените разговорное слово «ахнул» стилистически нейтральным синонимом. "
                    "Напишите синоним."
                ),
                'solution': "Стилистически нейтральный синоним: 'воскликнул' или 'удивился'.",
                'answer': 'воскликнул'
            },
            '7': {
                'question': (
                    "Задание 7. Замените словосочетание «морской смольё» (предложение 10), "
                    "построенное на согласовании, синонимичным словосочетанием со связью управление."
                ),
                'solution': "Словосочетание со связью управление: 'смольё моря'.",
                'answer': 'смольё моря'
            },
            '8': {
                'question': (
                    "Задание 8. Выпишите грамматическую основу предложения 13: "
                    "«Серёжа немного расстроился, но потом разглядел в глубине камня какой-то отблеск»."
                ),
                'solution': "Грамматическая основа: 'Серёжа расстроился', 'разглядел отблеск'.",
                'answer': 'Серёжа расстроился, разглядел отблеск'
            },
            '9': {
                'question': (
                    "Задание 9. Среди предложений 7–12 найдите предложение с обособленным обстоятельством. "
                    "Напишите номер предложения."
                ),
                'solution': "В данном тексте обособленных обстоятельств нет. Ответ: нет",
                'answer': 'нет'
            }
        }
    }
}

# --- Список предметов ---
subjects = list(variants.keys())

# --- Кнопки ---
def send_subjects_keyboard(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(subjects), 2):
        markup.row(*subjects[i:i+2])
    bot.send_message(chat_id, "Выберите предмет:", reply_markup=markup)

def send_tasks_keyboard(chat_id, subject):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(1, 10):
        markup.row(str(i))
    markup.row('Назад')
    bot.send_message(chat_id, f"{subject}: выберите задание", reply_markup=markup)

# --- TTS ---
def send_voice(chat_id, text):
    tts = gTTS(text, lang='ru')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    bot.send_voice(chat_id, mp3_fp)

# --- Обработчики ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_state[chat_id] = {'subject': None, 'task': None, 'awaiting_answer': False}
    send_subjects_keyboard(chat_id)

@bot.message_handler(func=lambda m: m.text in subjects)
def handle_subject(message):
    chat_id = message.chat.id
    subject = message.text
    user_state[chat_id]['subject'] = subject
    send_tasks_keyboard(chat_id, subject)

@bot.message_handler(func=lambda m: m.text.isdigit() and 1 <= int(m.text) <= 9)
def handle_task(message):
    chat_id = message.chat.id
    task_num = int(message.text)
    state = user_state[chat_id]
    state['task'] = task_num
    state['awaiting_answer'] = True
    task = variants[state['subject']]['Вариант 1'][str(task_num)]
    if task_num == 1:
        # Задание 1 — голосовое
        send_voice(chat_id, task['voice_text'])
        bot.send_message(chat_id, "Прослушайте голосовое сообщение, затем введите изложение (~40% текста).")
    else:
        bot.send_message(chat_id, f"{task['question']}", reply_markup=ReplyKeyboardRemove())
        bot.send_message(chat_id, "Введите ваш ответ:")

@bot.message_handler(func=lambda m: True)
def handle_answer(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id, {})
    if not state.get('awaiting_answer'):
        bot.send_message(chat_id, "Выберите задание через кнопки.")
        return
    task_num = state.get('task')
    task = variants[state['subject']]['Вариант 1'][str(task_num)]
    user_answer = message.text.strip().lower()
    correct_answer = task.get('answer', '').lower()
    if task_num == 1:
        # Проверка изложения по ключевым словам (упрощенно)
        keywords = ['места', 'значимыми', 'родной', 'улица', 'смысл', 'воспоминания']
        matched = sum(1 for kw in keywords if kw in user_answer)
        if matched >= max(1, len(keywords)//2):
            bot.send_message(chat_id, f"✅ Хорошо! Ваше изложение содержит достаточное количество ключевых идей ({matched}/{len(keywords)}).")
        else:
            bot.send_message(chat_id, f"⚠️ Недостаточно ключевых идей ({matched}/{len(keywords)}). Попробуйте добавить детали.")
    else:
        if user_answer == correct_answer:
            bot.send_message(chat_id, f"✅ Верно!\nРешение:\n{task['solution']}")
        else:
            bot.send_message(chat_id, f"❌ Неверно.\nПравильный ответ: {task['answer']}\nРешение:\n{task['solution']}")
    state['awaiting_answer'] = False
    send_tasks_keyboard(chat_id, state['subject'])

if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
