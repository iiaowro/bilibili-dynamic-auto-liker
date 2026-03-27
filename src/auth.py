"""B站认证模块"""
import requests
import json
import logging
import os
import time
from typing import Optional, Dict
import qrcode

logger = logging.getLogger(__name__)


class BilibiliAuth:
    """B站认证类"""

    def __init__(self, cookies_file: str = 'cookies.json'):
        self.cookies_file = cookies_file
        self.cookies = {}
        self.user_info = {}
        self._load_cookies()

    def _load_cookies(self):
        """从文件加载 cookies"""
        if os.path.exists(self.cookies_file):
            try:
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    self.cookies = json.load(f)
                logger.info('Cookies 加载成功')
            except Exception as e:
                logger.warning(f'Cookies 加载失败: {e}')
                self.cookies = {}

    def _save_cookies(self):
        """保存 cookies 到文件"""
        try:
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(self.cookies, f)
            logger.info('Cookies 保存成功')
        except Exception as e:
            logger.error(f'Cookies 保存失败: {e}')

    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        if not self.cookies:
            return False

        # 检查必要的 cookie
        required_cookies = ['SESSDATA', 'bili_jct']
        for cookie_name in required_cookies:
            if cookie_name not in self.cookies:
                return False

        return True

    def _get_qrcode_key(self) -> Optional[str]:
        """获取二维码 key"""
        try:
            url = 'https://passport.bilibili.com/qrcode/getLoginUrl'
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    qrcode_key = data.get('data', {}).get('qrcode_key')
                    logger.info('成功获取二维码 Key')
                    return qrcode_key

            logger.error(f'获取二维码 key 失败')
            return None

        except Exception as e:
            logger.error(f'获取二维码 key 异常: {e}')
            return None

    def _display_qrcode(self, qrcode_url: str):
        """在控制台显示二维码"""
        try:
            # 生成二维码
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(qrcode_url)
            qr.make(fit=True)

            # 打印到控制台
            logger.info("\n" + "="*70)
            logger.info("请使用 B站 App 扫描下方二维码登录:")
            logger.info("="*70)
            qr.print_ascii(invert=True)
            logger.info("="*70)

            # 同时保存为图片
            qr.make_image().save('qrcode.png')
            logger.info("二维码已保存到 qrcode.png")

        except Exception as e:
            logger.error(f'显示二维码失败: {e}')
            logger.info(f'请手动访问此链接: {qrcode_url}')

    def _check_login_status(self, qrcode_key: str) -> Optional[Dict]:
        """检查登录状态"""
        try:
            url = 'https://passport.bilibili.com/qrcode/getLoginStatus'
            params = {'qrcode_key': qrcode_key}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data

            return None

        except Exception as e:
            logger.error(f'检查登录状态异常: {e}')
            return None

    def login(self) -> bool:
        """登录（使用二维码）"""
        try:
            logger.info("\n开始二维码登录流程...")

            # 获取二维码 key
            qrcode_key = self._get_qrcode_key()
            if not qrcode_key:
                logger.error('获取二维码失败')
                return False

            # 构造二维码 URL
            qrcode_url = f'https://passport.bilibili.com/qrcode/getLoginUrl?qrcode_key={qrcode_key}'

            # 显示二维码
            self._display_qrcode(qrcode_url)

            logger.info("\n请在 60 秒内扫描二维码...")

            # 轮询检查登录状态
            max_attempts = 60
            for attempt in range(max_attempts):
                time.sleep(1)

                result = self._check_login_status(qrcode_key)

                if not result:
                    continue

                code = result.get('code', -1)
                message = result.get('message', '')

                if code == -4:
                    logger.error('二维码已过期，请重新扫描')
                    return False
                elif code == -5:
                    logger.info(f'[{attempt+1}/{max_attempts}] 等待扫描二维码...')
                    continue
                elif code == -2:
                    logger.info('✓ 已扫描，请在手机上确认登录...')
                    continue
                elif code == 0:
                    logger.info('✓ 登录成功！')

                    # 提取 cookies
                    cookies_data = result.get('data', {}).get('cookie_info', {}).get('cookies', [])

                    for cookie in cookies_data:
                        self.cookies[cookie.get('name')] = cookie.get('value')

                    # 保存 cookies
                    self._save_cookies()

                    return True
                else:
                    logger.warning(f'登录返回错误: code={code}, message={message}')
                    return False

            logger.error('登录超时，请重试')
            return False

        except Exception as e:
            logger.error(f'登录异常: {e}')
            return False

    def get_cookies(self) -> Dict:
        """获取 cookies"""
        return self.cookies

    def set_cookies(self, cookies: Dict):
        """设置 cookies"""
        self.cookies = cookies
        self._save_cookies()

    def get_user_info(self) -> Optional[Dict]:
        """获取用户信息"""
        if not self.is_logged_in():
            return None

        try:
            url = 'https://api.bilibili.com/x/web-interface/nav'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.bilibili.com/'
            }

            response = requests.get(url, headers=headers, cookies=self.cookies, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    self.user_info = data.get('data', {})
                    return self.user_info

            logger.error('获取用户信息失败')
            return None

        except Exception as e:
            logger.error(f'获取用户信息出错: {e}')
            return None
