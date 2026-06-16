"""B站动态获取模块"""
import requests
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class DynamicFetcher:
    """获取B站关注用户动态的类"""

    def __init__(self, auth):
        self.auth = auth
        self.base_url = 'https://api.bilibili.com'

    def get_following_dynamics(self, limit: int = 20) -> List[Dict]:
        """获取关注用户的动态列表"""
        try:
            url = f'{self.base_url}/x/polymer/web-dynamic/v1/feed/all'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://t.bilibili.com/?tab=all',
                'Origin': 'https://t.bilibili.com',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9'
            }

            cookies = self.auth.get_cookies()

            params = {
                'timezone_offset': -480,
                'type': 'all',
                'platform': 'web',
                'page': 1,
                'features': 'itemOpusStyle,listOnlyfans,opusBigCover,onlyfansVote,decorationCard,onlyfansAssetsV2,forwardListHidden,ugcDelete,onlyfansQaCard,commentsNewVersion,avatarAutoTheme,sunflowerStyle,cardsEnhance,eva3CardOpus,eva3CardVideo,eva3CardComment,eva3CardVote,eva3CardUser',
                'web_location': '0.0',
                'x-bili-device-req-json': '{"platform":"web","device":"pc","spmid":"0.0"}'
            }

            logger.info('请求关注动态列表...')
            response = requests.get(url, headers=headers, params=params, cookies=cookies, timeout=15)

            if response.status_code != 200:
                logger.error(f'请求失败: HTTP {response.status_code}')
                return []

            data = response.json()
            if data.get('code') != 0:
                logger.error(f'API 错误: {data.get("message")} (可能是凭证已被风控判定失效)')
                return []

            dynamics = []
            items = data.get('data', {}).get('items', [])

            for item in items:
                try:
                    id_str = item.get('id_str')
                    if not id_str:
                        continue

                    if item.get('modules') is None:
                        continue

                    dynamics.append({'id': id_str})
                    logger.info(f'✓ 解析动态成功: id={id_str}')

                    if len(dynamics) >= limit:
                        break
                except Exception as e:
                    logger.warning(f'解析单条动态失败: {e}')
                    continue

            logger.info(f'本次成功获取 {len(dynamics)} 条有效动态')
            return dynamics

        except Exception as e:
            logger.error(f'获取动态出错: {e}')
            return []
