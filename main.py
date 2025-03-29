from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import PersonNormalMessageReceived, GroupNormalMessageReceived
import subprocess
import os
import re
import asyncio
from pkg.platform.types.message import Image, Plain

@register(name="小程序运行插件", description="一个小插件运行插件不必开关程序直接运行程序简单（可以用gpt直接写功能添加）", version="0.1", author="小馄饨")
class CommandExecutorPlugin(BasePlugin):
    lock = asyncio.Lock()  # 创建一个锁以确保线程安全
    command_queue = asyncio.Queue()  # 创建一个队列以存储待处理的命令

    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        await self.command_queue.put(ctx)  # 将命令上下文放入队列
        await self.process_commands()  # 处理命令

    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        await self.command_queue.put(ctx)  # 将命令上下文放入队列
        await self.process_commands()  # 处理命令

    async def process_commands(self):
        while not self.command_queue.empty():  # 当队列不为空时
            ctx = await self.command_queue.get()  # 从队列中获取命令上下文
            await self.execute_command(ctx)  # 执行命令
            await asyncio.sleep(2)  # 等待 2 秒再处理下一个命令

    async def execute_command(self, ctx: EventContext):
        async with self.lock:  # 使用锁确保线程安全
            receive_text = ctx.event.text_message
            cleaned_text = re.sub(r'@\S+\s*', '', receive_text).strip()  # 清理文本

            if cleaned_text.startswith('/'):  # 检查是否为命令
                parts = cleaned_text[1:].split(' ', 1)  # 分割命令和参数
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ''

                script_path = os.path.join(os.path.dirname(__file__), 'data', f"{command}.py")

                if os.path.exists(script_path):  # 检查脚本是否存在
                    try:
                        result = subprocess.check_output(['python', script_path, args], text=True, timeout=60)  # 设置超时为60秒
                        result = result.strip()
                        
                        # 如果返回的是图片路径且文件存在
                        if result.endswith(('.png', '.jpg', '.jpeg', '.gif')) and os.path.exists(result):
                            ctx.add_return("reply", [Image(path=result)])
                        else:
                            # 检查文本长度，如果超过200个字符则转换为图片
                            if len(result) > 200:
                                # 使用新的文本转图片模块
                                text2image_path = os.path.join(os.path.dirname(__file__), 'data', 'text2image.py')
                                # 检查text2image.py是否存在
                                if os.path.exists(text2image_path):
                                    try:
                                        img_path = subprocess.check_output(['python', text2image_path, result], text=True, timeout=30).strip()
                                        if img_path and os.path.exists(img_path):
                                            ctx.add_return("reply", [Image(path=img_path)])
                                        else:
                                            # 如果转换失败，使用普通文本
                                            messages = self.convert_message(result)
                                            ctx.add_return("reply", messages)
                                    except Exception:
                                        # 如果执行失败，使用普通文本
                                        messages = self.convert_message(result)
                                        ctx.add_return("reply", messages)
                                else:
                                    messages = self.convert_message(result)
                                    ctx.add_return("reply", messages)
                            else:
                                messages = self.convert_message(result)
                                ctx.add_return("reply", messages)
                    except subprocess.CalledProcessError as e:  # 捕获脚本执行错误
                        ctx.add_return("reply", [f"执行失败: {e.output}"])  # 返回错误消息
                    except Exception as e:  # 捕获其他异常
                        ctx.add_return("reply", [f"发生错误: {str(e)}"])  # 返回通用错误消息
                    ctx.prevent_default()  # 防止后续处理
                # else 分支已删除

    def convert_message(self, message):
        parts = []
        last_end = 0
        image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')  # 修改正则表达式以匹配任何路径
        
        for match in image_pattern.finditer(message):
            start, end = match.span()
            if start > last_end:
                parts.append(Plain(message[last_end:start]))
            image_path = match.group(1)
            # 检查是否为本地路径
            if os.path.exists(image_path):
                parts.append(Image(path=image_path))
            else:  # 如果不是本地路径，则假定为URL
                parts.append(Image(url=image_path))
            last_end = end
        if last_end < len(message):
            parts.append(Plain(message[last_end:]))
        return parts if parts else [Plain(message)]