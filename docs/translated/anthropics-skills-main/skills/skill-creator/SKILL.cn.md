---
name: skill-creator
description: 创建新 skills，修改和改进现有 skills，并衡量 skill 性能。当用户想要从头创建 skill、编辑或优化现有 skill、运行 evals 测试 skill、通过方差分析对 skill 性能进行 benchmark，或优化 skill 描述以提高触发准确性时使用。
---

# Skill Creator

一个用于创建新 skills 并对其进行迭代改进的 skill。

宏观来看，创建 skill 的过程如下：

- 确定 skill 的功能及其大致实现方式
- 编写 skill 草稿
- 创建一些测试 prompt，并在其上运行 claude-with-access-to-the-skill
- 帮助用户定性和定量地评估结果
  - 当运行在后台进行时，如果没有定量 evals，则起草一些（如果已经有了，可以原样使用，或者如果你觉得需要改变则进行修改）。然后向用户解释它们（或者如果它们已经存在，解释那些已经存在的）
  - 使用 `eval-viewer/generate_review.py` 脚本向用户展示结果供其查看，并让他们查看定量指标
- 根据用户对结果的评估反馈重写 skill（如果定量 benchmarks 中出现了明显的缺陷，也要进行修改）
- 重复直到满意为止
- 扩展测试集并尝试更大规模的测试

使用此 skill 时，你的任务是弄清楚用户处于此过程的哪个阶段，然后介入并帮助他们推进这些阶段。例如，他们可能会说“我想为 X 制作一个 skill”。你可以帮助缩小他们的意图范围，编写草稿，编写测试用例，弄清楚他们想如何评估，运行所有 prompt，并重复此过程。

另一方面，也许他们已经有了 skill 草稿。在这种情况下，你可以直接进入循环的评估/迭代部分。

当然，你应该始终保持灵活，如果用户说“我不需要运行一堆评估，只需跟我随意聊聊”，你可以照做。

然后，在 skill 完成后（同样，顺序是灵活的），你还可以运行 skill 描述改进器，我们有一个单独的脚本用于优化 skill 的触发。

明白了吗？很好。

## 与用户沟通

Skill creator 可能会被对编码术语熟悉程度各异的人群使用。如果你还没听说过（你怎么可能听说过，这只是最近才开始的趋势），现在的趋势是 Claude 的强大能力正激励水管工打开终端，父母和祖父母去谷歌搜索“how to install npm”。另一方面，大部分用户可能具备相当好的计算机素养。

所以请注意上下文线索，以了解如何组织你的沟通语言！在默认情况下，给你一些参考：

- “evaluation”和“benchmark”处于临界点，但可以使用
- 对于“JSON”和“assertion”，在直接使用而不解释之前，你需要从用户那里看到明确的线索，表明他们知道这些是什么

如果你有疑问，简要解释术语是可以的，如果你不确定用户是否理解，可以随意用简短的定义来澄清术语。

---

## 创建 skill

### 捕捉意图

首先理解用户的意图。当前的对话可能已经包含用户想要捕获的工作流（例如，他们说“把它变成一个 skill”）。如果是这样，首先从对话历史中提取答案——使用的工具、步骤序列、用户所做的更正、观察到的输入/输出格式。用户可能需要填补空白，并应在进入下一步之前进行确认。

1. 这个 skill 应该让 Claude 能够做什么？
2. 这个 skill 何时应该触发？（什么用户短语/上下文）
3. 预期的输出格式是什么？
4. 我们是否应该设置测试用例来验证 skill 是否有效？具有客观可验证输出（文件转换、数据提取、代码生成、固定工作流步骤）的 skills 受益于测试用例。具有主观输出（写作风格、艺术）的 skills 通常不需要。根据 skill 类型建议适当的默认设置，但让用户决定。

### 访谈与研究

主动询问有关边缘情况、输入/输出格式、示例文件、成功标准和依赖关系的问题。在弄清楚这部分之前，先不要编写测试 prompt。

