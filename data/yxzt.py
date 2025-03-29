#!/usr/bin/env python3
import psutil
import time
import datetime
import os
import socket
import platform
from PIL import Image, ImageDraw, ImageFont
import sys
import io
import tempfile # <--- 新增导入 tempfile
import uuid     # <--- 新增导入 uuid 用于生成唯一文件名

# --- 配置 (保持不变) ---
FONT_SIZE = 14
LINE_SPACING = 4
PADDING = 20
BACKGROUND_COLOR = (25, 25, 25)
TEXT_COLOR = (230, 230, 230)
IMAGE_FORMAT = 'PNG' # 可以定义图片格式

# --- 助手函数 (保持不变) ---
# ... (format_bytes, format_uptime, create_bar, get_cpu_temperature, get_network_type 代码省略) ...
def format_bytes(size):
    power = 2**10; n = 0; power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size >= power and n < len(power_labels) -1: size /= power; n += 1
    return f"{size:.1f} {power_labels[n]}B"
def format_uptime(seconds):
    delta = datetime.timedelta(seconds=seconds); days = delta.days; hours, rem = divmod(delta.seconds, 3600); minutes, _ = divmod(rem, 60)
    parts = []; P=parts.append
    if days > 0: P(f"{days}天")
    if hours > 0: P(f"{hours}小时")
    if minutes > 0 or (days == 0 and hours == 0): P(f"{minutes}分钟")
    return " ".join(parts) if parts else "小于1分钟"
