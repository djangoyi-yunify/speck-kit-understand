---
name: skill-creator
description: 创建新 skills，修改和改进现有 skills，并衡量 skill 性能。当用户希望从头创建 skill，编辑或优化现有 skill，运行 evals 测试 skill，通过方差分析对 skill 性能进行基准测试，或优化 skill 的描述以提高触发准确性时使用。
---

# Skill Creator

一个用于创建新 skills 并对其进行迭代改进的 skill。

总体而言，创建 skill 的过程如下：

- 确定 skill 的功能以及大致的实现方式
- 编写 skill 草稿
- 创建一些测试 prompts，并对它们运行 claude-with-access-to-the-skill
- 帮助用户对结果进行定性和定量评估
  - 在后台运行的同时，如果没有定量的 evals，请草拟一些（如果已经存在，你可以按原样使用，或者如果你觉得需要修改，也可以进行调整）。然后向用户解释这些 evals（或者如果它们已经存在，解释现有的那些）
  - 使用 `eval-viewer/generate_review.py` 脚本向用户展示结果供其查看，并让他们查看定量指标
- 根据用户对结果的评估反馈重写 skill（如果定量 benchmarks 中显示出明显的缺陷，也要进行修改）
- 重复此过程直到满意为止
- 扩大测试集，并在更大规模上再次尝试

使用此 skill 时，你的任务是确定用户处于流程的哪个阶段，然后介入并帮助他们推进这些阶段。例如，他们可能会说“我想为 X 制作一个 skill”。你可以帮助缩小他们的意图范围，编写草稿，编写测试用例，确定他们想要如何评估，运行所有 prompts，并重复此过程。

另一方面，也许他们已经有了 skill 的草稿。在这种情况下，你可以直接进入循环的评估/迭代部分。

当然，你应该始终保持灵活，如果用户说“我不需要运行一堆评估，只要跟着感觉走”，你也可以照做。

然后，在 skill 完成后（但这同样顺序灵活），你还可以运行 skill 描述改进器，我们有专门的脚本来优化 skill 的触发。

明白了吗？很好。

## 与用户沟通

Skill creator 可能会被对代码术语熟悉程度各异的人群使用。如果你还没听说过（这也不怪你，毕竟这只是最近才开始的趋势），现在的趋势是 Claude 的能力正在激励水管工打开他们的终端，父母和祖父母去谷歌搜索“如何安装 npm”。另一方面，大多数用户可能具备相当的计算机素养。

因此，请注意上下文线索，以了解如何组织你的沟通措辞！在默认情况下，为了给你一些概念：

- “evaluation”和“benchmark”处于临界状态，但可以使用
- 对于“JSON”和“assertion”，你需要在用户表现出他们知道这些是什么的明确线索后，才能不加解释地使用它们

如果你不确定，可以简要解释术语，如果你不确定用户是否能理解，可以随时用简短的定义来澄清术语。

---

## 创建 skill

### 捕捉意图

首先理解用户的意图。当前的对话可能已经包含了用户想要捕捉的工作流（例如，他们说“把这个变成一个 skill”）。如果是这样，首先从对话历史中提取答案——使用的工具、步骤顺序、用户所做的更正、观察到的输入/输出格式。用户可能需要填补空白，并应在进入下一步之前进行确认。

1. 这个 skill 应该让 Claude 能够做什么？
2. 这个 skill 应该何时触发？（什么用户短语/上下文）
3. 预期的输出格式是什么？
4. 我们是否应该设置测试用例来验证 skill 是否有效？具有客观可验证输出的 skill（文件转换、数据提取、代码生成、固定工作流步骤）受益于测试用例。具有主观输出的 skill（写作风格、艺术）通常不需要。根据 skill 类型建议适当的默认设置，但让用户决定。

### 访谈与研究

主动询问关于边缘情况、输入/输出格式、示例文件、成功标准和依赖关系的问题。在解决这部分问题之前，暂缓编写测试 prompts。

