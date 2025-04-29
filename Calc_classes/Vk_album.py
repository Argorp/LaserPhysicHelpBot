import os
import vk_api
import logging


LOGIN = ''
PASSWORD = ''
ALBUM_ID = 1
GROUP_ID = 2

logging.basicConfig(
    filename='bot_work.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)


class Vk_upload:
    def __init__(self):
        self.upload = None
        self.login = LOGIN
        self.password = PASSWORD
        self.path = os.path.join('static', 'img')
        self.vk_sess = vk_api.VkApi(
            login=LOGIN,
            password=PASSWORD,
            auth_handler=self.two_factor_handler,
            captcha_handler=self.captcha_handler
        )
        self.album_id = ALBUM_ID
        self.group_id = GROUP_ID
        try:
            self.vk_sess.auth(token_only=True)
        except vk_api.AuthError as e:
            logging.error(f"Ошибка авторизации: {str(e)}")
            print(f"Ошибка авторизации: {str(e)}")
            return

    @staticmethod
    def two_factor_handler():
        code = input("Введите код двухфакторной аутентификации: ")
        return code, False

    @staticmethod
    def captcha_handler(captcha):
        print(f"Откройте ссылку в браузере: {captcha.get_url()}")
        return input("Введите текст капчи: ")

    def run(self):
        self.upload = vk_api.VkUpload(self.vk_sess)
        for file_name in os.listdir(self.path):
            file_path = os.path.join(self.path, file_name)
            try:
                self.upload.photo(
                    file_path,
                    album_id=self.album_id,
                    group_id=self.group_id
                )
                logging.info(f"График {file_name} успешно загружен!")
            except Exception as e:
                logging.error(f"Ошибка загрузки {file_name}: {str(e)}")
                print(f"Ошибка загрузки {file_name}: {str(e)}")