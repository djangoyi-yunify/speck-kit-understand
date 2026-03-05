---
description: 根据用户需求为当前功能生成自定义检查清单。
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## 检查清单目的：“英语单元测试”

**关键概念**：检查清单是**针对需求编写的单元测试**——它们验证特定领域中需求的质量、清晰度和完整性。

**不用于验证/测试**：

- ❌ 不是“验证按钮点击是否正确”
- ❌ 不是“测试错误处理是否有效”
- ❌ 不是“确认 API 是否返回 200”
- ❌ 不是检查代码/实现是否符合规范

**用于需求质量验证**：

- ✅ “是否为所有卡片类型定义了视觉层级要求？”（完整性）
- ✅ “‘突出显示’是否通过具体尺寸/位置进行了量化？”（清晰度）
- ✅ “所有交互元素的悬停状态要求是否一致？”（一致性）
- ✅ “是否定义了键盘导航的无障碍要求？”（覆盖率）
- ✅ “规范是否定义了 Logo 图片加载失败时的处理方式？”（边界情况）

**隐喻**：如果你的规范是用英语编写的代码，那么检查清单就是它的单元测试套件。你是在测试需求是否编写良好、完整、无歧义且具备实施条件——而不是测试实现是否有效。

## 用户输入

```text
$ARGUMENTS
```

在继续之前，你**必须**考虑用户输入（如果不为空）。

## 执行步骤

1. **Setup**: 从 repo 根目录运行 `{SCRIPT}` 并解析 JSON 以获取 FEATURE_DIR 和 AVAILABLE_DOCS 列表。
   - 所有文件路径必须是绝对路径。
   - 对于参数中的单引号（如 "I'm Groot"），使用转义语法：例如 'I'\''m Groot'（或尽可能使用双引号："I'm Groot"）。

2. **Clarify intent (dynamic)**: 生成最多三个初始上下文澄清问题（无预定义目录）。它们必须：
   - 基于用户措辞 + 从 spec/plan/tasks 中提取的信号生成
   - 仅询问会实质性改变清单内容的信息
   - 如果在 `$ARGUMENTS` 中已经明确，则单独跳过
   - 精确性优于广度

   生成算法：
   1. 提取信号：功能领域关键词（如 auth, latency, UX, API）、风险指标、利益相关者提示以及明确交付物。
   2. 将信号聚类为候选关注领域（最多 4 个），按相关性排序。
   3. 识别可能的受众和时机（author, reviewer, QA, release），如果未明确的话。
   4. 检测缺失维度：范围广度、深度/严谨度、风险强调、排除边界、可测量的验收标准。
   5. 从以下原型中选择制定问题：
      - 范围细化（例如，“这应该包括与 X 和 Y 的集成接触点，还是仅限于本地模块的正确性？”）
      - 风险优先级（例如，“这些潜在风险领域中哪一个应接受强制性门禁检查？”）
      - 深度校准（例如，“这是一个轻量级的提交前健全性列表，还是一个正式的发布门禁？”）
      - 受众定位（例如，“这仅由作者使用，还是在 PR review 期间由同行使用？”）
      - 边界排除（例如，“我们应该明确排除本轮的性能调优项吗？”）
      - 场景类别缺口（例如，“未检测到恢复流程——rollback / 部分失败路径是否在范围内？”）

   问题格式规则：
   - 如果展示选项，生成一个紧凑的表格，包含列：Option | Candidate | Why It Matters
   - 最多限制为 A–E 选项；如果自由回答更清晰，则省略表格
   - 切勿要求用户重述他们已经说过的内容
   - 避免推测性类别（不要捏造）。如果不确定，明确询问：“确认 X 是否属于范围。”

   无法交互时的默认值：
   - Depth: Standard
   - Audience: Reviewer (PR)（如果与代码相关）；否则为 Author
   - Focus: Top 2 relevance clusters

   输出问题（标记 Q1/Q2/Q3）。回答后：如果 ≥2 个场景类别（Alternate / Exception / Recovery / Non-Functional domain）仍不清楚，你可以再询问最多两个针对性的后续问题（Q4/Q5），每个问题需附带一行理由（例如，“未解决的恢复路径风险”）。总问题数不得超过五个。如果用户明确拒绝更多提问，则跳过升级。

