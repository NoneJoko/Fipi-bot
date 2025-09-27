# coding: utf-8
import os
import io
import threading
import re
import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from gtts import gTTS

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

# ----- Состояние пользователей -----
user_state = {}  # chat_id -> {'subject','variant','task', 'awaiting_answer':bool}

# ----- Данные: Вариант 1 (Русский язык), задания 1-9 -----
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
            '1': {
                'voice_text': (
                    "У каждого из нас есть места, которые становятся особенными, "
                    "наполняясь глубоким личным смыслом. Для кого-то это родной дом, "
                    "для другого — старая улица, хранящая память о важных встречах. "
                    "Такие места обладают удивительной силой: они способны вернуть нас в прошлое, "
                    "напомнить о пережитом и заставить задуматься о будущем. Часто именно с этими уголками связаны наши самые тёплые воспоминания."
                ),
                'solution': "Пример сжатого изложения: выделите 3 микротемы (особенные места; их сила; важность сохранения памяти).",
                'answer': 'сделано'
            },
            '2': {
                'question': text_part2 + "\n\nЗадание 2. Почему Серёжа сначала решил, что нашёл янтарь?\n"
                                        "1. Камень был похож на смолу и блестел на солнце.\n"
                                        "2. Отец мальчика был экспертом по минералам.\n"
                                        "3. Камень лежал среди обычной гальки.\n"
                                        "4. Мальчик давно мечтал найти именно янтарь.",
                'solution': "В предложении 5 камень блестел на солнце, поэтому Серёжа решил, что это янтарь. Ответ: 1",
                'answer': '1'
            },
            '3': {
                'question': text_part2 + "\n\nЗадание 3. Укажите вариант, в котором средством выразительности речи является сравнение.\n"
                                        "1. День клонился к вечеру, и длинные тени падали от скал на песок.\n"
                                        "2. Он был тёмным, почти чёрным, но там, где его касались лучи заходящего солнца, вспыхивали яркие искры.\n"
                                        "3. Они положили камень в карман и пошли дальше, а море по-прежнему шумело, накатывая на берег волну за волной.\n"
                                        "4. Он, как верный друг, всегда готов был подарить чувство защищённости.",
                'solution': "Сравнение употреблено в варианте 4: 'Он, как верный друг...'. Ответ: 4",
                'answer': '4'
            },
            '4': {
                'question': "Задание 4. В каком слове правописание приставки определяется правилом: "
                            "«Если после приставки следует глухой согласный, то на конце её пишется -С»?\n"
                            "1. расстроился\n2. внимательно\n3. отполировать\n4. вспыхивали",
                'solution': "Правильный ответ: 'расстроился' (приставка РАС- перед глухим согласным).",
                'answer': '1'
            },
            '5': {
                'question': "Задание 5. В каком слове правописание суффикса определяется правилом: "
                            "«В наречиях, образованных от прилагательных с помощью приставок ИЗ-, ДО-, С-, пишется суффикс -А»?\n"
                            "1. задумавшись\n2. издалека\n3. внимательно\n4. по-прежнему",
                'solution': "Правильный ответ: 'издалека'. Ответ: 2",
                'answer': '2'
            },
            '6': {
                'question': "Задание 6. Замените разговорное слово «ахнул» (предложение 6) стилистически нейтральным синонимом. Напишите один нейтральный синоним.",
                'solution': "Например: 'воскликнул' или 'удивился'.",
                'answer': ['воскликнул', 'удивился']
            },
            '7': {
                'question': "Задание 7. Замените словосочетание «морской смольё» (предложение 10), построенное на согласовании, синонимичным словосочетанием со связью управление. Напишите получившееся словосочетание.",
                'solution': "Ответ: 'смольё моря'.",
                'answer': 'смольё моря'
            },
            '8': {
                'question': "Задание 8. Выпишите грамматическую основу предложения 13: "
                            "«Серёжа немного расстроился, но потом разглядел в глубине камня какой-то отблеск».",
                'solution': "Грамматические основы: 'Серёжа расстроился' и '(он) разглядел отблеск'.",
                'answer': 'серёжа расстроился, разглядел отблеск'
            },
            '9': {
                'question': "Задание 9. Среди предложений 7–12 найдите предложение с обособленным обстоятельством. Напишите номер этого предложения или 'нет', если такого нет.",
                'solution': "В данном фрагменте обособленного обстоятельства нет. Ответ: нет",
                'answer': 'нет'
            }
        }
    }
}