检查可用的 MCPs —— 如果对研究有用（搜索文档、查找类似的 skills、查阅最佳实践），如果可用，通过 subagents 并行研究，否则在线研究。准备好上下文以减少用户的负担。

### 编写 SKILL.md

根据用户访谈，填写以下组件：

- **name**：Skill 标识符
- **description**：何时触发，做什么。这是主要的触发机制——包括 skill 的功能以及何时使用的具体上下文。所有“何时使用”的信息都在这里，而不是在正文中。注意：目前 Claude 倾向于“欠触发” skills——即在它们有用时不使用它们。为了解决这个问题，请让 skill 描述稍微“强硬”一点。例如，与其写“如何构建一个简单的快速仪表板来显示内部 Anthropic 数据”，不如写“如何构建一个简单的快速仪表板来显示内部 Anthropic 数据。每当用户提到仪表板、数据可视化、内部指标或想要显示任何类型的公司数据时，即使他们没有明确要求‘仪表板’，也要务必使用此 skill。”
- **compatibility**：所需工具、依赖项（可选，很少需要）
- **skill 的其余部分 :)**

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
1. **Metadata** (name + description) - 始终位于上下文中（约 100 词）
2. **SKILL.md body** - 当 skill 触发时位于上下文中（理想情况 <500 行）
3. **Bundled resources** - 按需加载（无限制，scripts 可在未加载的情况下执行）

这些字数统计为近似值，如有必要可适当放宽。

**关键模式：**
- 将 SKILL.md 保持在 500 行以内；若接近此限制，请增加层级并提供明确指引，告知使用该 skill 的模型下一步该去哪里继续跟进。
- 在 SKILL.md 中清晰引用文件，并指导何时读取
- 对于大型参考文件（>300 行），应包含目录

**领域组织**：当 skill 支持多个 domains/frameworks 时，按变体进行组织：

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

这是不言而喻的，但 skills 绝不能包含恶意软件、漏洞利用代码或任何可能破坏系统安全的内容。如果对 skill 的内容进行描述，其意图不应让用户感到意外。不要配合创建具有误导性的 skills 或旨在协助未授权访问、数据渗出或其他恶意活动的 skills 的请求。不过，像“扮演某某”之类的情况是可以接受的。

#### 写作模式

在指令中优先使用祈使句。

**定义输出格式** - 你可以这样操作：

```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**示例模式** - 包含示例很有用。你可以像这样格式化（但如果示例中包含 "Input" 和 "Output"，你可能需要稍作调整）：

```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### 写作风格

尝试向模型解释事情为何重要，以代替生硬陈旧的 MUST 要求。运用心智理论，尽量使技能具有通用性，而非仅仅局限于特定示例。首先撰写草稿，然后以全新的视角审视并进行改进。

### 测试用例

完成技能草稿编写后，设计 2-3 个切合实际的测试提示词——即真实用户真正会提出的问题。与用户分享这些提示词：[无需严格使用此措辞] “这里有几个我想尝试的测试用例。这些看起来合适吗？您想添加更多吗？” 然后运行它们。

将测试用例保存到 `evals/evals.json`。暂不要编写断言——仅保留提示词。您将在下一步运行期间编写断言。

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

完整的 schema 请参阅 `references/schemas.md`（包括稍后要添加的 `assertions` 字段）。

## 运行和评估测试用例

本节是一个连续的过程——不要中途停止。请勿使用 `/skill-test` 或任何其他测试技能。

将结果放入与技能目录同级的 `<skill-name>-workspace/` 中。在工作区内，按迭代（`iteration-1/`、`iteration-2/` 等）组织结果，在迭代目录内，每个测试用例对应一个目录（`eval-0/`、`eval-1/` 等）。不要预先创建所有这些目录——只需在过程中按需创建。

### 步骤 1：在同一轮次中生成所有运行（with-skill 和 baseline）

