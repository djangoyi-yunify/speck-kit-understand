---
description: 根据自然语言功能描述创建或更新功能规格说明。
handoffs: 
  - label: 构建技术计划
    agent: speckit.plan
    prompt: Create a plan for the spec. I am building with...
  - label: 明确规格需求
    agent: speckit.clarify
    prompt: Clarify specification requirements
    send: true
scripts:
  sh: scripts/bash/create-new-feature.sh "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 "{ARGS}"
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前，你**必须**考虑用户输入（如果不为空）。

## 概述

用户在触发消息中 `/speckit.specify` 之后输入的文本**即**为功能描述。即使下方字面出现 `{ARGS}`，也请假设该描述在此对话中始终可用。除非用户提供了空命令，否则不要要求用户重复。

基于该功能描述，请执行以下操作：

1. **生成一个简洁的简称**（2-4 个词）用于分支：
   - 分析功能描述并提取最有意义的关键词
   - 创建一个能捕捉功能本质的 2-4 词简称
   - 尽可能使用“动词-名词”格式（例如 "add-user-auth", "fix-payment-bug"）
   - 保留技术术语和缩写（OAuth2, API, JWT 等）
   - 保持简洁但具有足够的描述性，以便一眼就能理解该功能
   - 示例：
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. 通过使用 `--short-name`（以及 `--json`）运行脚本来**创建功能分支**，并且不要传递 `--number`（脚本会自动检测所有分支和 spec 目录中下一个可用的全局编号）：

   - Bash 示例：`{SCRIPT} --json --short-name "user-auth" "Add user authentication"`
   - PowerShell 示例：`{SCRIPT} -Json -ShortName "user-auth" "Add user authentication"`

   **重要提示**：
   - 不要传递 `--number` —— 脚本会自动确定正确的下一个编号
   - 始终包含 JSON 标志（Bash 使用 `--json`，PowerShell 使用 `-Json`），以便可靠地解析输出
   - 每个功能只能运行此脚本一次
   - JSON 作为输出在终端中提供 —— 始终参考它以获取所需的实际内容
   - JSON 输出将包含 BRANCH_NAME 和 SPEC_FILE 路径
   - 对于参数中的单引号，如 "I'm Groot"，请使用转义语法：例如 'I'\''m Groot'（或者尽可能使用双引号："I'm Groot"）

3. 加载 `templates/spec-template.md` 以了解所需的章节。

4. 遵循此执行流程：

    1. 从输入中解析用户描述
       如果为空：错误 "No feature description provided"
    2. 从描述中提取关键概念
       识别：参与者、操作、数据、约束
    3. 对于不明确的方面：
       - 根据上下文和行业标准进行合理推测
       - 仅在以下情况下使用 [NEEDS CLARIFICATION: specific question] 标记：
         - 该选择显著影响功能范围或用户体验
         - 存在多种合理的解释且含义不同
         - 不存在合理的默认值
       - **限制：总共最多 3 个 [NEEDS CLARIFICATION] 标记**
       - 按影响程度优先处理澄清：范围 > 安全/隐私 > 用户体验 > 技术细节
    4. 填写用户场景与测试章节
       如果没有清晰的用户流程：错误 "Cannot determine user scenarios"
    5. 生成功能需求
       每个需求必须是可测试的
       对未指定的细节使用合理的默认值（在假设章节中记录假设）
    6. 定义成功标准
       创建可衡量、与技术无关的结果
       包括定量指标（时间、性能、容量）和定性指标（用户满意度、任务完成情况）
       每个标准必须在不涉及实现细节的情况下可验证
    7. 识别关键实体（如果涉及数据）
    8. 返回：SUCCESS（规格说明书已准备好进行规划）

5. 使用模板结构将规格说明书写入 SPEC_FILE，用从功能描述（参数）中得出的具体细节替换占位符，同时保留章节顺序和标题。

6. **规格说明书质量验证**：编写初始规格说明书后，根据质量标准进行验证：

   a. **创建规格质量检查清单**：使用检查清单模板结构，在 `FEATURE_DIR/checklists/requirements.md` 处生成检查清单文件，包含以下验证项：

```markdown
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
```

