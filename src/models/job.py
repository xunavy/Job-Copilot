"""
职位与求职全流程核心数据模型
包含岗位模型、候选人画像模型、匹配评分模型、投递跟踪模型、面试复盘模型与能力提升规划模型。
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class JobSource(str, Enum):
    """职位来源枚举"""
    BOSS = "boss_zhipin"
    FIVE_ONE_JOB = "51job"
    LIEPIN = "liepin"
    LINKEDIN = "linkedin"
    WECHAT_MOMENTS = "wechat_moments"
    XIAOHONGSHU = "xiaohongshu"
    MANUAL = "manual_entry"


class ApplicationStatus(str, Enum):
    """应聘流转状态枚举"""
    DISCOVERED = "discovered"          # 发现新岗位
    MATCHED = "matched"                # 匹配通过
    TAILORED = "tailored"              # 针对性简历已就绪
    COMMUNICATING = "communicating"    # 已打招呼/沟通中
    APPLIED = "applied"                # 已正式投递/上传简历
    VIEWED = "viewed"                  # HR已查看简历
    INTERVIEW_ROUND_1 = "interview_1"  # 技术一面
    INTERVIEW_ROUND_2 = "interview_2"  # 架构/系统设计二面
    INTERVIEW_ROUND_3 = "interview_3"  # HR/终面
    OFFER = "offer"                    # 已获Offer
    REJECTED = "rejected"              # 淘汰或终止
    ARCHIVED = "archived"              # 已归档


class InterviewStage(str, Enum):
    """面试阶段分类"""
    TECH_SCREENING = "tech_screening"      # 技术初试/八股与项目基础
    TECH_DEEP_DIVE = "tech_deep_dive"      # 架构设计与系统深度攻关
    MANAGEMENT_HR = "management_hr"        # 行为面试/综合素质与HR谈判


class JobPost(BaseModel):
    """职位信息模型"""
    id: str = Field(..., description="全局唯一职位标识")
    title: str = Field(..., description="职位名称")
    company: str = Field(..., description="公司名称")
    city: str = Field(..., description="工作城市与区域")
    salary_range: str = Field(..., description="薪资范围（例如：25k-40k·15薪）")
    source: JobSource = Field(..., description="信息来源平台")
    source_url: Optional[str] = Field(None, description="原始岗位链接")
    source_contact: Optional[str] = Field(None, description="发帖人/猎头联系方式或微信")
    
    # 职位画像分析
    description_raw: str = Field(..., description="原始JD描述内容")
    required_skills: List[str] = Field(default_factory=list, description="必备硬性技术栈要求")
    preferred_skills: List[str] = Field(default_factory=list, description="加分技术要求")
    experience_years: int = Field(default=0, description="最低工作年限要求")
    education_required: str = Field(default="本科", description="学历门槛")
    risk_flags: List[str] = Field(default_factory=list, description="潜在风险提示（如：高频加班、外包）")
    
    published_at: str = Field(default="2026-09-28", description="岗位在招发布与验证时间")
    verified_active: bool = Field(default=True, description="是否经过真实在招状态有效性核验")
    created_at: datetime = Field(default_factory=datetime.now, description="记录抓取时间")



class CandidateProfile(BaseModel):
    """求职者个人主画像知识库"""
    name: str = Field(..., description="候选人姓名")
    target_roles: List[str] = Field(..., description="期望目标岗位")
    expected_salary_min: int = Field(..., description="最低期望薪资（k/月）")
    years_of_experience: int = Field(..., description="实际工作年限")
    education: str = Field(..., description="最高学历及院校")
    core_skills: List[str] = Field(..., description="核心优势技术栈")
    master_resume_md: str = Field(..., description="候选人全量主简历（Markdown）")
    project_highlights: List[Dict[str, str]] = Field(default_factory=list, description="高价值项目亮点库")


class MatchReport(BaseModel):
    """职位与候选人双向匹配评估报告"""
    job_id: str = Field(..., description="关联职位ID")
    score: int = Field(..., ge=0, le=100, description="综合契合度得分（0-100）")
    strengths: List[str] = Field(default_factory=list, description="匹配亮点与加分优势")
    gaps: List[str] = Field(default_factory=list, description="技能与经历短板缺口")
    recommendation: str = Field(..., description="投递建议（极力推荐/可尝试/不建议）")
    ats_keywords_hit: List[str] = Field(default_factory=list, description="命中的ATS核心关键词")


class TailoredResume(BaseModel):
    """自适应定制化简历"""
    job_id: str = Field(..., description="关联职位ID")
    target_company: str = Field(..., description="目标公司")
    tailored_markdown: str = Field(..., description="优化后的定制简历Markdown全文")
    pdf_path: Optional[str] = Field(None, description="导出的PDF文件本地绝对路径")
    custom_greeting: str = Field(..., description="针对该职位的精准打招呼用语")
    star_rephrased_points: List[str] = Field(default_factory=list, description="基于STAR法则重点重构的核心经历")


class InterviewReviewRecord(BaseModel):
    """面试针对性复盘与下一轮突击记录"""
    job_id: str = Field(..., description="关联职位ID")
    company: str = Field(..., description="公司名称")
    stage: InterviewStage = Field(..., description="面试轮次阶段")
    interview_date: datetime = Field(default_factory=datetime.now, description="面试时间")
    questions_and_answers: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="核心问答复盘（包含问题、求职者现场回答、评估得分、漏洞剖析）"
    )
    performance_score: int = Field(default=80, ge=0, le=100, description="现场表现自评/AI评分")
    next_round_prep: List[str] = Field(default_factory=list, description="下一轮重点押题与准备要点")
    urgent_skills_to_cram: List[str] = Field(default_factory=list, description="急需突击背诵或理解的知识点")


class SkillGapActionPlan(BaseModel):
    """反馈评估与技能差距行动计划"""
    job_id: str = Field(..., description="关联职位ID")
    final_feedback: str = Field(..., description="面试最终反馈或未通过归因")
    weakness_areas: List[str] = Field(default_factory=list, description="暴露的能力短板领域")
    learning_action_items: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="具体提升行动清单（包含：技能名称、学习资源推荐、落地实战任务、预估耗时）"
    )
    radar_update: Dict[str, int] = Field(
        default_factory=dict, 
        description="更新后的技能雷达指标分值"
    )