对于每个测试用例，在同一轮次中生成两个 subagent——一个使用技能，一个不使用。这一点很重要：不要先生成 with-skill 运行，然后再回来处理 baseline。一次性启动所有任务，以便它们能在大致相同的时间完成。

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
- **创建新 skill**：完全没有 skill。相同的 prompt，无 skill path，保存到 `without_skill/outputs/`。
- **改进现有 skill**：旧版本。编辑前，对 skill 进行快照（`cp -r <skill-path> <workspace>/skill-snapshot/`），然后将 baseline subagent 指向该快照。保存到 `old_skill/outputs/`。

为每个测试用例编写一个 `eval_metadata.json`（assertions 目前可以为空）。根据测试内容为每个 eval 赋予一个描述性名称——不要只是 "eval-0"。目录也使用此名称。如果本次迭代使用新的或修改过的 eval prompts，请为每个新的 eval 目录创建这些文件——不要假设它们会从之前的迭代中沿用。

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### 步骤 2：在 runs 进行期间，起草断言

不要干等 runs 结束 —— 你可以高效利用这段时间。为每个测试用例起草定量断言，并向用户解释。如果 `evals/evals.json` 中已存在断言，请审查它们并解释其检查内容。

良好的断言是客观可验证的，且具有描述性名称 —— 它们应在 benchmark viewer 中清晰可读，以便浏览结果的人能立即理解每项检查的内容。主观技能（写作风格、设计质量）更适合进行定性评估 —— 不要强行对需要人工判断的内容设置断言。

断言起草完成后，更新 `eval_metadata.json` 文件和 `evals/evals.json`。同时向用户解释他们将在 viewer 中看到的内容 —— 包括定性输出和定量 benchmark。

### 步骤 3：随着 runs 完成，捕获计时数据

当每个 subagent 任务完成时，你会收到一条包含 `total_tokens` 和 `duration_ms` 的通知。请立即将此数据保存到运行目录下的 `timing.json` 中：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

这是捕获此数据的唯一机会——它通过任务通知传递，且未在其他地方持久化。请在通知到达时即时处理，而不是尝试批量处理。

### 步骤 4：评分、聚合并启动查看器

一旦所有运行完成：

1. **对每次运行进行评分** —— 生成一个 grader subagent（或进行内联评分），读取 `agents/grader.md` 并根据输出评估每个断言。将结果保存到每个运行目录下的 `grading.json` 中。`grading.json` 的 expectations 数组必须使用 `text`、`passed` 和 `evidence` 字段（而不是 `name`/`met`/`details` 或其他变体）—— 查看器依赖于这些确切的字段名称。对于可以通过编程方式检查的断言，编写并运行脚本而不是通过目测检查 —— 脚本更快、更可靠，并且可以在迭代中复用。

2. **聚合到 benchmark** —— 从 skill-creator 目录运行聚合脚本：

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

此操作会生成 `benchmark.json` 和 `benchmark.md`，其中包含每种配置的 pass_rate、time 和 tokens，以及 mean ± stddev 和 delta。如果手动生成 benchmark.json，请参阅 `references/schemas.md` 以了解 viewer 所需的确切 schema。
请将每个 with_skill 版本排在其 baseline 对应版本之前。

3. **执行一轮 analyst pass** —— 阅读 benchmark 数据，找出 aggregate stats 可能掩盖的模式。关于具体的观察重点，请参阅 `agents/analyzer.md`（其中的 "Analyzing Benchmark Results" 章节），例如无论 skill 如何总是通过的 assertions（non-discriminating）、高方差的 evals（可能属于 flaky），以及 time/token tradeoffs。

4. **启动 viewer**，同时加载定性输出和定量数据：

```bash
nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
```

对于第 2 次及后续 iteration，还需传入 `--previous-workspace <workspace>/iteration-<N-1>`。

**Cowork / headless 环境：** 如果 `webbrowser.open()` 不可用或环境无显示界面，请使用 `--static <output_path>` 写入独立的 HTML 文件，而非启动服务器。当用户点击 "Submit All Reviews" 时，Feedback 将作为 `feedback.json` 文件下载。下载后，将 `feedback.json` 复制到 workspace 目录中，供下一次 iteration 读取。

