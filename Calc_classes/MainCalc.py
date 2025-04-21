from math import log10, floor
import sqlite3
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
        if value == 0:
            return "0"

        abs_value = abs(value)
        exp = floor(log10(abs_value))
        coeff = value / 10 ** exp
        coeff_rounded = round(coeff, 3)
        # Убираем лишние нули после запятой
        if coeff_rounded == int(coeff_rounded):
            formatted_coeff = str(int(coeff_rounded))
        else:
            formatted_coeff = f"{coeff_rounded:.3f}".rstrip('0').rstrip('.')

        return f"{formatted_coeff} × 10^{exp}"

    def bad_params(self):
        return "Неправильный тип данных!"

    def flat_top(self, message) -> str:
        try:
            nums = list(map(int, message.text.split()))
            power = nums[0] * 1000
            square = (pi * (nums[1] / 2) ** 2) * 100
            result = power / square
            return f"Флюенс лазерной системы составляет: {self.format_result(result)} Дж/см²"
        except (ValueError, IndexError):
            return self.bad_params()

    def gaussian(self, message) -> str:
        try:
            nums = list(map(int, message.text.split()))
            power = nums[0] * 1000
            square = ((pi * (nums[1] / 2) ** 2) / 2) * 100
            result = power / square
            return f"Флюенс лазерной системы составляет: {self.format_result(result)} Дж/см²"
        except (ValueError, IndexError):
            return self.bad_params()

    def translate_elv_to_nm(self, message) -> str:
        try:
            energy = float(message.text)
            len_foton = h_const * light_speed / (energy * one_el_v)
            return f"Длина волны света составляет: {self.format_result(len_foton)} м"
        except ValueError:
            return self.bad_params()

    def translate_nm_to_elv(self, message) -> str:
        try:
            len_foton = float(message.text)
            energy = h_const * light_speed / (len_foton * 1e-9)
            return f"Энергия фотона составляет: {self.format_result(energy)} В"
        except ValueError:
            return self.bad_params()

    def translate_freq_to_nm(self, message) -> str:
        try:
            freq = float(message.text) * one_TGz
            len_foton = light_speed / freq
            return f"Длина волны света составляет: {self.format_result(len_foton)} м"
        except ValueError:
            return self.bad_params()

    def translate_nm_to_freq(self, message) -> str:
        try:
            len_foton = float(message.text)
            freq = light_speed / (len_foton * 1e-9)
            return f"Частота излучения составляет: {self.format_result(freq / one_TGz)} Гц"
        except ValueError:
            return self.bad_params()

    def write_an_comment(self, com: str, id_user: int):
        con = sqlite3.connect('Bot_db.db')
        cur = con.cursor()
        cur.execute("""INSERT INTO user_comment(user_name, comment) VALUES (?, ?)""", (id_user, com))
        con.commit()
        con.close()