检查可用的 MCPs —— 如果对研究有用（搜索文档、查找相似 skills、查阅最佳实践），如果可用，通过 subagents 并行研究，否则在线研究。准备好上下文以减轻用户的负担。

### 编写 SKILL.md

根据用户访谈，填写以下组件：

- **name**：Skill 标识符
- **description**：何时触发，做什么。这是主要的触发机制——包括 skill 做什么以及在何种具体上下文下使用它。所有“何时使用”的信息都放在这里，而不是正文中。注意：目前 Claude 有一种“触发不足” skills 的倾向——即在有用时不使用它们。为了解决这个问题，请让 skill 描述稍微“强势”一点。例如，与其写“如何构建一个简单快速的仪表板以显示内部 Anthropic 数据。”，不如写“如何构建一个简单快速的仪表板以显示内部 Anthropic 数据。每当用户提到仪表板、数据可视化、内部指标，或想要显示任何类型的公司数据时，即使他们没有明确要求‘仪表板’，也务必使用此 skill。”
- **dependencies**：（如果适用）
- **inputs**：（如果适用）
- **outputs**：（如果适用）

### Skill 编写指南

#### Skill 的结构

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### 渐进式披露

Skills 使用三级加载系统：
1. **Metadata** (名称 + 描述) - 始终位于上下文中（约 100 词）
2. **SKILL.md body** - 当 skill 触发时位于上下文中（理想情况下 <500 行）
3. **Bundled resources** - 按需加载（无限制，脚本可在不加载的情况下执行）

这些词数仅为近似值，如有需要可适当超出。

**关键模式：**
- 将 SKILL.md 保持在 500 行以内；如果接近此限制，请增加一个层级结构，并附带清晰的指引，说明使用该 skill 的模型下一步应去往何处进行跟进。
- 在 SKILL.md 中清晰引用文件，并指导何时读取它们。
- 对于大型参考文件（>300 行），需包含目录。

**领域组织**：当 skill 支持多个领域/框架时，按变体进行组织：

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Claude 仅读取相关的参考文件。

#### 无意外原则

不言而喻，技能不得包含恶意软件、漏洞利用代码或任何可能危及系统安全的内容。如果对技能的内容进行描述，其意图不应让用户感到意外。不要配合创建误导性技能，或旨在协助未经授权访问、数据窃取或其他恶意活动的技能的请求。不过，诸如“扮演 XYZ”之类的内容是允许的。

#### 编写模式

在指令中优先使用祈使语气。

**定义输出格式** - 你可以这样做：

```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**示例模式** - 包含示例很有用。您可以按如下方式格式化（但如果示例中包含 "Input" 和 "Output"，您可能需要稍作调整）：

```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### 写作风格

尝试向模型解释事情为何重要，而非生硬陈旧地强制要求。运用心智理论，尽量使技能具有通用性，而非局限于特定示例。首先撰写草稿，然后以全新的视角审视并加以改进。

### 测试用例

编写完技能草稿后，构思 2-3 个真实的测试提示词——即真实用户实际会提出的内容。与用户分享这些提示词：[不必完全照搬原话] “这里有几个我想尝试的测试用例。这些看起来没问题吗，还是你想添加更多？” 然后运行它们。

将测试用例保存到 `evals/evals.json`。暂时不要编写断言——只保留提示词。你将在下一步运行过程中起草断言。

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

请参阅 `references/schemas.md` 查看完整 schema（包括稍后将添加的 `assertions` 字段）。

## 运行和评估测试用例

本节是一个连续的操作流程——请勿中途停止。切勿使用 `/skill-test` 或任何其他测试 skill。

将结果放入与 skill 目录同级的 `<skill-name>-workspace/` 中。在工作区内，按迭代组织结果（`iteration-1/`、`iteration-2/` 等），在迭代目录下，每个测试用例对应一个目录（`eval-0/`、`eval-1/` 等）。请勿提前创建所有目录——只需在过程中按需创建。

### 步骤 1：在同一轮次中派生所有运行（with-skill 和 baseline）

