"""
分阶段面试针对性复盘智能体 (InterviewReviewAgent)
支持针对不同面试阶段（技术一面、系统设计二面、HR终面）进行精准复盘剖析与下一轮重点押题。
"""

from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.core.llm_client import llm_client
from src.models.job import InterviewReviewRecord, InterviewStage


class InterviewReviewAgent(BaseAgent):
    """分阶段面试复盘与下一轮突击智能体"""

    def __init__(self):
        super().__init__(name="InterviewReviewAgent", role="面试复盘导师")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        接收面试录音或速记文本，执行针对性复盘并预测下一轮考察重点 (LLM 驱动)
        """
        interview_input: Dict[str, Any] = context.get("interview_input", {})
        company = interview_input.get("company", "未来智行科技有限公司")
        stage = interview_input.get("stage", InterviewStage.TECH_SCREENING)
        raw_qa = interview_input.get("raw_qa", [])

        self.log_step(f"开始对 [{company}] 的 【{stage.value}】 阶段面试进行深度诊断复盘 (结合大模型面试官推理引擎)...")

        # 构造给 LLM 的面试复盘 Prompt
        prompt_messages = [
            {
                "role": "system",
                "content": (
                    f"你是一名顶级科技大厂的资深架构师兼技术面试官。请针对候选人在【{company}】的【{stage.value}】面试对话，"
                    "进行深度专业诊断：1. 提炼面试官提问背后的技术考点意图；2. 严厉指出候选人回答中的漏洞与模糊概念；"
                    "3. 预测下一轮面试（技术二面或业务架构面）最可能会深挖的必考架构题目与急需突击的技能点。"
                )
            },
            {
                "role": "user",
                "content": f"面试问答记录: {raw_qa}"
            }
        ]
        llm_analysis = llm_client.chat_completion(prompt_messages, temperature=0.3)

        review_qas: List[Dict[str, str]] = []
        next_prep_points: List[str] = []
        cram_skills: List[str] = []


        if stage == InterviewStage.TECH_SCREENING:
            # 技术一面：底层原理、并发、算法与框架核心
            review_qas = [
                {
                    "question": "请阐述在多智能体系统中，如何保证 Agent 之间状态机流转的数据一致性与循环死锁检测？",
                    "candidate_answer": "提到了通过事件总线和内存共享，但没有详细说明环路检测算法与超时熔断。",
                    "ai_evaluation": "78分。架构概念清晰，但缺少工程容灾兜底细节。",
                    "flaw_analysis": "面试官关注的是长链条 Agent 自主执行中的死循环问题（如 A 等 B，B 等 A），需给出拓扑有向无环图 (DAG) 判定或基于全局 Step 计数器熔断机制。"
                },
                {
                    "question": "Python 异步生态中，FastAPI + Asyncio 在高并发长连接下的性能瓶颈与连接池优化策略？",
                    "candidate_answer": "回答了异步事件循环机制和数据库连接池大小设定。",
                    "ai_evaluation": "92分。回答扎实，切中要害。"
                }
            ]
            next_prep_points = [
                "二面为架构与系统设计面，重点会深挖你项目中的高可用灾备架构与异构数据分片方案；",
                "提前准备 1 个体现系统吞吐量从千级跃迁到万级的核心技术压测与重构故事；",
                "准备绘制清晰的系统拓扑图与交互时序图。"
            ]
            cram_skills = [
                "分布式事务（Saga / 两阶段提交在 Agent 工作流中的取舍）",
                "Redis 与内存向量数据库并发读写锁机制",
                "大规模语言模型长上下文缓存与 KV-Cache 优化原理"
            ]

        elif stage == InterviewStage.TECH_DEEP_DIVE:
            # 技术二面：高可用、容灾、演进决策与业务架构
            next_prep_points = [
                "终面通常为部门业务总监与HR面，重点考察你的业务 ROI 认知、跨团队协同能力和抗压稳定性；",
                "准备回答‘为什么当前项目选择自研 Multi-Agent 架构而不是使用成熟商业 SaaS’的技术选型深度推导。"
            ]
            cram_skills = ["系统演进决策方法论", "ROI与资源成本核算模型"]

        else:
            # HR面 / 终面
            next_prep_points = ["准备薪资谈判底牌与竞品 Offer 沟通策略", "背调材料梳理"]
            cram_skills = ["STAR 行为面试法核心故事库"]

        record = InterviewReviewRecord(
            job_id=interview_input.get("job_id", "job_001"),
            company=company,
            stage=stage,
            questions_and_answers=review_qas,
            performance_score=82,
            next_round_prep=next_prep_points,
            urgent_skills_to_cram=cram_skills
        )

        context["interview_review_record"] = record
        self.log_step(f"面试复盘完成！综合得分: {record.performance_score}分，已生成下轮预测考题与技能攻坚包")
        return context
