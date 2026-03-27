print(">>> Python 脚本启动成功，正在初始化...", flush=True)

import time
import requests

class BilibiliAutoLiker:
    def __init__(self, user_id, access_token):
        self.user_id = user_id
        self.access_token = access_token

    def get_latest_dynamics(self):
        url = f'https://api.bilibili.com/x/space/dynamic/{self.user_id}'
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['data']['cards']
        return None

    def like_post(self, dynamic_id):
        like_url = 'https://api.bilibili.com/x/v2/dm/like'
        payload = {'dynamic_id': dynamic_id, 'type': 1}
        headers = {'Authorization': f'Bearer {self.access_token}'}
        requests.post(like_url, headers=headers, json=payload)

    def auto_like(self):
        while True:
            dynamics = self.get_latest_dynamics()
            if dynamics:
                for card in dynamics[:20]:
                    dynamic_id = card['item']['id']
                    self.like_post(dynamic_id)
            time.sleep(3600)

if __name__ == '__main__':
    USER_ID = 'your_user_id'
    ACCESS_TOKEN = 'your_access_token'
    auto_liker = BilibiliAutoLiker(USER_ID, ACCESS_TOKEN)
    auto_liker.auto_like()
