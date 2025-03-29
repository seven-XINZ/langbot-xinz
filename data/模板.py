import httpx
import sys
import asyncio

async def get_weather(city: str):
    api_url = "https://api.vvhan.com/api/weather"  # 天气API地址
    params = {"city": city}  # 使用用户提供的城市名

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        # 检查返回的数据是否有效
        if data.get('success'):
            weather_data = data['data']
            air_data = data['air']
            weather_info = (
                f"城市: {data['city']}\n"
                f"日期: {weather_data['date']}\n"
                f"星期: {weather_data['week']}\n"
                f"天气: {weather_data['type']}\n"
                f"温度范围: {weather_data['low']} - {weather_data['high']}\n"
                f"风向: {weather_data['fengxiang']}\n"
                f"风力: {weather_data['fengli']}\n"
                f"空气质量: {air_data['aqi_name']} (AQI: {air_data['aqi']})\n"
                f"提示: {data['tip']}"
            )
            return weather_info
        else:
            return "获取天气信息失败，请检查城市名称或稍后再试。"

async def main():
    city = sys.argv[1] if len(sys.argv) > 1 else "北京"  # 默认城市为北京
    weather_info = await get_weather(city)
    print(weather_info)

if __name__ == "__main__":
    asyncio.run(main())
