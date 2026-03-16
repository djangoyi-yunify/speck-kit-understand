---
name: skill-creator
description: 创建新技能，修改和改进现有技能，并衡量技能性能。当用户希望从头开始创建技能、编辑或优化现有技能、运行 evals 以测试技能、通过方差分析对技能性能进行基准测试，或优化技能描述以提高触发准确性时使用。
---

# Skill Creator

一个用于创建新技能并对其进行迭代改进的 skill。

宏观来看，创建 skill 的过程如下：

- 确定 skill 的功能以及大致的实现方式
- 编写 skill 的草稿
- 创建一些测试 prompt，并在这些 prompt 上运行拥有该 skill 访问权限的 Claude
- 帮助用户对结果进行定性和定量评估
  - 在后台运行的同时，如果还没有定量的 evals，则起草一些（如果已有，可以按原样使用，或者如果你觉得需要更改，也可以进行修改）。然后向用户解释这些 evals（或者如果它们已经存在，解释那些已经存在的 evals）
  - 使用 `eval-viewer/generate_review.py` 脚本向用户展示结果供其查看，并让他们查看定量指标
- 根据用户对结果的评估反馈重写 skill（同时也针对定量基准测试中暴露出的明显缺陷进行修改）
- 重复此过程直到满意为止
- 扩展测试集并在更大规模上再次尝试

使用此 skill 时，你的任务是判断用户处于流程中的哪个阶段，然后介入并帮助他们推进这些阶段。例如，他们可能会说“我想为 X 制作一个 skill”。你可以帮助明确他们的具体意图、编写草稿、编写测试用例、确定他们想要的评估方式、运行所有 prompt，并重复此过程。

另一方面，也许他们已经有了 skill 的草稿。在这种情况下，你可以直接进入循环中的评估/迭代部分。

当然，你应该始终保持灵活，如果用户说“我不需要运行一堆评估，跟着我的感觉走就行”，那你也可以照做。

然后，在 skill 完成后（但再次强调，顺序是灵活的），你还可以运行 skill description improver（我们有一个单独的脚本用于此），以优化 skill 的触发。

明白了吗？好的。

## 与用户沟通

Skill creator 的用户可能涵盖对代码术语熟悉程度各不相同的人群。如果你还没听说过（你怎么可能听说过呢，这也是最近才开始的趋势），现在的趋势是 Claude 的强大能力正在激励水管工打开终端，父母和祖父母去谷歌搜索“如何安装 npm”。另一方面，大部分用户可能都具备相当的计算机素养。

所以请注意上下文线索，以了解如何措辞你的沟通！在默认情况下，仅为了给你一个概念：

- “evaluation”和“benchmark”处于边缘地带，但可以使用
- 对于“JSON”和“assertion”，在未加解释直接使用之前，你需要从用户那里看到明确的线索，表明他们知道这些是什么

如果你不确定，可以简要解释术语；如果你不确定用户是否理解，请随时用简短的定义澄清术语。

---

## 创建 skill

### 捕捉意图

从理解用户的意图开始。当前的对话可能已经包含了用户想要捕获的工作流（例如，他们说“把这个变成一个 skill”）。如果是这样，首先从对话历史中提取答案——使用的工具、步骤顺序、用户所做的修正、观察到的输入/输出格式。用户可能需要填补空白，并应在进入下一步之前进行确认。

1. 这个 skill 应该让 Claude 能够做什么？
2. 这个 skill 何时应该触发？（哪些用户短语/上下文）
3. 预期的输出格式是什么？
4. 我们是否应该设置测试用例来验证 skill 是否有效？具有客观可验证输出（文件转换、数据提取、代码生成、固定工作流步骤）的 skill 受益于测试用例。具有主观输出（写作风格、艺术创作）的 skill 通常不需要。根据 skill 类型建议适当的默认设置，但让用户决定。

### 访谈与研究

主动询问有关边缘情况、输入/输出格式、示例文件、成功标准和依赖项的问题。等到这部分解决后，再编写测试 prompt。

