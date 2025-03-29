#!/usr/bin/env python3
"""
插件名称: MyPlugin
版本: 1.0.0
描述: 这是一个插件模板，用于展示基本的插件结构和功能
作者: Your Name
许可证: MIT
"""

import os
import sys
import time
import logging
import argparse
from typing import Dict, List, Any, Optional, Union

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MyPlugin")

# 插件配置
DEFAULT_CONFIG = {
    "interval": 60,  # 执行间隔(秒)
    "output_format": "text",  # 输出格式: text, json, html
    "debug": False,  # 是否开启调试模式
}

class MyPlugin:
    """插件主类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化插件
        
        Args:
            config: 插件配置字典，覆盖默认配置
        """
        # 合并配置
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
            
        # 初始化插件状态
        self.running = False
        self.data = {}
        
        # 如果开启调试模式，设置日志级别为DEBUG
        if self.config["debug"]:
            logger.setLevel(logging.DEBUG)
            
        logger.debug(f"插件初始化完成，配置: {self.config}")
        
    def start(self) -> None:
        """启动插件"""
        if self.running:
            logger.warning("插件已经在运行中")
            return
            
        self.running = True
        logger.info("插件已启动")
        
        try:
            while self.running:
                self._run_once()
                time.sleep(self.config["interval"])
        except KeyboardInterrupt:
            logger.info("收到中断信号，插件停止运行")
        except Exception as e:
            logger.error(f"插件运行出错: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self) -> None:
        """停止插件"""
        self.running = False
        logger.info("插件已停止")
    
    def _run_once(self) -> None:
        """执行一次插件逻辑"""
        logger.debug("开始执行插件逻辑")
        
        try:
            # 1. 收集数据
            self.data = self._collect_data()
            
            # 2. 处理数据
            processed_data = self._process_data(self.data)
            
            # 3. 输出结果
            output = self._format_output(processed_data)
            
            # 4. 返回或展示结果
            self._handle_output(output)
            
        except Exception as e:
            logger.error(f"执行插件逻辑时出错: {e}")
            if self.config["debug"]:
                import traceback
                logger.debug(traceback.format_exc())
    
    def _collect_data(self) -> Dict[str, Any]:
        """收集数据
        
        Returns:
            包含收集到的数据的字典
        """
        # 这里实现具体的数据收集逻辑
        # 例如: 系统状态、网络请求、文件读取等
        logger.debug("正在收集数据...")
        
        # 示例: 收集系统信息
        data = {
            "timestamp": time.time(),
            "hostname": os.uname().nodename,
            "system": os.uname().sysname,
            "version": os.uname().release,
        }
        
        return data
    
    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理收集到的数据
        
        Args:
            data: 收集到的原始数据
            
        Returns:
            处理后的数据
        """
        # 这里实现数据处理逻辑
        # 例如: 计算、过滤、转换等
        logger.debug("正在处理数据...")
        
        # 示例: 添加一些计算结果
        processed_data = data.copy()
        processed_data["uptime"] = time.time() - os.stat('/proc/1').st_ctime
        processed_data["formatted_time"] = time.strftime("%Y-%m-%d %H:%M:%S", 
                                                       time.localtime(data["timestamp"]))
        
        return processed_data
    
    def _format_output(self, data: Dict[str, Any]) -> str:
        """根据配置格式化输出
        
        Args:
            data: 要格式化的数据
            
        Returns:
            格式化后的字符串
        """
        # 根据配置选择不同的输出格式
        logger.debug(f"正在格式化输出，格式: {self.config['output_format']}")
        
        if self.config["output_format"] == "json":
            import json
            return json.dumps(data, indent=2)
        
        elif self.config["output_format"] == "html":
            # 简单的HTML格式示例
            html = "<html><body><h1>插件输出</h1><table>"
            for key, value in data.items():
                html += f"<tr><td>{key}</td><td>{value}</td></tr>"
            html += "</table></body></html>"
            return html
        
        else:  # 默认文本格式
            text = "=== 插件输出 ===\n"
            for key, value in data.items():
                text += f"{key}: {value}\n"
            return text
    
    def _handle_output(self, output: str) -> None:
        """处理格式化后的输出
        
        Args:
            output: 格式化后的输出字符串
        """
        # 根据需要处理输出
        # 例如: 打印到控制台、写入文件、发送到服务器等
        logger.debug("正在处理输出...")
        
        # 示例: 打印到控制台
        print(output)
        
        # 示例: 写入文件
        # with open("plugin_output.txt", "w") as f:
        #     f.write(output)

# 命令行接口
def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="MyPlugin - 一个示例插件")
    
    parser.add_argument("--interval", type=int, default=DEFAULT_CONFIG["interval"],
                        help=f"执行间隔(秒)，默认: {DEFAULT_CONFIG['interval']}")
    
    parser.add_argument("--output-format", choices=["text", "json", "html"], 
                        default=DEFAULT_CONFIG["output_format"],
                        help=f"输出格式，默认: {DEFAULT_CONFIG['output_format']}")
    
    parser.add_argument("--debug", action="store_true", 
                        help="启用调试模式")
    
    parser.add_argument("--run-once", action="store_true",
                        help="只运行一次，不循环")
    
    return parser.parse_args()

# 主函数
def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 创建配置字典
    config = {
        "interval": args.interval,
        "output_format": args.output_format,
        "debug": args.debug,
    }
    
    # 创建插件实例
    plugin = MyPlugin(config)
    
    # 运行插件
    if args.run_once:
        plugin._run_once()
    else:
        plugin.start()

if __name__ == "__main__":
    main()
