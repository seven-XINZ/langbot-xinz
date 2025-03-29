import logging
import json
import requests
from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
# 导入事件类
from pkg.plugin.events import *

# 设置要发送的 URL 和令牌
reload_url = "http://localhost:5300/api/v1/settings/provider.json/data"
config_url = "http://localhost:5300/api/v1/settings/provider.json"  # 获取配置的正确URL
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiMTM2NzEyNDU5QHFxLmNvbSIsImlzcyI6IkxhbmdCb3QtY29tbXVuaXR5IiwiZXhwIjoxNzMyOTQyNDAzfQ.iys9mv_b7UmO55NmyXBsJJnRBKWIYuMEfqDvjrO4FzU"  # 请替换为有效的令牌

# 配置文件路径
config_file_path_on = r"D:\Q接入\测试\QChatGPT\data\config\provider - 色色.json"  # 开启色色时的配置文件路径
config_file_path_off = r"D:\Q接入\测试\QChatGPT\data\config\provider - 002低.json"  # 关闭色色时的配置文件路径

# 读取原始配置文件内容
def load_config_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            logging.info(f"成功加载配置文件: {file_path}")
            return config_data  # 返回配置数据本身
    except Exception as e:
        logging.error(f"读取配置文件时出错: {e}")
        return None

# 设置请求头
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 发送 GET 请求以获取当前配置状态
def get_current_config():
    try:
        logging.info(f"发送 GET 请求到 {config_url} 以获取当前配置...")

        # 发送 GET 请求到正确的 URL，确认配置
        response = requests.get(config_url, headers=headers, timeout=10)

        if response.status_code == 200:
            response_data = response.json()  # 解析返回的 JSON
            logging.info(f"当前配置: {response_data}")
        else:
            logging.error(f"获取当前配置失败: {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        logging.error("请求超时，获取当前配置失败！")
    except requests.exceptions.RequestException as e:
        logging.error(f"请求时出错: {e}")

# 发送 PUT 请求进行配置更新
def test_reload(config_data):
    if config_data is None:
        logging.error("没有有效的配置数据，无法执行热重载！")
        return

    try:
        logging.info(f"发送 PUT 请求到 {reload_url} 更新配置...")
        
        # 直接将配置数据包装为 "data": config_data 发送
        payload = { "data": config_data }
        
        # 发送 PUT 请求
        response = requests.put(reload_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            response_data = response.json()  # 解析返回的 JSON
            if response_data.get("msg") == "ok":  # 检查 msg 是否为 "ok"
                logging.info("配置更新成功！")
                # 配置更新后，使用 GET 请求验证
                get_current_config()
            else:
                logging.error(f"配置更新失败，返回消息: {response_data}")
        else:
            logging.error(f"配置更新失败: {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        logging.error("请求超时，配置更新失败！")
    except requests.exceptions.RequestException as e:
        logging.error(f"请求时出错: {e}")

# 关闭色色功能
def close_colorful():
    config_data = load_config_from_file(config_file_path_off)  # 使用关闭色色的配置文件
    if config_data:
        logging.info("关闭色色功能")
        test_reload(config_data)

# 开启色色功能
def open_colorful():
    config_data = load_config_from_file(config_file_path_on)  # 使用开启色色的配置文件
    if config_data:
        logging.info("开启色色功能")
        test_reload(config_data)

# 注册插件
@register(name="ColorfulControl", description="控制色色功能的插件", version="0.1", author="RockChinQ")
class ColorfulControlPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        pass

    # 异步初始化
    async def initialize(self):
        pass

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        if msg == "开启色色":  # 如果消息为开启色色
            open_colorful()  # 调用开启色色函数
            ctx.add_return("reply", ["色色功能已开启！"])
            ctx.prevent_default()
        elif msg == "关闭色色":  # 如果消息为关闭色色
            close_colorful()  # 调用关闭色色函数
            ctx.add_return("reply", ["色色功能已关闭！"])
            ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 GroupNormalMessageReceived 的对象
        if msg == "开启色色":  # 如果消息为开启色色
            open_colorful()  # 调用开启色色函数
            ctx.add_return("reply", ["色色功能已开启！"])
            ctx.prevent_default()
        elif msg == "关闭色色":  # 如果消息为关闭色色
            close_colorful()  # 调用关闭色色函数
            ctx.add_return("reply", ["色色功能已关闭！"])
            ctx.prevent_default()

    # 插件卸载时触发
    def __del__(self):
        pass
