"""B站点赞管理模块"""
import requests
import logging
import time
import random

logger = logging.getLogger(__name__)

class LikeManager:
    """B站点赞管理类"""

    def __init__(self, auth):
        self.auth = auth
        self.base_url = 'https://api.bilibili.com'
        self.max_retries = 3
        self.retry_delay = 3

    def like_dynamic(self, dynamic_id: str) -> bool:
        """点赞动态"""
        for attempt in range(self.max_retries):
            try:
                cookies = self.auth.get_cookies()
                csrf = cookies.get('bili_jct', '')
                
                if not csrf:
                    logger.error('✗ 未能提取到 csrf (bili_jct)，请检查环境变量是否正确填写')
                    return False

                url = f'{self.base_url}/x/dynamic/feed/dyn/thumb'

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': 'https://t.bilibili.com/?tab=all',
                    'Origin': 'https://t.bilibili.com',
                    'Content-Type': 'application/x-www-form-urlencoded',  # 必须以表单格式提交
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.9'
                }

                # 必须将 csrf 作为表单体的一部分发送
                data = {
                    'dyn_id_str': dynamic_id,
                    'up': 1,
                    'csrf': csrf
                }

                logger.info(f'尝试点赞动态: {dynamic_id}')
                response = requests.post(url, headers=headers, data=data, cookies=cookies, timeout=10)

                if response.status_code == 200:
                    result = response.json()
                    code = result.get('code')
                    message = result.get('message', '')

                    if code == 0:
                        logger.info(f'✓ 动态 {dynamic_id} 点赞成功')
                        return True
                    elif code == 65006:
                        logger.info(f'⚠ 动态 {dynamic_id} 之前已点过赞，跳过')
                        return True  
                    elif code == -101:
                        logger.error('✗ 账号未登录，或当前环境变量中的 Cookie 已被风控强制下线')
                        return False
                    else:
                        logger.warning(f'API 返回异常 (code={code}): {message}')
                else:
                    logger.warning(f'HTTP 错误: {response.status_code}')

            except Exception as e:
                logger.warning(f'点赞异常 (尝试 {attempt + 1}/{self.max_retries}): {e}')

            if attempt < self.max_retries - 1:
                actual_delay = self.retry_delay + random.uniform(0.5, 2.5)
                logger.info(f'等待 {actual_delay:.1f} 秒后重试...')
                time.sleep(actual_delay)

        logger.error(f'✗ 动态 {dynamic_id} 点赞失败')
        return False
