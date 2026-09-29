# 贡献指南 (Contributing Guide)

感谢您对 **FindJob Copilot** 开源社区的关注与支持！我们欢迎所有开发者、求职者及 AI Agent 爱好者共同参与构建更加智能化、安全、有温度的个人求职助手。

---

## 🛠️ 本地开发环境准备

1. **克隆仓库**：
   ```bash
   git clone https://github.com/<your-username>/FindJob-Copilot.git
   cd FindJob-Copilot
   ```

2. **创建虚拟环境并安装依赖**：
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux / macOS
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

3. **初始化配置文件**：
   ```bash
   cp .env.example .env
   # 按需配置本地端口或模型参数
   ```

4. **运行全量自动化测试**：
   ```bash
   python -m unittest tests/test_audit_and_api.py
   ```

---

## 📋 提交规范 (Commit & Pull Request)

### 1. 分支管理策略
- `main` 分支为稳定主分支，受保护禁止直接 push；
- 新功能开发请基于 `main` 切出特性分支：`feat/your-feature-name`；
- 漏洞或缺陷修复请切出修复分支：`fix/issue-description`。

### 2. 提交信息规范 (Conventional Commits)
请遵循标准提交格式：
```
<type>(<scope>): <subject>
```
常用类别：
- `feat`: 新增特性或智能体能力
- `fix`: 修复已知缺陷或 Bug
- `docs`: 仅文档更新（README、架构图、说明）
- `test`: 补充或修正自动化测试
- `refactor`: 代码重构（不改变功能与 API）
- `perf`: 性能调优

### 3. 代码质量与安全守则
- **绝不提交任何真实 API Key、个人账号密码或私密路径**；
- 确保新增或修改的功能编写了对应的单元测试，且 `python -m unittest` 全部绿灯通过；
- 保障前后端接口交互的一致性，确保所有状态流转与关键操作均正确织入审计追踪引擎。
