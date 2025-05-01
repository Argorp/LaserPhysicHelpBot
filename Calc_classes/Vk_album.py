import os
import vk_api
import logging

ALBUM_ID = 307346501
GROUP_ID = 230183619

logging.basicConfig(
    filename='bot_work.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

class Vk_upload:
    def __init__(self):
        self.upload = None
        self.path = os.path.join('static', 'img')
        self.vk_sess = vk_api.VkApi(token="?")
        self.upload = vk_api.VkUpload(self.vk_sess)
        self.album_id = ALBUM_ID
        self.group_id = GROUP_ID

    def run(self, username, profile_link):
        for file_name in os.listdir(self.path):
            file_path = os.path.join(self.path, file_name)
            try:
                caption = ""
                if username and profile_link:
                    caption = f"Автор: {username}\nПрофиль: {profile_link}"
                self.upload.photo(
                    file_path,
                    album_id=self.album_id,
                    group_id=self.group_id,
                    caption=caption
                )
                logging.info(f"График {file_name} успешно загружен!")
                print(f"График {file_name} успешно загружен!")
            except Exception as e:
                logging.error(f"Ошибка загрузки {file_name}: {str(e)}")
                print(f"Ошибка загрузки {file_name}: {str(e)}")