import asyncio
from bilibili_api import live, Credential, Danmaku

async def main():
    credential = Credential(
        sessdata="",
        bili_jct="",
        buvid3=""
    )
    room_display_id = 9121226

    # 创建直播间对象（使用 LiveRoom）
    room = live.LiveRoom(room_display_id, credential=credential)

    # 创建弹幕对象
    danmaku = Danmaku(text="你好，这是用Python发送的第一条弹幕")

    try:
        await room.send_danmaku(danmaku)
        print("✅ 弹幕发送成功！")
    except Exception as e:
        print(f"❌ 发送失败：{e}")

if __name__ == '__main__':
    asyncio.run(main())