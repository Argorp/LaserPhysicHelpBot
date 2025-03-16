import matplotlib
import telebot
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import chirp, find_peaks, peak_widths

PhysicHelpBot = telebot.TeleBot('?')

from telebot import types

"""Константы"""
light_speed = 3 * 10 ** 8  # м / с
h_const = 6.64 * 10 ** -34  # Дж / с
one_el_v = 1.602176634 * 10 ** -19  # эВ -> Дж
one_TGz = 10 ** 12  # 1 ТГц -> 10^12 Гц
pi = 3.141592653589793238462643383279502884
coff_for_fluence = 1
matplotlib.use('agg')


@PhysicHelpBot.message_handler(commands=['start'])
def startBot(message):
    first_mess = (f"<b>{message.from_user.first_name} {message.from_user.last_name}</b>, привет!\nМой функционал можешь прочитать по нажатию кнопки."
                  f" Спасибо, что решил воспользоваться моими функциями")
    markup = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text='Описание', callback_data='description')
    button_energy = types.InlineKeyboardButton(text='Перевод энергии фотона в длину света',
                                               callback_data='translate')
    button_calc = types.InlineKeyboardButton(text="Посчитать строку", callback_data='calc')
    button_about_len = types.InlineKeyboardButton(text="О длине волны", callback_data="about_len")
    button_about_fluence = types.InlineKeyboardButton(text="Вычисление флюенса лазерной системы",
                                                      callback_data="fluence")
    resonance = types.InlineKeyboardButton(text="Показать график резонанса", callback_data="resonance")
    user_ans = types.InlineKeyboardButton(text="Написать отзыва о работе", callback_data="user_responce")
    markup.add(button_yes)
    markup.add(button_energy)
    markup.add(button_calc)
    markup.add(button_about_len)
    markup.add(resonance)
    markup.add(button_about_fluence)
    markup.add(user_ans)
    PhysicHelpBot.send_message(message.chat.id, first_mess, parse_mode='html', reply_markup=markup)


@PhysicHelpBot.message_handler(content_types=['text'])
def Random_text(message):
    first_mess = "Используйте кнопки для правильной работы"
    PhysicHelpBot.send_message(message.chat.id, first_mess)


@PhysicHelpBot.message_handler(content_types=['document'])
def graphic_peak_widths(message):
    try:
        chat_id = message.chat.id
        file_info = PhysicHelpBot.get_file(message.document.file_id)
        downloaded_file = PhysicHelpBot.download_file(file_info.file_path).decode().strip('\r').strip('\n').split()
        x = np.array([float(i) for i in downloaded_file])
        peaks, _ = find_peaks(x)
        results_half = peak_widths(x, peaks, rel_height=0.5)
        results_full = peak_widths(x, peaks, rel_height=1)
        plt.plot(x)
        plt.plot(peaks, x[peaks], "x")
        plt.hlines(*results_half[1:], color="C2")
        plt.hlines(*results_full[1:], color="C3")
        plt.savefig("test.png")
        PhysicHelpBot.send_photo(chat_id, photo=open('test.png', 'rb'))
    except Exception as e:
        PhysicHelpBot.reply_to(message, e)