检查可用的 MCP —— 如果对研究有用（搜索文档、查找类似 skill、查阅最佳实践），如果可用，则通过 subagent 并行研究，否则在对话中进行。准备好上下文以减少用户的负担。

### 编写 SKILL.md

根据用户访谈，填写以下组件：

- **name**：Skill 标识符
- **description**：何时触发，它的作用。这是主要的触发机制——包括 skill 的功能以及何时使用它的具体上下文。所有“何时使用”的信息都放在这里，而不是正文中。注意：目前 Claude 倾向于“触发不足”——即在该有用的时候不使用它们。为了防止这种情况，请让 skill 描述稍微“强势”一点。例如，与其写“如何构建一个简单快速的仪表板来显示内部 Anthropic 数据”，不如写“如何构建一个简单快速的仪表板来显示内部 Anthropic 数据。每当用户提到仪表板、数据可视化、内部指标，或想要显示任何类型的公司数据时，即使他们没有明确要求‘仪表板’，也要务必使用此 skill。”
- **compatibility**：所需工具、依赖项（可选，很少需要）
- **skill 的其余部分 :)**

### Skill 编写指南

#### Skill 的剖析

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

Skills 采用三级加载系统：
1. **Metadata**（名称 + 描述）- 始终存在于上下文中（约 100 词）
2. **SKILL.md body** - 当 skill 触发时存在于上下文中（理想情况 <500 行）
3. **Bundled resources** - 按需加载（无限制，脚本可在未加载状态下执行）

这些字数仅为近似值，如有需要可适当增加篇幅。

**关键模式：**
- 保持 SKILL.md 在 500 行以内；如果接近此限制，请增加一个层级，并明确指出使用该 skill 的 model 接下来应去往何处进行后续操作。
- 在 SKILL.md 中清晰地引用文件，并指导何时读取它们。
- 对于大型参考文件（>300 行），需包含目录。

**领域组织**：当一个 skill 支持多个领域/框架时，请按变体进行组织：

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Claude 仅读取相关的参考文件。

#### 不令人惊讶原则

不言而喻，技能不得包含恶意软件、漏洞利用代码或任何可能危及系统安全的内容。若经描述，技能内容的意图不应令用户感到意外。请勿配合创建误导性技能，或旨在协助未授权访问、数据窃取或其他恶意活动的技能。不过，诸如“扮演 XYZ”之类的内容是可以的。

#### 写作模式

指令中优先使用祈使句。

**定义输出格式** - 你可以这样做：

```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**示例模式** - 包含示例很有用。您可以按如下格式编排（但如果示例中包含 "Input" 和 "Output"，您可能需要稍作调整）：

```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### 写作风格

与其使用生硬陈旧的强制性指令（MUST），不如尝试向模型解释事物为何重要。运用 theory of mind，尽量使技能具有通用性，而非仅局限于特定示例。先写一份草稿，然后以全新的视角审视并进行改进。

### 测试用例

编写完技能草稿后，构思 2-3 个现实的测试 prompts —— 即真实用户实际会说出的那种内容。将其分享给用户：[不必完全使用这段原话] “我想尝试这几个测试用例。它们看起来合适吗？还是你想添加更多？” 然后运行它们。

将测试用例保存到 `evals/evals.json`。暂不要编写 assertions —— 只需包含 prompts。你将在下一步运行过程中起草 assertions。

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

请参阅 `references/schemas.md` 获取完整 schema（包括稍后将添加的 `assertions` 字段）。

## 运行和评估测试用例

本节是一个连续的流程 —— 请勿中途停止。请勿使用 `/skill-test` 或任何其他测试技能。

将结果放入 `<skill-name>-workspace/` 中，该目录应与技能目录同级。在工作区内，按迭代组织结果（`iteration-1/`、`iteration-2/` 等），在迭代目录内，每个测试用例各占一个目录（`eval-0/`、`eval-1/` 等）。不要预先创建所有目录 —— 随用随建。

