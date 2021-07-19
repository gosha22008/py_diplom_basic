import requests
from tqdm import tqdm
import json
from os import path
import time


class UploaderPhoto:
    def __init__(self, id_vk, ya_token, file_name='Info file.json'):
        self.id_vk = id_vk
        self.ya_token = ya_token
        self.loc_f_name = file_name

    def get_headers_yandex(self):
        return {'Content-Type': 'application/json',
                'Authorization': self.ya_token
                }

    def vk_pars(self):
        url_vk = 'https://api.vk.com/method/photos.get?'
        vk_params = {'owner_id': self.id_vk,
                     'album_id': 'profile',
                     'extended': 1,
                     'v': '5.131',
                     'access_token': '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008',
                     'photo_sizes': 1,
                     'count': 5
                     }
        result_vk = requests.get(url_vk, params=vk_params)
        if result_vk.status_code == 200 and 'error' not in result_vk.json().keys():
            return result_vk
        else:
            print('Плохой ответ от VK')
            return

    def create_direct(self):
        url_create_dir = 'https://cloud-api.yandex.net/v1/disk/resources?path=py_diplom_basic'
        headers = self.get_headers_yandex()
        res = requests.put(url_create_dir, headers=headers)
        if res.status_code == 201:
            print("Папка 'py_diplom_basic' успешно создана")
        elif res.status_code == 409:
            print(res.json()['message'])

    def is_file(self, loc_f_name):
        return path.isfile(loc_f_name)

    def is_not_empty(self, loc_f_name):
        with open(loc_f_name, encoding='utf-8') as f:
            data = f.read()
            if data:
                return data
            else:
                return

    def write_file_json(self, loc_f_name, list_data):
        with open(loc_f_name, 'w') as f:
            json.dump(list_data, f, ensure_ascii=False, indent=2, )

    def read_file_json(self, loc_f_name):
        with open(loc_f_name, encoding='utf-8') as f:
            data = json.load(f)
            return data

    def write_file(self, list_data, loc_f_name):
        if self.is_file(loc_f_name):
            if self.is_not_empty(loc_f_name):
                data = self.read_file_json(loc_f_name)
                data += list_data
                self.write_file_json(loc_f_name, data)
            else:
                self.write_file_json(loc_f_name, list_data)
        else:
            self.write_file_json(loc_f_name, list_data)

    def list_of_names(self, loc_f_name):
        list_name = []
        if self.is_file(self.loc_f_name):
            if self.is_not_empty(self.loc_f_name):
                data = self.read_file_json(self.loc_f_name)
                for d in data:
                    list_name.append(d['file_name'].strip('.jpg'))
        return list_name

    def upload_photo(self):
        url_ya_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload?'
        res = self.vk_pars()
        if res:
            for item in tqdm(res.json()['response']['items'], desc='Photos uploading', unit=' photo'):
                list_data = []
                name = f"{item['likes']['count']}"
                if name in self.list_of_names(self.loc_f_name):
                    name += '_' + str(time.time())
                ya_params = {'path': f"py_diplom_basic/{name}.jpg",
                                     'url': item['sizes'][-1]['url']}
                response = requests.post(url_ya_upload, params=ya_params, headers=self.get_headers_yandex())
                data = {
                    'file_name': f'{name}.jpg',
                    'size': item['sizes'][-1]['type'],
                    'data_save': time.ctime(item['date']),
                    'data_upload': time.ctime(),
                    'status upload': response.status_code
                }
                list_data.append(data)
                self.write_file(list_data, self.loc_f_name)
            else:
                return


if __name__ == '__main__':
    uploader = UploaderPhoto('552934290', 'OAuth AQAAAAACJZ2EAADLW_OhWaLRokrop1qAcqIKtso')
    uploader.create_direct()
    uploader.upload_photo()
