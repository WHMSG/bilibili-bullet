import asyncio
import random
import sys
import time
from bilibili_api import live, Credential, Danmaku
from bilibili_api.exceptions import ResponseCodeException

# ==================== 配置区域 ====================
# 多条弹幕的默认内容（用于模式2）
MULTIPLE_MESSAGES = ["xx", "xx", "xx", "xx", "xx",
                     "xx", "xx", "xx", "xx", "xx"]

# 循环发送时的随机延迟范围（秒），支持小数
DEFAULT_INTERVAL_RANGE = (5, 6)  # 最小值, 最大值

# 当遇到频率过快错误（10030/10031）时的等待时间（秒）
RATE_LIMIT_WAIT = 1


ACCOUNTS = [
    {
        "name": "",
        "sessdata": "",
        "bili_jct": "",
        "buvid3": "",
    },
    
]
# ===================================================

# ==================== 直播间预设 ====================
# 每个直播间可独立设置 prefix 和 suffix
ROOMS = {
    1: {"name": "xx", "id": 0, "prefix": "10", "suffix": "01"},

}
# ===================================================

async def send_single_to_all(rooms_list, text, prefix, suffix):
    """向所有账号的直播间发送单条弹幕（并发），使用指定的前后缀"""
    tasks = []
    for room_obj, acc_name in rooms_list:
        full_text = prefix + text + suffix
        danmaku = Danmaku(text=full_text)
        tasks.append(send_single_one(room_obj, danmaku, acc_name))
    await asyncio.gather(*tasks)

async def send_single_one(room, danmaku, name):
    """单个账号发送单条弹幕"""
    try:
        await room.send_danmaku(danmaku)
        print(f"[{name}] ✅ 发送成功: {danmaku.text}")
    except Exception as e:
        print(f"[{name}] ❌ 发送失败: {e}")

async def run_multiple_for_account(room, messages, interval_range, name, stop_event, prefix, suffix):
    """单个账号循环发送（独立任务），使用指定的前后缀"""
    print(f"[{name}] 开始循环发送，间隔 {interval_range[0]:.1f}-{interval_range[1]:.1f} 秒")
    print(f"[{name}] 弹幕列表: {messages}")
    print(f"[{name}] 前缀: {prefix!r}, 后缀: {suffix!r}")
    index = 0
    while not stop_event.is_set():
        msg = messages[index]
        full_msg = prefix + msg + suffix
        danmaku = Danmaku(text=full_msg)
        try:
            await room.send_danmaku(danmaku)
            print(f"[{name}] 发送: {full_msg}")
            wait_time = random.uniform(interval_range[0], interval_range[1])
            # 等待，同时检查停止事件
            for _ in range(int(wait_time * 10)):
                if stop_event.is_set():
                    break
                await asyncio.sleep(0.1)
        except ResponseCodeException as e:
            if e.code in (10030, 10031):
                print(f"[{name}] ⚠️ 发送过快被限制（{e.code}），等待 {RATE_LIMIT_WAIT} 秒后继续...")
                for _ in range(int(RATE_LIMIT_WAIT * 10)):
                    if stop_event.is_set():
                        break
                    await asyncio.sleep(0.1)
            else:
                print(f"[{name}] ❌ 发送失败（{e.code}）：{e.msg}")
                await asyncio.sleep(5)
        except Exception as e:
            print(f"[{name}] ❌ 未知错误：{e}")
            await asyncio.sleep(5)
        index = (index + 1) % len(messages)
    print(f"[{name}] 已停止")

async def start_multiple_all(rooms_list, messages, interval_range, prefix, suffix):
    """启动所有账号的循环发送任务，返回任务列表和停止事件"""
    stop_event = asyncio.Event()
    tasks = []
    for room_obj, name in rooms_list:
        task = asyncio.create_task(run_multiple_for_account(room_obj, messages, interval_range, name, stop_event, prefix, suffix))
        tasks.append(task)
    return tasks, stop_event

