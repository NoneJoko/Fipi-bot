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

# ----- Данные: Русский язык + Математика -----
text_part2_rus = (
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
            '2': {'question': text_part2_rus + "\n\nЗадание 2. Почему Серёжа сначала решил, что нашёл янтарь?\n1) Камень был похож на смолу и блестел на солнце\n2) Отец мальчика был экспертом по минералам\n3) Камень лежал среди обычной гальки\n4) Мальчик давно мечтал найти именно янтарь",
                  'solution': "В предложении 5 камень блестел на солнце → Серёжа решил, что это янтарь. Ответ: 1", 'answer':'1'},
            '3': {'question': text_part2_rus + "\n\nЗадание 3. Укажите вариант, в котором средством выразительности речи является сравнение.\n1) День клонился к вечеру, и длинные тени падали от скал на песок\n2) Он был тёмным, почти чёрным, но там, где его касались лучи заходящего солнца, вспыхивали яркие искры\n3) Они положили камень в карман и пошли дальше, а море по-прежнему шумело, накатывая на берег волну за волной\n4) Он, как верный друг, всегда готов был подарить чувство защищённости",
                  'solution': "Сравнение в варианте 4. Ответ: 4", 'answer':'4'},
            '4': {'question': "Задание 4. В каком слове правописание приставки определяется правилом: «Если после приставки следует глухой согласный, то на конце её пишется -С»?\n1) расстроился\n2) внимательно\n3) отполировать\n4) вспыхивали",
                  'solution': "Правильный ответ: 'расстроился'", 'answer':'1'},
            '5': {'question': "Задание 5. В каком слове правописание суффикса определяется правилом: «В наречиях, образованных от прилагательных с помощью приставок ИЗ-, ДО-, С-, пишется суффикс -А»?\n1) задумавшись\n2) издалека\n3) внимательно\n4) по-прежнему",
                  'solution': "Правильный ответ: 'издалека'. Ответ: 2", 'answer':'2'},
            '6': {'question': "Задание 6. Замените разговорное слово «ахнул» (предложение 6) стилистически нейтральным синонимом. Напишите один нейтральный синоним.",
                  'solution': "Например: 'воскликнул' или 'удивился'.", 'answer': ['воскликнул', 'удивился']},
            '7': {'question': "Задание 7. Замените словосочетание «морской смольё» (предложение 10) с согласованием на синонимичное со связью управление.",
                  'solution': "Ответ: 'смольё моря'.", 'answer':'смольё моря'},
            '8': {'question': "Задание 8. Выпишите грамматическую основу предложения 13: «Серёжа немного расстроился, но потом разглядел в глубине камня какой-то отблеск».",
                  'solution': "Грамматические основы: 'Серёжа расстроился' и '(он) разглядел отблеск'.", 'answer':'серёжа расстроился, разглядел отблеск'},
            '9': {'question': "Задание 9. Среди предложений 7–12 найдите предложение с обособленным обстоятельством. Напишите номер или 'нет'.",
                  'solution': "Обособленного обстоятельства нет. Ответ: нет", 'answer':'нет'}
        }
    },
    'Математика': {
        'Вариант 1': {
            # Часть 1
            '1': {'question': "Вычислите: -12 + 15 - 8", 'solution': "-12+15=3; 3-8=-5", 'answer':'-5'},
            '2': {'question': "На координатной прямой отмечены точки A(5,0), B(5,2), C(5,5), D(5,7). Одна из точек соответствует числу 56/11. Какая?\n1) A 2) B 3) C 4) D",
                  'solution': "56/11 ≈5,09 → точка A", 'answer':'1'},
            '3': {'question': "Какое число принадлежит промежутку [7;8]?\n1) √7 2) √51 3) √61 4) √69",
                  'solution': "√61 ≈7,81 ∈ [7;8]. Ответ: 3", 'answer':'3'},
            '4': {'question': "Найдите значение выражения 4x-(6x-13) при x=1,5", 'solution': "10", 'answer':'10'},
            '5': {'question': "Соответствие промежутков функции: А) возрастает Б) убывает. Промежутки: 1)[-2;1] 2)[-1;1] 3)[1;3] 4)[0;3]. Впишите цифры: А-?, Б-?",
                  'solution': "А-3, Б-1", 'answer':'3,1'},
            '6': {'question': "Арифметическая прогрессия 3,7,11,... Найдите a11", 'solution': "a11=43", 'answer':'43'},
            '7': {'question': "Упростите (5a²-5b²)/(a²-ab) : 5(a+b)/a при a=1.2,b=0.2", 'solution': "1", 'answer':'1'},
            '8': {'question': "Решите x²-3x-18=0. Если два корня, дайте больший", 'solution': "6", 'answer':'6'},
            '9': {'question': "Треугольник ABC, C=90°, AC=12, sin A=2/3. Найдите AB", 'solution': "AB=36/√5", 'answer':'36/√5'},
            '10': {'question': "В окружности с центром O, диаметры AD и BC, угол ABO=75°. Найдите ODC", 'solution': "75°", 'answer':'75'},
            '11': {'question': "Площадь трапеции с основаниями 5 и 9, высотой 4", 'solution': "S=28", 'answer':'28'},
            '12': {'question': "Треугольник на клетках, катеты 4 и 5. Площадь?", 'solution': "S=10", 'answer':'10'},
            '13': {'question': "Какие утверждения верны?\n1)Площадь квадрата = произведение диагоналей\n2)Сумма острых углов прямоугольного треугольника=90°\n3)Любой равнобедренный треугольник остроугольный\nВ ответ: номера верных", 'solution': "2", 'answer':'2'},
            '14': {'question': "Сколько учеников получили балл по математике выше, чем по физике?", 'solution': "8", 'answer':'8'},
            '15': {'question': "В 200 г творога жир 15%. Сколько г жиров?", 'solution': "30", 'answer':'30'},
            '16': {'question': "20 пазлов: 15 с машинами, 5 с городами. Вероятность для Маши?", 'solution': "0,75", 'answer':'0,75'},
            '17': {'question': "Разность температуры по графику: макс=12°, мин=2°", 'solution': "10", 'answer':'10'},
            '18': {'question': "Проезд: 4 взрослых + 12 школьников. Стоимость?", 'solution': "1980", 'answer':'1980'},
            '19': {'question': "Два участка 30*40 м, бассейн 100 м². Свободная площадь?", 'solution': "2300", 'answer':'2300'},
            # Часть 2
            '20': {'question': "Система: x²+y²=25, xy=12. Решите", 'solution': "x=3,y=4 или x=4,y=3", 'answer':'x=3,y=4 или x=4,y=3'},
            '21': {'question': "Три велосипедиста. Найдите скорость третьего.", 'solution': "v3=20", 'answer':'20'},
            '22': {'question': "График y=(x²+2x+1)(x+3)/(x+1). m: y=m ровно 1 точка", 'solution': "m=0,-1", 'answer':'0,-1'},
            '23': {'question': "Прямоугольная трапеция AB=12, CD=13, AD=16. Найдите BH к CD", 'solution': "BH≈5,2", 'answer':'5,2'},
            '24': {'question': "В остроугольном ABC высоты BB₁, CC₁. Докажите BB₁C₁=BCC₁", 'solution': "равны", 'answer':'равны'},
            '25': {'question': "Треугольник ABC, точка D на AC: AB=BD=DC, угол ABC=30°. Найдите углы ABC", 'solution': "30°,75°,75°", 'answer':'30,75,75'}
        }
    }
}