3. **Understand user request**: 合并 `$ARGUMENTS` + 澄清性回答：
   - 推导清单主题（例如 security, review, deploy, ux）
   - 整合用户提到的明确必选项
   - 将焦点选择映射到类别脚手架
   - 从 spec/plan/tasks 推断任何缺失的上下文（不要捏造）

4. **Load feature context**: 从 FEATURE_DIR 读取：
   - spec.md: 功能需求和范围
   - plan.md（如果存在）：技术细节、依赖项
   - tasks.md（如果存在）：实施任务

   **上下文加载策略**:
   - 仅加载与活动关注区域相关的必要部分（避免全文件转储）
   - 优先将长章节总结为简洁的场景/需求要点
   - 使用渐进式披露：仅在检测到缺口时添加后续检索
   - 如果源文档很大，生成临时摘要项而不是嵌入原始文本

5. **Generate checklist** - 创建“需求单元测试”：
   - 创建 `FEATURE_DIR/checklists/` 目录（如果不存在）
   - 生成唯一的清单文件名：
     - 使用基于领域的简短描述性名称（例如 `ux.md`, `api.md`, `security.md`）
     - 格式：`[domain].md`
   - 文件处理行为：
     - 如果文件不存在：创建新文件，项目编号从 CHK001 开始
     - 如果文件存在：将新项目追加到现有文件，继续上一次的 CHK ID（例如，如果最后一项是 CHK015，则新项目从 CHK016 开始）
   - 切勿删除或替换现有清单内容 - 始终保留并追加

   **核心原则 - 测试需求，而非实现**：
   每个清单项目必须评估需求本身是否具备：
   - **Completeness（完整性）**：是否记录了所有必要的需求？
   - **Clarity（清晰度）**：需求是否明确且具体？
   - **Consistency（一致性）**：需求之间是否相互一致？
   - **Measurability（可测量性）**：需求能否被客观验证？
   - **Coverage（覆盖度）**：是否涵盖了所有场景/边缘情况？

   **类别结构** - 按需求质量维度对项目分组：
   - **Requirement Completeness**（是否记录了所有必要需求？）
   - **Requirement Clarity**（需求是否具体且无歧义？）
   - **Requirement Consistency**（需求是否一致且无冲突？）
   - **Acceptance Criteria Quality**（验收标准是否可测量？）
   - **Scenario Coverage**（是否涵盖所有流程/情况？）
   - **Edge Case Coverage**（是否定义了边界条件？）
   - **Non-Functional Requirements**（性能、安全、可访问性等 - 是否已指定？）
   - **Dependencies & Assumptions**（是否已记录并验证？）
   - **Ambiguities & Conflicts**（需要澄清什么？）

   **如何编写清单项目 - “英语单元测试”**：

   ❌ **错误**（测试实现）：
   - “验证着陆页显示 3 张剧集卡片”
   - “测试桌面端悬停状态是否工作”
   - “确认点击 Logo 导航回主页”

   ✅ **正确**（测试需求质量）：
   - “是否指定了精选剧集的确切数量和布局？[Completeness]”
   - “‘突出显示’是否通过具体的尺寸/位置进行了量化？[Clarity]”
   - “所有交互元素的悬停状态需求是否一致？[Consistency]”
   - “是否为所有交互式 UI 定义了键盘导航需求？[Coverage]”
   - “是否指定了 Logo 图片加载失败时的回退行为？[Edge Cases]”
   - “是否定义了异步剧集数据的加载状态？[Completeness]”
   - “Spec 是否定义了竞争 UI 元素的视觉层级？[Clarity]”

   **项目结构**：
   每个项目应遵循以下模式：
   - 询问需求质量的问题格式
   - 关注（Spec/Plan 中）写了什么（或没写什么）
   - 在括号中包含质量维度 [Completeness/Clarity/Consistency/etc.]
   - 检查现有需求时引用 Spec 章节 `[Spec §X.Y]`
   - 检查缺失需求时使用 `[Gap]` 标记

   **按质量维度的示例**：

   Completeness（完整性）：
   - “是否为所有 API 失败模式定义了错误处理需求？[Gap]”
   - “是否为所有交互元素指定了可访问性需求？[Completeness]”
   - “是否定义了响应式布局的移动端断点需求？[Gap]”

   Clarity（清晰度）：
   - “‘快速加载’是否通过具体的时序阈值进行了量化？[Clarity, Spec §NFR-2]”
   - “‘相关剧集’的选择标准是否明确定义？[Clarity, Spec §FR-5]”
   - “‘突出’是否通过可测量的视觉属性定义？[Ambiguity, Spec §FR-4]”

   Consistency（一致性）：
   - “所有页面的导航需求是否一致？[Consistency, Spec §FR-10]”
   - “着陆页和详情页之间的卡片组件需求是否一致？[Consistency]”

   Coverage（覆盖度）：
   - “是否定义了零状态场景（无剧集）的需求？[Coverage, Edge Case]”
   - “是否涉及并发用户交互场景？[Coverage, Gap]”
   - “是否指定了部分数据加载失败的需求？[Coverage, Exception Flow]”

   Measurability（可测量性）：
   - “视觉层级需求是否可测量/可测试？[Acceptance Criteria, Spec §FR-1]”
   - “‘平衡的视觉权重’能否被客观验证？[Measurability, Spec §FR-2]”

   **场景分类与覆盖**（关注需求质量）：
   - 检查是否存在以下场景的需求：Primary, Alternate, Exception/Error, Recovery, Non-Functional
   - 对于每个场景类别，询问：“[场景类型] 需求是否完整、清晰且一致？”
   - 如果缺少场景类别：“[场景类型] 需求是故意排除还是缺失？[Gap]”
   - 当发生状态变更时包含弹性/rollback：“是否定义了迁移失败的 rollback 需求？[Gap]”

   **可追溯性要求**：
   - 最低要求：≥80% 的项目必须包含至少一个可追溯性引用
   - 每个项目应引用：Spec 章节 `[Spec §X.Y]`，或使用标记：`[Gap]`, `[Ambiguity]`, `[Conflict]`, `[Assumption]`
   - 如果不存在 ID 体系：“是否建立了需求和验收标准 ID 方案？[Traceability]”

   **发现与解决问题**（需求质量问题）：
   询问关于需求本身的问题：
   - 歧义：“术语‘快’是否通过具体指标量化？[Ambiguity, Spec §NFR-1]”
   - 冲突：“导航需求在 §FR-10 和 §FR-10a 之间是否冲突？[Conflict]”
   - 假设：“‘Podcast API 总是可用’的假设是否经过验证？[Assumption]”
   - 依赖：“是否记录了外部 Podcast API 需求？[Dependency, Gap]”
   - 缺失定义：“‘视觉层级’是否通过可测量标准定义？[Gap]”

   **内容整合**：
   - 软上限：如果原始候选项目 > 40，按风险/影响进行优先级排序
   - 合并检查相同需求方面的近似重复项
   - 如果 >5 个低影响的边缘情况，创建一个项目：“需求中是否解决了边缘情况 X、Y、Z？[Coverage]”

   **🚫 绝对禁止** - 这些使其成为实现测试，而非需求测试：
   - ❌ 任何以“验证”、“测试”、“确认”、“检查” + 实现行为开头的项目
   - ❌ 引用代码执行、用户操作、系统行为
   - ❌ “正确显示”、“工作正常”、“按预期运行”
   - ❌ “点击”、“导航”、“渲染”、“加载”、“执行”
   - ❌ 测试用例、测试计划、QA 流程
   - ❌ 实现细节（框架、API、算法）

   **✅ 必需模式** - 这些测试需求质量：
   - ✅ “是否为 [场景] 定义/指定/记录了 [需求类型]？”
   - ✅ “是否通过具体标准量化/澄清了 [模糊术语]？”
   - ✅ “[章节 A] 和 [章节 B] 之间的需求是否一致？”
   - ✅ “[需求] 能否被客观测量/验证？”
   - ✅ “需求中是否解决了 [边缘情况/场景]？”
   - ✅ “Spec 是否定义了 [缺失方面]？”

