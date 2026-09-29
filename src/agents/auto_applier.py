"""
自动化投递与简历上传智能体 (AutoApplierAgent)
基于 Playwright 本地浏览器接管与人机协同机制，安全高效完成打招呼、投递与附件上传。
"""

import time
from typing import Any, Dict, List
from src.agents.base import BaseAgent
from src.models.job import ApplicationStatus, JobPost, TailoredResume


class AutoApplierAgent(BaseAgent):
    """自动化投递与上传执行智能体"""

    def __init__(self):
        super().__init__(name="AutoApplierAgent", role="自动化投递领航员")
        self.applied_record: set = set()

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        high_potential_jobs: List[JobPost] = context.get("high_potential_jobs", [])
        tailored_resumes: List[TailoredResume] = context.get("tailored_resumes", [])
        
        resume_map = {r.job_id: r for r in tailored_resumes}
        application_results: List[Dict[str, Any]] = []

        self.log_step(f"开始启动本地自动化安全投递流水线，待投递目标数量: {len(high_potential_jobs)}")

        for job in high_potential_jobs:
            if job.id in self.applied_record:
                self.log_step(f"跳过职位 [{job.company} - {job.title}]：检测到近期已投递，触发防重安全锁")
                continue

            custom_resume = resume_map.get(job.id)
            if not custom_resume:
                continue

            # 模拟 Playwright 浏览器接管投递逻辑
            result = self._execute_safe_apply(job, custom_resume)
            application_results.append(result)
            self.applied_record.add(job.id)

        context["application_results"] = application_results
        self.log_step(f"本次自动化投递批次完成，成功投递/发起沟通: {len(application_results)} 家")
        return context

    def _execute_safe_apply(self, job: JobPost, resume: TailoredResume) -> Dict[str, Any]:
        """执行安全投递与人机协同接管逻辑"""
        self.log_step(f"正在自动化访问平台并打开岗位页面: {job.title} @ {job.company} ({job.source.value})")
        
        # 1. 拟人化延迟（模拟真人鼠标与阅读间隔）
        time.sleep(0.3)
        
        # 2. 模拟触发平台风控检测判定
        simulated_risk_challenge = (job.source.value == "boss_zhipin")
        
        if simulated_risk_challenge:
            self.log_step("⚠️ 触发平台滑块/安全人机验证！进入 [人机协同 (Human-in-the-Loop)] 模式...")
            self.log_step(">> [系统提示] 已向本地桌面发送接管通知，等待用户在本地浏览器完成滑块拖动...")
            # 真实场景中此处等待用户完成滑动，这里模拟用户本地成功完成
            self.log_step("✅ 人机验证已通过！自动化投递智能体恢复执行控制权。")

        # 3. 填入定向沟通话术与上传定制简历
        self.log_step(f"发送定向问候语: '{resume.custom_greeting[:35]}...'")
        self.log_step(f"自动化挂载上传针对性定制简历附件: [{resume.pdf_path}]")
        self.log_step(f"🎉 投递成功！状态更新为: 【{ApplicationStatus.COMMUNICATING.value}】")

        return {
            "job_id": job.id,
            "company": job.company,
            "title": job.title,
            "status": ApplicationStatus.COMMUNICATING.value,
            "greeting_sent": resume.custom_greeting,
            "resume_path": resume.pdf_path,
            "source": job.source.value
        }
