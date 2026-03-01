---
description: 根据交互式输入或提供的原则输入，创建或更新项目章程，确保所有依赖模板保持同步。
handoffs: 
  - label: 构建规格说明
    agent: speckit.specify
    prompt: 根据更新后的章程实现功能规格说明。我想构建...
---

## 用户输入```text
$ARGUMENTS
```在继续之前，你 **必须** 考虑用户输入（如果不为空）。

## 大纲

你正在更新位于 `.specify/memory/constitution.md` 的项目宪法。此文件是一个模板，包含方括号中的占位符标记（例如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]`）。你的任务是 收集/推导具体值， 精确填充模板，以及 将任何修订传播到依赖工件。

**注意**：如果 `.specify/memory/constitution.md` 尚不存在，它应该在项目设置期间从 `.specify/templates/constitution-template.md` 初始化。如果缺失，请先复制模板。

请遵循以下执行流程：

1. 加载位于 `.specify/memory/constitution.md` 的现有宪法。
   - 识别形式为 `[ALL_CAPS_IDENTIFIER]` 的每个占位符标记。
   **重要**：用户可能需要比模板中使用的原则更少或更多的原则。如果指定了数量，请尊重该数量——遵循通用模板。你将相应地更新文档。

2. 收集/推导占位符的值：
   - 如果用户输入（对话）提供了值，请使用它。
   - 否则从现有 repo 上下文推断（README, docs, 嵌入的先前宪法版本）。
   - 对于治理日期：`RATIFICATION_DATE` 是原始通过日期（如果未知则询问或标记 TODO），如果进行了更改，`LAST_AMENDED_DATE` 为今天，否则保留之前的日期。
   - `CONSTITUTION_VERSION` 必须根据语义化版本控制规则递增：
     - MAJOR：不向后兼容的治理/原则移除或重新定义。
     - MINOR：新增原则/章节或实质性扩展的指导。
     - PATCH：澄清、措辞、拼写错误修复、非语义改进。
   - 如果版本升级类型模糊，请在最终确定前提出理由。

3. 起草更新后的宪法内容：
   - 将每个占位符替换为具体文本（除了项目选择暂未定义的有意保留的模板槽位外，不得保留方括号标记——明确证明任何保留项的合理性）。
   - 保留标题层级，注释在替换后可以删除，除非它们仍提供澄清指导。
   - 确保每个原则部分包含：简洁的名称行，描述不可协商规则的段落（或项目符号列表），以及（如不明显）明确的理由。
   - 确保治理部分列出修正程序、版本控制策略和合规审查预期。

4. 一致性传播检查清单（将先前的检查清单转换为主动验证）：
   - 阅读 `.specify/templates/plan-template.md` 并确保任何“宪法检查”或规则与更新的原则保持一致。
   - 阅读 `.specify/templates/spec-template.md` 以对齐范围/需求——如果宪法添加/删除了强制部分或约束，请更新。
   - 阅读 `.specify/templates/tasks-template.md` 并确保任务分类反映新增或删除的原则驱动任务类型（例如 observability, versioning, testing discipline）。
   - 阅读 `.specify/templates/commands/*.md` 中的每个命令文件（包括本文件），以验证在需要通用指导时，没有遗留过时的引用（例如仅限 CLAUDE 等特定 Agent 名称）。
   - 阅读任何运行时指导文档（例如 `README.md`、`docs/quickstart.md` 或存在的特定 Agent 指导文件）。更新对已更改原则的引用。

5. 生成同步影响报告（更新后作为 HTML 注释前置在宪法文件顶部）：
   - 版本变更：old → new
   - 已修改原则列表（如果重命名则为 old title → new title）
   - 新增部分
   - 删除部分
   - 需要更新的模板（✅ 已更新 / ⚠ 待定）及其文件路径
   - 后续 TODO（如果有故意推迟的占位符）。

6. 最终输出前的验证：
   - 没有剩余未解释的方括号标记。
   - 版本行与报告匹配。
   - 日期采用 ISO 格式 YYYY-MM-DD。
   - 原则必须是声明性的、可测试的，并且没有模糊语言（"should" → 在适当情况下替换为 MUST/SHOULD 并说明理由）。

7. 将完成的宪法写回 `.specify/memory/constitution.md`（覆盖）。

8. 向用户输出最终摘要，包括：
   - 新版本及升级理由。
   - 任何标记为需要手动跟进的文件。
   - 建议的提交信息（例如 `docs: amend constitution to vX.Y.Z (principle additions + governance update)`）。

格式与样式要求：

- 完全按照模板使用 Markdown 标题（不要降低/提升级别）。
- 换行长理由行以保持可读性（理想情况下 <100 字符），但不要强制使用别扭的断行。
- 各部分之间保持一个空行。
- 避免尾随空格。

如果用户提供部分更新（例如仅修订一个原则），仍需执行验证和版本决策步骤。

如果缺少关键信息（例如确实未知的通过日期），请插入 `TODO(<FIELD_NAME>): explanation` 并将其列入同步影响报告的推迟项目中。

不要创建新模板；始终对现有的 `.specify/memory/constitution.md` 文件进行操作。