对于每个测试用例，在同一轮次中派生两个 subagent——一个使用 skill，一个不使用。这一点很重要：不要先派生 with-skill 运行，然后再回头处理 baseline。同时启动所有任务，以便它们大致同时完成。

**With-skill 运行：**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline 运行**（相同的 prompt，但 baseline 取决于上下文）：
- **创建新 skill**：完全没有 skill。相同的 prompt，无 skill path，保存到 `without_skill/outputs/`。
- **改进现有 skill**：旧版本。编辑前，对 skill 建立快照（`cp -r <skill-path> <workspace>/skill-snapshot/`），然后将 baseline subagent 指向该快照。保存到 `old_skill/outputs/`。

为每个测试用例编写一个 `eval_metadata.json`（assertions 暂时可以为空）。根据测试内容为每个 eval 起一个描述性名称——不要只是 "eval-0"。目录名称也使用该名称。如果本次迭代使用了新的或修改过的 eval prompts，请为每个新的 eval 目录创建这些文件——不要假设它们会从之前的迭代中沿用。

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### 步骤 2：当运行进行时，起草断言

不要干等运行结束——你可以充分利用这段时间。为每个测试用例起草定量断言，并向用户解释。如果 `evals/evals.json` 中已存在断言，请检查它们并解释其检查内容。

优秀的断言是客观可验证的，并且具有描述性名称——它们应在基准查看器中清晰可读，以便查看结果的人能立即理解每项检查的内容。主观技能（写作风格、设计质量）更适合进行定性评估——不要对需要人工判断的内容强行添加断言。

断言起草完成后，更新 `eval_metadata.json` 文件和 `evals/evals.json`。同时向用户解释他们将在查看器中看到的内容——包括定性输出和定量基准。

### 步骤 3：当运行完成时，捕获计时数据

当每个 subagent 任务完成时，你会收到一条包含 `total_tokens` 和 `duration_ms` 的通知。立即将此数据保存到运行目录下的 `timing.json` 中：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

这是捕获此数据的唯一机会——它随任务通知传递，未在其他地方持久化。请在通知到达时逐个处理，而不是尝试批量处理。

### 步骤 4：评分、聚合并启动 viewer

一旦所有运行完成：

1. **对每次运行进行评分** —— 生成一个 grader subagent（或内联评分），读取 `agents/grader.md` 并根据输出评估每个断言。将结果保存到每个运行目录下的 `grading.json` 中。`grading.json` 的 expectations 数组必须使用 `text`、`passed` 和 `evidence` 字段（而不是 `name`/`met`/`details` 或其他变体）—— viewer 依赖于这些确切的字段名称。对于可以通过编程方式检查的断言，请编写并运行脚本，而不是人工检查 —— 脚本更快、更可靠，并且可以在迭代中复用。

2. **聚合为基准测试** —— 从 skill-creator 目录运行聚合脚本：

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

此操作会生成 `benchmark.json` 和 `benchmark.md`，其中包含每种配置的 pass_rate、time 和 tokens，以及 mean ± stddev 和 delta。如果手动生成 benchmark.json，请参阅 `references/schemas.md` 以了解 viewer 所需的确切 schema。将每个 with_skill 版本置于其对应的 baseline 版本之前。

3. **进行分析师审查** —— 阅读 benchmark 数据，找出汇总统计数据可能掩盖的模式。请参阅 `agents/analyzer.md`（"Analyzing Benchmark Results" 章节）了解具体关注点，例如无论是否有 skill 都通过的断言、高方差的 evals（可能不稳定）以及 time/token 的权衡。

4. **启动 viewer**，加载定性输出和定量数据：

```bash
nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
```

对于第 2 次及以后的迭代，还需传入 `--previous-workspace <workspace>/iteration-<N-1>`。

**协作 / 无头环境：** 如果 `webbrowser.open()` 不可用或环境无显示器，请使用 `--static <output_path>` 写入一个独立的 HTML 文件，而非启动服务器。当用户点击 "Submit All Reviews" 时，反馈将作为 `feedback.json` 文件下载。下载后，将 `feedback.json` 复制到工作区目录中，供下一次迭代读取。

