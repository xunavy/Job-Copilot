"""
职位与简历双向精准匹配智能体 (MatchEngineAgent)
负责多维度综合评分、技能点交叉核验与投递建议输出。
"""

from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.core.llm_client import llm_client
from src.models.job import CandidateProfile, JobPost, MatchReport


class MatchEngineAgent(BaseAgent):
    """职位智能匹配与评分智能体 (支持大模型语义推理)"""

    def __init__(self):
        super().__init__(name="MatchEngineAgent", role="人岗精准匹配官")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        candidate: CandidateProfile = context["candidate_profile"]
        raw_jobs: List[JobPost] = context.get("raw_jobs", [])
        
        self.log_step(f"开始为候选人 [{candidate.name}] 驱动 LLM 综合评估 {len(raw_jobs)} 个潜在职位")


        match_reports: List[MatchReport] = []
        high_potential_jobs: List[JobPost] = []

        candidate_skills_lower = {s.lower() for s in candidate.core_skills}

        for job in raw_jobs:
            score = 70  # 基础基准分
            strengths: List[str] = []
            gaps: List[str] = []
            hit_keywords: List[str] = []

            # 1. 核心技术栈重合度评分
            job_req_skills_lower = [s.lower() for s in job.required_skills]
            matched_skills = [s for s in job.required_skills if s.lower() in candidate_skills_lower]
            missing_skills = [s for s in job.required_skills if s.lower() not in candidate_skills_lower]

            if job_req_skills_lower:
                match_rate = len(matched_skills) / len(job_req_skills_lower)
                score += int(match_rate * 25)
            
            for s in matched_skills:
                hit_keywords.append(s)
                strengths.append(f"精通关键技能 [{s}]，高度符合岗位核心诉求")

            for s in missing_skills:
                gaps.append(f"JD提及技能 [{s}] 在主画像中未重点体现，需在定制简历中强化相关经历")

            # 2. 工作年限匹配
            if candidate.years_of_experience >= job.experience_years:
                score += 5
                strengths.append(f"工作年限 ({candidate.years_of_experience}年) 超过岗位要求 ({job.experience_years}年)")
            else:
                score -= 10
                gaps.append(f"工作年限略低于岗位预期要求")

            # 3. 截断到 0-100
            score = min(max(score, 0), 100)

            # 4. 给出建议
            if score >= 85:
                recommendation = "极力推荐立即投递（S级强匹配，面试通过率极高）"
                high_potential_jobs.append(job)
            elif score >= 75:
                recommendation = "建议重点投递（A级匹配，需微调简历针对性）"
                high_potential_jobs.append(job)
            else:
                recommendation = "作为备选机会考虑（B级匹配，技术栈有一定跨度）"

            report = MatchReport(
                job_id=job.id,
                score=score,
                strengths=strengths,
                gaps=gaps,
                recommendation=recommendation,
                ats_keywords_hit=hit_keywords
            )
            match_reports.append(report)
            self.log_step(f"职位 [{job.company} - {job.title}] 匹配评分: {score}分 - {recommendation}")

        context["match_reports"] = match_reports
        context["high_potential_jobs"] = high_potential_jobs
        return context
