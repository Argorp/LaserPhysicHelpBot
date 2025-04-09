import sqlite3
from math import log10, floor
from constants import *


class ButtonCalc:
    def __init__(self):
        self.color_ranges = {}
        con = sqlite3.connect('Bot_db.db')
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM colors_param""").fetchall()
        for temp in result:
            start, end = map(int, temp[2].split('-'))
            self.color_ranges[temp[1]] = (start, end)
        con.close()

    @staticmethod
    def format_result(value: float) -> str:
        SI_PREFIXES = [
            (1e-24, 'и', 1e24),
            (1e-21, 'з', 1e21),
            (1e-18, 'а', 1e18),
            (1e-15, 'ф', 1e15),
            (1e-12, 'п', 1e12),
            (1e-9, 'н', 1e9),
            (1e-6, 'мк', 1e6),
            (1e-3, 'м', 1e3),
            (1, '', 1),
            (1e3, 'к', 1e-3),
            (1e6, 'М', 1e-6),
            (1e9, 'Г', 1e-9),
            (1e12, 'Т', 1e-12)
        ]
        if value == 0:
            return "0"
        abs_value = abs(value)
        # Ищем подходящую приставку
        for threshold, prefix, multiplier in SI_PREFIXES:
            if abs_value >= threshold:
                scaled_value = value * multiplier
                formatted_value = round(scaled_value, 3)
                # Всегда форматируем до 3 знаков после запятой
                return f"{formatted_value:.3f} {prefix}"

        # Если не нашли подходящую приставку (очень маленькое число)
        exp = floor(log10(abs_value))
        coeff = round(value / 10 ** exp, 3)
        return f"{coeff:.3f} × 10^{exp}"

    def bad_params(self):
        return "Неправильный тип данных!"

    def write_an_comment(self, com: str, id_user: int):
        con = sqlite3.connect('Bot_db.db')
        cur = con.cursor()
        cur.execute("""INSERT INTO user_comment(user_name, comment) VALUES (?, ?)""", (id_user, com))
        con.commit()
        con.close()

    def flat_top(self, message) -> str:
        try:
            nums = list(map(int, message.text.split()))
            power = nums[0] * 1000
            square = (pi * (nums[1] / 2) ** 2) * 100
            result = power / square
            return f"Флюенс лазерной системы составляет: {self.format_result(result)}Дж/см²"
        except (ValueError, IndexError):
            return self.bad_params()

    def gaussian(self, message) -> str:
        try:
            nums = list(map(int, message.text.split()))
            power = nums[0] * 1000
            square = ((pi * (nums[1] / 2) ** 2) / 2) * 100
            result = power / square
            return f"Флюенс лазерной системы составляет: {self.format_result(result)}Дж/см²"
        except (ValueError, IndexError):
            return self.bad_params()

    def translate_elv_to_nm(self, message) -> str:
        try:
            energy = float(message.text)
            len_foton = h_const * light_speed / (energy * one_el_v)
            return f"Длина волны света составляет: {self.format_result(len_foton)}м"
        except ValueError:
            return self.bad_params()

    def translate_nm_to_elv(self, message) -> str:
        try:
            len_foton = float(message.text)
            energy = h_const * light_speed / (len_foton * 1e-9)
            return f"Энергия фотона составляет: {self.format_result(energy)}В"
        except ValueError:
            return self.bad_params()

    def translate_freq_to_nm(self, message) -> str:
        try:
            freq = float(message.text) * one_TGz
            len_foton = light_speed / freq
            return f"Длина волны света составляет: {self.format_result(len_foton)}м"
        except ValueError:
            return self.bad_params()

    def translate_nm_to_freq(self, message) -> str:
        try:
            len_foton = float(message.text)
            freq = light_speed / (len_foton * 1e-9)
            return f"Частота излучения составляет: {self.format_result(freq / one_TGz)}Гц"
        except ValueError:
            return self.bad_params()