import httpx
import asyncio

async def get_random_sexy_text():
    api_url = "https://api.vvhan.com/api/text/sexy"  # 骚话 API 地址
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url)
            response.raise_for_status()  # 检查请求是否成功
            
            # 直接返回 API 响应的文本内容
            return response.text.strip()  # 去除前后的空白字符
        except Exception as e:
            return f"请求失败: {e}"

async def main():
    sexy_text = await get_random_sexy_text()
    print(sexy_text)

if __name__ == "__main__":
    asyncio.run(main())
