---
name: skill-creator
description: 创建新 Skill，修改和改进现有 Skill，并衡量 Skill 性能。当用户希望从头创建 Skill、编辑或优化现有 Skill、运行 evals 以测试 Skill、通过方差分析对 Skill 性能进行基准测试，或优化 Skill 的描述以提高触发准确性时使用。
---

# Skill Creator

一个用于创建新 Skill 并对其进行迭代改进的 Skill。

从宏观层面来看，创建 Skill 的过程如下：

- 确定你希望 Skill 做什么，以及大致的实现方式
- 编写 Skill 草稿
- 创建一些测试 Prompt，并在其上运行 claude-with-access-to-the-skill
- 帮助用户定性和定量地评估结果
  - 当运行在后台进行时，如果没有现成的定量 evals，则起草一些（如果有，可以按原样使用，或者如果你觉得需要改变，也可以修改）。然后向用户解释它们（或者如果它们已经存在，解释那些已经存在的）
  - 使用 `eval-viewer/generate_review.py` 脚本向用户展示结果供其查看，并允许他们查看定量指标
- 根据用户对结果的评估反馈重写 Skill（如果定量基准测试中发现了明显的缺陷，也要重写）
- 重复直到满意为止
- 扩大测试集并在更大范围内再次尝试

使用此 Skill 时，你的任务是判断用户处于此过程的哪个阶段，然后介入并帮助他们推进这些阶段。例如，他们可能会说“我想为 X 制作一个 Skill”。你可以帮助缩小范围、编写草稿、编写测试用例、确定他们想要如何评估、运行所有 Prompt 并重复此过程。

另一方面，也许他们已经有了 Skill 的草稿。在这种情况下，你可以直接进入循环中的 eval/iterate（评估/迭代）部分。

当然，你应该始终保持灵活，如果用户说“我不需要运行一堆评估，跟我随便聊聊就行”，你可以照做。

然后，在 Skill 完成后（同样，顺序是灵活的），你还可以运行 skill description improver（Skill 描述改进器），我们有一个单独的脚本用于优化 Skill 的触发。

明白了吗？很好。

## 与用户沟通

Skill Creator 的用户群体可能涵盖对编程术语熟悉程度各异的人群。如果你还没听说过（你怎么可能听说过，这也就是最近才开始的事），现在有一种趋势，Claude 的强大能力正在激励水管工打开终端，父母和祖父母去谷歌搜索“how to install npm”。另一方面，大多数用户可能都具备相当的计算机素养。

因此，请注意上下文线索，以了解如何措辞！在默认情况下，给你一点参考：

- “evaluation”和“benchmark”处于临界状态，但可以使用
- 对于“JSON”和“assertion”，你需要在没有解释的情况下使用它们之前，看到用户确实了解这些内容的明确线索

如果你不确定，简要解释术语是可以的；如果你不确定用户是否能理解，请随时用简短的定义澄清术语。

---

## 创建 Skill

### 捕捉意图

从理解用户的意图开始。当前的对话可能已经包含了用户想要捕捉的 Workflow（例如，他们说“把它变成一个 Skill”）。如果是这样，首先从对话历史中提取答案 —— 使用的工具、步骤顺序、用户所做的更正、观察到的输入/输出格式。用户可能需要填补空白，并应在进入下一步之前进行确认。

1. 这个 Skill 应该让 Claude 能够做什么？
2. 这个 Skill 何时应该触发？（什么用户短语/上下文）
3. 预期的输出格式是什么？
4. 我们是否应该设置测试用例来验证 Skill 是否有效？具有客观可验证输出（文件转换、数据提取、代码生成、固定 Workflow 步骤）的 Skill 受益于测试用例。具有主观输出（写作风格、艺术）的 Skill 通常不需要。根据 Skill 类型建议适当的默认值，但让用户决定。

### 访谈与研究

主动询问关于边缘情况、输入/输出格式、示例文件、成功标准和依赖项的问题。在解决这部分问题之前，请暂缓编写测试 Prompt。

