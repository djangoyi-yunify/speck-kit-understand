---
description: 使用计划模板执行实施规划 Workflow，以生成设计产物。
handoffs: 
  - label: 创建 Tasks
    agent: speckit.tasks
    prompt: 将计划拆分为 Tasks
    send: true
  - label: 创建 Checklist
    agent: speckit.checklist
    prompt: 为以下领域创建 Checklist...
scripts:
  sh: scripts/bash/setup-plan.sh --json
  ps: scripts/powershell/setup-plan.ps1 -Json
agent_scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
---

## 用户输入```text
$ARGUMENTS
```如果用户输入不为空，在继续之前你**必须**对其进行考量。

## 大纲

1. **设置**：从仓库根目录运行 `{SCRIPT}` 并解析 JSON 以获取 FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH。对于参数中的单引号，例如 "I'm Groot"，使用转义语法：例如 'I'\''m Groot'（或者如果可能，使用双引号："I'm Groot"）。

2. **加载上下文**：读取 FEATURE_SPEC 和 `/memory/constitution.md`。加载 IMPL_PLAN 模板（已复制）。

3. **执行计划工作流**：遵循 IMPL_PLAN 模板中的结构执行以下操作：
   - 填充 Technical Context（将未知项标记为 "NEEDS CLARIFICATION"）
   - 根据 constitution 填充 Constitution Check 部分
   - 评估 gates（如果违规且无正当理由，则报 ERROR）
   - Phase 0：生成 research.md（解决所有 NEEDS CLARIFICATION）
   - Phase 1：生成 data-model.md, contracts/, quickstart.md
   - Phase 1：通过运行 agent script 更新 agent context
   - 设计后重新评估 Constitution Check

4. **停止并报告**：命令在 Phase 2 规划后结束。报告 branch、IMPL_PLAN 路径和生成的 artifacts。

## 阶段

### Phase 0：大纲与研究

1. 从上面的 **Technical Context 中提取未知项**：
   - 对于每个 NEEDS CLARIFICATION → 研究任务
   - 对于每个 dependency → 最佳实践任务
   - 对于每个 integration → 模式任务

2. **生成并分发研究 agents**：```text
For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
```3. **整合发现** 到 `research.md` 中，使用以下格式：
   - Decision: [选择了什么]
   - Rationale: [为什么选择]
   - Alternatives considered: [评估过哪些其他方案]

**输出**: 已解决所有 NEEDS CLARIFICATION 的 research.md

### Phase 1: 设计与契约

**前置条件:** `research.md` 已完成

1. **从功能规格中提取实体** → `data-model.md`:
   - 实体名称、字段、关系
   - 需求中的验证规则
   - 状态转换（如适用）

2. **定义接口契约** (如果项目有外部接口) → `/contracts/`:
   - 确定项目向用户或其他系统暴露哪些接口
   - 记录适合该项目类型的契约格式
   - 示例：库的公开 API、CLI 工具的命令 Schema、Web 服务的端点、解析器的语法、应用程序的 UI 契约
   - 如果项目纯属内部使用（构建脚本、一次性工具等），则跳过

3. **Agent 上下文更新**:
   - 运行 `{AGENT_SCRIPT}`
   - 这些脚本会检测当前使用的是哪个 AI Agent
   - 更新相应的 Agent 特定上下文文件
   - 仅添加当前计划中的新技术
   - 保留标记之间的手动添加内容

**输出**: data-model.md, /contracts/*, quickstart.md, agent-specific 文件

## 关键规则

- 使用绝对路径
- 若关卡失败或有未解决的澄清项，则报错