---
description: 根据交互式或提供的原则输入创建或更新项目章程，确保所有依赖模板保持同步。
handoffs: 
  - label: 构建规格说明
    agent: speckit.specify
    prompt: 基于更新后的章程实现功能规格说明。我想构建...
---

## 用户输入```text
$ARGUMENTS
```在继续之前，你**必须**考虑用户输入（如果不为空）。

## 大纲

你正在更新位于 `.specify/memory/constitution.md` 的项目 constitution。此文件是一个**模板**，包含方括号中的占位符标记（例如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]`）。你的任务是 基于现有上下文推导具体值、 精确填充模板，以及 将任何修订传播到相关制品。

**注意**：如果 `.specify/memory/constitution.md` 尚不存在，它应该在项目设置期间从 `.specify/templates/constitution-template.md` 初始化。如果缺失，请先复制模板。

按照以下执行流程操作：

1. 加载位于 `.specify/memory/constitution.md` 的现有 constitution。
   - 识别每个形式为 `[ALL_CAPS_IDENTIFIER]` 的占位符标记。
   **重要**：用户可能需要比模板中使用的原则更少或更多的原则。如果指定了数量，请尊重该数量——遵循通用模板。你将相应地更新文档。

2. 收集/推导占位符的值：
   - 如果用户输入（对话）提供了值，则使用它。
   - 否则从现有仓库上下文推断（README、文档、之前嵌入的 constitution 版本）。
   - 对于治理日期：`RATIFICATION_DATE` 是原始采纳日期（如果未知则询问或标记 TODO），`LAST_AMENDED_DATE` 如果进行了更改则为今天，否则保留之前的日期。
   - `CONSTITUTION_VERSION` 必须按照语义版本控制规则递增：
     - MAJOR：向后不兼容的治理/原则移除或重新定义。
     - MINOR：新增原则/章节或实质性扩展的指导。
     - PATCH：澄清、措辞、错别字修复、非语义性改进。
   - 如果版本升级类型不明确，请在最终确定前提出理由。

3. 起草更新后的 constitution 内容：
   - 用具体文本替换每个占位符（不留下方括号标记，除非项目选择暂不定义而有意保留的模板槽位——明确说明任何保留的原因）。
   - 保留标题层级，注释在替换后可以删除，除非它们仍然提供澄清性指导。
   - 确保每个原则章节：简洁的名称行，捕获不可协商规则的段落（或项目符号列表），如果不明显则提供明确的理由。
   - 确保治理章节列出修订程序、版本控制策略和合规审查期望。

4. 一致性传播检查清单（将之前的检查清单转换为主动验证）：
   - 读取 `.specify/templates/plan-template.md` 并确保任何"Constitution Check"或规则与更新后的原则一致。
   - 读取 `.specify/templates/spec-template.md` 以确保范围/需求对齐——如果 constitution 添加/删除了强制性章节或约束，则进行更新。
   - 读取 `.specify/templates/tasks-template.md` 并确保任务分类反映新的或删除的原则驱动任务类型（例如，可观测性、版本控制、测试规范）。
   - 读取 `.specify/templates/commands/*.md` 中的每个命令文件（包括此文件），以验证当需要通用指导时没有过时的引用（如 CLAUDE 等特定代理名称）残留。
   - 读取任何运行时指导文档（例如 `README.md`、`docs/quickstart.md` 或特定代理指导文件（如果存在））。更新对已更改原则的引用。

5. 生成同步影响报告（作为 HTML 注释前置在更新后的 constitution 文件顶部）：
   - 版本变更：旧版本 → 新版本
   - 修改的原则列表（如果重命名，则为旧标题 → 新标题）
   - 添加的章节
   - 删除的章节
   - 需要更新的模板（✅ 已更新 / ⚠ 待处理）及文件路径
   - 后续 TODO，如果有意推迟的占位符。

6. 最终输出前的验证：
   - 没有残留未解释的方括号标记。
   - 版本行与报告匹配。
   - 日期采用 ISO 格式 YYYY-MM-DD。
   - 原则是声明性的、可测试的，并且没有模糊语言（"should" → 在适当情况下用 MUST/SHOULD 理由替换）。

7. 将完成的 constitution 写回 `.specify/memory/constitution.md`（覆盖）。

8. 向用户输出最终摘要：
   - 新版本及升级理由。
   - 任何标记为需要手动跟进的文件。
   - 建议的提交信息（例如 `docs: amend constitution to vX.Y.Z (principle additions + governance update)`）。

格式和风格要求：

- 完全按照模板中的方式使用 Markdown 标题（不要降级/升级层级）。
- 折行较长的理由行以保持可读性（理想情况下 <100 字符），但不要强制用别扭的换行。
- 章节之间保持单个空行。
- 避免尾部空格。

如果用户提供部分更新（例如，仅一个原则修订），仍然执行验证和版本决策步骤。

如果缺少关键信息（例如，批准日期确实未知），插入 `TODO(<FIELD_NAME>): explanation` 并在同步影响报告的延迟项目下列出。

不要创建新模板；始终对现有 `.specify/memory/constitution.md` 文件进行操作。