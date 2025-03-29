import httpx
import asyncio

async def fetch_color_image():
    api_url = "https://image.anosu.top/pixiv/json"

    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=params)  # 发送 POST 请求
        response_data = response.json()

        if response_data.get("code") == 0:  # 检查状态码
            return response_data.get("data", [])
        else:
            print(f"错误信息: {response_data.get('error')}")
            return []

async def main():
    images = await fetch_color_image()  # 调用获取色图的函数
    if isinstance(images, list) and images:
        original_url = images[0]["urls"]["original"]  # 获取原图链接
        markdown_image_link = f"![Anime Image]({original_url})"  # 转换为 Markdown 格式
        print(markdown_image_link)  # 打印 Markdown 图片链接
    else:
        print("获取图片失败")  # 打印失败信息

if __name__ == "__main__":
    asyncio.run(main())  # 运行主函数
