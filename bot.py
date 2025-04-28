import matplotlib
import telebot
import matplotlib.pyplot as plt
import numpy as np
import logging
from scipy.signal import find_peaks, peak_widths
from telebot import types

from Calc_classes.Vk_album import Vk_upload
from Calc_classes.WeatherHolder import WeatherHandler
from Calc_classes.MainCalc import ButtonCalc

logging.basicConfig(
    filename='bot_work.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

LaserPhysicHelpBot = telebot.TeleBot('') # токен лежит в тг
WEATHER_API_KEY = ''  # API ключ для погоды
ADMIN_ID = 0
matplotlib.use('agg') # это нужно для графика

# Чистка логов
def safe_log_clear():
    handlers = logging.getLogger().handlers[:]
    for handler in handlers:
        if isinstance(handler, logging.FileHandler):
            logging.getLogger().removeHandler(handler)
            handler.close()

    clear_log_file()

    file_handler = logging.FileHandler("bot_work.log", encoding="utf-8")
    logging.getLogger().addHandler(file_handler)


def clear_log_file():
    try:
        with open("bot_work.log", "w", encoding="utf-8") as f:
            f.truncate(0)  # Полная очистка файла
        print("Лог-файл успешно очищен")
    except Exception as e:
        print(f"Ошибка очистки лога: {str(e)}")


@LaserPhysicHelpBot.message_handler(commands=['clear_logs'])
def clear_log_command(message):
    if message.from_user.id == ADMIN_ID:
        clear_log_file()
        LaserPhysicHelpBot.reply_to(message, "Лог-файл очищен")
    else:
        LaserPhysicHelpBot.reply_to(message, "У вас нет прав на эту операцию")

user_states = {}

@LaserPhysicHelpBot.message_handler(commands=['start'])
def startBot(message):
    # это стартовое сообщение
    first_mess = (f"<b>{message.from_user.first_name} {message.from_user.last_name}</b>, "
                  f"привет!\nМой функционал можешь прочитать по нажатию кнопки."
                  f" Спасибо, что решил воспользоваться моими функциями :)")
    # создаются кнопки, для работы с ботом
    markup = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text='Описание', callback_data='description')
    button_energy = types.InlineKeyboardButton(text='Перевод энергии фотона в длину света',
                                               callback_data='translate')
    button_calc = types.InlineKeyboardButton(text="Посчитать строку", callback_data='calc')
    button_about_len = types.InlineKeyboardButton(text="О длине волны", callback_data="about_len")
    button_about_fluence = types.InlineKeyboardButton(text="Вычисление флюенса лазерной системы",
                                                      callback_data="fluence")
    resonance = types.InlineKeyboardButton(text="Показать график резонанса", callback_data="resonance")
    user_ans = types.InlineKeyboardButton(text="Написать отзыв о работе", callback_data="user_response")
    weather = types.InlineKeyboardButton(text="Показать погоду в городе", callback_data="weather")
    # добавление кнопок
    markup.add(button_yes, button_energy, button_calc, button_about_len,
               resonance, button_about_fluence, user_ans, weather, row_width=1)
    LaserPhysicHelpBot.send_message(message.chat.id, first_mess, parse_mode='html', reply_markup=markup)


# при случайном вводе текста, пишется ошибка
@LaserPhysicHelpBot.message_handler(content_types=['text'])
def Random_text(message):
    first_mess = "Используйте кнопки для правильной работы"
    text = str(message.text)
    # логируем сообщения
    logging.warning(f"Случайный текст пользователя: {text}")
    LaserPhysicHelpBot.send_message(message.chat.id, first_mess)


# Принимает только файл в формате example.txt
# О расчёте подробнее здесь: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.peak_widths.html
@LaserPhysicHelpBot.message_handler(content_types=['document'],
                                    func=lambda message: user_states.get(message.chat.id) == "waiting_for_txt")
def graphic_peak_widths(message):
    if not message.document.file_name.endswith('.txt'):
        LaserPhysicHelpBot.reply_to(message, "❌ Файл должен быть .txt!")
        return
    user_states.pop(message.chat.id, None)
    try:
        chat_id = message.chat.id
        file_info = LaserPhysicHelpBot.get_file(message.document.file_id)
        downloaded_file = LaserPhysicHelpBot.download_file(file_info.file_path).decode().strip('\r').strip('\n').split()
        x = np.array([float(i) for i in downloaded_file])
        peaks, _ = find_peaks(x)
        results_half = peak_widths(x, peaks, rel_height=0.5)
        results_full = peak_widths(x, peaks, rel_height=1)
        plt.plot(x)
        plt.plot(peaks, x[peaks], "x")
        plt.hlines(*results_half[1:], color="C2")
        plt.hlines(*results_full[1:], color="C3")
        plt.savefig("static/img/graph.png")
        LaserPhysicHelpBot.send_photo(chat_id, photo=open('static/img/graph.png', 'rb'))
        vk_conn.run()
    except Exception as e:
        LaserPhysicHelpBot.reply_to(message, f"⚠️ Ошибка: {str(e)}")