6. **Structure Reference**: 按照 `templates/checklist-template.md` 中的规范模板生成清单，用于标题、元数据部分、类别标题和 ID 格式。如果模板不可用，使用：H1 标题、目的/创建元数据行、包含 `- [ ] CHK### <requirement item>` 行的 `##` 类别部分，ID 从 CHK001 开始全局递增。

7. **Report**: 输出清单文件的完整路径、项目数量，并总结运行是创建了新文件还是追加到现有文件。总结：
   - 选定的关注领域
   - 深度级别
   - 参与者/时机
   - 整合的任何用户指定的明确必选项

**重要**：每次 `/speckit.checklist` 命令调用都使用一个简短、描述性的清单文件名，并创建新文件或追加到现有文件。这允许：
- 不同类型的多个清单（例如 `ux.md`, `test.md`, `security.md`）
- 简单、易记的文件名，表明清单用途
- 在 `checklists/` 文件夹中轻松识别和导航

为避免混乱，请使用描述性类型，并在完成后清理过时的清单。

## 示例清单类型与示例项目

**UX 需求质量：** `ux.md`

示例项目（测试需求，而非实现）：

- “视觉层级需求是否通过可测量标准定义？[Clarity, Spec §FR-1]”
- “UI 元素的数量和位置是否明确指定？[Completeness, Spec §FR-1]”
- “交互状态需求（悬停、聚焦、激活）是否一致定义？[Consistency]”
- “是否为所有交互元素指定了可访问性需求？[Coverage, Gap]”
- “是否定义了图片加载失败时的回退行为？[Edge Case, Gap]”
- “‘突出显示’能否被客观测量？[Measurability, Spec §FR-4]”