注意：请使用 generate_review.py 创建 viewer；无需编写自定义 HTML。

5. **告知用户** 类似如下内容：“我已在浏览器中打开结果。有两个标签页 — 'Outputs' 允许您点击查看每个 test case 并留下反馈，'Benchmark' 显示定量比较。完成后，请回到这里通知我。”

### 用户在 viewer 中看到的内容

"Outputs" 标签页一次显示一个 test case：
- **Prompt**：给定的任务
- **Output**：skill 生成的文件，尽可能在页面内渲染
- **Previous Output** (iteration 2+)：折叠部分，显示上一次 iteration 的输出
- **Formal Grades**（如运行了 grading）：折叠部分，显示断言通过/失败情况
- **Feedback**：一个随输入自动保存的文本框
- **Previous Feedback** (iteration 2+)：上次的评论，显示在文本框下方

"Benchmark" 标签页显示统计摘要：每个 configuration 的通过率、耗时和 token 使用情况，以及每次评估的细分数据和分析师观察。

通过 prev/next 按钮或方向键进行导航。完成后，他们点击 "Submit All Reviews"，这将把所有反馈保存到 `feedback.json`。

### 步骤 5：读取反馈

当用户告诉你他们完成时，读取 `feedback.json`：

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

空反馈意味着用户认为没问题。将改进重点放在用户提出具体不满的测试用例上。

使用完毕后终止 viewer server：

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## 改进 Skill

这是循环的核心。你已经运行了测试用例，用户已审查结果，现在你需要根据他们的反馈改进 skill。

### 如何思考改进

1. **从反馈中进行归纳。** 这里的宏观目标是，我们正试图创建可以在数百万个不同的 prompt 中使用数百万次（可能字面意义上的，甚至更多，谁知道呢）的 skill。在这里，你和用户只在几个示例上反复迭代，因为这有助于加快进度。用户对这些示例了如指掌，评估新输出对他们来说很快。但是，如果你和用户共同开发的 skill 仅适用于这些示例，那它就是无用的。如果遇到顽固的问题，不要进行繁琐的过拟合修改，或者添加压迫性的强制性约束（MUST），你可以尝试拓展思路，使用不同的隐喻，或推荐不同的工作模式。尝试的成本相对较低，也许你会发现很棒的东西。

2. **保持 prompt 简练。** 移除那些没有发挥作用的内容。务必阅读记录，而不仅仅是最终输出——如果 skill 似乎让模型浪费大量时间做无效工作，你可以尝试删除导致这种情况的 skill 部分，看看会发生什么。

3. **解释原因。** 尽力解释你要求模型做每件事背后的**原因**。如今的 LLM *非常聪明*。它们拥有良好的心智理论，当被赋予良好的引导时，它们可以超越死板的指令，真正把事情做成。即使来自用户的反馈简短或充满挫败感，也要尝试真正理解任务，理解用户为什么这样写以及他们实际写了什么，然后将这种理解传达至指令中。如果你发现自己用全大写书写 ALWAYS 或 NEVER，或使用超级僵硬的结构，那是一个警示信号——如果可能，请重构并解释推理过程，以便模型理解你要求事项的重要性。这是一种更人性化、强大且有效的方法。

4. **寻找跨测试用例的重复工作。** 阅读测试运行的记录，注意 subagent 是否都独立编写了类似的 helper scripts 或对某事采取了相同的多步骤方法。如果所有 3 个测试用例都导致 subagent 编写了 `create_docx.py` 或 `build_chart.py`，这是一个强烈的信号，表明 skill 应该打包该脚本。编写一次，将其放入 `scripts/`，并告诉 skill 使用它。这能节省未来每一次调用的重复造轮子成本。

这项任务相当重要（我们要在这里创造每年数十亿美元的经济价值！），你的思考时间不是瓶颈；慢慢来，仔细斟酌。我建议先写一份修订草案，然后重新审视并加以改进。真正尽力深入用户的头脑，理解他们的需求。

