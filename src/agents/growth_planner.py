"""
反馈评估与技能成长计划智能体 (GrowthPlannerAgent)
针对面试反馈剖析能力瓶颈，动态更新能力雷达图，输出切实可行的技能补全实战行动清单。
"""

from typing import Any, Dict
from src.agents.base import BaseAgent
from src.models.job import SkillGapActionPlan


class GrowthPlannerAgent(BaseAgent):
    """反馈评估与技能闭环跃迁智能体"""

    def __init__(self):
        super().__init__(name="GrowthPlannerAgent", role="技能成长规划官")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        interview_record = context.get("interview_review_record")
        company = interview_record.company if interview_record else "目标企业"
        
        self.log_step(f"开始基于 [{company}] 面试表现与反馈，进行能力差距诊断并制定技能补全跃迁计划...")

        # 1. 提炼薄弱点
        weaknesses = [
            "分布式 Agent 状态机循环死锁检测与自愈策略不够扎实",
            "生产级高并发异步事件循环底层的内存泄漏防范经验欠缺",
            "面试现场对业务 ROI 量化数字敏锐度可进一步加强"
        ]

        # 2. 制定落地行动清单
        action_items = [
            {
                "skill": "分布式 Agent 死锁检测与容灾熔断",
                "recommended_resource": "研读《Designing Data-Intensive Applications》第 8 章与 LangGraph 源码死循环熔断器实现",
                "practical_task": "为当前工程编写一个环路依赖检测与超时自动 fallback 的单元测试与中间件",
                "estimated_hours": "6小时"
            },
            {
                "skill": "Asyncio 高并发连接池深度调优",
                "recommended_resource": "Python 官方 Asyncio 内部运行机制深度解析与 uvloop 性能剖析",
                "practical_task": "针对模拟高频抓取场景，完成单机 2000 并发压力测试并输出优化基准报告",
                "estimated_hours": "8小时"
            },
            {
                "skill": "商业化与业务架构 ROI 表达优化",
                "recommended_resource": "麦肯锡金字塔原理在技术答辩中的应用指南",
                "practical_task": "用 STAR + ROI 结构重新归纳过往经历中为业务节省成本、提高转化率的具体案例",
                "estimated_hours": "4小时"
            }
        ]

        # 3. 动态更新能力雷达分值
        updated_radar = {
            "核心技术硬实力": 88,
            "系统架构设计": 85,
            "业务理解与ROI": 80,
            "工程容灾与排障": 78,
            "现场表达与沟通": 86
        }

        plan = SkillGapActionPlan(
            job_id=interview_record.job_id if interview_record else "job_001",
            final_feedback=f"在 [{company}] 的技术面试中表现优异，技术广度受认可；在超大规模分布式容错设计与高可用容灾实战细节上有进一步补强空间。",
            weakness_areas=weaknesses,
            learning_action_items=action_items,
            radar_update=updated_radar
        )

        context["skill_gap_action_plan"] = plan
        self.log_step("能力差距闭环成长计划已制定就绪，技能雷达图已同步更新！")
        return context
