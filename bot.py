import os
import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from gtts import gTTS
import threading

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)
user_state = {}

# --- Задания и текст ---
text_part2 = (
    "(1)Серёжа и его отец шли берегом моря, усыпанным крупной галькой. "
    "(2)День клонился к вечеру, и длинные тени падали от скал на песок. "
    "(3)Отец шёл молча, задумавшись, а Серёжа бросал в воду плоские камешки, стараясь пустить их по воде как можно дальше. "
    "(4)Вдруг он заметил необычный камень. "
    "(5)Он был тёмным, почти чёрным, но там, где его касались лучи заходящего солнца, вспыхивали яркие искры. "
    "(6)Мальчик поднял его и ахнул от удивления: это был кусок твёрдого смолистого вещества. "
    "(7)«Папа, смотри, янтарь!» — крикнул он. "
    "(8)Отец взял в руки находку, внимательно рассмотрел её и улыбнулся. "
    "(9)«Нет, сынок, это не янтарь. "
    "(10)Это морской смольё, или гагат. "
    "(11)Его иногда называют чёрным янтарём, но это совсем другой минерал. "
    "(12)Он тоже тёплый на ощупь и очень красив, если его отполировать». "
    "(13)Серёжа немного расстроился, но потом разглядел в глубине камня какой-то отблеск. "
    "(14)«А можно мы его заберём с собой?» — спросил он. "
    "(15)«Конечно, — ответил отец. "
    "(16)— Из него может получиться отличный талисман на память о сегодняшнем дне». "
    "(17)Они положили камень в карман и пошли дальше, а море по-прежнему шумело, накатывая на берег волну за волной."
)

variants = {
    'Русский язык': {
        'Вариант 1': {
            '1': {  # Задание 1 — голосовое
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
            '2': {'question': f'{text_part2}\n\nЗадание 2. Почему Серёжа сначала решил, что нашёл янтарь?\n'
                              '1. Камень был похож на смолу и блестел на солнце.\n'
                              '2. Отец мальчика был экспертом.\n'
                              '3. Камень лежал среди обычной гальки.\n'
                              '4. Мальчик давно мечтал найти именно янтарь.',
                  'solution': 'В предложении 5 камень блестел на солнце.',
                  'answer': '1'},
            '3': {'question': f'{text_part2}\n\nЗадание 3. Укажите вариант со сравнением (1–4)\n'
                              '1. День клонился к вечеру.\n'
                              '2. Он был тёмным, почти чёрным.\n'
                              '3. Они положили камень в карман.\n'
                              '4. Он, как верный друг, всегда готов был подарить чувство защищённости.',
                  'solution': 'Сравнение присутствует в варианте 4: "как верный друг".',
                  'answer': '4'},
            '4': {'question': f'{text_part2}\n\nЗадание 4. В каком слове приставка перед глухим согласным?\n1. расстроился\n2. внимательно\n3. отполировать\n4. вспыхивали',
                  'solution': 'Приставка РАС- пишется перед глухим согласным (слово «расстроился»).',
                  'answer': '1'},
            '5': {'question': f'{text_part2}\n\nЗадание 5. В каком слове наречие с приставкой ИЗ-, ДО-, С-?\n1. задумавшись\n2. издалека\n3. внимательно\n4. по-прежнему',
                  'solution': 'В слове «издалека» есть приставка ИЗ- и суффикс -А.',
                  'answer': '2'},
            '6': {'question': f'{text_part2}\n\nЗадание 6. Замените разговорное слово «ахнул» стилистически нейтральным синонимом.',
                  'solution': 'воскликнул или удивился',
                  'answer': 'воскликнул'},
            '7': {'question': f'{text_part2}\n\nЗадание 7. Замените словосочетание «морской смольё» на управление.',
                  'solution': 'смольё моря',
                  'answer': 'смольё моря'},
            '8': {'question': f'{text_part2}\n\nЗадание 8. Выпишите грамматическую основу предложения 13.',
                  'solution': 'Серёжа расстроился, разглядел отблеск',
                  'answer': 'Серёжа расстроился, разглядел отблеск'},
            '9': {'question': f'{text_part2}\n\nЗадание 9. Среди предложений 7–12 найдите предложение с обособленным обстоятельством.',
                  'solution': 'Обособленных обстоятельств нет',
                  'answer': 'нет'}
        }
    }
}

subjects = list(variants.keys())

# --- Генерация голосового файла для Задания 1 ---
tts_file = "exposition.ogg"
if not os.path.exists(tts_file):
    tts = gTTS(variants['Русский язык']['Вариант 1']['1']['voice_text'], lang='ru')
    tts.save(tts_file)

def send_voice_repeating(chat_id, delay=300):
    """Отправка голосового сообщения и повтор через delay секунд."""
    with open(tts_file, 'rb') as f:
        bot.send_voice(chat_id, f)
    threading.Timer(delay, lambda: send_voice_repeating(chat_id, delay)).start()

# --- Клавиатуры ---
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
    state['awaiting_answer'] = False
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Задание 1')
    markup.row('Часть 2')
    bot.send_message(chat_id, "Выберите Задание 1 или Часть 2 (задания 2–9):", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id, {})

    # Ожидаем ответ
    if state.get('awaiting_answer') and 'task_num' in state:
        subject = state['subject']
        variant = state['variant']
        task_num = state['task_num']
        task = variants[subject][variant][task_num]
        user_answer = message.text.strip().lower()
        correct_answer = task.get('answer','').strip().lower()
        if user_answer == correct_answer:
            bot.send_message(chat_id, f"✅ Верно!\nРешение:\n{task['solution']}")
        else:
            bot.send_message(chat_id, f"❌ Неверно.\nПравильный ответ: {task['answer']}\nРешение:\n{task['solution']}")
        state['awaiting_answer'] = False
        del state['task_num']
        # Возврат к выбору Задание 1 / Часть 2
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
        state['awaiting
