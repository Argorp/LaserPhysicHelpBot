import sqlite3
from constants import *


class Button_calc:
    def __init__(self):
        self.dict = dict()
        con = sqlite3.connect('Bot_db.db')
        cur = con.cursor()
        result = cur.execute("""select * from colors_param""").fetchall()
        for temp in result:
            fir, sec = list(map(int, temp[2].split('-')))
            self.dict[temp[1]] = (fir, sec)
        con.close()

    def bad_params(self):
        return "Неправильный тип данных!"

    def write_an_comment(self, com, id_user):
        con = sqlite3.connect('Bot_db.db')
        cur = con.cursor()
        print(com)
        print(id_user)
        cur.execute("""INSERT INTO user_comment(user_name, comment) VALUES (?, ?)""", (id_user, com))
        con.commit()
        con.close()

    def flat_top(self, message) -> str:
        try:
            nums = list(map(int, message.text.split()))
            power = nums[0] * 1000
            square = (pi * (nums[1] / 2) ** 2) * 100
            return f"Флюенс лазерной системы составляет: {power / square} Дж/см ^ 2"
        except ValueError:
            self.bad_params()

    def gaussian(self, message) -> str:
        try:
            nums = list(map(int, message.text.split()))
            power = nums[0] * 1000
            square = ((pi * (nums[1] / 2) ** 2) / 2) * 100
            return f"Флюенс лазерной системы составляет: {power / square} Дж/см ^ 2"
        except ValueError:
            self.bad_params()

    def translate_elv_to_nm(self, message) -> str:
        try:
            energy = int(message.text)
            len_foton = h_const * light_speed / (energy * one_el_v)
            return f"Длина волны света составляет: {len_foton} нм"
        except ValueError:
            self.bad_params()

    def translate_nm_to_elv(self, message):
        try:
            len_foton = int(message.text)
            energy = h_const * light_speed / (len_foton * 10 ** -9)
            return f"Энергия фотона составляет: {energy} эВ"
        except ValueError:
            self.bad_params()

    def translate_freq_to_nm(self, message):
        try:
            freq = int(message.text) * one_TGz
            len_foton = light_speed / freq
            return f"Длина волны света составляет: {len_foton} нм"
        except ValueError:
            self.bad_params()

    def translate_nm_to_freq(self, message):
        try:
            len_foton = int(message.text)
            freq = light_speed / (len_foton * 10 ** -9)
            return f"Частота излучения составляет: {freq / one_TGz} TГц"
        except ValueError:
            self.bad_params()