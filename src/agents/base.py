"""
多智能体协同基类与通信协议
定义每个专业智能体的标准生命周期、输入输出标准契约与日志跟踪。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")


class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.logger = logging.getLogger(self.name)
        
    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能体执行入口
        :param context: 包含执行任务所需的全局上下文与数据
        :return: 智能体更新后的数据结果
        """
        pass
    
    def log_step(self, message: str) -> None:
        """记录智能体动作"""
        self.logger.info(f"[{self.role}] {message}")
