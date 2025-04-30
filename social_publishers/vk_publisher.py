import requests

class VKPublisher:
    def __init__(self, vk_api_key, group_id):
        self.vk_api_key = vk_api_key
        self.group_id = group_id

    def upload_photo(self, image_url):
        upload_url_response = requests.get(
            url='https://api.vk.com/method/photos.getWallUploadServer',
            params={
                'access_token': self.vk_api_key,
                'v': '5.236',
                'group_id': self.group_id
            }
        ).json()

        if 'error' in upload_url_response:
            print("Ошибка при получении URL загрузки фото:", upload_url_response)  # 🔥 Логируем ошибку
            raise Exception(upload_url_response['error']['error_msg'])

        upload_url = upload_url_response['response']['upload_url']
        image_data = requests.get(image_url).content
        upload_response = requests.post(upload_url, files={'photo': ('image.jpg', image_data)}).json()

        if 'error' in upload_response:
            print("Ошибка при загрузке фото:", upload_response)  # 🔥 Логируем ошибку
            raise Exception(upload_response['error']['error_msg'])

        save_response = requests.get(
            url='https://api.vk.com/method/photos.saveWallPhoto',
            params={
                'access_token': self.vk_api_key,
                'v': '5.236',
                'group_id': self.group_id,
                'photo': upload_response['photo'],
                'server': upload_response['server'],
                'hash': upload_response['hash']
            }
        ).json()

        if 'error' in save_response:
            print("Ошибка при сохранении фото:", save_response)  # 🔥 Логируем ошибку
            raise Exception(save_response['error']['error_msg'])

        photo_id = save_response['response'][0]['id']
        owner_id = save_response['response'][0]['owner_id']

        return f'photo{owner_id}_{photo_id}'

    def publish_post(self, content, image_url=None):
        params = {
            'access_token': self.vk_api_key,
            'from_group': 1,
            'v': '5.236',
            'owner_id': f'-{self.group_id}',
            'message': content
        }
        if image_url:
            try:
                attachment = self.upload_photo(image_url)
                params['attachments'] = attachment
            except Exception as e:
                print("Ошибка загрузки изображения:", e)  # 🔥 Логируем ошибку
                return {"error": str(e)}

        response = requests.post('https://api.vk.com/method/wall.post', params=params).json()

        # 🔥 Выводим полный ответ от VK API
        print("Ответ VK API:", response)

        if 'error' in response:
            print("Ошибка публикации в VK:", response['error'])  # 🔥 Логируем ошибку

        return response
