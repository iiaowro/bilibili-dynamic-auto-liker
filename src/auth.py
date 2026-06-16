"""B站认证模块（环境变量版）"""
import os
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)

GLOBAL_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com/',
    'Origin': 'https://www.bilibili.com',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

class BilibiliAuth:
    """基于环境变量的B站认证类"""

    def __init__(self):
        self.cookies: Dict[str, str] = {}
        self.user_info: Dict = {}
        self.load_from_env()

    def load_from_env(self) -> bool:
        """从环境变量加载核心认证参数，并尝试补全设备指纹"""
        bili_jct = os.getenv('BILI_JCT')
        dedeuserid = os.getenv('DEDEUSERID')
        sessdata = os.getenv('SESSDATA')

        if not all([bili_jct, dedeuserid, sessdata]):
            logger.error("✗ 环境变量缺失！请确保系统环境变量中包含 BILI_JCT, DEDEUSERID, SESSDATA")
            return False

        # 填入核心凭据
        self.cookies = {
            'bili_jct': bili_jct,
            'DedeUserID': dedeuserid,
            'SESSDATA': sessdata
        }
        
        # 【关键抗风控步骤】补全设备指纹 Cookie
        # 如果不带 buvid3，直接请求点赞或动态接口极易导致 Cookie 被风控强制下线
        self._complement_device_cookies()
        
        logger.info("✓ 成功从环境变量加载认证凭据")
        return True

    def _complement_device_cookies(self):
        """通过请求 B 站首页，被动获取并补全必要的设备指纹 Cookie"""
        try:
            logger.info("正在向B站申请分配设备指纹(buvid3)...")
            session = requests.Session()
            # 携带核心 Cookie 去访问一次主页，让 B 站服务器在 Response 中塞回设备指纹
            response = session.get('https://www.bilibili.com/', headers=GLOBAL_HEADERS, cookies=self.cookies, timeout=10)
            
            # 合并新获取到的追踪 Cookie（如 buvid3, b_nut 等）
            bili_cookies = session.cookies.get_dict()
            if 'buvid3' in bili_cookies:
                logger.info("✓ 成功激活并获取到设备指纹 buvid3")
            
            self.cookies.update(bili_cookies)
        except Exception as e:
            logger.warning(f"⚠ 尝试获取设备指纹时出现异常（可能影响抗风控效果）: {e}")

    def is_logged_in(self) -> bool:
        """检查核心 Cookie 是否存在"""
        required = ['SESSDATA', 'bili_jct', 'DedeUserID']
        return all(k in self.cookies for k in required)

    def get_cookies(self) -> Dict[str, str]:
        """获取全量 cookies"""
        return self.cookies

    def get_user_info(self) -> Optional[Dict]:
        """校验并获取用户信息"""
        if not self.is_logged_in():
            return None

        try:
            url = 'https://api.bilibili.com/x/web-interface/nav'
            response = requests.get(url, headers=GLOBAL_HEADERS, cookies=self.cookies, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    self.user_info = data.get('data', {})
                    logger.info(f"✓ 登录验证成功，当前用户: {self.user_info.get('uname')}")
                    return self.user_info
                else:
                    logger.error(f"✗ 凭据校验失败，B站返回: {data.get('message')} (Code: {data.get('code')})")
            return None
        except Exception as e:
            logger.error(f"✗ 获取用户信息出错: {e}")
            return None