@PhysicHelpBot.callback_query_handler(func=lambda call: True)
def response(function_call):
    if function_call.message:
        if function_call.data == "description":
            second_mess = ("Что я могу:\n"
                           "1. Перевод некоторых физических величин\n"
                           "2. Вычислять положение резонанса по спектру\n"
                           "3. Вычислять Вычисление флюенса лазерной системы по средней мощности\n"
                           "4. Вычислять Вычисление флюенса лазерной системы по средней мощности\n"
                           "5. Посчитать строковое выражение (степень вводить через **)")
            PhysicHelpBot.send_message(function_call.message.chat.id, second_mess)
            PhysicHelpBot.answer_callback_query(function_call.id)
        elif function_call.data == 'translate':
            second_mess = "Выберите перевод"
            button = types.InlineKeyboardMarkup()
            button_elv_to_nm = types.InlineKeyboardButton(text="эВ в длину волны", callback_data="elv_to_nm")
            button_nm_to_elv = types.InlineKeyboardButton(text="длина волны в эВ", callback_data="nm_to_elv")
            button_freq_to_nm = types.InlineKeyboardButton(text="частота в длину волны", callback_data="freq_to_nm")
            button_nm_to_freq = types.InlineKeyboardButton(text="длина волны в частоту", callback_data="nm_to_freq")
            button.add(button_elv_to_nm, button_nm_to_elv)
            button.add(button_freq_to_nm, button_nm_to_freq)
            PhysicHelpBot.send_message(function_call.message.chat.id, second_mess, reply_markup=button)
            PhysicHelpBot.answer_callback_query(function_call.id)
        elif function_call.data == 'calc':
            second_mess = "Введите строкой пример"
            msg = PhysicHelpBot.send_message(function_call.message.chat.id, second_mess)
            PhysicHelpBot.answer_callback_query(function_call.id)
            PhysicHelpBot.register_next_step_handler(msg, calc)
        elif function_call.data == 'elv_to_nm':
            msg = PhysicHelpBot.send_message(function_call.message.chat.id, "Введите значение в эВ без степени")
            PhysicHelpBot.answer_callback_query(function_call.id)
            PhysicHelpBot.register_next_step_handler(msg, translate_elv_to_nm)
        elif function_call.data == 'nm_to_elv':
            msg = PhysicHelpBot.send_message(function_call.message.chat.id, "Введите значение в нм без степени")
            PhysicHelpBot.answer_callback_query(function_call.id)
            PhysicHelpBot.register_next_step_handler(msg, translate_nm_to_elv)
        elif function_call.data == 'freq_to_nm':
            msg = PhysicHelpBot.send_message(function_call.message.chat.id, "Введите значение в ТГц без степени")
            PhysicHelpBot.answer_callback_query(function_call.id)
            PhysicHelpBot.register_next_step_handler(msg, translate_freq_to_nm)
        elif function_call.data == 'nm_to_freq':
            msg = PhysicHelpBot.send_message(function_call.message.chat.id, "Введите значение в нм без степени")
            PhysicHelpBot.answer_callback_query(function_call.id)
            PhysicHelpBot.register_next_step_handler(msg, translate_nm_to_freq)
        elif function_call.data == 'about_len':
            msg = PhysicHelpBot.send_message(function_call.message.chat.id, "Введите значение в нм без степени")
            PhysicHelpBot.answer_callback_query(function_call.id)
            PhysicHelpBot.register_next_step_handler(msg, about_len)
        elif function_call.data == 'resonance':
            PhysicHelpBot.send_message(function_call.message.chat.id, "Отправьте файл в формате .txt в одну строку")
            PhysicHelpBot.answer_callback_query(function_call.id)
        elif function_call.data == "fluence":
            button = types.InlineKeyboardMarkup()
            butt_flat_top = types.InlineKeyboardButton(text="C плоской вершиной", callback_data="flat-top")
            butt_gaussian = types.InlineKeyboardButton(text="Гауссовская", callback_data="gaussian")
            button.add(butt_flat_top)
            button.add(butt_gaussian)
            PhysicHelpBot.send_message(function_call.message.chat.id, "Какой тип лазерной системы?",
                                       reply_markup=button)
            PhysicHelpBot.answer_callback_query(function_call.id)
        elif function_call.data == "flat-top":
            msg = PhysicHelpBot.send_message(function_call.message.chat.id,
                                             "Введите мощность в МДж и площадь луча в мм")
            PhysicHelpBot.answer_callback_query(function_call.id)
            PhysicHelpBot.register_next_step_handler(msg, flat_top)
        elif function_call.data == "gaussian":
            msg = PhysicHelpBot.send_message(function_call.message.chat.id,
                                             "Введите мощность в МДж и площадь луча в мм")
            PhysicHelpBot.answer_callback_query(function_call.id)
            PhysicHelpBot.register_next_step_handler(msg, gaussian)
        elif function_call.data == "user_responce":
            msg = PhysicHelpBot.send_message(function_call.message.chat.id, "Расскажите, что вам понравилось в моей "
                                                                            "работе, а что нет")
            PhysicHelpBot.answer_callback_query(function_call.id)
            PhysicHelpBot.register_next_step_handler(msg, remember_ans)


