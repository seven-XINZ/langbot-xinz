import os
import sys
import json
import time
import requests
from pixai import PixaiAPI

def translate_baidu(text, from_lang='zh', to_lang='en'):
    if not text.strip():  # 检查输入是否为空
        return "输入不能为空"
    
    # 标准化输入，替换中文标点为英文标点
    text = text.replace("，", ",")  # 替换中文逗号为英文逗号
    
    url = 'https://fanyi.baidu.com/ait/text/translate'
    headers = {
        'referer': 'https://fanyi.baidu.com',
        'Content-Type': 'application/json',
        'Origin': 'https://fanyi.baidu.com',
        'accept': 'text/event-stream',
    }
    data = {
        'query': text,
        'from': from_lang,
        'to': to_lang
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # 检查请求是否成功
        
        result = response.text.split('\n')
        translation = []
        
        for item in result:
            if item.startswith('data: '):
                json_data = json.loads(item[6:])
                if 'errno' in json_data:
                    if json_data['errno'] == 0:
                        if 'data' in json_data and 'list' in json_data['data']:
                            translation.extend(item['dst'] for item in json_data['data']['list'])
                    else:
                        return f"翻译失败，错误信息：{json_data.get('errmsg', '未知错误')}，errno: {json_data['errno']}"
        
        return 'nsfw,(lora:wind_lift_no_panties_v1:1), pussy,super fine illustration, vibrant colors, masterpiece, sharp focus, best quality, depth of field, cinematic lighting, ultra detailed, lora:more_details:0.5,(masterpiece, best quality:1.3), (absurdres absolutely resolution), (8k), (detailed beautiful face and eyes), (detailed illustration), (super fine illustration), __PROMPT__,' + '\n'.join(translation) if translation else "未获取到翻译结果"
    
    except Exception as e:
        return f"请求失败，错误信息：{str(e)}"

def main(prompt):
    # 翻译用户输入的内容
    translated_prompt = translate_baidu(prompt, from_lang='zh', to_lang='en')
    if translated_prompt.startswith("翻译失败") or translated_prompt.startswith("请求失败"):
        print(translated_prompt)
        return

    # 设置API Token
    token = 'eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCJ9.eyJsZ2EiOjE3NDI2MzczMTgsImlhdCI6MTc0MjYzNzMyMiwiZXhwIjoxNzQzMjQyMTIyLCJpc3MiOiJwaXhhaSIsInN1YiI6IjE2MTQ0NjczNzg0ODQ2ODE0MDEiLCJqdGkiOiIxODYwMTIzMDgwMzcyMzk5MTUxIn0.AXZbn2-OwRzID6NHI-MgEBNwghgdCYWgwq6nVN6TIpPjh7vQEyblv_G40acwhzn2w04SSAhiBXukj24b16ywkMjbAb3LucKKK1dy9CovZsN1XwMwXnJl0C675nVFTJH6m7fuEXs5xzuXiH09K8JhQwnXvfdhjX0M0ebYKdUZgGoJq3Oa'
    client = PixaiAPI(token)

    # 创建生成任务
    startGeneration = client.createGenerationTask(
        prompts=translated_prompt,
        steps='23',
        modelId='1648918127446573124'
    )

    # 循环检查任务状态
    while True:
        time.sleep(5)  # 每5秒检查一次状态
        raw_response = client.getTaskById(startGeneration)

        # 检查返回的数据是否有效
        if isinstance(raw_response, str) and raw_response.startswith("http"):
            # 如果返回的是图像 URL，直接输出
            markdown_output = f"![生成的图像]({raw_response})"
            print(markdown_output)
            break
        elif raw_response and 'data' in raw_response:
            task_data = raw_response['data'].get('task')
            if task_data and 'media' in task_data:
                image_urls = task_data['media'].get('urls', [])
                if image_urls:
                    # 提取图像 URL
                    imageurlurl = image_urls[0].get('url')
                    if imageurlurl:
                        # 返回 Markdown 格式的图像链接
                        markdown_output = f"![生成的图像]({imageurlurl})"
                        print(markdown_output)
                        break
                else:
                    print("图像URL列表为空，正在重新尝试...")
            else:
                print("任务数据无效，正在重新尝试...")
        else:
            print("返回数据无效，正在重新尝试...")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("请提供关键词，例如：python ./画色图.py Jk少女")
    else:
        prompt = sys.argv[1]
        main(prompt)