### 步骤 1：在同一轮次中生成所有运行（with-skill 和 baseline）

对于每个测试用例，在同一轮次中生成两个子代理 —— 一个使用技能，一个不使用。这一点很重要：不要先生成 with-skill 运行，然后再回来处理 baseline。一次性启动所有内容，以便它们大约在同一时间完成。

**With-skill 运行：**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**基线运行**（同样的提示词，但基线取决于上下文）：
- **创建新的 Skill**：完全没有 Skill。同样的提示词，没有 Skill 路径，保存到 `without_skill/outputs/`。
- **改进现有的 Skill**：旧版本。在编辑之前，对 Skill 建立快照（`cp -r <skill-path> <workspace>/skill-snapshot/`），然后将基线 subagent 指向该快照。保存到 `old_skill/outputs/`。

为每个测试用例编写一个 `eval_metadata.json`（断言目前可以为空）。根据测试内容为每个 eval 起一个描述性的名称——不要只是 "eval-0"。将此名称也用于目录名。如果此次迭代使用新的或修改过的 eval 提示词，请为每个新的 eval 目录创建这些文件——不要假设它们会从之前的迭代中继承。

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### 步骤 2：当运行正在进行时，起草 assertions

不要只是等待运行结束——你可以高效利用这段时间。为每个测试用例起草定量的 assertions 并向用户解释。如果 `evals/evals.json` 中已经存在 assertions，请审查它们并解释它们检查的内容。

好的 assertions 是客观可验证的，并且具有描述性名称——它们应该在 benchmark viewer 中清晰可读，以便有人扫视结果时能立即理解每一项检查的内容。主观技能（写作风格、设计质量）最好通过定性方式评估——不要强行将 assertions 用于需要人工判断的事物上。

一旦起草完成，请使用 assertions 更新 `eval_metadata.json` 文件和 `evals/evals.json`。还要向用户解释他们将在 viewer 中看到什么——包括定性输出和定量 benchmark。

### 步骤 3：当运行完成时，捕获计时数据

当每个 subagent task 完成时，你会收到一个包含 `total_tokens` 和 `duration_ms` 的通知。请立即将此数据保存到运行目录中的 `timing.json`：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

这是捕获此数据的唯一机会——它随任务通知传递，不会在其他地方持久化。应在通知到达时逐一处理，而不是尝试进行批处理。

### 步骤 4：评分、聚合并启动查看器

所有运行完成后：

1. **对每次运行进行评分** —— 生成一个评分子代理（或进行内联评分），该代理读取 `agents/grader.md` 并根据输出评估每个断言。将结果保存到每个运行目录下的 `grading.json` 文件中。`grading.json` 的 expectations 数组必须使用 `text`、`passed` 和 `evidence` 字段（不能使用 `name`/`met`/`details` 或其他变体）—— 查看器依赖于这些精确的字段名称。对于可以通过编程方式检查的断言，请编写并运行脚本，而非进行人工目测 —— 脚本更快、更可靠，且可在多次迭代中重用。

2. **聚合为基准测试** —— 在 skill-creator 目录下运行聚合脚本：

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

这会生成 `benchmark.json` 和 `benchmark.md`，其中包含每个 configuration 的 pass_rate、time 和 tokens，以及 mean ± stddev 和 delta。如果手动生成 benchmark.json，请参阅 `references/schemas.md` 了解 viewer 期望的确切 schema。
将每个 with_skill version 排在其对应的 baseline counterpart 之前。

3. **进行一轮分析** —— 阅读基准测试数据并揭示聚合统计数据可能掩盖的模式。请参阅 `agents/analyzer.md`（“Analyzing Benchmark Results”一节）以了解需要关注的内容——例如无论 skill 如何总是通过的断言（无区分度）、高方差的评估（可能不稳定）以及 time/token 权衡。

4. **启动 viewer**，同时加载定性输出和定量数据：

```bash
nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
```

对于第 2 次及以后的迭代，还需传递 `--previous-workspace <workspace>/iteration-<N-1>`。

