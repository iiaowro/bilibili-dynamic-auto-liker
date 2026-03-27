import requests
import json
from datetime import datetime

# Function to fetch current user's following dynamics from Bilibili API

def fetch_following_dynamics(mid):
    url = f'https://api.bilibili.com/x/relation/followings?vmid={mid}&pn=1&ps=30'
    headers = {
        'User-Agent': 'Mozilla/5.0',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f'Failed to fetch data: {response.status_code}')
        return None

if __name__ == '__main__':
    user_mid = 'YOUR_USER_MID'  # Replace with the actual mid
    dynamics = fetch_following_dynamics(user_mid)
    print(dynamics)