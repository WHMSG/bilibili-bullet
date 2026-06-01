# bilibili-
此代码用于B站直播间弹幕发送测试，仅供学习Python异步编程与B站API调用。禁止用于违反B站社区规则或法律法规的行为，使用者需自行承担违规后果。   This code is for testing bilibili live danmaku sending. For learning Python async and B站 API only. Do not violate bilibili rules or laws. Users bear all consequences.


# B站直播弹幕自动发送工具

本工具基于 `bilibili-api-python` 开发，支持**每个直播间独立设置前后缀**，并具备自动重试、频率限制处理等功能。

## ✨ 功能特点

- 可为不同直播间预设不同的**弹幕前后缀**（例如直播间1加后缀“01”，直播间2不加）
- 两种发送模式：单条发送 / 循环批量发送
- 循环发送可自定义延迟范围（支持小数点，如0.1秒）
- 自动处理发送频率过快错误（错误码10030/10031），等待后可继续
- 直播间选择菜单（数字键快速切换）
- 支持手动输入房间号

## 📦 环境要求

- Python 3.8 或更高版本
- 需要联网（访问B站API）

## 🔧 安装与依赖

1. 克隆或下载脚本到本地。
2. 打开终端（命令提示符），进入脚本所在目录。
3. 安装所需Python库：

bash
pip install bilibili-api-python aiohttp curl_cffi httpx



1. 获取B站账号凭证
脚本需要三个Cookie值：SESSDATA、bili_jct、buvid3。获取方法：

使用Chrome/Edge浏览器登录B站（https://www.bilibili.com）

按 F12 打开开发者工具 → 切换到 “应用(Application)” 标签

左侧找到 Cookie → https://www.bilibili.com

在右侧表格中分别复制 SESSDATA、bili_jct、buvid3 的值

2. 修改脚本中的账号配置
打开脚本文件 bilibili_danmaku_tool.py，找到 ACCOUNTS 列表，按如下格式填入你的账号信息（可添加多个账号）：

python
```
ACCOUNTS = [
    {
        "name": "账号1昵称",                     # 任意标识名
        "sessdata": "你复制的SESSDATA",
        "bili_jct": "你复制的bili_jct",
        "buvid3": "你复制的buvid3",
    },
    {
        "name": "账号2昵称",
        "sessdata": "另一个账号的SESSDATA",
        "bili_jct": "另一个账号的bili_jct",
        "buvid3": "另一个账号的buvid3",
    },
]
```
3. 配置直播间及前后缀
找到 ROOMS 字典，按如下格式添加你常去的直播间，并可为每个直播间设置独立的 prefix（前缀）和 suffix（后缀）：

python
ROOMS = {
    1: {"name": "xx", "id": 0, "prefix": "10", "suffix": "01"},
    
    # 更多直播间...
}
name：直播间显示名称（菜单中显示）

id：直播间的数字房间号（从直播间网址获得，如 live.bilibili.com/9121226）

prefix：发送弹幕时自动添加的前缀（可留空）

suffix：发送弹幕时自动添加的后缀（可留空）

4. 配置弹幕列表与延迟
在脚本顶部的配置区域：

python
循环发送时的弹幕列表（每条弹幕会循环发送）
MULTIPLE_MESSAGES = ["弹幕1", "弹幕2", "弹幕3"]

循环发送时的随机延迟范围（秒），支持小数
DEFAULT_INTERVAL_RANGE = (5, 6)  # 最小值, 最大值

当遇到频率过快错误（10030/10031）时的等待时间（秒）
RATE_LIMIT_WAIT = 1


运行脚本
在终端中执行：

bash
python bilibili_danmaku_tool.py
