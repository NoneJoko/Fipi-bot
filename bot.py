import os
import telebot
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise SystemExit("Environment variable TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

# Хранение состояния пользователей
user_state = {}

# Полные задания Русского языка, Вариант 1
variants = {
    'Русский язык': {
        'Вариант 1': {
            '1': {
                'question': (
                    "Часть 1. Изложение\n\n"
                    "Задание 1. Прослушайте текст и напишите сжатое изложение.\n\n"
                    "Текст для аудирования:\n"
                    "«У каждого из нас есть места, которые становятся особенными, наполняясь глубоким личным смыслом. "
                    "Для кого-то это родной дом, где прошло детство, для другого — старая улица, хранящая память о важных встречах. "
                    "Такие места обладают удивительной силой: они способны вернуть нас в прошлое, напомнить о пережитом, заставить задуматься о будущем. "
                    "Часто именно с этими уголками связаны наши самые тёплые воспоминания. Мы мысленно возвращаемся туда в трудные минуты, ища поддержки и утешения. "
                    "Они, как верные друзья, всегда готовы подарить нам чувство защищённости и душевного покоя. "
                    "Важно сохранять в памяти эти островки нашего личного счастья. Они помогают нам оставаться собой, не забывать о своих корнях и истинных ценностях в стремительном потоке жизни»."
                ),
                'solution': (
                    "Пример изложения: У каждого человека есть особенные места, наполненные глубоким личным смыслом. "
                    "Это может быть родной дом или улица, хранящая память о важных событиях. "
                    "Такие места обладают силой возвращать нас в прошлое и заставлять задуматься о будущем. "
                    "С ними часто связаны тёплые воспоминания. Мы мысленно возвращаемся туда в трудные минуты, находя поддержку и утешение. "
                    "Эти места дарят чувство защищённости и покоя. "
                    "Важно хранить в памяти эти островки счастья. Они помогают нам оставаться собой, помнить о корнях и истинных ценностях."
                ),
                'answer': 'сделано'
            },
            '2': {
                'question': (
                    "Задание 2. В каком варианте ответа содержится информация, необходимая для обоснования "
                    "ответа на вопрос: «Почему Серёжа сначала решил, что нашёл янтарь?»\n\n"
                    "1. Камень был похож на смолу и блестел на солнце.\n"
                    "2. Отец мальчика был экспертом по минералам.\n"
                    "3. Камень лежал среди обычной гальки.\n"
                    "4. Мальчик давно мечтал найти именно янтарь."
                ),
                'solution': "В предложении 5 описывается камень, который блестел на солнце, что вызвало ассоциацию с янтарём.",
                'answer': '1'
            },
            '3': {
                'question': (
                    "Задание 3. Укажите вариант, в котором средством выразительности речи является сравнение.\n\n"
                    "1. День клонился к вечеру, и длинные тени падали от скал на песок.\n"
                    "2. Он был тёмным, почти чёрным, но там, где его касались лучи заходящего солнца, вспыхивали яркие искры.\n"
                    "3. Они положили камень в карман и пошли дальше, а море по-прежнему шумело, накатывая на берег волну за волной.\n"
                    "4. Он, как верный друг, всегда готов был подарить чувство защищённости."
                ),
                'solution': 'Сравнение встречается в варианте 4: "как верный друг".',
                'answer': '4'
            },
            '4': {
                'question': (
                    "Задание 4. В каком слове правописание приставки определяется правилом: "
                    "«Если после приставки следует глухой согласный, то на конце её пишется -С»?\n\n"
                    "1. расстроился\n2. внимательно\n3. отполировать\n4. вспыхивали"
                ),
                'solution': 'Приставка РАС- пишется перед глухим согласным (слово «расстроился»).',
                'answer': '1'
            },
            '5': {
                'question': (
                    "Задание 5. В каком слове правописание суффикса определяется правилом: "
                    "«В наречиях, образованных от прилагательных с помощью приставок ИЗ-, ДО-, С-, пишется суффикс -А»?\n\n"
                    "1. задумавшись\n2. издалека\n3. внимательно\n4. по-прежнему"
                ),
                'solution': 'В слове «издалека» есть приставка ИЗ- и суффикс -А.',
                'answer': '2'
            },
            '6': {
                'question': "Задание 6. Замените разговорное слово «ахнул» стилистически нейтральным синонимом.",
                'solution': 'воскликнул или удивился',
                'answer': 'воскликнул'
            },
            '7': {
                'question': "Задание 7. Замените словосочетание «морской смольё» с согласования на управление.",
                'solution': 'смольё моря',
                'answer': 'смольё моря'
            },
            '8': {
                'question': "Задание 8. Выпишите грамматическую основу предложения 13.",
                'solution': 'Серёжа расстроился, разглядел отблеск',
                'answer': 'Серёжа расстроился, разглядел отблеск'
            },
            '9': {
                'question': "Задание 9. Среди предложений 7–12 найдите предложение с обособленным обстоятельством.",
                'solution': 'В данных предложениях обособленных обстоятельств нет.',
                'answer': 'нет'
            }
        }
    }
}

subjects = list(variants.keys())

# Кнопки предметов
def send_subjects_keyboard(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(subjects), 2):
        markup.row(*subjects[i:i+2])
    bot.send_message(chat_id, "Выберите предмет:", reply_markup=markup)

# Кнопки вариантов
def send_variants_keyboard(chat_id, subject):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for v in variants[subject].keys():
        markup.row(v)
    bot.send_message(chat_id, f"Выберите вариант для {subject}:", reply_markup=markup)

# Кнопки заданий
def send_tasks_keyboard(chat_id, subject, variant):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for t in variants[subject][variant].keys():
        markup.row(str(t))
    markup.row('Назад')
    bot.send_message(chat_id, f"{subject} - {variant}: выберите задание", reply_markup=markup)

# Старт
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
