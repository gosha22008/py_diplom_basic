import  requests
from pprint import pprint


token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
# url = f'https://api.vk.com/method/users.get?user_ids=298267848&v=5.52&access_token={token}'
url = 'https://api.vk.com/method/photos.get?'
params = {'owner_id': '552934290',
          'album_id': 'profile',
          'extended': 1,
          'v': '5.52',
          'access_token': token
          }
res = requests.get(url, params=params)
pprint(res.json())