**Cowork / headless 环境：** 如果 `webbrowser.open()` 不可用或环境没有显示器，请使用 `--static <output_path>` 写入一个独立的 HTML 文件，而不是启动服务器。当用户点击 "Submit All Reviews" 时，反馈将作为 `feedback.json` 文件下载。下载后，将 `feedback.json` 复制到工作空间目录，以便下一次迭代时读取。

注意：请使用 generate_review.py 创建查看器；无需编写自定义 HTML。

5. **告知用户** 类似以下内容：“我已在浏览器中打开了结果。有两个标签页 —— ‘Outputs’ 让你可以点击查看每个测试用例并留下反馈，‘Benchmark’ 显示定量比较。完成后，回到这里告诉我。”

### 用户在查看器中看到的内容

“Outputs” 标签页一次显示一个测试用例：
- **Prompt**：给出的任务
- **Output**：skill 生成的文件，尽可能在页面内渲染
- **Previous Output** (迭代 2+)：折叠区域，显示上一次迭代的输出
- **Formal Grades**（如果运行了评分）：折叠区域，显示断言通过/失败情况
- **Feedback**：文本框，输入时自动保存
- **Previous Feedback** (迭代 2+)：上次的评论，显示在文本框下方

“Benchmark” 标签页显示统计摘要：每种配置的通过率、耗时和 token 使用情况，以及每次评估的细分数据和分析师观察结果。

可以通过上一页/下一页按钮或方向键进行导航。完成后，他们点击 "Submit All Reviews"，这会将所有反馈保存到 `feedback.json`。

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

空反馈意味着用户认为没问题。请将改进重点放在用户有具体不满的测试用例上。

使用完毕后，请终止 viewer server：

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## 改进技能

这是循环的核心。你已经运行了测试用例，用户已经审查了结果，现在你需要根据他们的反馈改进技能。

### 如何思考改进

1. **从反馈中进行泛化。** 这里的核心目标是，我们试图创建可以在数百万次不同的 prompts 中使用的技能（可能字面上就是百万次，甚至更多，谁知道呢）。在这里，你和用户只在少数几个示例上反复迭代，因为这有助于加快速度。用户对这些示例了如指掌，评估新输出对他们来说很快。但是，如果你和用户共同开发的技能仅适用于这些示例，那它就毫无用处。与其做一些繁琐的过拟合修改，或者设定压迫性的“必须（MUST）”约束，如果遇到顽固问题，不如尝试扩展思路，使用不同的隐喻，或推荐不同的工作模式。尝试的成本相对较低，也许你会找到很棒的方法。

2. **保持 prompt 精简。** 移除那些没有发挥作用的内容。务必阅读记录，而不仅仅是最终输出——如果看起来技能让模型浪费了大量时间做无用功，你可以尝试移除技能中导致这种情况的部分，看看会发生什么。

3. **解释原因。** 尽力解释你要求模型做每一件事的**原因**。如今的 LLMs *非常聪明*。它们具有良好的心智理论，在给予良好的引导下，能够超越死板的指令，真正把事情做成。即使用户的反馈简短或充满挫败感，也要尝试真正理解任务，理解用户为什么这样写以及他们实际写了什么，然后将这种理解传达给指令。如果你发现自己正在用全大写字母写“ALWAYS”或“NEVER”，或者使用超级僵化的结构，那就是一个警示信号——如果可能的话，重构并解释推理过程，让模型理解你要求的事情为何重要。这是一种更人性化、更强大且有效的方法。

4. **寻找跨测试用例的重复工作。** 阅读测试运行的记录，注意 subagents 是否都独立编写了类似的辅助脚本，或者对某事采取了相同的多步骤方法。如果所有 3 个测试用例都导致 subagent 编写了 `create_docx.py` 或 `build_chart.py`，这是一个强烈的信号，表明该技能应该内置该脚本。编写一次，将其放入 `scripts/`，并告诉技能使用它。这能节省后续每一次调用的时间，避免重复造轮子。

