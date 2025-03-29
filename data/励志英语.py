import requests

def get_daily_english():
    url = "https://api.vvhan.com/api/dailyEnglish?type=sj"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
        data = response.json()
        
        # 获取中文和英文内容
        zh_content = data['data'].get('zh', '未获取到中文内容')
        en_content = data['data'].get('en', '未获取到英文内容')
        
        return f"中文: {zh_content}\n英文: {en_content}"
    except requests.RequestException as e:
        return f"请求失败: {str(e)}"

if __name__ == "__main__":
    print(get_daily_english())
