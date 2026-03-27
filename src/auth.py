import requests
import time
import json

class BilibiliAuth:
    def __init__(self):
        self.cookies = None
        self.qr_code_url = 'https://passport.bilibili.com/x/passport-login/csrf'
        self.qr_login_url = 'https://passport.bilibili.com/qrcode/getLoginUrl'
        self.qr_login_status_url = 'https://passport.bilibili.com/qrcode/getLoginStatus'

    def get_qr_code(self):
        response = requests.get(self.qr_code_url)
        if response.status_code == 200:
            return response.json()['data']['image']['src']
        else:
            raise Exception('Failed to get QR code')

    def check_login_status(self, qr_key):
        response = requests.get(f'{self.qr_login_status_url}?qr_key={qr_key}')
        return response.json()

    def login(self):
        qr_code_response = self.get_qr_code()
        print(f'Scan this QR code to login: {qr_code_response}')
        time.sleep(3)
        qr_key = qr_code_response.split('/')[-1].split('.')[0]
        while True:
            status = self.check_login_status(qr_key)
            if status['data']['status'] == 1:
                self.cookies = status['data']['cookies']
                print('Login successful!')
                break
            elif status['data']['status'] == 2:
                print('Login failed or expired.')
                break
            time.sleep(3)

    def save_cookies(self, filepath='cookies.json'):
        if self.cookies:
            with open(filepath, 'w') as f:
                json.dump(self.cookies, f)
            print(f'Cookies saved to {filepath}.')
        else:
            print('No cookies to save.')

if __name__ == '__main__':
    auth = BilibiliAuth()
    auth.login()
    auth.save_cookies()