检查可用的 MCP —— 如果有助于研究（搜索文档、查找类似 Skill、查阅最佳实践），如果可用，通过 subagents 并行研究，否则在内联中进行。提前准备好上下文，以减轻用户的负担。

### 编写 SKILL.md

根据用户访谈，填写以下组件：

- **name**：Skill 标识符
- **description**：何时触发，做什么。这是主要的触发机制 —— 包括 Skill 的功能以及何时使用的具体上下文。所有“何时使用”的信息都在这里，而不是正文中。注意：目前 Claude 倾向于“触发不足（undertrigger）”Skill —— 即在它们有用的时候不使用它们。为了解决这个问题，请让 Skill 描述稍微“强势（pushy）”一点。例如，与其写“如何构建一个简单快速的 Dashboard 来显示 Anthropic 内部数据”，不如写“如何构建一个简单快速的 Dashboard 来显示 Anthropic 内部数据。每当用户提到 Dashboard、数据可视化、内部指标或想要显示任何类型的公司数据时，即使他们没有明确要求‘Dashboard’，也要确保使用此 Skill。”
- **compatibility**：所需工具、依赖项（可选，很少需要）
- **Skill 的其余部分 :)**

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

Skills 采用三级加载系统：
1. **Metadata**（名称 + 描述）- 始终位于上下文中（约 100 词）
2. **SKILL.md body** - 当 skill 触发时位于上下文中（理想情况下少于 500 行）
3. **Bundled resources** - 按需加载（无限制，脚本可在不加载的情况下执行）

这些字数仅为近似值，如有必要可适当增加。

**关键模式：**
- 将 SKILL.md 保持在 500 行以内；如果接近此限制，请增加一个额外的层级结构，并提供清晰的指引，说明使用该 skill 的模型下一步应转向何处进行后续操作。
- 在 SKILL.md 中清晰地引用文件，并说明何时读取它们。
- 对于大型参考文件（>300 行），包含目录。

**Domain organization**：当一个 skill 支持多个 domain/framework 时，按变体进行组织：

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Claude 仅读取相关的参考文件。

#### 无惊吓原则

虽然这显而易见，但 Skills 绝不能包含恶意软件、漏洞利用代码或任何可能危及系统安全的内容。Skills 的内容若被描述，其意图不应让用户感到意外。不要配合创建误导性 Skills 或旨在协助未授权访问、数据窃取或其他恶意活动的 Skills 的请求。不过，像“角色扮演 XYZ”之类的内容是可以接受的。

#### 写作模式

指令中请优先使用祈使句。

**定义输出格式** - 您可以这样做：

```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**示例模式** - 包含示例很有帮助。您可以像这样格式化（但如果示例中包含 "Input" 和 "Output"，您可能需要稍作调整）：

```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### 写作风格

尝试向模型解释事情为何重要，以此代替生硬陈旧的“必须（MUST）”。运用心智理论（theory of mind），尝试让 skill 具有通用性，而非局限于特定示例。先写一份草稿，然后用全新的眼光审视并加以改进。

### 测试用例

编写完 skill 草稿后，设计 2-3 个真实的测试 prompts —— 即真实用户实际上会提出的内容。与用户分享这些内容：[不必完全使用这种措辞] “这里有几个我想尝试的测试用例。这些看起来是否合适，或者你想添加更多？” 然后运行它们。

将测试用例保存到 `evals/evals.json`。暂时不要编写断言 —— 只写 prompts。你将在下一步运行过程中起草断言。

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

## 运行并评估测试用例

本节是一个连续的过程 —— 请勿中途停止。切勿使用 `/skill-test` 或任何其他测试 skill。

将结果放入 `<skill-name>-workspace/` 中，使其与 skill 目录同级。在 workspace 内，按迭代（`iteration-1/`、`iteration-2/` 等）组织结果，且在该迭代目录下，每个测试用例对应一个目录（`eval-0/`、`eval-1/` 等）。不要预先创建所有这些目录 —— 只需在过程中按需创建。