def remember_ans(message):
    with open("user_ans.txt", "w", encoding="utf-8") as f:
        f.writelines(message.text)
    f.close()
    PhysicHelpBot.send_message(message.chat.id, "Спасибо за ваш отзыв!\nМой разработчик обязательно рассмотрит ваш "
                                                "комментарий")


def flat_top(message):
    try:
        nums = list(map(int, message.text.split()))
        power = nums[0] * 1000
        square = (pi * (nums[1] / 2) ** 2) * 100
        PhysicHelpBot.send_message(message.chat.id, f"Флюенс лазерной системы составляет: {power / square} Дж/см ^ 2")
    except ValueError:
        PhysicHelpBot.send_message(message.chat.id, "Неправильный тип данных!")


def gaussian(message):
    try:
        nums = list(map(int, message.text.split()))
        power = nums[0] * 1000
        square = ((pi * (nums[1] / 2) ** 2) / 2) * 100
        PhysicHelpBot.send_message(message.chat.id, f"Флюенс лазерной системы составляет: {power / square} Дж/см ^ 2")
    except ValueError:
        PhysicHelpBot.send_message(message.chat.id, "Неправильный тип данных!")


def about_len(message):
    try:
        lens = int(message.text)
        if lens < 380 or lens > 780:
            PhysicHelpBot.send_message(message.chat.id, "Несуществующая длина волны!")
        else:
            colors = {
                (620, 780): "Красном",
                (585, 620): "Оранжевом",
                (575, 585): "Желтом",
                (550, 575): "Желто-Зеленом",
                (510, 550): "Зеленом",
                (480, 510): "Голубом",
                (450, 480): "Синем",
                (380, 450): "Фиолетовом"
            }
            resp = None
            for i in colors.keys():
                if i[0] <= lens <= i[1]:
                    resp = colors[i]
                    break
            PhysicHelpBot.send_message(message.chat.id,
                                       f"Вы спросили об этой длинне волны, а именно о {resp} цвете\nПрочитать больше можно по ссылке: https://astronomy.ru/forum/index.php/topic,50316.0.html")
    except ValueError:
        PhysicHelpBot.send_message(message.chat.id, "Неправильный тип данных!")


def translate_elv_to_nm(message):
    try:
        energy = int(message.text)
        len_foton = h_const * light_speed / (energy * one_el_v)
        PhysicHelpBot.send_message(message.chat.id, f"Длина волны света составляет: {len_foton} нм")
    except ValueError:
        PhysicHelpBot.send_message(message.chat.id, "Неправильный тип данных!")


def translate_nm_to_elv(message):
    try:
        len_foton = int(message.text)
        energy = h_const * light_speed / (len_foton * 10 ** -9)
        PhysicHelpBot.send_message(message.chat.id, f"Энергия фотона составляет: {energy} эВ")
    except ValueError:
        PhysicHelpBot.send_message(message.chat.id, "Неправильный тип данных!")


def translate_freq_to_nm(message):
    try:
        freq = int(message.text) * one_TGz
        len_foton = light_speed / freq
        PhysicHelpBot.send_message(message.chat.id, f"Длина волны света составляет: {len_foton} нм")
    except ValueError:
        PhysicHelpBot.send_message(message.chat.id, "Неправильный тип данных!")


def translate_nm_to_freq(message):
    try:
        len_foton = int(message.text)
        freq = light_speed / (len_foton * 10 ** -9)
        PhysicHelpBot.send_message(message.chat.id, f"Частота излучения составляет: {freq / one_TGz} TГц")
    except ValueError:
        PhysicHelpBot.send_message(message.chat.id, "Неправильный тип данных!")


def calc(mess):
    try:
        PhysicHelpBot.send_message(mess.chat.id, eval(mess.text))
    except ValueError as e:
        PhysicHelpBot.send_message(mess.chat.id, "e")


PhysicHelpBot.infinity_polling()
