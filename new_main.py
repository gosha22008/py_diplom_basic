import requests
from tqdm import tqdm
import json
from os import path
import time
from pprint import pprint


def is_file(loc_f_name):
    return path.isfile(loc_f_name)


def write_file_json(loc_f_name, data):
    with open(loc_f_name, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, )


def read_file_json(loc_f_name):
    with open(loc_f_name, encoding='utf-8') as f:
        data = json.load(f)
        return data


def get_token():
    tokens = read_file_json('tokens.json')
    return tokens


def is_not_empty(loc_f_name):
    with open(loc_f_name, encoding='utf-8') as f:
        data = f.read()
        if data:
            return data
        else:
            return


def list_of_names(loc_f_name):
    list_name = []
    if is_file(loc_f_name) and is_not_empty(loc_f_name):
        data = read_file_json(loc_f_name)
        for d in data:
            list_name.append(d['file_name'].strip('.jpg'))
    return list_name


def write_file(list_data, loc_f_name):
    if is_file(loc_f_name) and is_not_empty(loc_f_name):
        data = read_file_json(loc_f_name)
        data += list_data
        write_file_json(loc_f_name, data)
    else:
        write_file_json(loc_f_name, list_data)


class VK:
    def __init__(self):
        self.vk_id = self.username_id()
        self.count = self.count_method()

    def count_method(self):
        self.count = input('Введите кол-во фотографий для скачивания: ')
        if self.count:
            return self.count
        else:
            return 5

    def username_id(self):
        self.vk_id = input('Введите id или username пользователя: ')
        if self.vk_id.isdigit():
            return self.vk_id
        else:
            url = f'https://api.vk.com/method/users.get?'
            params = {'access_token': get_token()['vk_token'],
                      'v': '5.131',
                      'user_ids': self.vk_id
                      }
            result = requests.get(url, params)
            return result.json()['response'][0]['id']

    def vk_pars(self):
        url_vk = 'https://api.vk.com/method/photos.get?'
        vk_params = {'owner_id': self.vk_id,
                     'album_id': 'profile',
                     'extended': 1,
                     'v': '5.131',
                     'access_token': get_token()['vk_token'],
                     'photo_sizes': 1,
                     'count': self.count
                     }
        result_vk = requests.get(url_vk, params=vk_params)
        if result_vk.status_code == 200 and 'error' not in result_vk.json().keys():
            return result_vk
        else:
            print('Ошибка:', result_vk.json()['error']['error_msg'])
            return


class YD:
    def get_headers_yandex(self):
        return {'Content-Type': 'application/json',
                'Authorization': get_token()['ya_token']
                }

    def create_direct(self):
        url_create_dir = 'https://cloud-api.yandex.net/v1/disk/resources?path=py_diplom_basic'
        headers = self.get_headers_yandex()
        res = requests.put(url_create_dir, headers=headers)
        if res.status_code == 201:
            print("Папка 'py_diplom_basic' успешно создана")
        elif res.status_code == 409:
            print(res.json()['message'])

    def upload_photo(self):
        url_ya_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload?'
        vk = VK()
        res = vk.vk_pars()
        if res:
            for item in tqdm(res.json()['response']['items'], desc='Photos uploading', unit=' photo'):
                list_data = []
                name = f"{item['likes']['count']}"
                if name in list_of_names('Info file.json'):
                    name += '_' + str(time.ctime())
                    name = name.replace(':', '_')
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
                write_file(list_data, 'Info file.json')
            else:
                return


if __name__ == "__main__":
    kek = YD()
    kek.create_direct()
    kek.upload_photo()
