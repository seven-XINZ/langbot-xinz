import httpx
import asyncio
import json

async def get_random_poisonous_chicken_soup():
    api_url = "https://v2.api-m.com/api/dujitang"  # 毒鸡汤 API 地址
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url)
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析 JSON 响应
            data = response.json()
            if data['code'] == 200:
                return data['data']  # 返回文本内容
            else:
                return f"错误: {data['msg']}"
        except Exception as e:
            return f"请求失败: {e}"

async def main():
    poisonous_chicken_soup = await get_random_poisonous_chicken_soup()
    print(poisonous_chicken_soup)

if __name__ == "__main__":
    asyncio.run(main())
