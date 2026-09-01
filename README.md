# Bilibili Dynamic Auto Liker

[中文说明](#中文说明) | [English](#english)

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-GitHub%20Actions-orange)

---

## 中文说明

### 项目简介

一个自动为 B 站（Bilibili）关注用户的动态点赞的 Python 脚本。配合 GitHub Actions 定时任务使用，每小时自动运行一次，无需本地常驻，配置完成后即可"挂机"运行。

### 功能特性

- **Cookie 认证**：通过环境变量注入浏览器 Cookie（`SESSDATA`、`BILI_JCT`、`DEDEUSERID`），无需账号密码登录
- **设备指纹补全**：自动请求 B 站首页获取 `buvid3` 等设备指纹 Cookie，降低被风控拦截的概率
- **动态获取**：拉取关注流中最新 20 条动态
- **自动点赞**：携带 CSRF Token 逐条点赞，单条失败自动重试（最多 3 次），已点赞的动态自动跳过
- **拟人化间隔**：每次点赞成功后随机等待 5–12 秒，模拟真人浏览节奏
- **熔断保护**：连续失败 3 次即判定 Cookie 被风控，自动终止任务防止封号
- **定时调度**：内置 GitHub Actions 工作流，每小时自动执行，也支持手动触发

### 获取 Cookie

1. 在浏览器中登录 [bilibili.com](https://www.bilibili.com)
2. 按 `F12` 打开开发者工具，进入 **应用（Application）→ Cookie → https://www.bilibili.com**
3. 找到并复制以下三个字段的值：

| Cookie 字段 | 环境变量名 |
|---|---|
| `SESSDATA` | `SESSDATA` |
| `bili_jct` | `BILI_JCT` |
| `DedeUserID` | `DEDEUSERID` |

> ⚠️ Cookie 等同于你的登录凭据，请勿泄露给他人或提交到公开仓库。

### 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/iiaowro/bilibili-dynamic-auto-liker.git
cd bilibili-dynamic-auto-liker

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量（Linux / macOS）
export SESSDATA="你的SESSDATA"
export BILI_JCT="你的bili_jct"
export DEDEUSERID="你的DedeUserID"

# 3. 设置环境变量（Windows PowerShell）
$env:SESSDATA="你的SESSDATA"
$env:BILI_JCT="你的bili_jct"
$env:DEDEUSERID="你的DedeUserID"

# 4. 运行
python main.py
```

### GitHub Actions 部署（推荐）

1. Fork 本仓库
2. 进入你 Fork 后的仓库 → **Settings → Secrets and variables → Actions → New repository secret**，依次添加三个 Secret：
   - `SESSDATA`
   - `BILI_JCT`
   - `DEDEUSERID`
3. 在 **Actions** 页面启用工作流（默认每小时第 53 分钟自动运行，也可点击 **Run workflow** 手动触发）

Cookie 失效后（日志出现 `账号未登录或 Cookie 已失效`），重新按上一步骤获取并更新 Secrets 即可。

### 项目结构

```
├── main.py                          # 程序入口，任务调度与熔断逻辑
├── config.json                      # 预留配置文件（当前参数以源码为准）
├── requirements.txt                 # Python 依赖
├── src/
│   ├── auth.py                      # Cookie 认证与设备指纹补全
│   ├── dynamic_fetcher.py           # 关注动态列表获取
│   └── like_manager.py              # 动态点赞与重试
└── .github/workflows/python-app.yml # GitHub Actions 定时工作流
```

### 免责声明

- 本项目仅供个人学习与研究用途，请勿用于商业用途或大规模滥用。
- 使用自动化脚本可能违反 B 站用户协议，存在账号被限制的风险，请自行评估并合理控制使用频率。
- 本项目与 Bilibili 官方无关。

### 贡献

欢迎提交 Issue 和 Pull Request。

### 许可证

本项目基于 [MIT License](./LICENSE) 开源。

---

## English

### Overview

A Python script that automatically likes dynamics (posts) from users you follow on Bilibili. Designed to run as a scheduled GitHub Actions workflow (once per hour), so it works as a "set and forget" solution with no local server required.

### Features

- **Cookie-based auth**: Injects browser cookies via environment variables (`SESSDATA`, `BILI_JCT`, `DEDEUSERID`) — no password login needed
- **Device fingerprint**: Automatically fetches `buvid3` and other fingerprint cookies from the Bilibili homepage to reduce the chance of being blocked by risk control
- **Dynamic fetching**: Pulls the latest 20 dynamics from your following feed
- **Auto liking**: Likes each dynamic with the CSRF token; retries up to 3 times on failure and skips already-liked posts
- **Human-like pacing**: Randomly waits 5–12 seconds after each successful like to mimic human browsing
- **Circuit breaker**: Stops automatically after 3 consecutive failures when the cookie is judged to be blocked, protecting your account
- **Scheduled runs**: Built-in GitHub Actions workflow runs hourly and also supports manual triggering

### Getting Your Cookies

1. Log in to [bilibili.com](https://www.bilibili.com) in your browser
2. Open DevTools with `F12`, go to **Application → Cookies → https://www.bilibili.com**
3. Copy the values of the following three fields:

| Cookie field | Environment variable |
|---|---|
| `SESSDATA` | `SESSDATA` |
| `bili_jct` | `BILI_JCT` |
| `DedeUserID` | `DEDEUSERID` |

> ⚠️ Cookies are equivalent to your login credentials. Never share them or commit them to a public repository.

### Local Usage

```bash
# 1. Clone the repository
git clone https://github.com/iiaowro/bilibili-dynamic-auto-liker.git
cd bilibili-dynamic-auto-liker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables (Linux / macOS)
export SESSDATA="your_SESSDATA"
export BILI_JCT="your_bili_jct"
export DEDEUSERID="your_DedeUserID"

# 3. Set environment variables (Windows PowerShell)
$env:SESSDATA="your_SESSDATA"
$env:BILI_JCT="your_bili_jct"
$env:DEDEUSERID="your_DedeUserID"

# 4. Run
python main.py
```

### GitHub Actions Deployment (Recommended)

1. Fork this repository
2. In your fork, go to **Settings → Secrets and variables → Actions → New repository secret** and add three secrets:
   - `SESSDATA`
   - `BILI_JCT`
   - `DEDEUSERID`
3. Enable the workflow on the **Actions** page (it runs automatically at minute 53 of every hour by default; you can also click **Run workflow** to trigger it manually)

If your cookie expires (the log shows `账号未登录或 Cookie 已失效`), simply grab fresh cookies and update the secrets.

### Project Structure

```
├── main.py                          # Entry point: task orchestration & circuit breaker
├── config.json                      # Reserved config file (values are hardcoded for now)
├── requirements.txt                 # Python dependencies
├── src/
│   ├── auth.py                      # Cookie auth & device fingerprint
│   ├── dynamic_fetcher.py           # Following-feed fetching
│   └── like_manager.py              # Liking with retries
└── .github/workflows/python-app.yml # GitHub Actions scheduled workflow
```

### Disclaimer

- This project is for personal learning and research only. Do not use it for commercial purposes or large-scale abuse.
- Automated scripts may violate Bilibili's Terms of Service and may result in account restrictions. Evaluate the risks yourself and use it responsibly.
- This project is not affiliated with Bilibili.

### Contributing

Issues and pull requests are welcome!

### License

This project is licensed under the [MIT License](./LICENSE).