### 步骤 1：在同一轮次中启动所有运行（with-skill 和 baseline）

对于每个测试用例，在同一轮次中启动两个 subagent —— 一个使用 skill，一个不使用。这一点很重要：切勿先启动 with-skill 运行，然后再回头处理 baseline。请一次性启动所有任务，以便它们能大致同时完成。

**With-skill 运行：**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline run**（相同的 prompt，但 baseline 取决于上下文）：
- **Creating a new skill**：完全没有 skill。相同的 prompt，没有 skill path，保存到 `without_skill/outputs/`。
- **Improving an existing skill**：旧版本。编辑前，先对 skill 进行快照（`cp -r <skill-path> <workspace>/skill-snapshot/`），然后将 baseline subagent 指向该快照。保存到 `old_skill/outputs/`。

为每个测试用例编写一个 `eval_metadata.json`（assertions 目前可以为空）。根据测试内容为每个 eval 起一个描述性名称 —— 不要只叫 "eval-0"。目录名也使用此名称。如果本次迭代使用新的或修改过的 eval prompts，请为每个新的 eval 目录创建这些文件 —— 不要假设它们会从之前的迭代中继承。

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### 步骤 2：运行进行期间，起草断言

不要只是等待运行结束 —— 您可以高效利用这段时间。为每个测试用例起草定量断言，并向用户解释。如果 `evals/evals.json` 中已存在断言，请审查并解释它们检查的内容。

优秀的断言是客观可验证的，且具有描述性名称 —— 它们在基准测试查看器中应清晰易读，以便浏览结果的人能立即理解每个断言的检查内容。主观技能（写作风格、设计质量）更适合定性评估 —— 不要强行对需要人工判断的内容使用断言。

断言起草完毕后，更新 `eval_metadata.json` 文件和 `evals/evals.json`。同时向用户解释他们将在查看器中看到的内容 —— 包括定性输出和定量基准测试。

### 步骤 3：运行完成后，捕获计时数据

当每个 subagent 任务完成时，您会收到包含 `total_tokens` 和 `duration_ms` 的通知。请立即将此数据保存到运行目录中的 `timing.json` 文件：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

这是捕获此数据的唯一机会——它通过任务通知传来，且未在其他地方持久化保存。应在每个通知到达时立即处理，而不是尝试批量处理。

### 步骤 4：评分、聚合并启动查看器

一旦所有运行完成：

1. **对每次运行进行评分** —— 生成一个 grader subagent（或进行内联评分），读取 `agents/grader.md` 并根据输出评估每个 assertion。将结果保存到每个运行目录下的 `grading.json` 中。`grading.json` 的 expectations 数组必须使用字段 `text`、`passed` 和 `evidence`（而不是 `name`/`met`/`details` 或其他变体）—— 查看器依赖于这些确切的字段名称。对于可以通过编程方式检查的 assertion，编写并运行脚本而非肉眼检查 —— 脚本更快、更可靠，且可跨迭代重用。

2. **聚合到 benchmark** —— 从 skill-creator 目录运行聚合脚本：

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

这会生成 `benchmark.json` 和 `benchmark.md`，其中包含每个配置的 pass_rate、time 和 tokens，以及 mean ± stddev 和 delta。如果手动生成 benchmark.json，请参阅 `references/schemas.md` 了解查看器所需的确切 schema。
将每个 with_skill 版本放在其对应的 baseline 版本之前。

3. **进行分析师审查** — 阅读基准测试数据，揭示聚合统计数据可能隐藏的模式。请参阅 `agents/analyzer.md`（“Analyzing Benchmark Results”章节）了解需要注意的内容——例如无论 skill 如何都始终通过的断言、高方差 evals（可能 flaky）以及 time/token 权衡。

4. **启动查看器**，同时包含定性输出和定量数据：

```bash
nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
```

对于 iteration 2+，还需传递 `--previous-workspace <workspace>/iteration-<N-1>`。

