"""
FindJob Copilot 本地 Web API 与控制中心后端服务
基于 FastAPI 构建，提供全套业务 RESTful API 与系统全生命周期操作审计记录接口。
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

# 解决 Windows 控制台默认编码问题
for stream_name in ('stdout', 'stderr'):
    stream = getattr(sys, stream_name)
    if stream and hasattr(stream, 'reconfigure'):
        try:
            stream.reconfigure(encoding='utf-8')
        except Exception:
            pass

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.db.database import get_audit_logs, init_database
from src.services.job_service import JobService

# 初始化数据库结构与业务服务
init_database()
service = JobService()
service.seed_initial_data_if_empty()

app = FastAPI(
    title="FindJob Copilot API",
    description="智能求职多智能体副驾驶本地服务与审计中枢",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
INDEX_FILE = STATIC_DIR / "index.html"


# 请求体验证模型
class AddJobRequest(BaseModel):
    title: str
    company: str
    salary: str = "30k-50k"
    city: str = "北京/远程"
    description: str
    source: str = "manual_entry"


class UpdateStageRequest(BaseModel):
    stage: str


class ReviewRequest(BaseModel):
    company: str
    stage: str = "tech_screening"
    raw_qa: Optional[List[Dict[str, str]]] = None


# ==================== 页面托管 ====================

@app.get("/")
def get_dashboard_ui():
    """返回可视化求职看板与控制中心网页"""
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
    return {"message": "FindJob Copilot 启动成功，static/index.html 缺失"}


# ==================== 业务 API ====================

@app.get("/api/dashboard")
def get_dashboard():
    """获取仪表盘概览数据指标"""
    return service.get_dashboard_summary()


@app.get("/api/jobs")
def list_jobs(stage: Optional[str] = Query(None, description="按泳道阶段筛选")):
    """获取职位列表"""
    return service.list_jobs(stage=stage)


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    """获取单个职位详情与定制简历信息"""
    job = service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    return job


@app.post("/api/jobs")
def create_job(req: AddJobRequest):
    """手动录入新职位，自动触发智能体打分分析与审计"""
    job_id = service.add_custom_job(
        title=req.title,
        company=req.company,
        salary=req.salary,
        city=req.city,
        description=req.description,
        source=req.source
    )
    return {"success": True, "job_id": job_id, "message": "职位录入并分析完成"}


@app.post("/api/jobs/{job_id}/stage")
def update_stage(job_id: str, req: UpdateStageRequest):
    """更新职位所处阶段（状态流转）"""
    ok = service.update_job_stage(job_id, req.stage)
    if not ok:
        raise HTTPException(status_code=404, detail="职位未找到")
    return {"success": True, "message": f"状态成功变更为【{req.stage}】"}


@app.post("/api/jobs/{job_id}/tailor")
def tailor_resume(job_id: str):
    """为指定职位生成/重构定制简历"""
    try:
        res = service.tailor_resume_for_job(job_id)
        return {"success": True, "data": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/jobs/{job_id}/apply")
def apply_job(job_id: str):
    """对指定职位执行自动化安全投递"""
    try:
        res = service.apply_for_job(job_id)
        return {"success": True, "data": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class SearchPipelineRequest(BaseModel):
    keyword: Optional[str] = "AI Agent 架构师"
    city: Optional[str] = "北京/远程"


@app.post("/api/pipeline/daily")
def trigger_daily_pipeline(req: Optional[SearchPipelineRequest] = None):
    """触发每日多源嗅探与全量匹配流水线，支持自定义关键词与目标城市"""
    kw = req.keyword if req and req.keyword else "AI Agent 架构师"
    ct = req.city if req and req.city else "北京/远程"
    summary = service.run_full_discovery_pipeline(keyword=kw, city=ct)
    return {"success": True, "data": summary}



@app.post("/api/pipeline/review")
def trigger_interview_review(req: ReviewRequest):
    """提交面试复盘并获取下轮押题与技能提升计划"""
    qa_list = req.raw_qa or [
        {
            "question": "请阐述在多智能体系统中，如何保证 Agent 之间状态机流转的数据一致性？",
            "candidate_answer": "回答了事件总线机制，但对死循环熔断提及较少。"
        }
    ]
    res = service.submit_interview_review(
        company=req.company,
        stage_str=req.stage,
        qa_list=qa_list
    )
    return {"success": True, "data": res}


# ==================== 核心审计 API ====================

@app.get("/api/audit/logs")
def get_system_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    action: Optional[str] = Query(None, description="按动作代码过滤")
):
    """
    获取系统所有操作审计日志（不可篡改流水追踪）
    """
    logs = get_audit_logs(limit=limit, action_filter=action)
    return {
        "total": len(logs),
        "logs": logs
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 65)
    print("🚀 [FindJob Copilot] 本地多智能体全功能服务启动...")
    print("👉 WebUI 控制台地址: http://127.0.0.1:8000")
    print("📜 审计日志与API文档: http://127.0.0.1:8000/docs")
    print("=" * 65 + "\n")
    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, reload=False)
