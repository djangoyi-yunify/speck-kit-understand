---
description: 根据用户需求为当前功能生成自定义检查清单。
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## 检查清单目的：“针对英语的单元测试”

**关键概念**：检查清单是**针对需求编写的单元测试**——它们验证特定领域内需求的质量、清晰度和完整性。

**非用于验证/测试**：

- ❌ 非“验证按钮点击正确”
- ❌ 非“测试错误处理是否生效”
- ❌ 非“确认 API 返回 200”
- ❌ 非检查代码/实现是否符合规范

**用于需求质量验证**：

- ✅ “是否为所有卡片类型定义了视觉层级需求？”（完整性）
- ✅ “‘突出显示’是否通过具体的尺寸/位置进行了量化？”（清晰度）
- ✅ “悬停状态需求在所有交互元素中是否保持一致？”（一致性）
- ✅ “是否定义了键盘导航的无障碍需求？”（覆盖率）
- ✅ “规范是否定义了 logo 图片加载失败时的处理方式？”（边缘情况）

**隐喻**：如果你的规范是用英语编写的代码，那么检查清单就是它的单元测试套件。你正在测试需求是否编写良好、完整、无歧义且准备好实施——而不是测试实现是否有效。

## 用户输入```text
$ARGUMENTS
```在继续之前，你**必须**考虑用户输入（如果非空）。

## 执行步骤

1. **Setup**: 从仓库根目录运行 `{SCRIPT}` 并解析 JSON 以获取 FEATURE_DIR 和 AVAILABLE_DOCS 列表。
   - 所有文件路径必须是绝对路径。
   - 对于参数中的单引号，如 "I'm Groot"，请使用转义语法：例如 'I'\''m Groot'（或尽可能使用双引号："I'm Groot"）。

2. **Clarify intent (dynamic)**: 推导最多三个初始上下文澄清问题（不使用预设目录）。它们必须：
   - 基于用户的措辞 + 从 spec/plan/tasks 中提取的信号生成
   - 仅询问那些会实质性改变检查清单内容的信息
   - 如果在 `$ARGUMENTS` 中已经明确，则单独跳过
   - 追求精确而非广度

   生成算法：
   1. 提取信号：特性领域关键词（如 auth, latency, UX, API）、风险指标、利益相关者提示以及明确的交付物。
   2. 将信号聚类为候选关注领域（最多 4 个），按相关性排序。
   3. 识别可能的受众与时机（作者、审查者、QA、发布），如果未明确指出的话。
   4. 检测缺失的维度：范围广度、深度/严谨性、风险侧重、排除边界、可度量的验收标准。
   5. 从以下原型中选择并制定问题：
      - 范围细化（例如，“是否应包含与 X 和 Y 的集成接触点，还是仅限于本地模块的正确性？”）
      - 风险优先级（例如，“这些潜在风险领域中，哪些应接受强制性门禁检查？”）
      - 深度校准（例如，“这是一个轻量级的提交前健全性检查列表，还是正式的发布门禁？”）
      - 受众框架（例如，“这仅由作者使用，还是在 PR 审查期间由同行使用？”）
      - 边界排除（例如，“我们是否应在本轮明确排除性能调优项？”）
      - 场景类别缺失（例如，“未检测到恢复流程——回滚/部分失败路径是否在范围内？”）

   问题格式规则：
   - 如果提供选项，生成一个紧凑的表格，包含列：Option | Candidate | Why It Matters
   - 选项上限为 A–E；如果自由形式的回答更清晰，则省略表格
   - 永远不要要求用户重述他们已经说过的内容
   - 避免推测性类别（禁止臆造）。如果不确定，请明确询问：“确认 X 是否属于范围。”

   无法交互时的默认值：
   - Depth: Standard
   - Audience: Reviewer (PR) 如果与代码相关；否则为 Author
   - Focus: Top 2 relevance clusters

   输出问题（标记为 Q1/Q2/Q3）。回答后：如果 ≥2 个场景类别（Alternate / Exception / Recovery / Non-Functional domain）仍不清楚，你**可以**再问最多两个针对性的后续问题（Q4/Q5），每个附带一行理由（例如，“未解决的恢复路径风险”）。总问题数不得超过五个。如果用户明确拒绝更多提问，则跳过升级。

3. **Understand user request**: 结合 `$ARGUMENTS` + 澄清回答：
   - 推导检查清单主题（例如，security, review, deploy, ux）
   - 整合用户提到的明确必选项
   - 将选定的焦点映射到分类脚手架
   - 从 spec/plan/tasks 推断任何缺失的上下文（不要臆造）

4. **Load feature context**: 从 FEATURE_DIR 读取：
   - spec.md: Feature requirements and scope
   - plan.md (if exists): Technical details, dependencies
   - tasks.md (if exists): Implementation tasks

   **上下文加载策略**:
   - 仅加载与当前关注领域相关的必要部分（避免全文件转储）
   - 优先将长段落总结为简洁的场景/需求要点
   - 使用渐进式披露：仅在检测到缺口时进行后续检索
   - 如果源文档很大，生成临时摘要项而不是嵌入原始文本

5. **Generate checklist** - 创建 "Unit Tests for Requirements"：
   - 如果 `FEATURE_DIR/checklists/` 目录不存在，则创建
   - 生成唯一的检查清单文件名：
     - 使用基于领域的简短描述性名称（例如 `ux.md`, `api.md`, `security.md`）
     - 格式：`[domain].md`
     - 如果文件已存在，则追加到现有文件
   - 从 CHK001 开始顺序编号
   - 每次运行 `/speckit.checklist` 都会创建一个新文件（绝不覆盖现有检查清单）

   **核心原则 - 测试需求，而非实现**：
   每个检查项必须评估需求本身：
   - **Completeness（完整性）**：是否记录了所有必要的需求？
   - **Clarity（清晰度）**：需求是否明确且具体？
   - **Consistency（一致性）**：需求之间是否协调一致？
   - **Measurability（可度量性）**：需求能否被客观验证？
   - **Coverage（覆盖度）**：是否覆盖了所有场景/边缘情况？

   **分类结构** - 按需求质量维度分组：
   - **Requirement Completeness**（是否记录了所有必要的需求？）
   - **Requirement Clarity**（需求是否具体且无歧义？）
   - **Requirement Consistency**（需求是否一致且无冲突？）
   - **Acceptance Criteria Quality**（验收标准是否可度量？）
   - **Scenario Coverage**（是否覆盖了所有流程/情况？）
   - **Edge Case Coverage**（是否定义了边界条件？）
   - **Non-Functional Requirements**（性能、安全、可访问性等 - 是否已指定？）
   - **Dependencies & Assumptions**（是否记录并验证了依赖和假设？）
   - **Ambiguities & Conflicts**（需要澄清什么？）

   **如何编写检查项 - "Unit Tests for English"**：

   ❌ **错误**（测试实现）：
   - "Verify landing page displays 3 episode cards"
   - "Test hover states work on desktop"
   - "Confirm logo click navigates home"

   ✅ **正确**（测试需求质量）：
   - "Are the exact number and layout of featured episodes specified?" [Completeness]
   - "Is 'prominent display' quantified with specific sizing/positioning?" [Clarity]
   - "Are hover state requirements consistent across all interactive elements?" [Consistency]
   - "Are keyboard navigation requirements defined for all interactive UI?" [Coverage]
   - "Is the fallback behavior specified when logo image fails to load?" [Edge Cases]
   - "Are loading states defined for asynchronous episode data?" [Completeness]
   - "Does the spec define visual hierarchy for competing UI elements?" [Clarity]

   **项目结构**：
   每个项目应遵循以下模式：
   - 询问需求质量的问题格式
   - 关注已写入（或未写入）spec/plan 的内容
   - 在括号中包含质量维度 [Completeness/Clarity/Consistency/etc.]
   - 检查现有需求时引用 spec 章节 `[Spec §X.Y]`
   - 检查缺失需求时使用 `[Gap]` 标记

   **按质量维度分类的示例**：

   Completeness（完整性）：
   - "Are error handling requirements defined for all API failure modes? [Gap]"
   - "Are accessibility requirements specified for all interactive elements? [Completeness]"
   - "Are mobile breakpoint requirements defined for responsive layouts? [Gap]"

   Clarity（清晰度）：
   - "Is 'fast loading' quantified with specific timing thresholds? [Clarity, Spec §NFR-2]"
   - "Are 'related episodes' selection criteria explicitly defined? [Clarity, Spec §FR-5]"
   - "Is 'prominent' defined with measurable visual properties? [Ambiguity, Spec §FR-4]"

   Consistency（一致性）：
   - "Do navigation requirements align across all pages? [Consistency, Spec §FR-10]"
   - "Are card component requirements consistent between landing and detail pages? [Consistency]"

   Coverage（覆盖度）：
   - "Are requirements defined for zero-state scenarios (no episodes)? [Coverage, Edge Case]"
   - "Are concurrent user interaction scenarios addressed? [Coverage, Gap]"
   - "Are requirements specified for partial data loading failures? [Coverage, Exception Flow]"

   Measurability（可度量性）：
   - "Are visual hierarchy requirements measurable/testable? [Acceptance Criteria, Spec §FR-1]"
   - "Can 'balanced visual weight' be objectively verified? [Measurability, Spec §FR-2]"

   **场景分类与覆盖**（关注需求质量）：
   - 检查是否存在以下场景的需求：Primary, Alternate, Exception/Error, Recovery, Non-Functional
   - 对于每个场景类别，询问：“[scenario type] 需求是否完整、清晰且一致？”
   - 如果场景类别缺失：“[scenario type] 需求是故意排除还是缺失？[Gap]”
   - 当发生状态变更时包含弹性/回滚：“是否定义了迁移失败的回滚需求？[Gap]”

   **可追溯性要求**：
   - 最低要求：≥80% 的项目必须包含至少一个可追溯性引用
   - 每个项目应引用：spec 章节 `[Spec §X.Y]`，或使用标记：`[Gap]`, `[Ambiguity]`, `[Conflict]`, `[Assumption]`
   - 如果不存在 ID 体系：“是否建立了需求与验收标准的 ID 体系？[Traceability]”

   **揭示与解决问题**（需求质量问题）：
   针对需求本身提出问题：
   - 歧义：“术语 'fast' 是否有具体的指标量化？[Ambiguity, Spec §NFR-1]”
   - 冲突：“导航需求在 §FR-10 和 §FR-10a 之间是否存在冲突？[Conflict]”
   - 假设：“'podcast API 始终可用' 的假设是否经过验证？[Assumption]”
   - 依赖：“外部 podcast API 需求是否已记录？[Dependency, Gap]”
   - 定义缺失：“'visual hierarchy' 是否有可度量的标准定义？[Gap]”

   **内容整合**：
   - 软上限：如果原始候选项 > 40，按风险/影响排序优先级
   - 合并检查同一需求方面的近似重复项
   - 如果 >5 个低影响的边缘情况，创建一个项目：“需求中是否解决了边缘情况 X, Y, Z？[Coverage]”

   **🚫 绝对禁止** - 以下行为会使其变成实现测试，而非需求测试：
   - ❌ 任何以 "Verify", "Test", "Confirm", "Check" + 实现行为开头的项目
   - ❌ 引用代码执行、用户操作、系统行为
   - ❌ "Displays correctly", "works properly", "functions as expected"
   - ❌ "Click", "navigate", "render", "load", "execute"
   - ❌ 测试用例、测试计划、QA 流程
   - ❌ 实现细节（框架、API、算法）

   **✅ 必需模式** - 这些是测试需求质量的：
   - ✅ "Are [requirement type] defined/specified/documented for [scenario]?"
   - ✅ "Is [vague term] quantified/clarified with specific criteria?"
   - ✅ "Are requirements consistent between [section A] and [section B]?"
   - ✅ "Can [requirement] be objectively measured/verified?"
   - ✅ "Are [edge cases/scenarios] addressed in requirements?"
   - ✅ "Does the spec define [missing aspect]?"

6. **Structure Reference**: 按照 `templates/checklist-template.md` 中的规范模板生成检查清单，包括标题、元数据部分、分类标题和 ID 格式。如果模板不可用，使用：H1 标题，purpose/created 元数据行，包含 `- [ ] CHK### <requirement item>` 行的 `##` 分类部分，ID 从 CHK001 开始全局递增。