subjects = list(variants.keys())

# ----- Вспомогательные функции -----
def send_voice(chat_id, text):
    tts = gTTS(text=text, lang='ru')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    bot.send_voice(chat_id, fp)

def check_answer(user_ans, correct):
    if isinstance(correct, list):
        return user_ans.lower() in [c.lower() for c in correct]
    else:
        return user_ans.lower() == str(correct).lower()

# ----- Старт бота -----
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for sub in subjects:
        markup.add(sub)
    bot.send_message(chat_id, "Выберите предмет:", reply_markup=markup)
    user_state[chat_id] = {}

# ----- Выбор предмета -----
@bot.message_handler(func=lambda m: m.chat.id in user_state and 'subject' not in user_state[m.chat.id])
def choose_subject(message):
    chat_id = message.chat.id
    subject = message.text
    if subject not in subjects:
        bot.send_message(chat_id, "Выберите предмет с клавиатуры")
        return
    user_state[chat_id]['subject'] = subject
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for variant in variants[subject]:
        markup.add(variant)
    bot.send_message(chat_id, f"Выберите вариант для {subject}:", reply_markup=markup)

# ----- Выбор варианта -----
@bot.message_handler(func=lambda m: m.chat.id in user_state and 'variant' not in user_state[m.chat.id])
def choose_variant(message):
    chat_id = message.chat.id
    variant = message.text
    subject = user_state[chat_id]['subject']
    if variant not in variants[subject]:
        bot.send_message(chat_id, "Выберите вариант с клавиатуры")
        return
    user_state[chat_id]['variant'] = variant
    user_state[chat_id]['task'] = None
    send_task(chat_id)

# ----- Отправка задания -----
def send_task(chat_id):
    subject = user_state[chat_id]['subject']
    variant = user_state[chat_id]['variant']
    if subject == 'Русский язык' and 'task' not in user_state[chat_id]:
        user_state[chat_id]['task'] = '1'
    if user_state[chat_id]['task'] is None:
        user_state[chat_id]['task'] = '1'
    task_num = user_state[chat_id]['task']
    task = variants[subject][variant][task_num]
    
    if subject == 'Русский язык' and task_num == '1':
        # Голосовое сообщение дважды через 5 минут
        def send_twice():
            send_voice(chat_id, task['voice_text'])
            threading.Timer(300, lambda: send_voice(chat_id, task['voice_text'])).start()
        threading.Thread(target=send_twice).start()
        bot.send_message(chat_id, f"Задание 1: прослушайте текст, затем введите ответ (текст).")
        user_state[chat_id]['awaiting_answer'] = True
    else:
        bot.send_message(chat_id, f"Задание {task_num}: {task.get('question','нет текста')}")
        user_state[chat_id]['awaiting_answer'] = True

# ----- Проверка ответа -----
@bot.message_handler(func=lambda m: m.chat.id in user_state and user_state[m.chat.id].get('awaiting_answer', False))
def answer_task(message):
    chat_id = message.chat.id
    user_ans = message.text.strip()
    state = user_state[chat_id]
    subject = state['subject']
    variant = state['variant']
    task_num = state['task']
    task = variants[subject][variant][task_num]
    
    if check_answer(user_ans, task['answer']):
        bot.send_message(chat_id, "✅ Верно!")
    else:
        bot.send_message(chat_id, f"❌ Неверно. Решение: {task['solution']}")
    
    # Переход к следующему задания
    next_task_num = str(int(task_num)+1)
    if next_task_num in variants[subject][variant]:
        state['task'] = next_task_num
        state['awaiting_answer'] = False
        send_task(chat_id)
    else:
        bot.send_message(chat_id, "Все задания завершены.", reply_markup=ReplyKeyboardRemove())
        state.clear()

bot.infinity_polling()