subjects = list(variants.keys())

# ----- Утилиты: нормализация и проверка -----
def normalize_text(s: str) -> str:
    s = s or ''
    s = s.strip().lower()
    s = s.replace('ё', 'е')
    s = re.sub(r'\s+', ' ', s)
    s = s.strip(' .,-–—()[]{}"\'')
    return s

def numeric_from_text(s: str):
    m = re.search(r'\b([1-9])\b', s)
    return m.group(1) if m else None

def check_answer(user_answer_raw: str, correct):
    ua = normalize_text(user_answer_raw)
    # if correct is list
    if isinstance(correct, (list, tuple)):
        for c in correct:
            if normalize_text(c) == ua:
                return True, ', '.join(correct)
        for c in correct:
            key = normalize_text(c)
            if key in ua:
                return True, ', '.join(correct)
        return False, ', '.join(correct)
    # numeric expected
    if re.fullmatch(r'\d', str(correct)):
        num = numeric_from_text(user_answer_raw) or ua
        if num == str(correct):
            return True, str(correct)
        return False, str(correct)
    # textual expected
    corr = normalize_text(str(correct))
    if ua == corr:
        return True, corr
    corr_words = [w for w in re.split(r'\W+', corr) if w]
    if corr_words:
        matched = sum(1 for w in corr_words if w in ua)
        if matched >= max(1, len(corr_words)//2):
            return True, corr
    return False, corr

# ----- Клавиатуры -----
def send_subjects_keyboard(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(subjects), 2):
        markup.row(*subjects[i:i+2])
    bot.send_message(chat_id, "Выберите предмет:", reply_markup=markup)

def send_tasks_keyboard(chat_id, subject):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    # 1..9 в ряды по 3
    row = []
    for i in range(1, 10):
        row.append(str(i))
        if len(row) == 3:
            markup.row(*row)
            row = []
    if row:
        markup.row(*row)
    markup.row('Назад')
    bot.send_message(chat_id, f"{subject}: выберите задание (1–9):", reply_markup=markup)

# ----- TTS + отправка voice note + автоудаление по длительности -----
def send_voice_autodelete(chat_id, text):
    """Отправляет voice note из текста (gTTS -> BytesIO), планирует удаление через duration+1s и возвращает Message."""
    tts = gTTS(text, lang='ru')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    msg = bot.send_voice(chat_id, fp)
    try:
        duration = msg.voice.duration or 0
    except Exception:
        duration = 0
    delay = int(duration) + 1  # запас 1 сек
    # планируем удаление
    threading.Timer(delay, lambda: safe_delete(chat_id, msg.message_id)).start()
    return msg

def safe_delete(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except Exception:
        pass  # игнорируем ошибки удаления

# ----- Логика: отправка первого voice, через 5 минут второй, после второго ждать окончания и разрешить ввод -----
def task1_playback_sequence(chat_id, voice_text):
    # первая отправка
    send_voice_autodelete(chat_id, voice_text)
    bot.send_message(chat_id, "Голосовое 1/2 отправлено — прослушайте полностью.")
    # вторая отправка через 5 минут
    def send_second():
        msg = send_voice_autodelete(chat_id, voice_text)
        bot.send_message(chat_id, "Голосовое 2/2 отправлено — после полного прослушивания вы сможете ввести изложение.")
        # определить длительность и через неё разрешить ввод
        try:
            dur = msg.voice.duration or 0
        except Exception:
            dur = 0
        # wait dur seconds + 1s buffer, затем разрешить ввод
        threading.Timer(int(dur) + 1, lambda: enable_answer_after_play(chat_id)).start()
    threading.Timer(300, send_second).start()  # 300s = 5 минут

def enable_answer_after_play(chat_id):
    st = user_state.get(chat_id)
    if not st:
        return
    st['awaiting_answer'] = True
    bot.send_message(chat_id, "Теперь введите сжатое изложение (примерно 40% текста), сохранив смысл.")

# ----- Обработчики -----
@bot.message_handler(commands=['start'])
def cmd_start(message):
    chat_id = message.chat.id
    user_state[chat_id] = {'subject': None, 'variant': 'Вариант 1', 'task': None, 'awaiting_answer': False}
    send_subjects_keyboard(chat_id)

@bot.message_handler(func=lambda m: m.text in subjects)
def on_choose_subject(message):
    chat_id = message.chat.id
    st = user_state.setdefault(chat_id, {'variant': 'Вариант 1', 'task': None, 'awaiting_answer': False})
    st['subject'] = message.text
    st['variant'] = 'Вариант 1'
    st['task'] = None
    st['awaiting_answer'] = False
    send_tasks_keyboard(chat_id, st['subject'])

@bot.message_handler(func=lambda m: m.text == 'Назад')
def on_back(message):
    chat_id = message.chat.id
    st = user_state.get(chat_id)
    if not st or not st.get('subject'):
        send_subjects_keyboard(chat_id)
    else:
        send_tasks_keyboard(chat_id, st['subject'])

@bot.message_handler(func=lambda m: m.text.isdigit() and 1 <= int(m.text) <= 9)
def on_choose_task(message):
    chat_id = message.chat.id
    st = user_state.get(chat_id)
    if not st or not st.get('subject'):
        bot.send_message(chat_id, "Сначала выберите предмет.")
        return
    # если уже ожидается ответ (пользователь ещё не ответил), не перезапускать выбор задания
    if st.get('awaiting_answer'):
        bot.send_message(chat_id, "Сначала введите ответ на текущее задание или нажмите 'Назад'.")
        return
    task_num = str(int(message.text))
    st['task'] = task_num
    st['awaiting_answer'] = False  # станет True либо сразу (для текстовых заданий) либо позже (для 1-го)
    task = variants[st['subject']][st['variant']].get(task_num)
    if not task:
        bot.send_message(chat_id, "Задание отсутствует.")
        return
    if task_num == '1':
        # запустить последовательность: отправка 1-го voice, через 5 минут второй, затем разрешение ответа
        task1_playback_sequence(chat_id, task['voice_text'])
        bot.send_message(chat_id, "Запущена последовательность воспроизведения задания 1 (2 раза).")
    else:
        # показываем полный текст задания и сразу ждём ответ
        st['awaiting_answer'] = True
        bot.send_message(chat_id, task.get('question', 'Условие отсутствует.'), reply_markup=ReplyKeyboardRemove())
        bot.send_message(chat_id, "Введите ваш ответ (для вариантов — введите номер 1/2/3/4):")

@bot.message_handler(func=lambda m: True)
def on_answer(message):
    chat_id = message.chat.id
    st = user_state.get(chat_id)
    if not st or not st.get('subject'):
        bot.send_message(chat_id, "Сначала выберите предмет и задание.")
        return
    if not st.get('awaiting_answer'):
        bot.send_message(chat_id, "Сначала выберите задание (1–9).")
        return
    task_num = st.get('task')
    if not task_num:
        bot.send_message(chat_id, "Ошибка состояния — выберите задание заново.")
        st['awaiting_answer'] = False
        return
    task = variants[st['subject']][st['variant']].get(task_num)
    if not task:
        bot.send_message(chat_id, "Задание отсутствует.")
        st['awaiting_answer'] = False
        return

    user_ans = message.text.strip()
    if task_num == '1':
        # простая смысловая проверка для изложения: ключевые корни
        keys = ['мест', 'родн', 'улиц', 'смысл', 'воспомин', 'поддерж']
        ua = normalize_text(user_ans)
        matched = sum(1 for k in keys if k in ua)
        threshold = max(1, int(len(keys) * 0.4))  # ~40% ключей
        if matched >= threshold:
            bot.send_message(chat_id, f"✅ Хорошо — найдено ключевых идей: {matched}/{len(keys)}.\n{task.get('solution')}")
        else:
            bot.send_message(chat_id, f"⚠️ Ключевых идей недостаточно: {matched}/{len(keys)}. Попробуйте дополнить изложение.\n{task.get('solution')}")
    else:
        ok, expected = check_answer(user_ans, task.get('answer'))
        if ok:
            bot.send_message(chat_id, f"✅ Верно.\nРешение:\n{task.get('solution')}")
        else:
            bot.send_message(chat_id, f"❌ Неверно.\nПравильный ответ: {expected}\nРешение:\n{task.get('solution')}")

    # После проверки возвращаем клавиатуру с заданиями (и сбрасываем состояние)
    st['awaiting_answer'] = False
    st['task'] = None
    send_tasks_keyboard(chat_id, st['subject'])

# ----- Запуск -----
if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