### 迭代循环

改进 skill 后：

1. 将你的改进应用到 skill 中
2. 将所有测试用例重新运行到一个新的 `iteration-<N+1>/` 目录中，包括 baseline 运行。如果你正在创建一个新的 skill，baseline 始终是 `without_skill`（无 skill）——这在迭代过程中保持不变。如果你正在改进现有的 skill，请自行判断什么作为 baseline 更有意义：用户带来的原始版本，还是上一次迭代。
3. 启动 reviewer，用 `--previous-workspace` 指向上一次迭代
4. 等待用户审查并告诉你他们已完成
5. 阅读新的反馈，再次改进，重复此过程

继续直到：
- 用户表示满意
- 反馈全为空（一切看起来都很好）
- 你没有取得实质性进展

---

## 高级：盲测比较

在需要对 skill 的两个版本进行更严格比较的情况下（例如，用户问“新版本真的更好吗？”），可以使用盲测比较系统。阅读 `agents/comparator.md` 和 `agents/analyzer.md` 了解详情。基本思想是：将两个输出提供给一个独立的 agent，但不告诉它哪个是哪个，让它判断质量。然后分析获胜者为何获胜。

这是可选的，需要 subagent，大多数用户不需要它。人工审查循环通常就足够了。

---

## Description 优化

SKILL.md frontmatter 中的 description 字段是决定 Claude 是否调用 skill 的主要机制。创建或改进 skill 后，提议优化 description 以提高触发准确性。

### 步骤 1：生成触发评估查询

创建 20 个评估查询——混合应触发和不应触发的查询。保存为 JSON：

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

查询必须真实，并且是 Claude Code 或 Claude.ai 用户实际会输入的内容。不要抽象的请求，而是具体、明确且包含丰富细节的请求。例如：文件路径、关于用户工作或处境的个人背景信息、列名和值、公司名称、URL。还需要一点背景故事。有些可能是小写的，或者包含缩写、拼写错误或口语化表达。请混合使用不同的长度，并侧重于边缘情况，而不是让它们过于简单直白（用户会有机会确认这些内容）。

差：`"Format this data"`，`"Extract text from PDF"`，`"Create a chart"`

