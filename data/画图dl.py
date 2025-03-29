import requests
import random
import sys

# API配置
API_URL = 'https://api.ephone.ai/ideogram/generate'
API_KEY = 'sk-oRr4Df4l4uAKOa2AgsDyuxaXyHHXZ6wN5NN4zapwuwc2Zh73'

def generate_image(prompt: str):
    """根据用户输入生成图像"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

    request_data = {
        "image_request": {
            "prompt": f"anime style，{prompt}",
            "model": "V_2_TURBO",
            "magic_prompt_option": "AUTO",
            "seed": random.randint(0, 2147483647)
        }
    }

    response = requests.post(API_URL, headers=headers, json=request_data)

    if response.status_code == 200:
        image_url = response.json()['data'][0]['url']
        return f"![图像]({image_url})"
    else:
        return f"错误信息: {response.text}"

def main():
    if len(sys.argv) < 2:
        print("请输入关键词")
        return

    prompt = ' '.join(sys.argv[1:]).strip()
    markdown_output = generate_image(prompt)

    print(markdown_output)

if __name__ == "__main__":
    main()
