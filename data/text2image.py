#!/usr/bin/env python3
import os
import time
import re
from PIL import Image, ImageDraw, ImageFont
import platform

# 配置
WIDTH = 800  # 图片宽度
FONT_SIZE = 32  # 字体大小
BACKGROUND_COLOR = (0, 0, 0)  
TEXT_COLOR = (255, 255, 255)  

def find_system_font():
    """查找系统字体"""
    font_path = None
    os_name = platform.system()
    
    if os_name == "Windows":
        # Windows上尝试查找微软雅黑
        win_font = "C:/Windows/Fonts/msyh.ttc"
        if os.path.exists(win_font):
            font_path = win_font
    
    # 如果找不到合适的字体，使用默认字体
    if not font_path:
        # 尝试查找其他常见字体
        common_fonts = [
            "C:/Windows/Fonts/simhei.ttf",  # Windows黑体
            "C:/Windows/Fonts/simsun.ttc",  # Windows宋体
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux文泉驿
            "/System/Library/Fonts/PingFang.ttc"  # macOS苹方
        ]
        
        for font in common_fonts:
            if os.path.exists(font):
                font_path = font
                break
    
    return font_path

def split_text_to_lines(text, font, max_width):
    """智能分割文本为多行"""
    lines = text.replace("\t", "    ").split('\n')
    final_lines = []
    
    for line in lines:
        # 计算当前行宽度
        try:
            line_width = font.getlength(line)
        except:
            # 对于旧版PIL，可能没有getlength方法
            try:
                line_width = font.getsize(line)[0]
            except:
                # 如果无法获取宽度，使用估计值
                line_width = len(line) * (FONT_SIZE / 2)
        
        # 如果行宽小于最大宽度，直接添加
        if line_width <= max_width:
            final_lines.append(line)
        else:
            # 否则需要分割行
            rest_text = line
            while True:
                # 估计可以放下的字符数
                char_count = int(len(rest_text) * (max_width / line_width))
                char_count = max(1, min(char_count, len(rest_text)))
                
                # 将行分割
                final_lines.append(rest_text[:char_count])
                rest_text = rest_text[char_count:]
                
                if not rest_text:
                    break
                    
                # 重新计算剩余文本宽度
                try:
                    line_width = font.getlength(rest_text)
                except:
                    try:
                        line_width = font.getsize(rest_text)[0]
                    except:
                        line_width = len(rest_text) * (FONT_SIZE / 2)
                
                if line_width <= max_width:
                    final_lines.append(rest_text)
                    break
    
    return final_lines

def text_to_image(text, output_path=None):
    """将文本转换为图片"""
    if output_path is None:
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 在cache目录创建临时文件
        cache_dir = os.path.join(script_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        output_path = os.path.join(cache_dir, f"text_{int(time.time())}.png")
    
    # 查找字体
    font_path = find_system_font()
    if not font_path:
        print("错误：找不到合适的字体")
        return None
    
    try:
        font = ImageFont.truetype(font_path, FONT_SIZE, encoding="utf-8")
    except Exception as e:
        print(f"加载字体失败: {e}")
        return None
    
    # 分割文本为行
    text_width = WIDTH - 80  # 留出边距
    lines = split_text_to_lines(text, font, text_width)
    
    # 计算图片高度
    line_height = FONT_SIZE + 3
    img_height = max(280, len(lines) * line_height + 65)
    
    # 创建图片
    img = Image.new('RGBA', (WIDTH, img_height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # 绘制文本
    x_offset = 20
    y_offset = 30
    for i, line in enumerate(lines):
        draw.text((x_offset, y_offset + line_height * i), line, fill=TEXT_COLOR, font=font)
    
    # 保存图片
    try:
        img.save(output_path)
        return output_path
    except Exception as e:
        print(f"保存图片失败: {e}")
        return None

# 测试
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        text = sys.argv[1]
        result = text_to_image(text)
        if result:
            print(result)
        else:
            print("转换失败")
    else:
        print("请提供要转换的文本内容") 