注意：请使用 generate_review.py 创建查看器；无需编写自定义 HTML。

5. **告知用户** 类似于：“我已在您的浏览器中打开结果。有两个标签页 —— ‘Outputs’ 允许您点击查看每个测试用例并留下反馈，‘Benchmark’ 显示定量比较。完成后，请回到此处告知我。”

### 用户在查看器中看到的内容

“Outputs” 标签页一次显示一个测试用例：
- **Prompt**：给定的任务
- **Output**：技能生成的文件，尽可能进行内联渲染
- **Previous Output**（第 2 次及以后的迭代）：显示上一次迭代输出的折叠区域
- **Formal Grades**（如果运行了评分）：显示断言通过/失败情况的折叠区域
- **Feedback**：输入时自动保存的文本框
- **Previous Feedback**（第 2 次及以后的迭代）：上次的评论，显示在文本框下方

“Benchmark” 标签页显示统计摘要：每个配置的通过率、耗时和 token 使用量，以及每次评估的细分数据和分析师观察。

通过上一个/下一个按钮或方向键进行导航。完成后，他们点击 "Submit All Reviews"，这将所有反馈保存到 `feedback.json`。

### 步骤 5：读取反馈

当用户告诉你他们已完成时，读取 `feedback.json`：

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

反馈为空意味着用户认为没问题。将改进重点集中在用户有具体抱怨的测试用例上。

使用完毕后终止 viewer server：

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## 改进 skill

这是循环的核心。你已经运行了测试用例，用户已经审查了结果，现在你需要根据他们的反馈来改进 skill。

### 如何思考改进

1. **从反馈中进行泛化。** 这里的大局在于，我们正试图创建能跨越许多不同 prompts 使用数百万次（或许是字面意思，甚至更多）的 skills。此刻你和用户仅针对几个示例反复迭代，因为这有助于加快进度。用户对这些示例了如指掌，因此评估新输出非常快。但是，如果你和用户共同开发的 skill 仅适用于这些示例，那它就毫无用处。与其进行繁琐且过拟合的修改，或是制定压迫性的强制约束（MUST），如果遇到顽固问题，不如尝试拓展思路，使用不同的隐喻，或推荐不同的工作模式。尝试成本相对较低，也许你会偶然发现很棒的方案。

2. **保持 prompt 精简。** 移除那些没有发挥作用的内容。务必阅读执行记录，而不仅仅是最终输出 —— 如果 skill 让模型浪费大量时间进行无效操作，你可以尝试删除 skill 中导致该行为的部分，观察后果。

3. **解释原因。** 尽力解释你要求模型做的每件事背后的**原因**。如今的 LLMs *非常聪明*。它们拥有良好的心智能力，当被给予良好的引导框架时，能够超越死板的指令，真正把事情做成。即使用户的反馈简短或带有挫败感，也要尝试真正理解任务，理解用户为何这样写以及他们实际写了什么，然后将这种理解转化为指令。如果你发现自己正在用全大写书写 ALWAYS 或 NEVER，或使用过度僵硬的结构，这就是一个警示信号 —— 如果可能，请重构并解释推理过程，让模型理解你所要求事项的重要性。这是一种更人性化、强大且有效的方法。

4. **寻找跨测试用例的重复工作。** 阅读测试运行的记录，注意 subagents 是否都独立编写了相似的辅助脚本，或对某事采取了相同的多步骤方法。如果所有 3 个测试用例中 subagent 都编写了 `create_docx.py` 或 `build_chart.py`，这就是一个强烈的信号，表明 skill 应该打包该脚本。编写一次，放入 `scripts/`，并指示 skill 使用它。这能避免未来的每次调用重复造轮子。

这项任务相当重要（我们正试图在此每年创造数十亿的经济价值！），你的思考时间并不是瓶颈；请花时间真正深思熟虑。我建议先写一份修改草案，然后重新审视并进行改进。务必尽力设身处地理解用户，明白他们的想要和需求。

