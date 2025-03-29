import requests
import os
import random
import sys

def generate_image(prompt: str):
    url = 'https://api.ephone.ai/ideogram/generate'
    headers = {
        'Authorization': 'Bearer sk-oRr4Df4l4uAKOa2AgsDyuxaXyHHXZ6wN5NN4zapwuwc2Zh73',
        'Content-Type': 'application/json',
    }

    request_data = {
        "image_request": {
            "prompt": f"anime style, Japanese anime, extremely detailed CG, HD wallpaper, ((masterpiece)), best quality, illustration, beautiful detailed background, cinematic lighting, dramatic, AI world, 1 girl, solo, looking at viewer, shirt, straight-on，{prompt}",
            "model": "V_2_TURBO",
            "magic_prompt_option": "AUTO",
            "seed": random.randint(0, 2147483647)
        }
    }

    response = requests.post(url, headers=headers, json=request_data)

    if response.status_code == 200:
        image_url = response.json()['data'][0]['url']
        return f"![图像]({image_url})"
    else:
        return f"错误信息: {response.text}"

def main():
    if len(sys.argv) < 2:
        print("请提供提示词，例如: 猫")
        return

    prompt = ' '.join(sys.argv[1:]).strip()
    markdown_output = generate_image(prompt)

    print(markdown_output)

if __name__ == "__main__":
    main()
