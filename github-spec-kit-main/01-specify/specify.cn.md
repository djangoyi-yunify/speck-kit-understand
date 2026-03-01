---
description: 根据自然语言功能描述创建或更新功能规格。
handoffs: 
  - label: 构建技术计划
    agent: speckit.plan
    prompt: 为规格创建计划。我正在使用...进行构建...
  - label: 明确规格需求
    agent: speckit.clarify
    prompt: 明确规格需求
    send: true
scripts:
  sh: scripts/bash/create-new-feature.sh --json "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 -Json "{ARGS}"
---

## 用户输入```text
$ARGUMENTS
```在继续之前，你**必须**考虑用户输入（如果不为空）。

## 概述

用户在触发消息中 `/speckit.specify` 后输入的文本**即为**功能描述。假设在本次对话中它始终可用，即使下方字面出现了 `{ARGS}`。除非用户提供了空命令，否则不要要求用户重复。

基于该功能描述，执行以下操作：

1. 为分支**生成简短名称**（2-4 个词）：
   - 分析功能描述并提取最有意义的关键词
   - 创建一个 2-4 个词的短名称，概括功能的精髓
   - 尽可能使用动宾格式（例如 "add-user-auth"、"fix-payment-bug"）
   - 保留技术术语和缩写（OAuth2、API、JWT 等）
   - 保持简洁，但要有足够的描述性以便一眼理解该功能
   - 示例：
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. **在创建新分支前检查现有分支**：

   a. 首先，获取所有远程分支以确保拥有最新信息：

   ```bash
git fetch --all --prune
```b. 为 short-name 查找所有来源中最高的功能编号：
   - 远程分支：`git ls-remote --heads origin | grep -E 'refs/heads/[0-9]+-<short-name>$'`
   - 本地分支：`git branch | grep -E '^[* ]*[0-9]+-<short-name>$'`
   - Specs 目录：检查匹配 `specs/[0-9]+-<short-name>` 的目录

c. 确定下一个可用的编号：
   - 从所有三个来源中提取编号
   - 找出最大的编号 N
   - 使用 N+1 作为新分支的编号

d. 使用计算出的编号和 short-name 运行脚本 `{SCRIPT}`：
   - 传入 `--number N+1` 和 `--short-name "your-short-name"` 以及功能描述
   - Bash 示例：`{SCRIPT} --json --number 5 --short-name "user-auth" "Add user authentication"`
   - PowerShell 示例：`{SCRIPT} -Json -Number 5 -ShortName "user-auth" "Add user authentication"`

**重要提示**：
- 检查所有三个来源（远程分支、本地分支、Specs 目录）以找到最大的编号
- 仅匹配具有精确 short-name 模式的分支/目录
- 如果未找到具有此 short-name 的现有分支/目录，则从编号 1 开始
- 每个功能只能运行此脚本一次
- JSON 在终端中作为输出提供 - 始终参考它以获取所需的实际内容
- JSON 输出将包含 BRANCH_NAME 和 SPEC_FILE 路径
- 对于参数中的单引号（如 "I'm Groot"），请使用转义语法：例如 'I'\''m Groot'（或者尽可能使用双引号："I'm Groot"）

3. 加载 `templates/spec-template.md` 以了解必需的章节。

4. 遵循此执行流程：

    1. 从 Input 解析用户描述
       如果为空：ERROR "No feature description provided"
    2. 从描述中提取关键概念
       识别：actors, actions, data, constraints
    3. 对于不明确的方面：
       - 根据上下文和行业标准进行合理推测
       - 仅在以下情况标记 [NEEDS CLARIFICATION: specific question]：
         - 该选择显著影响功能范围或用户体验
         - 存在具有不同含义的多种合理解释
         - 不存在合理的默认值
       - **限制：总共最多 3 个 [NEEDS CLARIFICATION] 标记**
       - 按影响优先处理澄清：scope > security/privacy > user experience > technical details
    4. 填充 User Scenarios & Testing 章节
       如果没有清晰的用户流程：ERROR "Cannot determine user scenarios"
    5. 生成 Functional Requirements
       每个需求必须是可测试的
       对未指定的细节使用合理的默认值（在 Assumptions 章节记录假设）
    6. 定义 Success Criteria
       创建可衡量的、与技术无关的结果
       包括定量指标（时间、性能、量）和定性衡量标准（用户满意度、任务完成度）
       每个标准必须在不涉及实现细节的情况下可验证
    7. 识别 Key Entities（如果涉及数据）
    8. 返回：SUCCESS (spec ready for planning)

5. 使用模板结构将规范写入 SPEC_FILE，用从功能描述（参数）中提取的具体细节替换占位符，同时保持章节顺序和标题不变。

6. **规范质量验证**：编写初始规范后，根据质量标准对其进行验证：

   a. **创建规范质量检查清单**：使用检查清单模板结构在 `FEATURE_DIR/checklists/requirements.md` 处生成一个检查清单文件，包含以下验证项：```markdown
# Specification Quality Checklist: [FEATURE NAME]
      
      **Purpose**: Validate specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]
      
      ## Content Quality
      
      - [ ] No implementation details (languages, frameworks, APIs)
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed
      
      ## Requirement Completeness
      
      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified
      
      ## Feature Readiness
      
      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No implementation details leak into specification
      
      ## Notes
      
      - Items marked incomplete require spec updates before `/speckit.clarify` or `/speckit.plan`