### 迭代循环

改进 skill 后：

1. 将你的改进应用到 skill 中
2. 将所有测试用例重新运行到一个新的 `iteration-<N+1>/` 目录中，包括基线运行。如果你正在创建一个新的 skill，基线始终是 `without_skill`（无 skill）—— 这在迭代过程中保持不变。如果你正在改进现有的 skill，请自行判断什么作为基线更合理：用户带来的原始版本，还是上一次迭代。
3. 启动 reviewer，并使用 `--previous-workspace` 指向上一次迭代
4. 等待用户审查并告诉你他们完成了
5. 阅读新的反馈，再次改进，重复此过程

持续进行直到：
- 用户表示满意
- 反馈全部为空（一切看起来都不错）
- 你没有取得实质性进展

---

## 高级：盲测对比

对于需要在 skill 的两个版本之间进行更严格比较的情况（例如，用户问“新版本真的更好吗？”），有一个盲测对比系统。请阅读 `agents/comparator.md` 和 `agents/analyzer.md` 了解详情。其基本思想是：将两个输出提供给一个独立的 agent，不告知它哪个是哪个，让它评判质量。然后分析获胜者为何获胜。

这是可选的，需要 subagents，大多数用户不需要它。人工审查循环通常就足够了。

---

## 描述优化

`SKILL.md` frontmatter 中的 description 字段是决定 Claude 是否调用 skill 的主要机制。在创建或改进 skill 后，提议优化描述以获得更好的触发准确性。

### 步骤 1：生成触发评估查询

创建 20 个评估查询 —— 混合应触发和不应触发的查询。保存为 JSON：

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

查询内容必须真实，必须是 Claude Code 或 Claude.ai 用户实际会输入的内容。不要抽象的请求，而要具体、明确且包含丰富细节的请求。例如，文件路径、关于用户工作或情况的个人背景信息、列名和值、公司名称、URL。还要有一点背景故事。有些可能是小写的，或者包含缩写、拼写错误或口语化表达。混合使用不同的长度，并关注边缘情况，而不是让它们过于清晰明确（用户将有机会对它们进行确认）。

反例：`"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

正例：`"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

对于 **should-trigger**（应触发）查询（8-10个），请考虑覆盖率。你需要同一意图的不同措辞——有些正式，有些随意。包括用户未明确说出技能或文件类型但显然需要它的情况。加入一些不常见的用例，以及该技能与另一技能竞争但应胜出的情况。

对于 **should-not-trigger**（不应触发）查询（8-10个），最有价值的是那些“差点命中”的情况——即与该技能共享关键词或概念，但实际上需要不同东西的查询。考虑相邻领域、因歧义措辞导致简单关键词匹配会触发但不应触发的情况，以及查询涉及该技能所做之事但上下文更适合使用其他工具的情况。

要避免的一个关键点：不要让 should-not-trigger 查询显得明显无关。针对 PDF 技能的负面测试，如果用 `"Write a fibonacci function"` 就太简单了——这测试不出任何东西。负面案例应该具有真正的迷惑性。

### 步骤 2：与用户一起审查

使用 HTML 模板向用户展示评估集以供审查：

1. 从 `assets/eval_review.html` 读取模板
2. 替换占位符：
   - `__EVAL_DATA_PLACEHOLDER__` → eval 项的 JSON 数组（周围不要加引号——这是一个 JS 变量赋值）
   - `__SKILL_NAME_PLACEHOLDER__` → 技能名称
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → 技能的当前描述
3. 写入临时文件（例如 `/tmp/eval_review_<skill-name>.html`）并打开它：`open /tmp/eval_review_<skill-name>.html`
4. 用户可以编辑查询、切换 should-trigger 状态、添加/删除条目，然后点击 "Export Eval Set"
5. 文件将下载到 `~/Downloads/eval_set.json` —— 检查 Downloads 文件夹以获取最新版本，以防存在多个文件（例如 `eval_set (1).json`）