好：`"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

对于 **should-trigger** 查询（8-10条），请考虑覆盖率。你需要针对同一意图的不同措辞——有些正式，有些随意。包括用户未明确指出技能或文件类型但显然需要它的情况。加入一些不常见的用例，以及该技能与其他技能存在竞争但应胜出的情况。

对于 **should-not-trigger** 查询（8-10条），最有价值的是那些“似是而非”的情况——即与技能共享关键词或概念，但实际上需要不同操作的查询。思考相邻领域、简单的关键词匹配会触发但不应触发的模糊措辞，以及查询涉及该技能的功能但上下文更适合使用其他工具的情况。

需要避免的关键点：不要让 should-not-trigger 查询显得明显无关。"Write a fibonacci function" 作为 PDF 技能的反向测试太容易了——这测不出任何东西。负面案例应该具有真正的迷惑性。

### Step 2: 与用户一起审查

使用 HTML 模板向用户展示评估集（eval set）以供审查：

1. 从 `assets/eval_review.html` 读取模板
2. 替换占位符：
   - `__EVAL_DATA_PLACEHOLDER__` → eval 项的 JSON 数组（周围不加引号——这是一个 JS 变量赋值）
   - `__SKILL_NAME_PLACEHOLDER__` → 技能名称
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → 技能的当前描述
3. 写入临时文件（例如 `/tmp/eval_review_<skill-name>.html`）并打开它：`open /tmp/eval_review_<skill-name>.html`
4. 用户可以编辑查询、切换 should-trigger 状态、添加/删除条目，然后点击 "Export Eval Set"
5. 文件将下载到 `~/Downloads/eval_set.json` —— 请检查 Downloads 文件夹以获取最新版本，以防存在多个文件（例如 `eval_set (1).json`）

这一步至关重要 —— 糟糕的 eval 查询会导致糟糕的描述。

### Step 3: 运行优化循环

告诉用户：“这需要一些时间 —— 我会在后台运行优化循环并定期检查进度。”

将 eval 集保存到工作区，然后在后台运行：

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

使用系统提示词中的 model ID（驱动当前会话的那个），以便触发测试与用户的实际体验相匹配。

在运行期间，定期查看输出尾部，向用户更新当前的迭代次数和得分情况。

这会自动处理完整的优化循环。它将评估集划分为 60% 的训练集和 40% 的保留测试集，评估当前描述（每个查询运行 3 次以获得可靠的触发率），然后根据失败的情况调用 Claude 提出改进建议。它会在训练集和测试集上重新评估每个新描述，最多迭代 5 次。完成后，它会在浏览器中打开一个 HTML 报告，显示每次迭代的结果，并返回包含 `best_description` 的 JSON —— 该描述是根据测试得分而非训练得分选出的，以避免过拟合。

### Skill 触发机制的工作原理

了解触发机制有助于设计更好的评估查询。Skills 会以其名称 + 描述的形式出现在 Claude 的 `available_skills` 列表中，Claude 根据该描述决定是否咨询 skill。重要的是要知道，Claude 仅针对其无法独自轻松处理的任务咨询 skills —— 诸如“阅读此 PDF”之类的简单单步查询可能不会触发 skill，即使描述完美匹配，因为 Claude 可以使用基本工具直接处理它们。当描述匹配时，复杂、多步骤或专业的查询会可靠地触发 skills。

这意味着你的评估查询应该足够充实，让 Claude 确实能从咨询 skill 中受益。像“读取文件 X”这样的简单查询是糟糕的测试用例 —— 无论描述质量如何，它们都不会触发 skills。

### 步骤 4：应用结果

从 JSON 输出中获取 `best_description` 并更新 skill 的 SKILL.md frontmatter。向用户展示修改前后的对比并报告得分。

---

### 打包并展示（仅在 `present_files` 工具可用时）

检查你是否有权访问 `present_files` 工具。如果没有，跳过此步骤。如果有，打包 skill 并向用户展示 .skill 文件：

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

打包完成后，请指引用户前往生成的 `.skill` 文件路径，以便其进行安装。

---

## Claude.ai 特定说明

在 Claude.ai 中，核心 workflow 相同（草稿 → 测试 → 审查 → 改进 → 重复），但由于 Claude.ai 没有 subagents，部分机制有所变化。需要调整的内容如下：

**运行测试用例**：没有 subagents 意味着无法并行执行。对于每个 test case，请阅读 skill 的 SKILL.md，然后遵循其指令自行完成 test prompt。请逐个执行。这不如独立的 subagents 严谨（因为 skill 是你编写的，也是你运行的，所以你拥有完整的上下文），但这作为一种健全性检查仍然有用——而且人工审查步骤可以弥补这一不足。跳过 baseline runs——只需使用 skill 按要求完成任务即可。

**审查结果**：如果你无法打开浏览器（例如 Claude.ai 的 VM 没有显示器，或者你处于远程服务器上），请完全跳过浏览器审查步骤。相反，直接在对话中展示结果。对于每个 test case，展示 prompt 和输出。如果输出是用户需要查看的文件（如 .docx 或 .xlsx），请将其保存到文件系统并告知用户位置，以便其下载和检查。请在对话中直接询问反馈：“这个看起来怎么样？有什么需要修改的地方吗？”

**基准测试**：跳过定量 benchmarking——它依赖于基线对比，在没有 subagents 的情况下没有意义。重点关注用户的定性反馈。

**迭代循环**：与之前相同——改进 skill，重新运行 test cases，征求反馈——只是中间没有浏览器审查步骤。如果你有文件系统，仍然可以将结果组织到迭代目录中。

**描述优化**：此部分需要 `claude` CLI 工具（具体为 `claude -p`），该工具仅在 Claude Code 中可用。如果你在 Claude.ai 上，请跳过此步骤。

**盲比较**：需要 subagents。跳过此步骤。

**打包**：`package_skill.py` 脚本可在任何具备 Python 和文件系统的环境中运行。在 Claude.ai 上，你可以运行该脚本，用户可以下载生成的 `.skill` 文件。

**更新现有 skill**：用户可能要求你更新现有的 skill，而非创建新的。在这种情况下：
- **保留原始名称。** 记下 skill 的目录名和 `name` frontmatter 字段——保持不变。例如，如果安装的 skill 是 `research-helper`，则输出 `research-helper.skill`（而非 `research-helper-v2`）。
- **编辑前复制到可写位置。** 安装的 skill 路径可能是只读的。请将其复制到 `/tmp/skill-name/`，在此处进行编辑，并从副本进行打包。
- **如果手动打包，请先在 `/tmp/` 中暂存**，然后复制到输出目录——直接写入可能因权限问题而失败。

---

## Cowork 特定说明

如果你处于 Cowork 环境中，主要需了解以下几点：

- 你拥有 subagents，因此主 workflow（并行生成 test cases、运行 baseline、评分等）均可正常运行。（但是，如果遇到严重的超时问题，可以串行而非并行运行 test prompts。）
- 你没有浏览器或显示器，因此在生成 eval viewer 时，请使用 `--static <output_path>` 写入一个独立的 HTML 文件，而非启动服务器。然后提供一个链接，供用户点击在其浏览器中打开该 HTML 文件。
- 无论出于何种原因，Cowork 的设置似乎会导致 Claude 在运行测试后不愿意生成 eval viewer，因此再次重申：无论你是在 Cowork 还是 Claude Code 中，运行测试后，都应始终使用 `generate_review.py` 生成 eval viewer 供人工查看示例，然后再自行修改 skill 并尝试纠正（不要编写你自己特制的 html 代码）。提前抱歉，但我这里要用全大写了：在你自己评估输入之前，**先生成 EVAL VIEWER**。你要让用户尽快看到它们！
- 反馈机制有所不同：由于没有运行中的服务器，查看器的“Submit All Reviews”按钮会将 `feedback.json` 作为文件下载。随后你可以读取该文件（可能需要先请求访问权限）。
- 打包功能正常——`package_skill.py` 只需要 Python 和文件系统即可运行。
- 描述优化（`run_loop.py` / `run_eval.py`）在 Cowork 中应该能正常工作，因为它通过 subprocess 使用 `claude -p`，而非浏览器，但请等到你完全完成 skill 制作且用户认可其状态良好后再进行此步骤。
- **更新现有 skill**：用户可能要求你更新现有的 skill，而非创建新的。请遵循上文 claude.ai 部分中的更新指南。

---

## 参考文件

`agents/` 目录包含专门 subagents 的指令。当需要生成相关 subagent 时，请阅读这些文件。

- `agents/grader.md` — 如何根据输出评估断言
- `agents/comparator.md` — 如何在两个输出之间进行盲 A/B 比较
- `agents/analyzer.md` — 如何分析一个版本为何优于另一个版本

`references/` 目录包含额外文档：
- `references/schemas.md` — evals.json、grading.json 等文件的 JSON 结构。

---

再次重复核心循环以作强调：

- 明确 skill 的主旨
- 起草或编辑 skill
- 在 test prompts 上运行 claude-with-access-to-the-skill
- 与用户一起评估输出：
  - 创建 benchmark.json 并运行 `eval-viewer/generate_review.py` 以帮助用户审查
  - 运行定量评估
- 重复此过程直到你和用户都满意为止
- 打包最终的 skill 并将其返还给用户。

如果你有 TodoList，请将上述步骤添加进去，以免遗忘。如果你在 Cowork 中，请务必将“在自己评估输入之前生成 eval viewer”这一项添加到 TodoList 中，以确保其被执行。

祝好运！