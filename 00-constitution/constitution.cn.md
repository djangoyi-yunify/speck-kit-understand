---
description: 根据交互式或提供的原则输入，创建或更新项目 constitution，确保所有依赖模板保持同步。
handoffs: 
  - label: 构建规范
    agent: speckit.specify
    prompt: 基于更新后的 constitution 实现功能规范。我想要构建...
---

## 用户输入```text
$ARGUMENTS
```在继续之前，你**必须**考虑用户输入（如果非空）。

## 概述

你正在更新位于 `.specify/memory/constitution.md` 的项目章程。该文件是一个模板，包含方括号内的占位符标记（例如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]`）。你的工作是 收集/推导具体值， 精确填充模板，以及 将任何修订传播到依赖工件。

**注意**：如果 `.specify/memory/constitution.md` 尚不存在，它应该是在项目设置期间从 `.specify/templates/constitution-template.md` 初始化的。如果缺失，请先复制模板。

遵循以下执行流程：

1. 加载位于 `.specify/memory/constitution.md` 的现有章程。
   - 识别每一个形式为 `[ALL_CAPS_IDENTIFIER]` 的占位符标记。
   **重要**：用户可能需要比模板中使用得更少或更多的原则。如果指定了数量，请尊重该要求——遵循通用模板。你将相应地更新文档。

2. 收集/推导占位符的值：
   - 如果用户输入（对话）提供了值，请使用它。
   - 否则从现有的仓库上下文（README、docs、之前嵌入的章程版本，如有）推断。
   - 对于治理日期：`RATIFICATION_DATE` 是原始通过日期（如果未知，请询问或标记为 TODO），如果进行了更改，`LAST_AMENDED_DATE` 为今天，否则保留以前的日期。
   - `CONSTITUTION_VERSION` 必须根据语义化版本控制规则递增：
     - MAJOR：不向后兼容的治理/原则删除或重新定义。
     - MINOR：新增原则/章节或实质性扩展的指导。
     - PATCH：澄清、措辞、错别字修正、非语义上的改进。
   - 如果版本升级类型不明确，请在最终确定前提出理由。

3. 起草更新后的章程内容：
   - 用具体文本替换每个占位符（除非项目选择暂不定义而有意保留的模板槽位，否则不得留下方括号标记——明确说明任何保留项的理由）。
   - 保留标题层级，一旦替换，注释可以删除，除非它们仍提供澄清性指导。
   - 确保每个原则章节包含：简练的名称行、包含不可协商规则的段落（或项目符号列表），以及如果不明显则需明确的理由。
   - 确保治理章节列出修订程序、版本控制策略和合规审查预期。

4. 一致性传播检查清单（将先前的检查清单转换为主动验证）：
   - 阅读 `.specify/templates/plan-template.md` 并确保任何“章程检查”或规则与更新的原则一致。
   - 阅读 `.specify/templates/spec-template.md` 以对齐范围/需求——如果章程添加/删除了强制性章节或约束，请更新。
   - 阅读 `.specify/templates/tasks-template.md` 并确保任务分类反映了新增或删除的原则驱动任务类型（例如，可观测性、版本控制、测试纪律）。
   - 阅读 `.specify/templates/commands/*.md` 中的每个命令文件（包括此文件），以验证当需要通用指导时，不存在过时的引用（如仅限 CLAUDE 等特定于 agent 的名称）。
   - 阅读任何运行时指导文档（例如 `README.md`、`docs/quickstart.md` 或特定于 agent 的指导文件，如存在）。更新对已更改原则的引用。

5. 生成同步影响报告（更新后作为 HTML 注释前置在章程文件顶部）：
   - 版本变更：old → new
   - 修改的原则列表（如果重命名，则为旧标题 → 新标题）
   - 新增章节
   - 删除章节
   - 需要更新的模板（✅ 已更新 / ⚠ 待处理）及文件路径
   - 后续 TODO，如果有意推迟了某些占位符。

6. 最终输出前的验证：
   - 没有未解释的剩余方括号标记。
   - 版本行与报告匹配。
   - 日期格式为 ISO YYYY-MM-DD。
   - 原则是声明性的、可测试的，且无模糊语言（“should” → 在适当情况下替换为 MUST/SHOULD 理由）。

7. 将完成的章程写回 `.specify/memory/constitution.md`（覆盖）。

8. 向用户输出最终摘要，包含：
   - 新版本及升级理由。
   - 任何标记为需手动跟进的文件。
   - 建议的提交信息（例如 `docs: amend constitution to vX.Y.Z (principle additions + governance update)`）。

格式与风格要求：

- 完全按照模板使用 Markdown 标题（不要降级/升级层级）。
- 换行长理由行以保持可读性（理想情况下 <100 个字符），但不要强制进行生硬的换行。
- 各章节之间保持单个空行。
- 避免尾部空格。

如果用户提供部分更新（例如，仅修订一个原则），仍需执行验证和版本决策步骤。

如果缺少关键信息（例如，确实未知的批准日期），插入 `TODO(<FIELD_NAME>): explanation` 并在同步影响报告的延期项目下列出。

不要创建新模板；始终在现有的 `.specify/memory/constitution.md` 文件上操作。