7. **Report**: 输出创建的检查清单的完整路径、项目计数，并提醒用户每次运行都会创建一个新文件。总结：
   - 选定的关注领域
   - 深度级别
   - 参与者/时机
   - 整合的任何用户明确指定的必选项

**重要提示**：每次调用 `/speckit.checklist` 命令都会使用简短的描述性名称创建一个检查清单文件，除非文件已存在。这允许：

- 不同类型的多个检查清单（例如 `ux.md`, `test.md`, `security.md`）
- 简单、易记且表明检查清单用途的文件名
- 在 `checklists/` 文件夹中轻松识别和导航

为避免混乱，请使用描述性类型并在完成后清理过时的检查清单。

## 检查清单类型示例及样本项

**UX Requirements Quality:** `ux.md`

样本项（测试需求，而非实现）：

- "Are visual hierarchy requirements defined with measurable criteria? [Clarity, Spec §FR-1]"
- "Is the number and positioning of UI elements explicitly specified? [Completeness, Spec §FR-1]"
- "Are interaction state requirements (hover, focus, active) consistently defined? [Consistency]"
- "Are accessibility requirements specified for all interactive elements? [Coverage, Gap]"
- "Is fallback behavior defined when images fail to load? [Edge Case, Gap]"
- "Can 'prominent display' be objectively measured? [Measurability, Spec §FR-4]"

