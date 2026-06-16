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
                    logger.error('✗ 未能提取到 csrf (bili_jct)，请检查环境变量')
                    return False

                # 更改为更稳定的聚合点赞接口
                url = f'{self.base_url}/x/dynamic/feed/dyn/thumb'

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': 'https://t.bilibili.com/?tab=all',
                    'Origin': 'https://t.bilibili.com',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.9'
                }

                # 【核心修复】添加了缺失的 'type': '1' 以及映射所需的 'dyn_id' 字段
                # B 站新版接口校验如果缺失 type，会直接报 4100001 参数错误
                data = {
                    'dyn_id_str': str(dynamic_id),
                    'dyn_id': int(dynamic_id),  # 部分后端节点需要数字类型的 ID
                    'up': '1',                  # '1' 表示点赞，'2' 表示取消点赞
                    'type': '1',                # 核心缺失参数：1 代表动态主体点赞
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
                    elif code == 65006 or "重复" in message:
                        logger.info(f'⚠ 动态 {dynamic_id} 之前已点过赞，跳过')
                        return True  
                    elif code == -101:
                        logger.error('✗ 账号未登录或 Cookie 已失效')
                        return False
                    elif code == 4100001:
                        logger.warning(f'⚠ 接口提示参数错误(4100001)，正在尝试备用老版协议兼容...')
                        # 如果新版聚合接口依然敏感，尝试走旧版独立动态点赞兼容路径
                        if self._fallback_like_dynamic(dynamic_id, csrf, cookies, headers):
                            return True
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

    def _fallback_like_dynamic(self, dynamic_id: str, csrf: str, cookies: dict, headers: dict) -> bool:
        """备用点赞路径：使用旧版 Web 动态点赞接口进行兼容"""
        try:
            url = f'{self.base_url}/x/dynamic/feed/dyn/thumb'
            # 简化版传统表单参数
            fallback_data = {
                'uid': cookies.get('DedeUserID', ''),
                'dynamic_id': dynamic_id,
                'up': 1,
                'csrf': csrf
            }
            res = requests.post(url, headers=headers, data=fallback_data, cookies=cookies, timeout=10)
            if res.status_code == 200 and res.json().get('code') == 0:
                logger.info(f'✓ 通过备用路径对动态 {dynamic_id} 点赞成功')
                return True
        except Exception:
            pass
        return False
