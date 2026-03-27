"""B站动态获取模块"""
import requests
import logging
import json
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
                'Referer': 'https://t.bilibili.com/?tab=all',
                'Origin': 'https://t.bilibili.com',
                'Accept': '*/*',
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

            logger.info('请求关注动态列表')

            response = requests.get(
                url,
                headers=headers,
                params=params,
                cookies=cookies,
                timeout=15
            )

            logger.info(f'API 响应状态码: {response.status_code}')

            if response.status_code != 200:
                logger.error(f'请求失败: HTTP {response.status_code}')
                return []

            data = response.json()

            if data.get('code') != 0:
                logger.error(f'API 错误: {data.get("message")}')
                return []

            dynamics = []
            items = data.get('data', {}).get('items', [])

            logger.info(f'获取到 {len(items)} 条原始项目')

            for item in items:
                try:
                    # 提取动态 ID
                    id_str = item.get('id_str')

                    if not id_str:
                        logger.debug('跳过无效的动态项（无 id_str）')
                        continue

                    # modules 可能为 null，需要检查
                    modules = item.get('modules')
                    if modules is None:
                        logger.debug(f'跳过动态 {id_str}（modules 为 null）')
                        continue

                    module_author = modules.get('module_author', {})
                    module_dynamic = modules.get('module_dynamic', {})

                    if module_author is None:
                        logger.debug(f'跳过动态 {id_str}（module_author 为 null）')
                        continue

                    dynamic = {
                        'id': id_str
                    }

                    dynamics.append(dynamic)
                    logger.info(f'✓ 解析动态: id={id_str}')

                    if len(dynamics) >= limit:
                        break

                except Exception as e:
                    logger.warning(f'解析动态失败: {e}')
                    continue

            logger.info(f'成功获取 {len(dynamics)} 条有效动态')
            return dynamics

        except Exception as e:
            logger.error(f'获取动态出错: {e}')
            import traceback
            logger.error(traceback.format_exc())
            return []
