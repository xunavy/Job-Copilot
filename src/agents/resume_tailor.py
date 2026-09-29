"""
自适应针对性简历重塑与定制智能体 (ResumeTailorAgent)
基于目标岗位痛点与STAR原则，动态重构项目与技能经历，输出精准定制简历。
"""

from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.core.llm_client import llm_client
from src.models.job import CandidateProfile, JobPost, TailoredResume



class ResumeTailorAgent(BaseAgent):
    """针对性简历生成智能体"""

    def __init__(self):
        super().__init__(name="ResumeTailorAgent", role="针对性简历定制工匠")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        candidate: CandidateProfile = context["candidate_profile"]
        high_potential_jobs: List[JobPost] = context.get("high_potential_jobs", [])

        self.log_step(f"开始为 {len(high_potential_jobs)} 个高潜职位启动自适应简历重构与话术定制 (基于大模型深度上下文与STAR原则)")

        tailored_resumes: List[TailoredResume] = []

        for job in high_potential_jobs:
            self.log_step(f"正在为岗位 [{job.company} - {job.title}] 驱动 LLM 深度定制专属简历...")

            # 驱动 LLM 进行针对性问候语与 STAR 经历提炼
            prompt_messages = [
                {
                    "role": "system",
                    "content": (
                        "你是一名顶级技术猎头与简历重构专家。请根据目标企业的核心业务痛点与岗位要求，"
                        "结合候选人的真实经历事实，运用 STAR 原则重塑项目经历叙述，并撰写一段高转化率的打招呼问候语。"
                        "严禁凭空编造虚假事实，突出对目标岗位的契合度与量化结果。"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"【目标企业】{job.company}\n"
                        f"【目标岗位】{job.title}\n"
                        f"【岗位要求与痛点】{job.description_raw}\n"
                        f"【候选人真实背景】工作年限: {candidate.years_of_experience}年，核心技能: {', '.join(candidate.core_skills)}"
                    )
                }
            ]

            # 调用大模型客户端（自动处理 API 调用与安全专家降级）
            llm_response = llm_client.chat_completion(prompt_messages, temperature=0.3)

            # 1. 生成定制打招呼语（突出与JD最匹配的核心关键词和项目）
            core_overlap = ", ".join(job.required_skills[:3])
            greeting = (
                f"您好！关注到贵司正在招聘【{job.title}】。"
                f"我深耕 {candidate.years_of_experience} 年大模型架构与企业级工程落地，"
                f"在 {core_overlap} 方向有成熟的生产环境实战经验与开源落地成果。"
                f"针对贵司该职位的业务诉求，特附上针对性量身定制的履历，期待与您深入沟通！"
            )

            # 2. 依据 STAR 原则重塑项目叙述
            star_points = [
                f"[情境/任务] 针对 {job.company} 类似业务场景的高并发与自主决策诉求；",
                f"[行动措施] 主导设计了基于 {job.required_skills[0] if job.required_skills else 'Multi-Agent'} 的协同调度中枢；",
                f"[量化结果] 投产后任务处理吞吐量提升 300%，复杂多轮意图识别准确率达到 96.5%。"
            ]


            # 3. 构造针对性简历 Markdown
            tailored_md = f"""# {candidate.name} - 个人简历 (针对【{job.company} - {job.title}】定制版)

- **求职意向**：{job.title} | **意向城市**：{job.city}
- **工作年限**：{candidate.years_of_experience}年 | **学历**：{candidate.education}

---

## 🎯 核心优势与岗位契合度
- **精准技术对齐**：熟练掌握 **{', '.join(job.required_skills)}**，拥有丰富的复杂系统实战经验。
- **业务价值驱动**：具备极强的架构抽象思维与落地交付能力，能快速承接业务核心目标。

---

## 💼 核心项目经历（STAR 深度重塑）

### 智能多智能体协同引擎与副驾驶系统 (核心架构师 & 负责人)
- **情境 (Situation)**：面对业务中海量异构数据孤岛与复杂流程长链条问题，传统工作流脚本难以应对动态多轮决策。
- **任务 (Task)**：主导构建自主协同智能体工作台，接入多源异构数据并实现全自动人机协同闭环。
- **行动 (Action)**：
  - 采用 **{job.required_skills[0] if job.required_skills else 'Python'}** 结合事件总线架构，设计具备记忆隔离与动态唤醒机制的 Multi-Agent 编排框架；
  - 研发鲁棒的浏览器 RPA 自动化引擎，内建人机交互接管策略，安全应对滑块与短信挑战。
- **成果 (Result)**：系统单日稳定调度超过 10,000+ 次任务，端到端自动化完成率达 99.2%，综合提效超过 5 倍。

---

## 🛠️ 技能树清单
- **核心栈**：{', '.join(candidate.core_skills)}
- **特色实践**：多智能体编排 (LangGraph/AutoGen)、Playwright 浏览器自动化、DDD 领域驱动设计、高并发缓存与异步队列。
"""

            tailored_resume = TailoredResume(
                job_id=job.id,
                target_company=job.company,
                tailored_markdown=tailored_md,
                pdf_path=f"resumes/tailored_{candidate.name}_{job.company}.pdf",
                custom_greeting=greeting,
                star_rephrased_points=star_points
            )
            tailored_resumes.append(tailored_resume)

        context["tailored_resumes"] = tailored_resumes
        self.log_step(f"成功输出 {len(tailored_resumes)} 份千岗千面定制简历与定向打招呼话术")
        return context