**API 需求质量：** `api.md`

示例项目：

- “是否为所有失败场景指定了错误响应格式？[Completeness]”
- “限流需求是否通过具体阈值量化？[Clarity]”
- “所有端点的认证需求是否一致？[Consistency]”
- “是否定义了外部依赖的重试/超时需求？[Coverage, Gap]”
- “需求中是否记录了版本控制策略？[Gap]”

**性能需求质量：** `performance.md`

示例项目：

- “性能需求是否通过具体指标量化？[Clarity]”
- “是否为所有关键用户旅程定义了性能目标？[Coverage]”
- “是否指定了不同负载条件下的性能需求？[Completeness]”
- “性能需求能否被客观测量？[Measurability]”
- “是否定义了高负载场景下的降级需求？[Edge Case, Gap]”

**安全需求质量：** `security.md`

示例项目：

- “是否为所有受保护资源指定了认证需求？[Coverage]”
- “是否为敏感信息定义了数据保护需求？[Completeness]”
- “威胁模型是否已记录且需求与其对齐？[Traceability]”
- “安全需求是否与合规义务一致？[Consistency]”
- “是否定义了安全失败/违规响应需求？[Gap, Exception Flow]”

## 反面示例：不该做什么

**❌ 错误 - 这些测试实现，而非需求：**

```markdown
- [ ] CHK001 - Verify landing page displays 3 episode cards [Spec §FR-001]
- [ ] CHK002 - Test hover states work correctly on desktop [Spec §FR-003]
- [ ] CHK003 - Confirm logo click navigates to home page [Spec §FR-010]
- [ ] CHK004 - Check that related episodes section shows 3-5 items [Spec §FR-005]
```

**✅ 正确 - 这些测试需求的质量：**

```markdown
- [ ] CHK001 - Are the number and layout of featured episodes explicitly specified? [Completeness, Spec §FR-001]
- [ ] CHK002 - Are hover state requirements consistently defined for all interactive elements? [Consistency, Spec §FR-003]
- [ ] CHK003 - Are navigation requirements clear for all clickable brand elements? [Clarity, Spec §FR-010]
- [ ] CHK004 - Is the selection criteria for related episodes documented? [Gap, Spec §FR-005]
- [ ] CHK005 - Are loading state requirements defined for asynchronous episode data? [Gap]
- [ ] CHK006 - Can "visual hierarchy" requirements be objectively measured? [Measurability, Spec §FR-001]
```

**关键区别：**

- 错误：测试系统是否正常工作
- 正确：测试需求是否编写正确
- 错误：行为验证
- 正确：需求质量确认
- 错误：“它是否做X？”
- 正确：“X是否被清晰定义？”