def select_room():
    """显示预设直播间列表，让用户选择，返回 (房间ID, 前缀, 后缀)"""
    while True:
        print("\n" + "="*40)
        print("可用直播间：")
        for key, room in ROOMS.items():
            # 显示时附带前后缀信息（可选）
            prefix_disp = f", 前缀: {room['prefix']}" if room['prefix'] else ""
            suffix_disp = f", 后缀: {room['suffix']}" if room['suffix'] else ""
            print(f"  {key}. {room['name']} (ID: {room['id']}){prefix_disp}{suffix_disp}")
        print("  0. 手动输入房间号")
        print("  q. 退出程序")
        choice = input("请输入数字选择直播间: ").strip().lower()
        if choice == 'q':
            print("退出程序")
            sys.exit(0)
        elif choice == '0':
            try:
                room_id = int(input("请输入直播间ID（数字）: ").strip())
                # 手动输入的房间，前后缀为空
                return room_id, "", ""
            except ValueError:
                print("输入无效，请重新输入")
                continue
        else:
            try:
                key = int(choice)
                if key in ROOMS:
                    room = ROOMS[key]
                    return room["id"], room.get("prefix", ""), room.get("suffix", "")
                else:
                    print("无效数字，请重新选择")
            except ValueError:
                print("输入无效，请重新输入")

def create_rooms_for_accounts(room_id):
    """为所有账号创建直播间对象，返回列表 [(room, name), ...]"""
    rooms = []
    for acc in ACCOUNTS:
        credential = Credential(
            sessdata=acc["sessdata"],
            bili_jct=acc["bili_jct"],
            buvid3=acc["buvid3"]
        )
        room = live.LiveRoom(room_id, credential=credential)
        rooms.append((room, acc["name"]))
    return rooms

async def main():
    while True:
        # 选择直播间，并获得该房间的前后缀
        room_id, room_prefix, room_suffix = select_room()
        print(f"已选择直播间 ID: {room_id}")
        if room_prefix:
            print(f"本直播间前缀: {room_prefix}")
        if room_suffix:
            print(f"本直播间后缀: {room_suffix}")

        # 为所有账号创建直播间对象
        rooms_list = create_rooms_for_accounts(room_id)

        # 主菜单循环
        current_tasks = None
        current_stop_event = None
        while True:
            print("\n" + "="*40)
            print("请选择模式：")
            print("1. 发送单条弹幕（所有账号同时发送）")
            print("2. 循环发送多条弹幕（所有账号同时循环）")
            print("0. 返回直播间选择")
            choice = input("请输入数字 (0/1/2): ").strip()

            if choice == '0':
                # 停止可能正在运行的循环任务
                if current_tasks:
                    print("正在停止循环任务...")
                    current_stop_event.set()
                    await asyncio.gather(*current_tasks, return_exceptions=True)
                    current_tasks = None
                    current_stop_event = None
                break  # 退出当前直播间的菜单，回到直播间选择

            elif choice == '1':
                # 单条弹幕模式
                text = input("请输入弹幕内容: ").strip()
                if text:
                    await send_single_to_all(rooms_list, text, room_prefix, room_suffix)
                else:
                    print("弹幕内容不能为空")

            elif choice == '2':
                # 循环发送模式
                if current_tasks:
                    print("已有循环任务正在运行，请先返回直播间选择再重新启动。")
                    continue
                print("启动所有账号的循环发送（按 Ctrl+C 停止）")
                current_tasks, current_stop_event = await start_multiple_all(rooms_list, MULTIPLE_MESSAGES, DEFAULT_INTERVAL_RANGE, room_prefix, room_suffix)
                try:
                    await asyncio.gather(*current_tasks)
                except asyncio.CancelledError:
                    print("\n收到停止信号，正在停止所有账号...")
                    current_stop_event.set()
                    await asyncio.gather(*current_tasks, return_exceptions=True)
                    current_tasks = None
                    current_stop_event = None
                except KeyboardInterrupt:
                    print("\n收到停止信号，正在停止所有账号...")
                    current_stop_event.set()
                    await asyncio.gather(*current_tasks, return_exceptions=True)
                    current_tasks = None
                    current_stop_event = None
                else:
                    current_tasks = None
                    current_stop_event = None
            else:
                print("无效输入，请重新选择")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")