```b. **Run Validation Check**：对照每个 checklist item 审查 spec：
   - 对于每个 item，判定其通过或失败
   - 记录发现的具体问题（引用相关 spec 章节）

   c. **Handle Validation Results**：

      - **如果所有 item 均通过**：将 checklist 标记为完成并继续执行步骤 6

      - **如果 item 失败（不包括 [NEEDS CLARIFICATION]）**：
        1. 列出失败的 item 及具体问题
        2. 更新 spec 以解决每个问题
        3. 重新运行 validation 直到所有 item 通过（最多 3 次迭代）
        4. 如果 3 次迭代后仍然失败，在 checklist notes 中记录剩余问题并向用户发出警告

      - **如果 [NEEDS CLARIFICATION] 标记仍然存在**：
        1. 从 spec 中提取所有 [NEEDS CLARIFICATION: ...] 标记
        2. **LIMIT CHECK**：如果存在超过 3 个标记，仅保留 3 个最关键的（按 scope/security/UX 影响排序），其余部分进行合理推测
        3. 对于每个需要澄清的内容（最多 3 个），按以下格式向用户展示选项：```markdown
## Question [N]: [Topic]
           
           **Context**: [Quote relevant spec section]
           
           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]
           
           **Suggested Answers**:
           
           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |
           
           **Your choice**: _[Wait for user response]_
```4. **关键 - 表格格式**：确保 markdown 表格格式正确：
   - 使用一致的间距并对齐竖线
   - 每个单元格的内容周围应有空格：`| Content |` 而非 `|Content|`
   - 表头分隔符必须至少有3个破折号：`|--------|`
   - 测试表格在 markdown 预览中是否正确渲染
5. 按顺序编号问题（Q1、Q2、Q3 - 最多3个）
6. 在等待回复之前，一次性提出所有问题
7. 等待用户回复所有问题的选择（例如，“Q1: A, Q2: Custom - [details], Q3: B”）
8. 更新 spec，将每个 [NEEDS CLARIFICATION] 标记替换为用户选择或提供的答案
9. 所有澄清解决后重新运行验证

d. **更新 Checklist**：每次验证迭代后，使用当前的通过/失败状态更新 checklist 文件

7. 报告完成情况，包括分支名称、spec 文件路径、checklist 结果以及下一阶段（`/speckit.clarify` 或 `/speckit.plan`）的准备情况。

**注意：** 脚本会在写入前创建并检出新分支，并初始化 spec 文件。

## 通用指南

## 快速指南

- 关注用户需要**什么**以及**为什么**。
- 避免涉及如何实现（不要包含技术栈、APIs、代码结构）。
- 为业务相关方编写，而非开发人员。
- 不要创建嵌入在 spec 中的任何 checklist。那将是一个单独的命令。

### 章节要求

- **强制章节**：每个功能都必须完成
- **可选章节**：仅在与功能相关时包含
- 当章节不适用时，将其完全删除（不要保留为“N/A”）

### AI 生成指南

根据用户提示创建此 spec 时：

1. **做出有根据的推测**：利用上下文、行业标准和常见模式填补空白
2. **记录假设**：在 Assumptions 章节记录合理的默认值
3. **限制澄清数量**：最多 3 个 [NEEDS CLARIFICATION] 标记 - 仅用于以下关键决策：
   - 显著影响功能范围或用户体验
   - 具有多种合理解读且含义不同
   - 缺乏任何合理的默认值
4. **确定澄清优先级**：范围 > 安全/隐私 > 用户体验 > 技术细节
5. **像测试人员一样思考**：每个模糊的需求都应无法通过“可测试且明确”的 checklist 项
6. **常见需要澄清的领域**（仅当不存在合理默认值时）：
   - 功能范围和边界（包含/排除特定用例）
   - 用户类型和权限（如果可能存在多种冲突的解读）
   - 安全/合规要求（当具有法律/财务重要性时）

**合理默认值的示例**（不要询问这些）：

- 数据保留：该领域的行业标准做法
- 性能目标：标准 web/mobile 应用预期，除非另有说明
- 错误处理：带有适当兜底方案的用户友好消息
- 认证方法：web 应用的标准基于会话或 OAuth2 方式
- 集成模式：使用适合项目的模式（web 服务用 REST/GraphQL，库用函数调用，工具用 CLI args 等）

### 成功标准指南

成功标准必须是：

1. **可衡量**：包含具体指标（时间、百分比、数量、比率）
2. **技术无关**：不提及框架、语言、数据库或工具
3. **以用户为中心**：从用户/业务角度描述结果，而非系统内部
4. **可验证**：无需了解实现细节即可测试/验证

**良好示例**：

- “用户可以在 3 分钟内完成结账”
- “系统支持 10,000 个并发用户”
- “95% 的搜索在 1 秒内返回结果”
- “任务完成率提高 40%”

**错误示例**（关注实现）：

- “API 响应时间低于 200ms”（过于技术化，使用“用户即时看到结果”）
- “数据库可处理 1000 TPS”（实现细节，使用面向用户的指标）
- “React 组件渲染高效”（特定于框架）
- “Redis 缓存命中率高于 80%”（特定于技术）