def create_bar(percent, length=15):
    if not 0 <= percent <= 100: percent = 0
    filled_length = int(length * percent // 100); bar = '■' * filled_length + '□' * (length - filled_length)
    return f"[{bar}]"
def get_cpu_temperature():
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
        for name, entries in temps.items():
            for entry in entries:
                if 'core' in entry.label.lower() or 'cpu' in entry.label.lower() or name in ('coretemp', 'k10temp', 'cpu_thermal'): return f"{entry.current:.1f}°C"
                if entries: return f"{entries[0].current:.1f}°C"
    return "N/A"
def get_network_type(interface_name):
    name_lower = interface_name.lower()
    if name_lower.startswith(('eth', 'en')): return "有线网络"
    if name_lower.startswith(('wlan', 'wl')): return "无线网络"
    if name_lower.startswith('lo'): return "虚拟网络"
    if name_lower.startswith(('docker', 'veth', 'br-')): return "虚拟/容器网络"
    return "未知类型"

# --- 主要数据获取函数 (保持不变) ---
def get_system_status_text():
    """获取所有系统状态信息并返回一个字符串列表。"""
    output_lines = []
    # System Info
    boot_time_timestamp = psutil.boot_time(); uptime_seconds = time.time() - boot_time_timestamp; uname = platform.uname(); py_version = platform.python_version()
    output_lines.extend(["┌── 系统信息 ────────────────────", "│", f"│ 运行时间: {format_uptime(uptime_seconds)}", f"│ Python版本: v{py_version}", f"│ 操作系统: {uname.system} {uname.release}", f"│ 主机名: {socket.gethostname()}", "│ "])
    # System Load
    cpu_cores = psutil.cpu_count(logical=True); 
    try:
        load1, load5, load15 = psutil.getloadavg(); safe_load = cpu_cores * 0.7
        output_lines.extend(["┌── 系统负载 ─────────────────────", f"│ 1分钟负载: {load1:.2f} {'✓' if load1 < safe_load else '✗'}", f"│ 5分钟负载: {load5:.2f} {'✓' if load5 < safe_load else '✗'}", f"│ 15分钟负载: {load15:.2f} {'✓' if load15 < safe_load else '✗'}"])
    except:
        output_lines.extend(["┌── 系统负载 ─────────────────────", "│ 无法获取系统负载信息"])
    output_lines.extend([f"│ CPU逻辑核心: {cpu_cores}", "│ "])
    
    # CPU Info
    cpu_freq = psutil.cpu_freq(); cpu_percent = psutil.cpu_percent(interval=0.1); cpu_model = platform.processor() or "N/A"
    physical_cores = psutil.cpu_count(logical=False); logical_cores = psutil.cpu_count(logical=True); process_count = len(psutil.pids())
    output_lines.extend(["┌── CPU信息 ────────────────────", f"│ CPU型号: {cpu_model}", f"│ 物理/逻辑核心: {physical_cores or 'N/A'}核 / {logical_cores or 'N/A'}线程", f"│ 当前主频: {cpu_freq.current:.0f} MHz" if cpu_freq else "│ 主频: N/A", f"│ CPU使用率: {create_bar(cpu_percent)} {cpu_percent:.1f}%", f"│ 进程总数: {process_count}", "│ "])
    
    # Memory Info
    mem = psutil.virtual_memory(); swap = psutil.swap_memory()
    output_lines.extend(["┌── 内存信息 ─────────────────────", f"│ 总内存: {format_bytes(mem.total)}", f"│ 已用内存: {format_bytes(mem.used)} {create_bar(mem.percent)} {mem.percent:.1f}%", f"│ 可用内存: {format_bytes(mem.available)}"])
    if swap.total > 0: output_lines.append(f"│ SWAP: {format_bytes(swap.used)}/{format_bytes(swap.total)} ({swap.percent:.1f}%)")
    else: output_lines.append("│ SWAP: 未启用")
    output_lines.append("│ ")
    
    # Disk Info
    output_lines.append("┌── 磁盘信息 ─────────────────────")
    partitions = psutil.disk_partitions(); added_disk_info = False
    for part in partitions:
        if 'loop' in part.device or part.fstype in ('squashfs', 'tmpfs', 'iso9660') or not os.path.exists(part.mountpoint): continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            if usage.total < 1 * (1024**3): continue
            if added_disk_info: output_lines.append("│")
            output_lines.extend([f"│ 挂载点: {part.mountpoint}", f"│ 总空间: {format_bytes(usage.total)}", f"│ 已用空间: {format_bytes(usage.used)} {create_bar(usage.percent)} {usage.percent:.1f}%", f"│ 可用空间: {format_bytes(usage.free)}"])
            added_disk_info = True
        except Exception as e: continue
    if not added_disk_info: output_lines.append("│ 未找到或无法读取主要磁盘信息。")
    output_lines.append("│ ")
    
    # Network Info - 简化版，不测量速度
    output_lines.append("┌── 网络信息 ─────────────────────")
    try:
        net_if_addrs = psutil.net_if_addrs(); added_net_info = False
        for interface, addrs in net_if_addrs.items():
            if interface == 'lo' or interface.startswith(('veth', 'br-', 'docker')): continue
            ip_addr, mac_addr = "N/A", "N/A"
            for addr in addrs:
                if addr.family == socket.AF_INET: ip_addr = addr.address
                elif addr.family == psutil.AF_LINK: mac_addr = addr.address
            if ip_addr != "N/A":  # 只显示有IP地址的接口
                if added_net_info: output_lines.append("│")
                output_lines.extend([f"│ 网卡名称: {interface}", f"│ IP地址: {ip_addr}", f"│ MAC地址: {mac_addr}"])
                added_net_info = True
        if not added_net_info: output_lines.append("│ 未找到活动的网络接口。")
    except:
        output_lines.append("│ 获取网络信息时出错")
    
    output_lines.append("└───────────────────────────────────")
    return output_lines

# --- 查找系统字体函数 (保持不变，安静模式) ---
def find_system_mono_font(font_size):
    """尝试查找并加载一个合适的系统自带等宽字体 (安静模式)。"""
    os_name = platform.system(); font = None
    font_names_to_try = []
    if os_name == "Windows": font_names_to_try = ["consola.ttf", "cour.ttf", "lucon.ttf"]
    elif os_name == "Darwin": font_names_to_try = ["Menlo.ttc", "Monaco.dfont", "Courier New.ttf"]
    elif os_name == "Linux": font_names_to_try = ["DejaVuSansMono.ttf", "LiberationMono-Regular.ttf", "NotoMono-Regular.ttf", "UbuntuMono-R.ttf", "DroidSansMono.ttf"]
    else: font_names_to_try = ["Courier New.ttf", "DejaVuSansMono.ttf"]
    for font_name in font_names_to_try:
        try: font = ImageFont.truetype(font_name, font_size); break
        except (IOError, OSError): continue
    return font

# --- 修改: 生成图片并保存到脚本所在目录，返回文件路径 ---
def generate_and_save_image_to_script_dir(lines, font_size=FONT_SIZE):
    """将文本行列表渲染到图片上，保存到脚本所在目录的cache文件夹，并返回该文件的绝对路径。"""

    try:
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 创建或清空cache文件夹
        cache_dir = os.path.join(script_dir, "cache")
        if os.path.exists(cache_dir):
            # 删除文件夹中的所有文件
            for file in os.listdir(cache_dir):
                file_path = os.path.join(cache_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"清理缓存文件失败: {e}")
        else:
            os.makedirs(cache_dir)

    except Exception as e:
        print(f"处理缓存目录失败: {e}")
        return None

    font = find_system_mono_font(font_size)
    if font is None: return None # 找不到字体则失败

    # 计算图片尺寸 (代码与之前类似，省略)
    draw = ImageDraw.Draw(Image.new('RGB', (1, 1))); max_width = 0; line_heights = []
    for line in lines:
        try:
            line_bbox = draw.textbbox((0, 0), line, font=font); line_width = line_bbox[2] - line_bbox[0]
            ascent, descent = font.getmetrics(); height = ascent + descent
            max_width = max(max_width, line_width); line_heights.append(height)
        except Exception: max_width = max(max_width, len(line) * font_size * 0.65); line_heights.append(font_size + LINE_SPACING)
    if not line_heights: return None
    total_height = sum(line_heights) + max(0, len(lines) - 1) * LINE_SPACING
    img_width = max_width + 2 * PADDING; img_height = total_height + 2 * PADDING

    # 创建图片并绘制文本
    img = Image.new('RGB', (int(img_width), int(img_height)), color=BACKGROUND_COLOR)
    d = ImageDraw.Draw(img)
    y_text = PADDING
    for i, line in enumerate(lines):
        try: d.text((PADDING, y_text), line, font=font, fill=TEXT_COLOR); y_text += line_heights[i] + LINE_SPACING
        except IndexError: continue

    try:
        # 生成唯一文件名
        unique_filename = f"status_{uuid.uuid4()}.{IMAGE_FORMAT.lower()}"
        # 构造完整路径（在cache文件夹中）
        full_script_path = os.path.join(cache_dir, unique_filename)

        # 保存图片
        img.save(full_script_path, format=IMAGE_FORMAT)

        # 返回保存后的文件绝对路径
        return full_script_path
    except Exception as e:
        print(f"错误：无法将图片保存到缓存目录: {e}")
        return None

# --- 修改: 供外部调用的主函数 ---
def generate_status_image_local_path():
    """
    获取系统状态文本，不再生成图片。
    """
    status_lines = get_system_status_text()
    if not status_lines:
        print("错误：未能获取到系统状态文本信息。")
        return None
    
    # 直接返回文本，不生成图片
    return "\n".join(status_lines)

# --- 主执行逻辑 (主要用于直接运行脚本进行测试) ---
if __name__ == "__main__":
    # 调用新的主函数获取系统状态文本
    status_text = generate_status_image_local_path()
    
    if status_text:
        try:
            print(status_text)
        except UnicodeEncodeError:
            # 处理GBK编码错误，将不能编码的字符替换为?
            print(status_text.encode('gbk', 'replace').decode('gbk'))
    else:
        print("未能成功获取系统状态信息。")