**Cowork / headless 环境：**如果 `webbrowser.open()` 不可用或环境没有显示器，请使用 `--static <output_path>` 写入一个独立的 HTML 文件，而不是启动服务器。当用户点击 "Submit All Reviews" 时，Feedback 将下载为 `feedback.json` 文件。下载后，将 `feedback.json` 复制到 workspace 目录中，以便下一次 iteration 获取。

注意：请使用 generate_review.py 创建 viewer；无需编写自定义 HTML。

5. **告诉用户**类似这样的话：“我已经在浏览器中打开了结果。有两个标签页 — 'Outputs' 允许你点击查看每个 test case 并留下 feedback，'Benchmark' 显示定量对比。完成后，回到这里告诉我。”

### 用户在 viewer 中看到的内容

"Outputs" 标签页一次显示一个 test case：
- **Prompt**：给出的任务
- **Output**：skill 生成的文件，尽可能在页面内渲染
- **Previous Output** (iteration 2+)：折叠区域，显示上一次 iteration 的输出
- **Formal Grades**（如果运行了 grading）：折叠区域，显示 assertion 通过/失败
- **Feedback**：一个文本框，输入时自动保存
- **Previous Feedback** (iteration 2+)：上次的评论，显示在文本框下方

"Benchmark" 标签页显示统计摘要：每个 configuration 的通过率、耗时和 token 使用量，以及按评估细分的 breakdown 和 analyst observations。

通过 prev/next 按钮或方向键进行导航。完成后，他们点击 "Submit All Reviews"，将所有 feedback 保存到 `feedback.json`。

### Step 5：读取 feedback

当用户告诉你他们完成了，读取 `feedback.json`：

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

反馈为空意味着用户认为没问题。请将改进重点放在用户有具体不满的测试用例上。

使用完毕后请终止 viewer server：

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## 改进技能

这是循环的核心环节。你已经运行了测试用例，用户也审查了结果，现在你需要根据他们的反馈来改进技能。

### 如何思考改进

1. **从反馈中归纳。** 这里的宏观大局是，我们正试图创建可以在数百万次（也许是字面意义上的，甚至更多，谁知道呢）不同的 prompt 中使用的技能。在这里，你和用户只针对少数示例反复迭代，因为这有助于加快进度。用户对这些示例了如指掌，因此评估新输出非常快。但是，如果你和用户共同开发的技能仅适用于这些示例，那它就毫无用处。如果遇到顽固问题，与其进行繁琐的过拟合修改，或者添加压迫性的强制性 MUST，不如尝试拓宽思路，使用不同的隐喻，或推荐不同的工作模式。尝试的成本相对较低，也许你会发现很棒的东西。

2. **保持 prompt 精简。** 移除那些没有发挥作用的内容。务必阅读记录，而不仅仅是最终输出 —— 如果看起来技能正在让模型浪费大量时间做无益的事情，你可以尝试删除技能中导致这种情况的部分，看看会发生什么。

3. **解释原因。** 尽力解释你要求模型做每件事背后的**原因**。如今的 LLM *非常聪明*。它们拥有良好的心智理论，当被赋予良好的框架时，它们能超越死记硬背的指令，真正把事情做成。即使来自用户的反馈简短或充满挫败感，也要尝试真正理解任务，以及用户为什么要写这些内容、他们实际写了什么，然后将这种理解传达进指令中。如果你发现自己用全大写写“ALWAYS”或“NEVER”，或者使用超级僵化的结构，那就是一个警示信号 —— 如果可能的话，重新构建并解释推理过程，让模型理解你要求的事情为何重要。这是一种更人性化、强大且有效的方法。

4. **寻找跨测试用例的重复工作。** 阅读测试运行的记录，注意 subagent 是否都独立编写了类似的辅助脚本，或者对某事采取了相同的多步骤方法。如果所有 3 个测试用例都导致 subagent 编写了 `create_docx.py` 或 `build_chart.py`，这是一个强烈的信号，表明技能应该打包该脚本。编写一次，将其放入 `scripts/`，并告诉技能使用它。这能让未来的每次调用免于重复造轮子。

