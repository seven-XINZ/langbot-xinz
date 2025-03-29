import httpx
import asyncio
import random

async def fetch_anime_image_url():
    # 定义所有的图片链接
    image_urls = [
        "https://r.storyo.cn/pic/cat",   # 小黑猫(表情包)
        "https://r.storyo.cn/pic/capoo",  # capoo(表情包)
        "https://r.storyo.cn/pic/kagura", # 神乐七奈(表情包)
        "https://r.storyo.cn/pic/chaijun", # 柴郡(表情包)
        "https://r.storyo.cn/pic/cute",   # 可爱(表情包)
        "https://r.storyo.cn/pic/naxida", # 纳西妲(表情包)
        "https://r.storyo.cn/pic/mansui", # 满穗(表情包)
        "https://r.storyo.cn/pic/congyu",  # 丛雨(表情包)
        "https://r.storyo.cn/pic/xinhai"   # 心海(表情包)
    ]

    # 随机选择一个图片链接
    selected_url = random.choice(image_urls)
    
    return selected_url  # 返回选中的链接

async def main():
    image_url = await fetch_anime_image_url()
    if image_url:
        markdown_image_link = f"![Anime Image]({image_url})"  # 转换为 Markdown 格式
        print(markdown_image_link)  # 打印 Markdown 图片链接
    else:
        print("获取图片失败")  # 打印失败信息

if __name__ == "__main__":
    asyncio.run(main())  # 运行主函数