这一步至关重要——糟糕的评估查询会导致糟糕的描述。

### 步骤 3：运行优化循环

告诉用户：“这需要一些时间——我会在后台运行优化循环并定期检查。”

将评估集保存到工作区，然后在后台运行：

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

使用你 system prompt 中的 model ID（即支持当前会话的那个），以便触发测试与用户的实际体验相符。

在运行过程中，定期追踪输出，向用户更新当前的迭代次数和得分情况。

这会自动处理完整的优化循环。它将 eval set 分为 60% 的 train 和 40% 的 held-out test，评估当前描述（每个 query 运行 3 次以获得可靠的触发率），然后调用 Claude 根据失败的情况提出改进建议。它会在 train 和 test 上重新评估每个新描述，最多迭代 5 次。完成后，它会在浏览器中打开一个 HTML 报告，显示每次迭代的结果，并返回包含 `best_description` 的 JSON —— 该描述是根据 test 得分而不是 train 得分选出的，以避免 overfitting。

### Skill 触发机制的工作原理

理解触发机制有助于设计更好的 eval queries。Skills 会显示在 Claude 的 `available_skills` 列表中，包含其名称和描述，Claude 根据该描述决定是否使用 skill。需要了解的重要一点是，Claude 只会针对它无法轻松独自处理的任务使用 skills —— 像 "read this PDF" 这样简单的一步查询可能不会触发 skill，即使描述完美匹配，因为 Claude 可以使用基本工具直接处理它们。当描述匹配时，复杂、多步或专业的 queries 会可靠地触发 skills。

这意味着你的 eval queries 应该足够充实，让 Claude 确实能从使用 skill 中受益。像 "read file X" 这样的简单查询是糟糕的测试用例 —— 无论描述质量如何，它们都不会触发 skills。

### Step 4: 应用结果

从 JSON 输出中获取 `best_description` 并更新 skill 的 SKILL.md frontmatter。向用户展示修改前后的内容并报告得分。

---

### 打包并展示（仅在 `present_files` tool 可用时）

检查你是否有权访问 `present_files` tool。如果没有，跳过此步骤。如果有，打包 skill 并向用户展示 .skill 文件：

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

打包完成后，引导用户找到生成的 `.skill` 文件路径，以便他们进行安装。

---

## Claude.ai 特定说明

在 Claude.ai 中，核心工作流程保持不变（起草 → 测试 → 审查 → 改进 → 循环），但由于 Claude.ai 没有 subagents，部分机制需要调整。以下是需要适配的内容：

**运行测试用例**：没有 subagents 意味着无法并行执行。对于每个测试用例，阅读 skill 的 SKILL.md，然后按照其指示自行完成测试提示。请逐个执行。这不如独立的 subagents 严谨（因为是你编写了 skill，现在又由你运行它，所以你拥有完整的上下文），但这是一种有效的完整性检查 —— 而且人工审查步骤可以弥补这一不足。跳过基线运行 —— 直接使用 skill 按要求完成任务即可。

**审查结果**：如果无法打开浏览器（例如 Claude.ai 的 VM 没有显示器，或者你在远程服务器上），请完全跳过浏览器审查环节。相反，直接在对话中展示结果。对于每个测试用例，展示提示词和输出结果。如果输出是用户需要查看的文件（如 .docx 或 .xlsx），将其保存到文件系统并告知用户位置，以便他们下载和检查。在对话中直接询问反馈：“这个看起来怎么样？有什么需要修改的地方吗？”

**基准测试**：跳过定量基准测试 —— 它依赖于基线对比，而在没有 subagents 的情况下这没有意义。重点关注用户的定性反馈。

**迭代循环**：与之前相同 —— 改进 skill，重新运行测试用例，征求反馈 —— 只是中间不再包含浏览器审查环节。如果你有文件系统，仍然可以将结果组织到迭代目录中。