这项任务相当重要（我们正试图每年创造数十亿美元的经济价值！），你的思考时间不是瓶颈；花点时间，真正仔细琢磨一下。我建议先写一份修改草案，然后重新审视并进行改进。尽全力进入用户的头脑，理解他们想要和需要什么。

### 迭代循环

改进技能后：

1. 将你的改进应用到技能中
2. 将所有测试用例重新运行到一个新的 `iteration-<N+1>/` 目录中，包括基线运行。如果你正在创建新技能，基线始终是 `without_skill`（无技能）—— 这在迭代过程中保持不变。如果你正在改进现有技能，请根据判断选择合理的基线：用户最初带来的版本，或者上一次迭代。
3. 启动 reviewer，使用 `--previous-workspace` 指向上一次迭代
4. 等待用户审查并告诉你他们完成了
5. 阅读新反馈，再次改进，重复此过程

继续进行，直到：
- 用户表示满意
- 反馈全部为空（一切看起来都很好）
- 你没有取得实质性的进展

---

## 进阶：盲测对比

如果你需要在技能的两个版本之间进行更严格的比较（例如，用户问“新版本真的更好吗？”），可以使用盲测对比系统。阅读 `agents/comparator.md` 和 `agents/analyzer.md` 了解详情。基本思路是：将两个输出提供给一个独立的 agent，但不告诉它哪个是哪个，让其判断质量。然后分析获胜者为何获胜。

这是可选的，需要 subagent，大多数用户不需要它。人工审查循环通常就足够了。

---

## 描述优化

`SKILL.md` frontmatter 中的 description 字段是决定 Claude 是否调用技能的主要机制。在创建或改进技能后，提议优化描述以提高触发准确性。

### 步骤 1：生成触发评估查询

创建 20 个 eval queries —— 混合 should-trigger（应触发）和 should-not-trigger（不应触发）。保存为 JSON：

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

查询内容必须真实可信，符合 Claude Code 或 Claude.ai 用户实际会输入的样子。不要抽象的请求，而要是具体、明确且包含丰富细节的请求。例如，文件路径、关于用户工作或情况的个人背景、列名和值、公司名称、URL。一些背景故事。有些可能是小写的，或者包含缩写、拼写错误或口语化表达。使用不同长度的混合，重点关注边缘情况，而不是让它们过于清晰明确（用户会有机会确认它们）。

反面示例：`"Format this data"`、`"Extract text from PDF"`、`"Create a chart"`

