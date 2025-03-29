import requests

def generate_loving_diary():
    url = "https://api.vvhan.com/api/text/dog"
    response = requests.get(url)

    if response.status_code == 200:
        # 直接返回响应文本
        return response.text.strip()  # 去除首尾空格
    else:
        return "请求失败"

# 调用函数并打印结果
result = generate_loving_diary()
print(result)