**API Requirements Quality:** `api.md`

样本项：

- "Are error response formats specified for all failure scenarios? [Completeness]"
- "Are rate limiting requirements quantified with specific thresholds? [Clarity]"
- "Are authentication requirements consistent across all endpoints? [Consistency]"
- "Are retry/timeout requirements defined for external dependencies? [Coverage, Gap]"
- "Is versioning strategy documented in requirements? [Gap]"

**Performance Requirements Quality:** `performance.md`

样本项：

- "Are performance requirements quantified with specific metrics? [Clarity]"
- "Are performance targets defined for all critical user journeys? [Coverage]"
- "Are performance requirements under different load conditions specified? [Completeness]"
- "Can performance requirements be objectively measured? [Measurability]"
- "Are degradation requirements defined for high-load scenarios? [Edge Case, Gap]"

**Security Requirements Quality:** `security.md`

样本项：

- "Are authentication requirements specified for all protected resources? [Coverage]"
- "Are data protection requirements defined for sensitive information? [Completeness]"
- "Is the threat model documented and requirements aligned to it? [Traceability]"
- "Are security requirements consistent with compliance obligations? [Consistency]"
- "Are security failure/breach response requirements defined? [Gap, Exception Flow]"

## 反面示例：切勿模仿

**❌ 错误 - 这些测试的是实现，而非需求：**```markdown
- [ ] CHK001 - Verify landing page displays 3 episode cards [Spec §FR-001]
- [ ] CHK002 - Test hover states work correctly on desktop [Spec §FR-003]
- [ ] CHK003 - Confirm logo click navigates to home page [Spec §FR-010]
- [ ] CHK004 - Check that related episodes section shows 3-5 items [Spec §FR-005]
```**✅ 正确 - 这些测试了需求质量：**```markdown
- [ ] CHK001 - Are the number and layout of featured episodes explicitly specified? [Completeness, Spec §FR-001]
- [ ] CHK002 - Are hover state requirements consistently defined for all interactive elements? [Consistency, Spec §FR-003]
- [ ] CHK003 - Are navigation requirements clear for all clickable brand elements? [Clarity, Spec §FR-010]
- [ ] CHK004 - Is the selection criteria for related episodes documented? [Gap, Spec §FR-005]
- [ ] CHK005 - Are loading state requirements defined for asynchronous episode data? [Gap]
- [ ] CHK006 - Can "visual hierarchy" requirements be objectively measured? [Measurability, Spec §FR-001]
```**关键区别：**

- 错误：测试系统是否正常工作
- 正确：测试需求是否编写正确
- 错误：行为验证
- 正确：需求质量确认
- 错误：“它能做 X 吗？”
- 正确：“X 是否已明确说明？”