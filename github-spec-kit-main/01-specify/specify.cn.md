---
description: 根据自然语言功能描述创建或更新功能规格说明书。
handoffs: 
  - label: 构建技术计划
    agent: speckit.plan
    prompt: 为功能规格创建计划。我正在使用...
  - label: 明确规格需求
    agent: speckit.clarify
    prompt: 明确规格需求
    send: true
scripts:
  sh: scripts/bash/create-new-feature.sh --json "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 -Json "{ARGS}"
---

## 用户输入

```text
$ARGUMENTS
```

在继续操作之前，你**必须**考虑用户输入（如果不为空）。

## 大纲

用户在触发消息中 `/speckit.specify` 后输入的文本**即**为功能描述。假设你在本次对话中始终拥有该内容，即使下方字面出现了 `{ARGS}`。除非用户提供了空命令，否则不要要求用户重复。

基于该功能描述，执行以下操作：

1. **生成一个简短的名称**（2-4 个单词）作为分支名：
   - 分析功能描述并提取最有意义的关键词
   - 创建一个 2-4 个单词的短名称，以体现功能的核心精髓
   - 尽可能使用“动作-名词”格式（例如 "add-user-auth", "fix-payment-bug"）
   - 保留技术术语和缩略词（OAuth2, API, JWT 等）
   - 保持简洁，但需具有足够的描述性以便一眼理解该功能
   - 示例：
     - "我想添加用户认证" → "user-auth"
     - "实现 API 的 OAuth2 集成" → "oauth2-api-integration"
     - "创建分析仪表板" → "analytics-dashboard"
     - "修复支付处理超时错误" → "fix-payment-timeout"

2. **在创建新分支之前检查现有分支**：

   a. 首先，拉取所有远程分支以确保我们拥有最新信息：

```bash
git fetch --all --prune
```

b. 在所有来源中查找该 short-name 的最高特性编号：
   - 远程分支：`git ls-remote --heads origin | grep -E 'refs/heads/[0-9]+-<short-name>$'`
   - 本地分支：`git branch | grep -E '^[* ]*[0-9]+-<short-name>$'`
   - Specs 目录：检查匹配 `specs/[0-9]+-<short-name>` 的目录

c. 确定下一个可用编号：
   - 从所有三个来源中提取所有编号
   - 找到最高编号 N
   - 使用 N+1 作为新分支编号

d. 使用计算出的编号和 short-name 运行脚本 `{SCRIPT}`：
   - 传入 `--number N+1` 和 `--short-name "your-short-name"` 以及特性描述
   - Bash 示例：`{SCRIPT} --json --number 5 --short-name "user-auth" "Add user authentication"`
   - PowerShell 示例：`{SCRIPT} -Json -Number 5 -ShortName "user-auth" "Add user authentication"`

**重要提示**：
- 检查所有三个来源（远程分支、本地分支、specs 目录）以找到最高编号
- 仅匹配具有完全相同 short-name 模式的分支/目录
- 如果未找到具有该 short-name 的现有分支/目录，则从编号 1 开始
- 每个特性只能运行此脚本一次
- JSON 在终端中作为输出提供 - 始终参考它以获取您需要的实际内容
- JSON 输出将包含 BRANCH_NAME 和 SPEC_FILE 路径
- 对于参数中的单引号，如 "I'm Groot"，请使用转义语法：例如 'I'\''m Groot'（或尽可能使用双引号："I'm Groot"）

3. 加载 `templates/spec-template.md` 以了解必需的章节。

4. 遵循此执行流程：

    1. 从 Input 解析用户描述
       如果为空：ERROR "No feature description provided"
    2. 从描述中提取关键概念
       识别：actors、actions、data、constraints
    3. 对于不明确的方面：
       - 根据上下文和行业标准进行合理推测
       - 仅在以下情况标记 [NEEDS CLARIFICATION: 具体问题]：
         - 选择会显著影响特性范围或用户体验
         - 存在多种合理解读且影响不同
         - 不存在合理的默认值
       - **限制：总共最多 3 个 [NEEDS CLARIFICATION] 标记**
       - 按影响程度优先排列澄清需求：scope > security/privacy > user experience > technical details
    4. 填写用户场景与测试章节
       如果没有清晰的用户流程：ERROR "Cannot determine user scenarios"
    5. 生成功能需求
       每个需求必须可测试
       对未指定的细节使用合理的默认值（在假设章节中记录假设）
    6. 定义成功标准
       创建可衡量、与技术无关的结果
       包括定量指标（时间、性能、数量）和定性衡量标准（用户满意度、任务完成度）
       每个标准必须在不涉及实现细节的情况下可验证
    7. 识别关键实体（如果涉及数据）
    8. 返回：SUCCESS（规格说明已准备好进行规划）

5. 使用模板结构将规格说明写入 SPEC_FILE，用从特性描述（参数）中得出的具体细节替换占位符，同时保持章节顺序和标题不变。

