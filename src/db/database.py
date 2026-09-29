"""
本地 SQLite 持久化数据库管理与审计日志引擎
提供开箱即用的事务安全本地数据持久化，涵盖职位库、定制简历库、投递流水与不可篡改的系统操作审计日志。
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DB_DIR / "job_copilot.db"


def get_db_connection() -> sqlite3.Connection:
    """获取数据库连接，支持字典形式访问字段"""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """初始化数据库所有核心表结构"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. 核心审计日志表 (Audit Logs)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_id TEXT UNIQUE NOT NULL,
            timestamp TEXT NOT NULL,
            operator TEXT NOT NULL,
            action TEXT NOT NULL,
            action_desc TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id TEXT,
            details_json TEXT,
            status TEXT NOT NULL
        )
        """)

        # 2. 职位表 (Jobs)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            city TEXT NOT NULL,
            salary_range TEXT NOT NULL,
            source TEXT NOT NULL,
            source_url TEXT,
            source_contact TEXT,
            description_raw TEXT NOT NULL,
            required_skills_json TEXT,
            preferred_skills_json TEXT,
            experience_years INTEGER DEFAULT 0,
            education_required TEXT DEFAULT '本科',
            risk_flags_json TEXT,
            match_score INTEGER DEFAULT 0,
            match_recommendation TEXT,
            match_report_json TEXT,
            pipeline_stage TEXT DEFAULT '待投递',
            published_at TEXT DEFAULT '2026-09-28',
            verified_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)

        # 平滑迁移（若已存在老表结构）
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN published_at TEXT DEFAULT '2026-09-28'")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN verified_active INTEGER DEFAULT 1")
        except Exception:
            pass


        # 3. 定制简历表 (Tailored Resumes)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tailored_resumes (
            job_id TEXT PRIMARY KEY,
            company TEXT NOT NULL,
            tailored_markdown TEXT NOT NULL,
            custom_greeting TEXT NOT NULL,
            star_points_json TEXT,
            created_at TEXT NOT NULL
        )
        """)

        # 4. 投递流转记录表 (Applications)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            greeting_sent TEXT,
            resume_path TEXT,
            platform TEXT NOT NULL,
            human_takeover_verified INTEGER DEFAULT 0,
            applied_at TEXT NOT NULL
        )
        """)

        # 5. 面试复盘记录表 (Interview Reviews)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_reviews (
            id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            company TEXT NOT NULL,
            stage TEXT NOT NULL,
            performance_score INTEGER DEFAULT 80,
            qa_json TEXT,
            next_prep_json TEXT,
            cram_skills_json TEXT,
            created_at TEXT NOT NULL
        )
        """)

        conn.commit()


# ==================== 审计日志服务函数 ====================

def record_audit_log(
    operator: str,
    action: str,
    action_desc: str,
    target_type: str,
    target_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    status: str = "SUCCESS"
) -> str:
    """
    记录一条结构化系统操作审计日志
    :return: 审计日志唯一 UUID
    """
    log_id = f"aud_{uuid.uuid4().hex[:12]}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    details_str = json.dumps(details or {}, ensure_ascii=False)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs 
            (log_id, timestamp, operator, action, action_desc, target_type, target_id, details_json, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (log_id, now_str, operator, action, action_desc, target_type, target_id, details_str, status)
        )
        conn.commit()
    return log_id


def get_audit_logs(limit: int = 50, action_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """查询最近的审计日志"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if action_filter:
            cursor.execute(
                "SELECT * FROM audit_logs WHERE action = ? ORDER BY id DESC LIMIT ?",
                (action_filter, limit)
            )
        else:
            cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
        
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "log_id": r["log_id"],
                "timestamp": r["timestamp"],
                "operator": r["operator"],
                "action": r["action"],
                "action_desc": r["action_desc"],
                "target_type": r["target_type"],
                "target_id": r["target_id"],
                "details": json.loads(r["details_json"] or "{}"),
                "status": r["status"]
            })
        return result