这项任务非常重要（我们要在这里创造每年数十亿美元的经济价值！），你的思考时间不是瓶颈；慢慢来，仔细斟酌。我建议先写一份修改草案，然后重新审视并进行改进。务必尽力站在用户的角度思考，理解他们想要和需要什么。

### 迭代循环

改进技能后：

1. 将你的改进应用到技能中
2. 将所有测试用例重新运行到一个新的 `iteration-<N+1>/` 目录中，包括基线运行。如果你正在创建一个新技能，基线始终是 `without_skill`（无技能）——这在各次迭代中保持不变。如果你正在改进现有技能，请根据判断选择作为基线合理的内容：用户带来的原始版本，还是上一次迭代。
3. 启动审查器，并使用 `--previous-workspace` 指向上一次迭代
4. 等待用户审查并告诉你他们已完成
5. 阅读新的反馈，再次改进，重复此过程

继续进行，直到：
- 用户表示满意
- 反馈全部为空（一切看起来都不错）
- 你没有取得实质性的进展

---

## 高级：盲测比较

对于想要更严格地比较技能的两个版本的情况（例如，用户问“新版本真的更好吗？”），有一个盲测比较系统。请阅读 `agents/comparator.md` 和 `agents/analyzer.md` 了解详情。基本思想是：将两个输出提供给一个独立的 agent，但不告诉它哪个是哪个，让它判断质量。然后分析获胜者获胜的原因。

这是可选的，需要 subagents，大多数用户不需要它。人工审查循环通常就足够了。

---

## 描述优化

SKILL.md 前置数据中的 description 字段是决定 Claude 是否调用技能的主要机制。在创建或改进技能后，建议优化描述以提高触发准确性。

### 步骤 1：生成触发评估查询

创建 20 个评估查询 —— 混合应触发和不应触发的查询。保存为 JSON：

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

查询内容必须真实，是 Claude Code 或 Claude.ai 用户实际会输入的内容。不要抽象的请求，而是具体、详细且包含大量细节的请求。例如，文件路径、关于用户工作或情况的个人背景、列名和值、公司名称、URL。少量的背景故事。有些可能是小写的，或者包含缩写、拼写错误或口语化表达。使用不同长度的混合，专注于边缘情况，而不是让它们界限分明（用户将有机会确认它们）。

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

对于 **should-trigger** 查询（8-10条），请考虑覆盖率。你需要同一意图的不同措辞——有些正式，有些随意。包括用户未明确命名 skill 或文件类型但显然需要它的案例。加入一些不常见的用例，以及该 skill 与另一个 skill 竞争但应胜出的情况。

对于 **should-not-trigger** 查询（8-10条），最有价值的是“差一点就命中”的情况——即与 skill 共享关键词或概念但实际上需要不同功能的查询。考虑相邻领域、会导致简单关键词匹配触发但不应该触发的歧义措辞，以及查询涉及 skill 所做之事但在更适合使用其他工具的上下文中的情况。

需要避免的关键点：不要让 should-not-trigger 查询明显不相关。例如，“编写一个斐波那契函数”作为 PDF skill 的负面测试太容易了——它测试不出任何东西。负面案例应该具有真正的迷惑性。

### 步骤 2：与用户一起审查

使用 HTML 模板向用户展示 eval set 以供审查：

1. 从 `assets/eval_review.html` 读取模板
2. 替换占位符：
   - `__EVAL_DATA_PLACEHOLDER__` → eval 项的 JSON 数组（周围没有引号——它是一个 JS 变量赋值）
   - `__SKILL_NAME_PLACEHOLDER__` → skill 的名称
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → skill 的当前描述
3. 写入临时文件（例如 `/tmp/eval_review_<skill-name>.html`）并打开它：`open /tmp/eval_review_<skill-name>.html`
4. 用户可以编辑查询、切换 should-trigger、添加/删除条目，然后点击 "Export Eval Set"
5. 文件下载到 `~/Downloads/eval_set.json` —— 检查 Downloads 文件夹以获取最新版本，以防存在多个文件（例如 `eval_set (1).json`）

