"""
系统核心功能与审计日志全流程自动化测试
验证所有可交互 API 端点及底层不可篡改审计流水记录。
"""

import sys
import unittest
from fastapi.testclient import TestClient

from src.server import app
from src.db.database import get_audit_logs


class TestAuditAndApi(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_dashboard_and_jobs(self):
        """测试获取仪表盘指标与职位列表"""
        res = self.client.get("/api/dashboard")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("today_scouted_jobs", data)

        res_jobs = self.client.get("/api/jobs")
        self.assertEqual(res_jobs.status_code, 200)
        jobs = res_jobs.json()
        self.assertTrue(len(jobs) > 0, "职位列表应有初始样本数据")

    def test_02_add_custom_job_with_audit(self):
        """测试用户在界面录入新职位，并验证审计记录"""
        res = self.client.post("/api/jobs", json={
            "title": "大模型与 Agent 资深技术专家",
            "company": "测试前沿实验室",
            "salary": "45k-65k",
            "city": "北京/远程",
            "description": "负责企业级 Multi-Agent 架构设计，精通 Python、LangGraph 与系统分布式容灾。",
            "source": "wechat_moments"
        })
        self.assertEqual(res.status_code, 200)
        job_id = res.json()["job_id"]

        # 验证审计日志中记录了 ADD_JOB
        audit_logs = get_audit_logs(limit=5, action_filter="ADD_JOB")
        self.assertTrue(len(audit_logs) > 0)
        latest = audit_logs[0]
        self.assertEqual(latest["operator"], "求职者手动录入")
        self.assertEqual(latest["target_id"], job_id)

    def test_03_stage_flow_and_tailor_apply(self):
        """测试职位状态流转、自适应简历定制与安全投递"""
        # 获取第一个职位
        jobs = self.client.get("/api/jobs").json()
        target_job = jobs[0]
        job_id = target_job["id"]

        # 1. 状态流转
        res_stage = self.client.post(f"/api/jobs/{job_id}/stage", json={"stage": "技术一面"})
        self.assertEqual(res_stage.status_code, 200)

        # 2. 定制简历
        res_tailor = self.client.post(f"/api/jobs/{job_id}/tailor")
        self.assertEqual(res_tailor.status_code, 200)
        self.assertIn("tailored_markdown", res_tailor.json()["data"])

        # 3. 执行投递
        res_apply = self.client.post(f"/api/jobs/{job_id}/apply")
        self.assertEqual(res_apply.status_code, 200)

        # 验证审计流水
        tailor_logs = get_audit_logs(limit=5, action_filter="TAILOR_RESUME")
        self.assertTrue(len(tailor_logs) > 0)

        apply_logs = get_audit_logs(limit=5, action_filter="AUTO_APPLY")
        self.assertTrue(len(apply_logs) > 0)

    def test_04_interview_review_and_growth_audit(self):
        """测试面试复盘与能力雷达成长审计"""
        res = self.client.post("/api/pipeline/review", json={
            "company": "测试智行科技",
            "stage": "tech_screening",
            "raw_qa": [{"question": "Agent 死循环检测如何实现？", "candidate_answer": "回答了计数器熔断机制。"}]
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertIn("next_round_prep", data)
        self.assertIn("performance_score", data)

        # 验证审计流水
        rev_logs = get_audit_logs(limit=5, action_filter="INTERVIEW_REVIEW")
        self.assertTrue(len(rev_logs) > 0)

    def test_05_audit_api(self):
        """测试审计日志查询接口"""
        res = self.client.get("/api/audit/logs?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["total"] > 0)
        self.assertTrue(len(data["logs"]) > 0)


if __name__ == "__main__":
    unittest.main()