# Каждая функция принимает каждую отдельную кнопку, чтобы различать, что нужно считать.
# Она зациклена, то есть при получении сигнала от кнопки, снова проходится по этим if-ам.
@LaserPhysicHelpBot.callback_query_handler(func=lambda call: True)
def response(function_call):
    if function_call.message:
        # Описание
        if function_call.data == "description":
            second_mess = ("Что я могу:\n"
                           "1. Перевод некоторых физических величин\n"
                           "2. Вычислять положение резонанса по спектру\n"
                           "3. Вычислять флюенс лазерной системы по средней мощности\n"
                           "4. Показывать информацию о погоде города\n"
                           "5. Посчитать строковое выражение (степень вводиться через **)")
            LaserPhysicHelpBot.send_message(function_call.message.chat.id, second_mess)
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
        # Выбор перевода
        elif function_call.data == 'translate':
            second_mess = "Выберите перевод"
            button = types.InlineKeyboardMarkup()
            button_elv_to_nm = types.InlineKeyboardButton(text="эВ в длину волны", callback_data="elv_to_nm")
            button_nm_to_elv = types.InlineKeyboardButton(text="длина волны в эВ", callback_data="nm_to_elv")
            button_freq_to_nm = types.InlineKeyboardButton(text="частота в длину волны", callback_data="freq_to_nm")
            button_nm_to_freq = types.InlineKeyboardButton(text="длина волны в частоту", callback_data="nm_to_freq")
            button.add(button_elv_to_nm, button_nm_to_elv)
            button.add(button_freq_to_nm, button_nm_to_freq)
            LaserPhysicHelpBot.send_message(function_call.message.chat.id, second_mess, reply_markup=button)
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
        # Минимальный калькулятор
        elif function_call.data == 'calc':
            second_mess = "Введите строкой пример"
            msg = LaserPhysicHelpBot.send_message(function_call.message.chat.id, second_mess)
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
            LaserPhysicHelpBot.register_next_step_handler(msg, calc)
        # Выбор одно из переводов (см. функции по register_next_step_handler)
        elif function_call.data == 'elv_to_nm':
            msg = LaserPhysicHelpBot.send_message(function_call.message.chat.id, "Введите значение в эВ без степени")
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
            LaserPhysicHelpBot.register_next_step_handler(msg, translate_elv_to_nm)
        elif function_call.data == 'nm_to_elv':
            msg = LaserPhysicHelpBot.send_message(function_call.message.chat.id, "Введите значение в нм без степени")
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
            LaserPhysicHelpBot.register_next_step_handler(msg, translate_nm_to_elv)
        elif function_call.data == 'freq_to_nm':
            msg = LaserPhysicHelpBot.send_message(function_call.message.chat.id, "Введите значение в ТГц без степени")
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
            LaserPhysicHelpBot.register_next_step_handler(msg, translate_freq_to_nm)
        elif function_call.data == 'nm_to_freq':
            msg = LaserPhysicHelpBot.send_message(function_call.message.chat.id, "Введите значение в нм без степени")
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
            LaserPhysicHelpBot.register_next_step_handler(msg, translate_nm_to_freq)
        # Расчёт о длине волны
        elif function_call.data == 'about_len':
            msg = LaserPhysicHelpBot.send_message(function_call.message.chat.id, "Введите значение в нм без степени")
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
            LaserPhysicHelpBot.register_next_step_handler(msg, about_len)
        # Расчёт графика (см. тег content_types=['document'])
        elif function_call.data == 'resonance':
            user_states[function_call.message.chat.id] = "waiting_for_txt"
            LaserPhysicHelpBot.send_message(
                function_call.message.chat.id,
                "Отправьте файл в формате .txt, данные расположите в одну строку"
            )
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
        elif function_call.data == "fluence":
            button = types.InlineKeyboardMarkup()
            butt_flat_top = types.InlineKeyboardButton(text="C плоской вершиной", callback_data="flat-top")
            butt_gaussian = types.InlineKeyboardButton(text="Гауссовская", callback_data="gaussian")
            button.add(butt_flat_top, butt_gaussian, row_width=1)
            LaserPhysicHelpBot.send_message(function_call.message.chat.id, "Выберите тип лазерной системы",
                                       reply_markup=button)
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
        elif function_call.data == "flat-top":
            msg = LaserPhysicHelpBot.send_message(function_call.message.chat.id,
                                             "Введите мощность в МДж и площадь луча в мм")
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
            LaserPhysicHelpBot.register_next_step_handler(msg, flat_top)
        elif function_call.data == "gaussian":
            msg = LaserPhysicHelpBot.send_message(function_call.message.chat.id,
                                             "Введите мощность в МДж и площадь луча в мм")
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
            LaserPhysicHelpBot.register_next_step_handler(msg, gaussian)
        # Получение отзыва пользователя (перезаписывается, как новый отзыв)
        elif function_call.data == "user_response":
            temp_str = ("Расскажите, что вам понравилось в моей работе, а что нет, а также, "
                        "что хотели бы добавить в мою функционал")
            msg = LaserPhysicHelpBot.send_message(function_call.message.chat.id, temp_str)
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
            LaserPhysicHelpBot.register_next_step_handler(msg, remember_ans)
        # Получение погоды
        elif function_call.data == "weather":
            msg = LaserPhysicHelpBot.send_message(function_call.message.chat.id, "Введите название города:")
            LaserPhysicHelpBot.answer_callback_query(function_call.id)
            LaserPhysicHelpBot.register_next_step_handler(msg, get_weather)


