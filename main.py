import time
import random
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

    # 1. 初始化认证（直接从系统环境变量中读取 BILI_JCT, DEDEUSERID, SESSDATA）
    auth = BilibiliAuth()
    
    if not auth.is_logged_in():
        logger.error("❌ 登录失败：环境变量缺失或无效。请检查 GitHub Secrets 中 BILI_JCT, DEDEUSERID, SESSDATA 的配置。")
        return

    # 2. 获取用户信息（验证凭据并同时在 B 站后端激活指纹 Cookie）
    user_info = auth.get_user_info()
    if user_info:
        logger.info(f"✅ 登录成功！用户名: {user_info.get('uname')} (UID: {user_info.get('mid')})")
    else:
        logger.error("❌ Cookie 校验失败或已被风控强制下线，请检查并更新 GitHub Secrets。")
        return

    # 3. 初始化功能组件
    fetcher = DynamicFetcher(auth)
    liker = LikeManager(auth)

    # 4. 执行本轮点赞任务
    logger.info("开始获取最新动态...")
    dynamics = fetcher.get_following_dynamics(limit=20)
    
    if not dynamics:
        logger.info("任务结束：未发现新动态、无更新或获取失败。")
        return

    success_count = 0
    fail_count = 0

    for dyn in dynamics:
        dyn_id = dyn.get('id')
        if not dyn_id:
            continue
            
        # 执行点赞
        is_success = liker.like_dynamic(dyn_id)
        
        if is_success:
            success_count += 1
            # 【关键抗风控】每成功点赞一条，随机等待 5 到 12 秒，模拟真人浏览停顿
            sleep_time = random.randint(5, 12)
            logger.info(f"等待 {sleep_time} 秒后继续下一条...")
            time.sleep(sleep_time)
        else:
            fail_count += 1
            # 如果连续失败超过 3 次，很可能是 Cookie 被 B 站强制下线或触发了图形验证码，直接熔断退出防止封号
            if fail_count >= 3:
                logger.error("❌ 连续点赞失败达到上限，判定当前 Cookie 已被风控拦截，自动熔断终止任务。")
                break
            time.sleep(5)  # 失败后固定等待 5 秒再试

    logger.info(f"🎉 本轮自动点赞任务执行完毕。成功: {success_count} 条, 失败/跳过: {fail_count} 条。")

if __name__ == '__main__':
    main()
