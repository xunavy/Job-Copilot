"""
FindJob Copilot 主入口与端到端运行演示
演示完整端到端多智能体协同求职流水线与分阶段复盘闭环。
"""

import json
import sys
import io

# 解决 Windows 控制台默认 GBK 编码输出时的编码异常
for stream_name in ('stdout', 'stderr'):
    stream = getattr(sys, stream_name)
    if stream and hasattr(stream, 'reconfigure'):
        try:
            stream.reconfigure(encoding='utf-8')
        except Exception:
            pass

from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.orchestrator import CopilotOrchestrator
from src.models.job import CandidateProfile, InterviewStage



def main():
    # 1. 模拟求职者基础主画像
    candidate = CandidateProfile(
        name="张三",
        target_roles=["大模型全栈架构师", "AI Agent 专家"],
        expected_salary_min=35,
        years_of_experience=6,
        education="985院校 计算机硕士",
        core_skills=[
            "Python", "LangGraph", "Multi-Agent", "FastAPI",
            "Playwright", "Docker", "微服务架构", "系统架构", "DDD"
        ],
        master_resume_md="""# 张三 - 全栈大模型与分布式系统架构师
6年高可用与AI系统研发经验，主导过多款高并发分布式系统与企业级 Agent 产品。
精通 Python、LangGraph、Multi-Agent 状态机编排与浏览器 RPA 自动化。
"""
    )

    orchestrator = CopilotOrchestrator()

    # 2. 初始上下文
    context = {
        "candidate_profile": candidate,
        "target_role": "AI Agent 架构师",
        "target_city": "北京/远程"
    }

    # 3. 运行第一条主干业务线：每日求职发现 -> 智能匹配 -> 简历重构 -> 自动化投递 -> 生成每日看板
    context = orchestrator.run_daily_job_seeking_pipeline(context)

    # 打印每日看板数据概览
    metrics = context["dashboard_metrics"]
    print("\n📊 =====【每日应聘与面试全景看板 Dashboard】=====")
    print(f"今日全网发现机会: {metrics['today_scouted_jobs']} 个")
    print(f"今日高匹配机会:   {metrics['today_high_match_jobs']} 个")
    print(f"今日已安全投递:   {metrics['today_auto_applied']} 家")
    print(f"当前沟通回复率:   {metrics['current_response_rate']}")
    print(f"当前推进中面试:   {metrics['active_interviews_count']} 场")
    print("求职流程泳道状态分布:", json.dumps(metrics["pipeline_stages"], ensure_ascii=False, indent=2))

    # 4. 模拟面试输入，运行第二条业务线：面试分阶段复盘 -> 考题预测 -> 技能差距补全行动计划
    context["interview_input"] = {
        "job_id": "job_sample_01",
        "company": "未来智行科技有限公司",
        "stage": InterviewStage.TECH_SCREENING,
    }

    context = orchestrator.run_interview_review_pipeline(context)

    # 打印复盘与技能成长计划
    review = context["interview_review_record"]
    plan = context["skill_gap_action_plan"]

    print("\n📝 =====【针对性面试复盘与下一轮突击指导】=====")
    print(f"复盘公司: {review.company} | 阶段: {review.stage.value} | 表现得分: {review.performance_score}分")
    print("下轮面试重点押题建议:")
    for idx, prep in enumerate(review.next_round_prep, 1):
        print(f"  {idx}. {prep}")
    print("急需突击背诵/理解技能点:")
    for skill in review.urgent_skills_to_cram:
        print(f"  - {skill}")

    print("\n🌱 =====【能力差距闭环成长行动清单】=====")
    print(f"面试综合评价: {plan.final_feedback}")
    print("落地行动项 (Action Items):")
    for item in plan.learning_action_items:
        print(f"  📌 技能: {item['skill']} (预估耗时: {item['estimated_hours']})")
        print(f"     学习资源: {item['recommended_resource']}")
        print(f"     实战任务: {item['practical_task']}")
    print("更新后能力雷达图分值:", json.dumps(plan.radar_update, ensure_ascii=False, indent=2))
    print("==================================================")


if __name__ == "__main__":
    main()
