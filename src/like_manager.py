"""B站点赞管理模块"""
import requests
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class LikeManager:
    """B站点赞管理类"""

    def __init__(self, auth):
        self.auth = auth
        self.base_url = 'https://api.bilibili.com'
        self.max_retries = 3
        self.retry_delay = 2

    def like_dynamic(self, dynamic_id: str) -> bool:
        """点赞动态

        Args:
            dynamic_id: 动态 ID

        Returns:
            是否点赞成功
        """
        for attempt in range(self.max_retries):
            try:
                url = f'{self.base_url}/x/dynamic/feed/dyn/thumb?csrf=b1f2000721577301804c96f4899aa23f'

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
                    'Referer': 'https://t.bilibili.com/?tab=all',
                    'Origin': 'https://t.bilibili.com',
                    'Content-Type': 'application/json',
                    'Accept': '*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.9'
                }

                cookies = self.auth.get_cookies()

                # 关键：使用 JSON 格式发送数据，up=2 表示点赞
                data = {
                    'dyn_id_str': dynamic_id,
                    'up': 1
                }

                logger.info(f'尝试点赞动态: {dynamic_id}')

                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    cookies=cookies,
                    timeout=10
                )

                logger.info(f'点赞响应状态码: {response.status_code}')

                if response.status_code == 200:
                    result = response.json()
                    code = result.get('code')
                    message = result.get('message', '')

                    if code == 0:
                        logger.info(f'✓ 动态 {dynamic_id} 点赞成功')
                        return True
                    elif code == 65006:
                        logger.info(f'⚠ 动态 {dynamic_id} 已点过赞，跳过')
                        return True  # 视为成功（已赞过）
                    else:
                        logger.warning(f'API 返回错误 (code={code}): {message}')
                else:
                    logger.warning(f'HTTP 错误: {response.status_code}')
                    logger.debug(f'响应内容: {response.text}')

            except Exception as e:
                logger.warning(f'点赞异常 (尝试 {attempt + 1}/{self.max_retries}): {e}')

            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries - 1:
                logger.info(f'等待 {self.retry_delay} 秒后重试...')
                time.sleep(self.retry_delay)

        logger.error(f'✗ 动态 {dynamic_id} 点赞失败')
        return False