def get_weather(message):
    try:
        handler = WeatherHandler(WEATHER_API_KEY)
        weather_data = handler.get_weather_data(message.text.strip())
        response = (
            f"🌍 Погода в городе {message.text.strip()}:\n\n"
            f"Сейчас ({weather_data['current']['time']}):\n"
            f"• Температура: {weather_data['current']['temp']}°C\n"
            f"• Ощущается как: {weather_data['current']['feels_like']}°C\n"
            f"• Описание: {weather_data['current']['description']}\n\n"
        )
        for i, period in enumerate(weather_data['forecast'][1:]):  # Пропускаем первый период (текущее время)
            response += (
                f"Через {(i + 1) * 3} часа ({period['time']}):\n"
                f"• Температура: {period['temp']}°C\n"
                f"• Ощущается как: {period['feels_like']}°C\n"
                f"• Описание: {period['description']}\n\n"
            )
        LaserPhysicHelpBot.send_message(message.chat.id, response)
    except ValueError as e:
        LaserPhysicHelpBot.send_message(message.chat.id, f"⚠️ {str(e)}")
    except Exception as e:
        LaserPhysicHelpBot.send_message(message.chat.id, f"⚠️ Произошла ошибка: {str(e)}")


def remember_ans(message):
    calc_for_buttons.write_an_comment(message.text, message.chat.id)
    response_bot = "Спасибо за ваш отзыв 💝!\nМой разработчик обязательно рассмотрит ваш отзыв."
    LaserPhysicHelpBot.send_message(message.chat.id, response_bot)

def flat_top(message):
    LaserPhysicHelpBot.send_message(message.chat.id, calc_for_buttons.flat_top(message))

def gaussian(message):
    LaserPhysicHelpBot.send_message(message.chat.id, calc_for_buttons.gaussian(message))

def translate_elv_to_nm(message):
    LaserPhysicHelpBot.send_message(message.chat.id, calc_for_buttons.translate_elv_to_nm(message))

def translate_nm_to_elv(message):
    LaserPhysicHelpBot.send_message(message.chat.id, calc_for_buttons.translate_nm_to_elv(message))

def translate_freq_to_nm(message):
    LaserPhysicHelpBot.send_message(message.chat.id, calc_for_buttons.translate_freq_to_nm(message))

def translate_nm_to_freq(message):
    LaserPhysicHelpBot.send_message(message.chat.id, calc_for_buttons.translate_nm_to_freq(message))

def calc(mess):
    try:
        LaserPhysicHelpBot.send_message(mess.chat.id, eval(mess.text))
    except ValueError as e:
        LaserPhysicHelpBot.send_message(mess.chat.id, str(e))

def about_len(message):
    try:
        lens = int(message.text)
        if lens < 380 or lens > 780:
            LaserPhysicHelpBot.send_message(message.chat.id, "Невидимая длина волны для человека")
        else:
            for cur_color in calc_for_buttons.color_ranges:
                start, end = calc_for_buttons.color_ranges[cur_color]
                if start <= lens <= end:
                    outer_str = (f"Вы спросили о длине волны {lens} нм. Это соответствует {cur_color} цвету\n"
                                 f"Прочитать больше можно по ссылке: https://astronomy.ru/forum/index.php/topic,50316.0.html")
                    LaserPhysicHelpBot.send_message(message.chat.id, outer_str)
                    break
    except ValueError:
        LaserPhysicHelpBot.send_message(message.chat.id, "Неправильный тип данных!")


if __name__ == "__main__":
    vk_conn = Vk_upload()
    calc_for_buttons = ButtonCalc()
    LaserPhysicHelpBot.infinity_polling()