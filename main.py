import time
import logging
from src.auth import BilibiliAuth
from src.dynamic_fetcher import DynamicFetcher
from src.like_manager import LikeManager

# 配置日志，确保 GitHub Actions 能实时看到输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    print(">>> Python 脚本启动成功，正在初始化...", flush=True)

    # 1. 初始化认证（自动读取 cookies.json）
    auth = BilibiliAuth(cookies_file='cookies.json')
    
    if not auth.is_logged_in():
        logger.error("❌ 登录失败：cookies.json 无效或未填充。请检查 GitHub Secrets 配置。")
        return

    # 2. 获取用户信息（验证 Cookie 是否真的有效）
    user_info = auth.get_user_info()
    if user_info:
        logger.info(f"✅ 登录成功！用户名: {user_info.get('uname')} (UID: {user_info.get('mid')})")
    else:
        logger.error("❌ Cookie 已失效，请更新 SESSDATA 等配置。")
        return

    # 3. 初始化功能组件
    fetcher = DynamicFetcher(auth)
    liker = LikeManager(auth)

    # 4. 执行一次点赞任务（不使用 while True，因为 GitHub Actions 本身有定时触发）
    logger.info("开始获取最新动态...")
    dynamics = fetcher.get_following_dynamics(limit=20)
    
    if not dynamics:
        logger.info("止步：没有发现新动态或获取失败。")
        return

    for dyn in dynamics:
        dyn_id = dyn.get('id')
        liker.like_dynamic(dyn_id)
        # 稍微延迟防止触发风控
        time.sleep(2)

    logger.info("🎉 本轮自动点赞任务执行完毕。")

if __name__ == '__main__':
    main()