正面示例：`"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

对于 **should-trigger** 查询（8-10条），要考虑覆盖范围。你需要同一意图的不同表达方式——有些正式，有些随意。包括用户没有明确说出技能名称或文件类型但明显需要它的情况。加入一些不常见的用例，以及该技能与另一技能竞争但应该胜出的情况。

对于 **should-not-trigger** 查询（8-10条），最有价值的是那些近似匹配——与技能共享关键词或概念但实际上需要其他功能的查询。考虑相邻领域、模糊表达（简单的关键词匹配会触发但不应该触发的情况），以及查询涉及技能功能但另一个工具更合适的场景。

关键要避免的是：不要让 should-not-trigger 查询明显不相关。把 "Write a fibonacci function" 作为 PDF 技能的负面测试太简单了——它测试不了任何东西。负面案例应该真正具有迷惑性。

### Step 2: 与用户一起审查

使用 HTML 模板向用户展示评估集以供审查：

1. 从 `assets/eval_review.html` 读取模板
2. 替换占位符：
   - `__EVAL_DATA_PLACEHOLDER__` → eval 项目的 JSON 数组（不要加引号——这是 JS 变量赋值）
   - `__SKILL_NAME_PLACEHOLDER__` → 技能名称
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → 技能的当前描述
3. 写入临时文件（如 `/tmp/eval_review_<skill-name>.html`）并打开：`open /tmp/eval_review_<skill-name>.html`
4. 用户可以编辑查询、切换 should-trigger、添加/删除条目，然后点击 "Export Eval Set"
5. 文件会下载到 `~/Downloads/eval_set.json` —— 检查 Downloads 文件夹获取最新版本，以防存在多个文件（如 `eval_set (1).json`）

这一步很重要——糟糕的评估查询会导致糟糕的描述。

### Step 3: 运行优化循环

告诉用户："This will take some time — I'll run the optimization loop in the background and check on it periodically."

将评估集保存到工作区，然后在后台运行：

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

使用系统提示（system prompt）中的 model ID（即驱动当前会话的那个），以便触发测试与用户的实际体验相符。

在运行期间，定期 tail 输出以向用户更新当前的迭代次数和分数情况。

这会自动处理完整的优化循环。它将 eval set 拆分为 60% 的 train（训练）集和 40% 的 held-out test（保留测试）集，评估当前的 description（将每个 query 运行 3 次以获得可靠的 trigger rate），然后根据失败的情况调用 Claude 提出改进建议。它会在 train 和 test 集上重新评估每个新的 description，最多迭代 5 次。完成后，它会在浏览器中打开一个 HTML 报告，显示每次迭代的结果，并返回包含 `best_description` 的 JSON —— 该 description 是根据 test score 而非 train score 选出的，以避免 overfitting（过拟合）。

### Skill 触发机制的工作原理

理解触发机制有助于设计更好的 eval queries。Skills 出现在 Claude 的 `available_skills` 列表中，包含其 name + description，Claude 根据该 description 决定是否调用 skill。需要了解的重要一点是，Claude 只会针对其无法轻易独立处理的任务调用 skills —— 像 "read this PDF" 这样简单的单步 queries 可能不会触发 skill，即使 description 完全匹配，因为 Claude 可以使用基本工具直接处理它们。当 description 匹配时，复杂的、多步骤的或专门的 queries 能够可靠地触发 skills。

这意味着你的 eval queries 应该足够充实，让 Claude 确实能从调用 skill 中受益。像 "read file X" 这样的简单 queries 是糟糕的测试用例 —— 无论 description 质量如何，它们都不会触发 skills。

### Step 4：应用结果

从 JSON 输出中获取 `best_description` 并更新 skill 的 SKILL.md frontmatter。向用户展示修改前后的对比并报告分数。

---

### Package and Present（仅当 `present_files` tool 可用时）

检查你是否拥有 `present_files` tool 的访问权限。如果没有，请跳过此步骤。如果有，请打包 skill 并向用户展示 .skill 文件：

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

打包完成后，告知用户生成的 `.skill` 文件路径，以便他们安装。

---

## Claude.ai 特定说明

在 Claude.ai 中，核心 workflow 是相同的（draft → test → review → improve → repeat），但由于 Claude.ai 没有 subagents，一些机制会有所变化。以下是需要调整的内容：

**运行测试用例**：没有 subagents 意味着无法并行执行。对于每个测试用例，阅读 skill 的 SKILL.md，然后按照其指示自行完成测试 prompt。逐个执行。这不如独立的 subagents 严谨（你编写了 skill，同时也在运行它，因此你拥有完整的上下文），但这是一种有用的健全性检查——人工审核步骤可以弥补这一点。跳过 baseline 运行——只需使用 skill 按要求完成任务即可。

**审查结果**：如果无法打开浏览器（例如 Claude.ai 的 VM 没有显示器，或者你在远程服务器上），则完全跳过浏览器审查。改为直接在对话中展示结果。对于每个测试用例，显示 prompt 和输出。如果输出是用户需要查看的文件（如 .docx 或 .xlsx），将其保存到文件系统并告知用户位置，以便他们下载和检查。在线询问反馈："这看起来怎么样？有什么需要修改的吗？"

**基准测试**：跳过定量基准测试——它依赖于 baseline 比较，没有 subagents 时没有意义。专注于用户的定性反馈。

**迭代循环**：与之前相同——改进 skill、重新运行测试用例、征求反馈——只是中间没有浏览器审查。如果你有文件系统，仍然可以将结果组织到迭代目录中。

**描述优化**：此部分需要 `claude` CLI 工具（具体是 `claude -p`），该工具仅在 Claude Code 中可用。如果在 Claude.ai 上，请跳过。

**盲测比较**：需要 subagents。跳过。

**打包**：`package_skill.py` 脚本可在任何有 Python 和文件系统的地方运行。在 Claude.ai 上，你可以运行它，用户可以下载生成的 `.skill` 文件。

**更新现有 skill**：用户可能要求你更新现有的 skill，而不是创建新的。在这种情况下：
- **保留原始名称。** 注意 skill 的目录名和 `name` frontmatter 字段——保持不变。例如，如果安装的 skill 是 `research-helper`，则输出 `research-helper.skill`（而不是 `research-helper-v2`）。
- **编辑前复制到可写位置。** 安装的 skill 路径可能是只读的。复制到 `/tmp/skill-name/`，在那里编辑，并从副本打包。
- **如果手动打包，先暂存在 `/tmp/`**，然后复制到输出目录——直接写入可能因权限问题而失败。

---

## Cowork 特定说明

如果你在 Cowork 中，主要需要注意以下几点：

- 你有 subagents，所以主 workflow（并行生成测试用例、运行 baseline、评分等）都可以正常工作。（但是，如果遇到严重的超时问题，可以串行而非并行运行测试 prompt。）
- 你没有浏览器或显示器，因此在生成 eval viewer 时，使用 `--static <output_path>` 写入独立的 HTML 文件，而不是启动服务器。然后提供一个链接，用户可以点击在浏览器中打开 HTML。
- 无论出于什么原因，Cowork 环境似乎会让 Claude 在运行测试后不愿意生成 eval viewer，所以再次强调：无论你在 Cowork 还是 Claude Code，运行测试后，你应该始终生成 eval viewer 让人类在你自己修订 skill 和尝试修正之前查看示例，使用 `generate_review.py`（而不是自己编写定制的 html 代码）。提前抱歉，但我要用全大写了：在你自己评估输入*之前*生成 EVAL VIEWER。你想尽快把它们展示给人类！
- 反馈机制不同：由于没有运行的服务器，查看器的 "Submit All Reviews" 按钮会将 `feedback.json` 作为文件下载。然后你可以从中读取（可能需要先请求访问权限）。
- 打包功能正常——`package_skill.py` 只需要 Python 和文件系统。
- 描述优化（`run_loop.py` / `run_eval.py`）在 Cowork 中应该可以正常工作，因为它通过 subprocess 使用 `claude -p`，而不是浏览器，但请在你完全完成 skill 制作且用户同意其状态良好之后再进行。
- **更新现有 skill**：用户可能要求你更新现有的 skill，而不是创建新的。请遵循上面 claude.ai 部分中的更新指导。

---

## 参考文件

agents/ 目录包含专门 subagents 的说明。当你需要生成相关 subagent 时阅读它们。

- `agents/grader.md` — 如何对输出进行断言评估
- `agents/comparator.md` — 如何在两个输出之间进行盲测 A/B 比较
- `agents/analyzer.md` — 如何分析一个版本为何胜过另一个

references/ 目录有额外的文档：
- `references/schemas.md` — evals.json、grading.json 等的 JSON 结构

---

再次重复核心循环以示强调：

- 弄清楚 skill 是关于什么的
- 起草或编辑 skill
- 在测试 prompt 上运行 claude-with-access-to-the-skill
- 与用户一起评估输出：
  - 创建 benchmark.json 并运行 `eval-viewer/generate_review.py` 帮助用户审查
  - 运行定量评估
- 重复直到你和用户都满意
- 打包最终的 skill 并返回给用户。

如果你有 TodoList 之类的东西，请把这些步骤添加进去，确保不会忘记。如果在 Cowork 中，请特别将 "Create evals JSON and run `eval-viewer/generate_review.py` so human can review test cases" 放入你的 TodoList，确保它被执行。

祝好运！