这一步很重要——糟糕的 eval 查询会导致糟糕的描述。

### 步骤 3：运行优化循环

告诉用户：“这需要一些时间——我将在后台运行优化循环并定期检查。”

将 eval set 保存到工作区，然后在后台运行：

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

使用系统提示词中的 model ID（即驱动当前会话的那个），以便触发测试与用户的实际体验相匹配。

运行期间，定期查看输出，向用户更新当前迭代次数和分数情况。

这会自动处理完整的优化循环。它将 eval set 按 60% train 和 40% held-out test 的比例划分，评估当前 description（每个 query 运行 3 次以获得可靠的 trigger rate），然后调用 Claude 根据失败情况提出改进建议。它会在 train 和 test 上重新评估每个新的 description，最多迭代 5 次。完成后，它会在浏览器中打开 HTML 报告，显示每次迭代的结果，并返回包含 `best_description` 的 JSON —— 该 description 根据 test score 而非 train score 选择，以避免过拟合。

### Skill 触发机制

理解触发机制有助于设计更好的 eval queries。Skills 会以 name + description 的形式出现在 Claude 的 `available_skills` 列表中，Claude 根据该 description 决定是否 consult 一个 skill。需要知道的重要一点是，Claude 只会为那些它无法轻松独立处理的任务 consult skills —— 像 "read this PDF" 这样简单的单步 query，即使 description 完美匹配，也可能不会触发 skill，因为 Claude 可以使用基本工具直接处理它们。复杂的、多步骤的或专门的 queries 在 description 匹配时会可靠地触发 skills。

这意味着你的 eval queries 应该足够有实质内容，让 Claude 确实能从 consult skill 中受益。像 "read file X" 这样的简单 queries 是糟糕的测试用例 —— 无论 description 质量如何，它们都不会触发 skills。

### 步骤 4：应用结果

从 JSON 输出中获取 `best_description`，更新 skill 的 SKILL.md frontmatter。向用户展示修改前后的对比并报告分数。

---

### 打包与展示（仅当 `present_files` 工具可用时）

检查你是否有权访问 `present_files` 工具。如果没有，跳过此步骤。如果有，打包 skill 并将 .skill 文件展示给用户：

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

打包完成后，指引用户前往生成的 `.skill` 文件路径，以便他们进行安装。

---

## Claude.ai 专用说明

在 Claude.ai 中，核心 workflow 是相同的（draft → test → review → improve → repeat），但由于 Claude.ai 没有 subagents，部分机制有所改变。以下是需要调整的内容：

**运行测试用例**：没有 subagents 意味着无法并行执行。对于每个测试用例，阅读 skill 的 SKILL.md，然后按照其指示自行完成测试 prompt。一次处理一个。这不如独立的 subagents 严谨（因为你编写了 skill 并且也在运行它，所以你拥有完整的上下文），但这是一种有用的健全性检查——而且人工审查步骤可以弥补这一点。跳过 baseline 运行——只需使用 skill 按要求完成任务即可。

**审查结果**：如果你无法打开浏览器（例如，Claude.ai 的 VM 没有显示器，或者你在远程服务器上），请完全跳过浏览器审查步骤。相反，直接在对话中展示结果。对于每个测试用例，显示 prompt 和输出。如果输出是用户需要查看的文件（如 .docx 或 .xlsx），将其保存到文件系统并告知用户位置，以便他们下载和检查。在线征求反馈：“这看起来怎么样？有什么需要修改的吗？”

**Benchmarking**：跳过定量 benchmarking——它依赖于 baseline 比较，没有 subagents 时这没有意义。专注于用户的定性反馈。

**迭代循环**：与之前相同——改进 skill，重新运行测试用例，征求反馈——只是中间没有浏览器审查环节。如果你有文件系统，仍然可以将结果组织到迭代目录中。