**描述优化**：此部分需要 `claude` CLI 工具（特别是 `claude -p`），该工具仅在 Claude Code 中可用。如果你在 Claude.ai 上，请跳过此步骤。

**盲测对比**：需要 subagents。请跳过。

**打包**：只要有 Python 和文件系统，`package_skill.py` 脚本就可以在任何地方运行。在 Claude.ai 上，你可以运行它，用户可以下载生成的 `.skill` 文件。

**更新现有 skill**：用户可能是要求你更新现有的 skill，而不是创建新的。在这种情况下：
- **保留原始名称。** 记下 skill 的目录名和 `name` frontmatter 字段 —— 保持它们不变。例如，如果安装的 skill 是 `research-helper`，则输出 `research-helper.skill`（而不是 `research-helper-v2`）。
- **编辑前复制到可写位置。** 安装的 skill 路径可能是只读的。复制到 `/tmp/skill-name/`，在那里编辑，并从副本进行打包。
- **如果手动打包，先存放在 `/tmp/` 中**，然后复制到输出目录 —— 直接写入可能因权限问题而失败。

---

## Cowork 特定说明

如果你身处 Cowork 环境，主要需要注意以下几点：

- 你拥有 subagents，因此主工作流程（并行生成测试用例、运行基线、评分等）均能正常运行。（但是，如果遇到严重的超时问题，可以改为串行而非并行运行测试提示。）
- 你没有浏览器或显示器，因此在生成评估查看器时，请使用 `--static <output_path>` 写入独立的 HTML 文件，而不是启动服务器。然后提供一个链接，供用户点击在他们的浏览器中打开该 HTML。
- 无论出于何种原因，Cowork 环境似乎会导致 Claude 在运行测试后不愿意生成评估查看器，所以再次重申：无论你是在 Cowork 还是 Claude Code 中，运行测试后，你都应该始终生成评估查看器供人工查看示例，然后再自己修改 skill 并尝试纠正，请使用 `generate_review.py`（而不是编写你自己特有的 HTML 代码）。抱歉我要用大写字母强调了：在你自己评估输入*之前*生成评估查看器。你需要尽快让用户看到它们！
- 反馈机制有所不同：由于没有运行中的服务器，查看器的“Submit All Reviews”按钮会将 `feedback.json` 作为文件下载。然后你可以从中读取（可能需要先请求访问权限）。
- 打包功能正常 —— `package_skill.py` 只需要 Python 和文件系统即可运行。
- 描述优化（`run_loop.py` / `run_eval.py`）在 Cowork 中应该能正常运行，因为它通过 subprocess 使用 `claude -p`，而不是浏览器，但请务必等到你完全完成 skill 制作且用户认可其状态良好后再进行。
- **更新现有 skill**：用户可能是要求你更新现有的 skill，而不是创建新的。请遵循上文 claude.ai 部分中的更新指导。

---

## 参考文件

agents/ 目录包含专门 subagents 的说明。当你需要生成相关 subagent 时，请阅读它们。

- `agents/grader.md` — 如何根据输出评估断言
- `agents/comparator.md` — 如何在两个输出之间进行盲测 A/B 对比
- `agents/analyzer.md` — 如何分析一个版本为何优于另一个版本

references/ 目录包含额外的文档：
- `references/schemas.md` — evals.json、grading.json 等的 JSON 结构。

---

再次重复此处的核心循环以示强调：

- 弄清楚 skill 的用途
- 起草或编辑 skill
- 在测试提示上运行 claude-with-access-to-the-skill
- 与用户一起评估输出：
  - 创建 benchmark.json 并运行 `eval-viewer/generate_review.py` 以帮助用户审查它们
  - 运行定量评估
- 重复此过程直到你和用户都满意为止
- 打包最终的 skill 并将其返还给用户。

如果你有待办事项列表，请将这些步骤添加进去，以确保不会遗忘。如果你在 Cowork 中，请务必将“创建 evals JSON 并运行 `eval-viewer/generate_review.py` 以便人工审查测试用例”放入你的待办事项列表，以确保执行此操作。

祝你好运！