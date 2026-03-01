---
description: 根据交互式或提供的原则输入创建或更新项目章程，确保所有依赖模板保持同步。
handoffs: 
  - label: 构建规格说明
    agent: speckit.specify
    prompt: 根据更新后的章程实现功能规格说明。我想要构建...
---

## 用户输入```text
$ARGUMENTS
```在继续之前，你**必须**考虑用户输入（如果不为空）。

## 概述

你正在更新位于 `.specify/memory/constitution.md` 的项目章程。该文件是一个模板，包含方括号内的占位符标记（例如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]`）。你的任务是 收集/推导具体数值， 精确填充模板，以及 在相关依赖产物中传播所有修订内容。

**注意**：如果 `.specify/memory/constitution.md` 尚不存在，它应该是在项目设置期间从 `.specify/templates/constitution-template.md` 初始化的。如果缺失，请先复制模板。

请遵循以下执行流程：

1. 加载位于 `.specify/memory/constitution.md` 的现有章程。
   - 识别所有格式为 `[ALL_CAPS_IDENTIFIER]` 的占位符标记。
   **重要**：用户要求的原则数量可能少于或多于模板中使用的数量。如果指定了数量，请遵守该数量 —— 遵循通用模板。你将相应地更新文档。

2. 收集/推导占位符的值：
   - 如果用户输入（对话）提供了值，则使用该值。
   - 否则从现有的 repo 上下文（README、docs、嵌入的先前章程版本）中推断。
   - 对于治理日期：`RATIFICATION_DATE` 是原始采纳日期（如果未知则询问或标记 TODO），如果进行了更改，`LAST_AMENDED_DATE` 为今天，否则保留之前的日期。
   - `CONSTITUTION_VERSION` 必须根据语义化版本控制规则递增：
     - MAJOR：不兼容向后兼容的治理/原则删除或重新定义。
     - MINOR：新增原则/章节或实质性扩展的指导。
     - PATCH：澄清、措辞、错别字修正、非语义性的改进。
   - 如果版本升级类型不明确，请在最终确定前提出理由。

3. 起草更新后的章程内容：
   - 将每个占位符替换为具体文本（除了项目选择暂不定义的有意保留的模板槽位外，不得保留括号标记 —— 明确说明任何保留的原因）。
   - 保留标题层级，注释一旦被替换即可移除，除非它们仍提供澄清性指导。
   - 确保每个原则章节包含：简洁的名称行，概括非协商规则的段落（或列表），如果不明显则提供明确的理由。
   - 确保治理章节列出修正程序、版本控制策略和合规审查期望。

4. 一致性传播检查清单（将先前的检查清单转换为主动验证）：
   - 读取 `.specify/templates/plan-template.md` 并确保任何“Constitution Check”或规则与更新后的原则一致。
   - 读取 `.specify/templates/spec-template.md` 以检查范围/需求的一致性 —— 如果章程添加/删除了强制性章节或约束，请进行更新。
   - 读取 `.specify/templates/tasks-template.md` 并确保任务分类反映新增或删除的原则驱动型任务类型（例如，observability、versioning、testing discipline）。
   - 读取 `.specify/templates/commands/*.md` 中的每个命令文件（包括此文件），以验证当需要通用指导时，不存在过时的引用（例如仅针对 CLAUDE 的特定名称）。
   - 读取任何运行时指导文档（例如 `README.md`、`docs/quickstart.md` 或特定 agent 的指导文件，如果存在）。更新对已更改原则的引用。

5. 生成同步影响报告（更新后作为 HTML 注释置于章程文件顶部）：
   - 版本变更：旧 → 新
   - 修改的原则列表（如果重命名则为旧标题 → 新标题）
   - 新增章节
   - 移除章节
   - 需要更新的模板（✅ 已更新 / ⚠ 待处理）及其文件路径
   - 跟进 TODO（如果有意推迟的占位符）。

6. 最终输出前的验证：
   - 没有遗留未解释的括号标记。
   - 版本行与报告匹配。
   - 日期采用 ISO 格式 YYYY-MM-DD。
   - 原则是声明性的、可测试的，且无模糊语言（“should” → 在适当位置替换为 MUST/SHOULD 理由）。

7. 将完成的章程写回 `.specify/memory/constitution.md`（覆盖）。

8. 向用户输出最终摘要，包含：
   - 新版本及升级理由。
   - 任何标记为需人工跟进的文件。
   - 建议的提交信息（例如 `docs: amend constitution to vX.Y.Z (principle additions + governance update)`）。

格式与样式要求：

- 完全按照模板使用 Markdown 标题（不要降级/升级层级）。
- 折叠长理由行以保持可读性（理想情况下 <100 个字符），但不要强制执行导致尴尬断行的换行。
- 章节之间保持单个空行。
- 避免尾部空格。

如果用户提供部分更新（例如，仅修订一个原则），仍需执行验证和版本决策步骤。

如果关键信息缺失（例如，批准日期确实未知），请插入 `TODO(<FIELD_NAME>): explanation` 并包含在同步影响报告的推迟项中。

不要创建新模板；始终在现有的 `.specify/memory/constitution.md` 文件上操作。