6. **规格说明质量验证**：编写初始规格说明后，根据质量标准进行验证：

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

   b. **运行验证检查**：对照检查表中的每一项审查 spec：
      - 针对每一项，判定其通过或失败
      - 记录发现的具体问题（引用相关的 spec 章节）

   c. **处理验证结果**：

      - **如果所有项目均通过**：将检查表标记为完成，并继续执行步骤 6

      - **如果项目失败（不包括 [NEEDS CLARIFICATION]）**：
        1. 列出失败的项目及具体问题
        2. 更新 spec 以解决每个问题
        3. 重新运行验证，直到所有项目通过（最多 3 次迭代）
        4. 如果 3 次迭代后仍然失败，在检查表备注中记录剩余问题并警告用户

      - **如果 [NEEDS CLARIFICATION] 标记仍存在**：
        1. 从 spec 中提取所有 [NEEDS CLARIFICATION: ...] 标记
        2. **LIMIT CHECK**：如果存在超过 3 个标记，仅保留 3 个最关键的（根据范围/安全/UX 影响判断），并对其余部分进行有根据的推测
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

        4. **关键 - 表格格式**：确保 Markdown 表格格式正确：
           - 使用一致的间距，管道符对齐
           - 每个单元格的内容周围应有空格：`| Content |` 而不是 `|Content|`
           - 表头分隔符必须至少包含 3 个破折号：`|--------|`
           - 测试表格在 Markdown 预览中是否正确渲染
        5. 按顺序对问题编号（Q1, Q2, Q3 - 最多 3 个）
        6. 在等待回复之前，一次性提出所有问题
        7. 等待用户回复其对所有问题的选择（例如，“Q1: A, Q2: Custom - [details], Q3: B”）
        8. 更新 spec，将每个 [NEEDS CLARIFICATION] 标记替换为用户选择或提供的答案
        9. 解决所有澄清问题后重新运行验证

   d. **更新检查表**：每次验证迭代后，更新检查表文件中的当前通过/失败状态

7. 报告完成情况，包括分支名称、spec 文件路径、检查表结果以及对下一阶段（`/speckit.clarify` 或 `/speckit.plan`）的准备情况。

**注意：** 该脚本在写入之前创建并检出新分支，并初始化 spec 文件。

## 一般准则

## 快速准则

- 关注用户需要**什么**以及**为什么**。
- 避免涉及**如何**实现（不要包含技术栈、API、代码结构）。
- 为业务相关方编写，而非开发人员。
- **不要**创建任何嵌入在 spec 中的检查表。那将是一个单独的命令。

### 章节要求

- **强制性章节**：每个功能都必须完成
- **可选章节**：仅在与此功能相关时包含
- 当某个章节不适用时，将其完全删除（不要保留为“N/A”）

### AI 生成指南

当根据用户提示创建此 spec 时：

1. **进行有根据的推测**：利用上下文、行业标准和通用模式来填补空白
2. **记录假设**：在“假设”章节中记录合理的默认值
3. **限制澄清数量**：最多使用 3 个 [NEEDS CLARIFICATION] 标记 - 仅用于以下关键决策：
   - 显著影响功能范围或用户体验
   - 存在多种合理解释且含义不同
   - 缺乏任何合理的默认值
4. **明确澄清优先级**：范围 > 安全/隐私 > 用户体验 > 技术细节
5. **像测试人员一样思考**：每个模糊的需求都应无法通过“可测试且明确”这一检查表项
6. **常见需要澄清的领域**（仅在不存在合理默认值时）：
   - 功能范围和边界（包含/排除特定用例）
   - 用户类型和权限（如果可能存在多种相互冲突的解释）
   - 安全/合规要求（当涉及法律/财务重要性时）

**合理默认值示例**（不要询问这些）：

- 数据保留：该领域的行业标准做法
- 性能目标：除非另有说明，否则为标准 Web/移动应用程序的预期
- 错误处理：用户友好的消息及适当的回退机制
- 认证方式：Web 应用程序的标准基于会话或 OAuth2 方式
- 集成模式：使用适合项目的模式（Web 服务用 REST/GraphQL，库用函数调用，工具用 CLI 参数等）

### 成功标准准则

成功标准必须是：

1. **可衡量**：包含具体指标（时间、百分比、数量、速率）
2. **技术无关**：不提及框架、语言、数据库或工具
3. **以用户为中心**：从用户/业务角度描述结果，而非系统内部
4. **可验证**：可以在不了解实现细节的情况下进行测试/验证

**良好示例**：

- “用户可以在 3 分钟内完成结账”
- “系统支持 10,000 个并发用户”
- “95% 的搜索在 1 秒内返回结果”
- “任务完成率提高 40%”

**不良示例**（关注实现）：

- “API 响应时间低于 200ms”（过于技术化，应使用“用户即时看到结果”）
- “数据库可以处理 1000 TPS”（实现细节，应使用面向用户的指标）
- “React 组件高效渲染”（特定于框架）
- “Redis 缓存命中率高于 80%”（特定于技术）