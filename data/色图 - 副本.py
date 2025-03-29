import httpx
import asyncio

async def fetch_anime_image_url():
    api_url = "https://api.anosu.top/img/"  # API 地址

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)  # 发送 GET 请求

        # 检查响应是否为重定向
        if response.is_redirect:
            return str(response.headers['Location'])  # 返回重定向 URL
        else:
            return str(response.url)  # 如果不是重定向，返回当前 URL

async def main():
    image_url = await fetch_anime_image_url()
    if image_url:
        markdown_image_link = f"![Anime Image]({image_url})"  # 转换为 Markdown 格式
        print(markdown_image_link)  # 打印 Markdown 图片链接
    else:
        print("获取图片失败")  # 打印失败信息

if __name__ == "__main__":
    asyncio.run(main())  # 运行主函数