**Description 优化**：此部分需要 `claude` CLI 工具（具体为 `claude -p`），该工具仅在 Claude Code 中可用。如果你在 Claude.ai 上，请跳过此步骤。

**盲测比较**：需要 subagents。跳过它。

**打包**：只要有 Python 和文件系统，`package_skill.py` 脚本就可以在任何地方运行。在 Claude.ai 上，你可以运行它，用户可以下载生成的 `.skill` 文件。

**更新现有 skill**：用户可能要求你更新现有的 skill，而不是创建一个新的。在这种情况下：
- **保留原始名称。** 注意 skill 的目录名和 `name` frontmatter 字段——保持它们不变。例如，如果安装的 skill 是 `research-helper`，则输出 `research-helper.skill`（而不是 `research-helper-v2`）。
- **编辑前复制到可写位置。** 安装的 skill 路径可能是只读的。复制到 `/tmp/skill-name/`，在那里编辑，并从副本打包。
- **如果手动打包，先暂存在 `/tmp/`**，然后复制到输出目录——由于权限问题，直接写入可能会失败。

---

## Cowork 专用说明

如果你在 Cowork 中，主要需要了解以下几点：

- 你拥有 subagents，因此主 workflow（并行生成测试用例、运行 baseline、评分等）都能正常工作。（但是，如果你遇到严重的超时问题，可以串行而不是并行运行测试 prompt。）
- 你没有浏览器或显示器，因此在生成 eval viewer 时，请使用 `--static <output_path>` 写入一个独立的 HTML 文件，而不是启动服务器。然后提供一个链接，用户可以点击该链接在浏览器中打开 HTML。
- 无论出于何种原因，Cowork 的设置似乎会导致 Claude 不愿在运行测试后生成 eval viewer，所以再次重申：无论你是在 Cowork 还是 Claude Code 中，运行测试后，你应该始终生成 eval viewer 供人工查看示例，然后再自己修订 skill 并尝试进行更正，使用 `generate_review.py`（而不是编写你自己的 HTML 代码）。提前抱歉，我要用全大写了：在你自己评估输入*之前*生成 EVAL VIEWER。你要尽快让人类看到它们！
- 反馈机制有所不同：由于没有运行服务器，查看器的 "Submit All Reviews" 按钮会将 `feedback.json` 作为文件下载。然后你可以从那里读取它（可能需要先请求访问权限）。
- 打包功能正常——`package_skill.py` 只需要 Python 和文件系统。
- Description 优化（`run_loop.py` / `run_eval.py`）在 Cowork 中应该能正常工作，因为它通过 subprocess 使用 `claude -p`，而不是浏览器，但请务必等到你完全完成 skill 制作且用户认可其状态良好后再进行。
- **更新现有 skill**：用户可能要求你更新现有的 skill，而不是创建一个新的。请遵循上文 claude.ai 部分中的更新指南。

---

## 参考文件

agents/ 目录包含专门 subagents 的说明。当你需要启动相关 subagent 时请阅读它们。

- `agents/grader.md` — 如何针对输出评估断言
- `agents/comparator.md` — 如何在两个输出之间进行盲测 A/B 比较
- `agents/analyzer.md` — 分析为何一个版本胜过另一个版本

references/ 目录包含额外的文档：
- `references/schemas.md` — evals.json、grading.json 等的 JSON 结构

---

为了强调，在此重复一次核心循环：

- 弄清楚 skill 是关于什么的
- 起草或编辑 skill
- 在测试 prompt 上运行能访问该 skill 的 claude
- 与用户一起评估输出：
  - 创建 benchmark.json 并运行 `eval-viewer/generate_review.py` 以帮助用户审查它们
  - 运行定量评估
- 重复直到你和用户满意为止
- 打包最终的 skill 并返回给用户。

如果你有 TodoList，请将这些步骤添加进去，以确保不会忘记。如果你在 Cowork 中，请务必将“创建 evals JSON 并运行 `eval-viewer/generate_review.py` 以便人工审查测试用例”放入你的 TodoList，以确保执行该操作。

祝好运！