b. **运行验证检查**：对照每个检查清单项审查 spec：
      - 对于每个项目，判定其通过或失败
      - 记录发现的具体问题（引用相关的 spec 章节）

   c. **处理验证结果**：

      - **如果所有项目均通过**：将检查清单标记为完成，并继续第 6 步

      - **如果有项目失败（不包括 [NEEDS CLARIFICATION]）**：
        1. 列出失败的项目及具体问题
        2. 更新 spec 以解决每个问题
        3. 重新运行验证，直到所有项目通过（最多 3 次迭代）
        4. 如果 3 次迭代后仍未通过，在检查清单备注中记录剩余问题并警告用户

      - **如果存在 [NEEDS CLARIFICATION] 标记**：
        1. 从 spec 中提取所有 [NEEDS CLARIFICATION: ...] 标记
        2. **限制检查**：如果标记超过 3 个，仅保留 3 个最关键的（按范围/安全性/UX 影响），其余部分进行合理推测
        3. 对于每个需要澄清的问题（最多 3 个），按以下格式向用户展示选项：

```markdown
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
```

4. **关键 - 表格格式**：确保 markdown 表格格式规范：
   - 使用一致的间距并对齐管道符
   - 每个单元格内容周围应包含空格：`| Content |` 而非 `|Content|`
   - 表头分隔符必须包含至少 3 个连字符：`|--------|`
   - 测试表格在 markdown 预览中能否正确渲染
5. 按顺序对问题编号（Q1, Q2, Q3 - 最多 3 个）
6. 在等待回复前一次性提出所有问题
7. 等待用户回复所有问题的选择（例如："Q1: A, Q2: Custom - [details], Q3: B"）
8. 更新 spec，将每个 [NEEDS CLARIFICATION] 标记替换为用户选择或提供的答案
9. 所有澄清事项解决后重新运行验证

d. **更新 Checklist**：每次验证迭代后，更新 checklist 文件记录当前的通过/失败状态

7. 报告完成情况，包括分支名称、spec 文件路径、checklist 结果以及对下一阶段（`/speckit.clarify` 或 `/speckit.plan`）的准备情况。

**注意：** 该脚本在写入前会创建并检出新分支，并初始化 spec 文件。

## 通用指南

## 快速指南

- 关注用户需要**什么** (WHAT) 以及**为什么** (WHY)。
- 避免**如何**实现（不涉及技术栈、API、代码结构）。
- 面向业务相关方编写，而非开发人员。
- **不要**创建任何嵌入在 spec 中的 checklist。这将由单独的命令处理。

### 章节要求

- **强制章节**：每个功能必须完成
- **可选章节**：仅在与功能相关时包含
- 当章节不适用时，将其完全删除（不要保留为 "N/A"）

### 针对 AI 生成

当根据用户提示创建此 spec 时：

1. **进行有根据的推测**：利用上下文、行业标准和常见模式填补空白
2. **记录假设**：在假设章节记录合理的默认值
3. **限制澄清项**：最多 3 个 [NEEDS CLARIFICATION] 标记——仅用于以下关键决策：
   - 显著影响功能范围或用户体验
   - 存在多种合理解读且具有不同影响
   - 缺乏任何合理的默认值
4. **确定澄清优先级**：范围 > 安全/隐私 > 用户体验 > 技术细节
5. **像测试人员一样思考**：每个模糊的需求都应无法通过 "可测试且明确" 的 checklist 项
6. **常见需澄清的领域**（仅当不存在合理默认值时）：
   - 功能范围和边界（包含/排除特定用例）
   - 用户类型和权限（如果可能存在多种相互冲突的解读）
   - 安全/合规要求（涉及法律/财务影响时）

**合理默认值的示例**（不要询问这些内容）：

- 数据保留：该领域的行业标准做法
- 性能目标：除非另有说明，否则采用标准 Web/移动应用的预期值
- 错误处理：用户友好的提示信息及适当的回退机制
- 认证方式：Web 应用的标准基于会话或 OAuth2 方式
- 集成模式：使用适合项目的模式（Web 服务使用 REST/GraphQL，库使用函数调用，工具使用 CLI 参数等）

### 成功标准指南

成功标准必须是：

1. **可衡量**：包含具体指标（时间、百分比、数量、比率）
2. **技术无关**：不提及框架、语言、数据库或工具
3. **以用户为中心**：从用户/业务视角描述结果，而非系统内部细节
4. **可验证**：无需了解实现细节即可进行测试/验证

**正面示例**：

- "用户可以在 3 分钟内完成结账"
- "系统支持 10,000 个并发用户"
- "95% 的搜索在 1 秒内返回结果"
- "任务完成率提高 40%"

**反面示例**（关注实现细节）：

- "API 响应时间低于 200ms"（过于技术化，应使用 "用户即时看到结果"）
- "数据库可处理 1000 TPS"（实现细节，应使用面向用户的指标）
- "React 组件高效渲染"（特定于框架）
- "Redis 缓存命中率高于 80%"（特定于技术）