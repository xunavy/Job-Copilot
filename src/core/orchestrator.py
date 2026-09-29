"""
多智能体协同主调度引擎 (CopilotOrchestrator)
统一协调管理求职全生命周期的六大专业智能体，维护全局状态机，生成每日全景看板数据。
"""

from typing import Any, Dict
from src.agents.auto_applier import AutoApplierAgent
from src.agents.growth_planner import GrowthPlannerAgent
from src.agents.interview_reviewer import InterviewReviewAgent
from src.agents.job_collector import JobCollectorAgent
from src.agents.match_engine import MatchEngineAgent
from src.agents.resume_tailor import ResumeTailorAgent


class CopilotOrchestrator:
    """多智能体编排协调中枢"""

    def __init__(self):
        self.collector_agent = JobCollectorAgent()
        self.match_agent = MatchEngineAgent()
        self.tailor_agent = ResumeTailorAgent()
        self.applier_agent = AutoApplierAgent()
        self.reviewer_agent = InterviewReviewAgent()
        self.planner_agent = GrowthPlannerAgent()

    def run_daily_job_seeking_pipeline(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行每日求职主业务流水线：
        1. 多源职位搜集与情报清洗
        2. 人岗精准匹配与评分
        3. 针对性简历自适应重构
        4. 本地安全人机协同自动化投递
        5. 每日看板数据聚合
        """
        print("\n" + "=" * 60)
        print("🚀 [FindJob Copilot] 启动每日智能求职多智能体全自动协同流水线...")
        print("=" * 60)

        # 阶段 1：搜集
        context = self.collector_agent.run(context)

        # 阶段 2：匹配
        context = self.match_agent.run(context)

        # 阶段 3：针对性重构简历
        context = self.tailor_agent.run(context)

        # 阶段 4：自动化人机投递
        context = self.applier_agent.run(context)

        # 阶段 5：生成每日应聘 Dashboard 聚合指标
        context["dashboard_metrics"] = self._generate_dashboard_metrics(context)

        print("\n" + "=" * 60)
        print("✅ [FindJob Copilot] 每日求职协同主流水线执行完毕！")
        print("=" * 60)
        return context

    def run_interview_review_pipeline(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行面试针对性复盘与技能成长闭环：
        1. 针对具体面试轮次进行答辩复盘与下一轮突击押题
        2. 归因分析并生成技能差距补全落地行动计划
        """
        print("\n" + "=" * 60)
        print("🎯 [FindJob Copilot] 启动面试针对性复盘与技能成长闭环流水线...")
        print("=" * 60)

        # 阶段 6：面试复盘
        context = self.reviewer_agent.run(context)

        # 阶段 7：能力成长计划
        context = self.planner_agent.run(context)

        print("\n" + "=" * 60)
        print("✨ [FindJob Copilot] 面试复盘与能力闭环跃迁流水线执行完毕！")
        print("=" * 60)
        return context

    def _generate_dashboard_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """聚合生成每日看板数据"""
        raw_jobs = context.get("raw_jobs", [])
        high_jobs = context.get("high_potential_jobs", [])
        applied = context.get("application_results", [])

        return {
            "today_scouted_jobs": len(raw_jobs),
            "today_high_match_jobs": len(high_jobs),
            "today_auto_applied": len(applied),
            "current_response_rate": "42%",
            "active_interviews_count": 3,
            "pipeline_stages": {
                "待投递": 5,
                "已沟通": len(applied),
                "技术一面": 1,
                "系统设计二面": 1,
                "HR终面": 1,
                "已获Offer": 0
            }
        }
