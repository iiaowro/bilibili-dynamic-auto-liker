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
                # 1. 获取包含设备指纹的全量 cookies
                cookies = self.auth.get_cookies()
                
                # 2. 提取 csrf token
                csrf = cookies.get('bili_jct', '')
                if not csrf:
                    logger.error('✗ 未在 Cookie 中找到 bili_jct，请检查登录状态或重新登录')
                    return False

                # 3. 保持原代码的 URL 拼接方式
                url = f'{self.base_url}/x/dynamic/feed/dyn/thumb?csrf={csrf}'

                # 4. 统一使用现代浏览器 UA，防止被识别为陈旧爬虫
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': 'https://t.bilibili.com/?tab=all',
                    'Origin': 'https://t.bilibili.com',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.9'
                }

                # 5. 保持完全一致的原始 JSON 数据格式
                data = {
                    'dyn_id_str': str(dynamic_id),
                    'up': 1
                }

                logger.info(f'尝试点赞动态: {dynamic_id}')

                response = requests.post(
                    url,
                    headers=headers,
                    json=data,  # 严格保持 json 格式发送
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
                        return True  
                    elif code == -101:
                        logger.error('✗ 账号未登录或 Cookie 已失效')
                        return False
                    else:
                        logger.warning(f'API 返回错误 (code={code}): {message}')
                else:
                    logger.warning(f'HTTP 错误: {response.status_code}')

            except Exception as e:
                logger.warning(f'点赞异常 (尝试 {attempt + 1}/{self.max_retries}): {e}')

            if attempt < self.max_retries - 1:
                # 稍微引入一点随机波动，降低 Actions 的机器特征
                actual_delay = self.retry_delay + random.uniform(0.5, 1.5)
                logger.info(f'等待 {actual_delay:.1f} 秒后重试...')
                time.sleep(actual_delay)

        logger.error(f'✗ 动态 {dynamic_id} 点赞失败')
        return False
