---
name: skill-creator
description: 创建新 skills，修改和改进现有 skills，并衡量 skill 性能。当用户想要从头创建 skill、编辑或优化现有 skill、运行 evals 测试 skill、通过方差分析对 skill 性能进行基准测试，或优化 skill 描述以提高触发准确性时使用。
---

# Skill Creator

一个用于创建新 skills 并对其进行迭代改进的 skill。

从宏观层面来看，创建 skill 的过程如下：

- 确定 skill 的功能及其大致实现方式
- 编写 skill 草稿
- 创建一些测试 prompts，并在其上运行 claude-with-access-to-the-skill
- 帮助用户定性和定量地评估结果
  - 当运行在后台进行时，如果没有定量 evals，请起草一些（如果已有，可以按原样使用，或者如果你觉得需要改变，也可以修改）。然后向用户解释它们（或者如果它们已经存在，解释那些已经存在的）
  - 使用 `eval-viewer/generate_review.py` 脚本向用户展示结果供其查看，并让他们查看定量指标
- 根据用户对结果的评估反馈重写 skill（如果从定量基准测试中发现了明显的缺陷，也要重写）
- 重复此过程直到满意
- 扩展测试集并尝试更大规模的测试

使用此 skill 时，你的任务是弄清楚用户处于流程的哪个阶段，然后切入并帮助他们推进这些阶段。例如，他们可能会说“我想为 X 制作一个 skill”。你可以帮助明确他们的意图，编写草稿，编写测试用例，确定他们想要如何评估，运行所有 prompts，并重复该过程。

另一方面，也许他们已经有了 skill 的草稿。在这种情况下，你可以直接进入循环的评估/迭代部分。

当然，你应该始终保持灵活，如果用户说“我不需要运行一堆评估，随意发挥就行”，你也可以照做。

然后，在 skill 完成后（再次强调，顺序是灵活的），你也可以运行 skill 描述改进器，我们有一个单独的脚本来优化 skill 的触发。

明白了吗？很好。

## 与用户沟通

Skill creator 可能会被对代码术语熟悉程度各异的人使用。如果你还没听说过（你怎么可能听说过，这也是最近才开始的事），现在的趋势是，Claude 的强大能力正在激发水管工打开终端，父母和祖父母去谷歌搜索“how to install npm”。另一方面，大多数用户可能具备相当的计算机素养。

因此，请注意语境线索，以了解如何措辞你的沟通！在默认情况下，为了给你一些概念：

- “evaluation”和“benchmark”处于临界状态，但可以使用
- 对于“JSON”和“assertion”，在没有解释的情况下使用它们之前，你需要看到用户确实了解这些是什么的明确线索

如果你不确定，可以简要解释术语，如果你不确定用户是否理解，可以自由地用简短的定义澄清术语。

---

## 创建 skill

### 捕捉意图

首先了解用户的意图。当前的对话可能已经包含用户想要捕获的 workflow（例如，他们说“将其变成一个 skill”）。如果是这样，首先从对话历史中提取答案——使用的工具、步骤顺序、用户所做的修正、观察到的输入/输出格式。用户可能需要填补空白，并应在进入下一步之前进行确认。

1. 这个 skill 应该让 Claude 能够做什么？
2. 这个 skill 什么时候应该触发？（什么用户短语/语境）
3. 预期的输出格式是什么？
4. 我们是否应该设置测试用例来验证 skill 是否有效？具有客观可验证输出的 skills（文件转换、数据提取、代码生成、固定 workflow 步骤）受益于测试用例。具有主观输出的 skills（写作风格、艺术）通常不需要。根据 skill 类型建议适当的默认设置，但让用户决定。

### 访谈与研究

主动询问关于边缘情况、输入/输出格式、示例文件、成功标准和依赖关系的问题。在解决这部分问题之前，请等待编写测试 prompts。

检查可用的 MCPs——如果对研究有用（搜索文档、查找类似 skills、查阅最佳实践），如果可用，通过 subagents 并行研究，否则在行内进行。准备好上下文以减轻用户的负担。

### 编写 SKILL.md

根据用户访谈，填写以下组件：

- **name**: Skill 标识符
- **description**: 何时触发，做什么。这是主要的触发机制——包括 skill 的功能以及何时使用的具体语境。所有“何时使用”的信息都放在这里，而不是正文中。注意：目前 Claude 有一种“触发不足”的倾向——即在有用的时候不使用它们。为了解决这个问题，请让 skill 描述稍微“主动”一点。例如，与其写“如何构建一个简单的快速仪表板来显示 Anthropic 内部数据。”，不如写“如何构建一个简单的快速仪表板来显示 Anthropic 内部数据。只要用户提到仪表板、数据可视化、内部指标或想要显示任何类型的公司数据，即使他们没有明确要求‘仪表板’，也要确保使用此 skill。”
- **compatibility**: 必需的工具、依赖项（可选，很少需要）
- **skill 的其余部分 :)**

### Skill 编写指南

#### Skill 剖析

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
1. **元数据** (名称 + 描述) - 始终位于上下文中 (~100 词)
2. **SKILL.md 正文** - skill 触发时位于上下文中 (< 500 行为佳)
3. **配套资源** - 按需使用 (无限制，脚本可直接执行无需加载)

这些字数仅为近似值，如有需要可适当超出。

**关键模式：**
- 将 SKILL.md 保持在 500 行以内；如果接近此限制，请增加一个层级，并提供清晰的指引，说明使用该 skill 的模型下一步应前往何处进行跟进。
- 在 SKILL.md 中清晰引用文件，并说明何时读取它们
- 对于大型参考文件 (>300 行)，请包含目录

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

#### 无惊吓原则

这一点不言而喻，但 skills 绝不能包含恶意软件、漏洞利用代码或任何可能危及系统安全的内容。如果对 Skill 的内容进行描述，其意图不应让用户感到意外。不要答应创建误导性 skills 或旨在协助未授权访问、数据窃取或其他恶意活动的 skills 的请求。不过，诸如“角色扮演为 XYZ”之类的情况是可以的。

#### 写作模式

在指令中优先使用祈使句形式。

**定义输出格式** - 您可以这样做：

```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**示例模式** - 包含示例很有用。你可以按如下方式格式化（但如果示例中包含 "Input" 和 "Output"，你可能需要稍作调整）：

```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### 写作风格

尝试向模型解释事情为何重要，以此代替强硬且陈旧的“必须（MUST）”式指令。运用心理理论，尝试让 skill 具备通用性，而非局限于特定的具体示例。先写一份草稿，然后以全新的视角审视并加以改进。

### 测试用例

编写完 skill 草稿后，设计 2-3 个逼真的测试提示词——即真实用户实际上会提问的内容。与用户分享这些测试用例：[你不必完全照搬这段话] “我想尝试这几个测试用例。这些看起来合适吗，还是你想增加更多？”然后运行它们。

将测试用例保存到 `evals/evals.json`。暂不要编写断言——只写提示词。你将在下一步运行过程中起草断言。

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

完整 schema 请见 `references/schemas.md`（包括您稍后将添加的 `assertions` 字段）。

## 运行和评估测试用例

本节内容是一个连续的序列 —— 请勿中途停止。请勿使用 `/skill-test` 或任何其他测试 skill。

将结果放入与 skill 目录同级的 `<skill-name>-workspace/` 中。在 workspace 内，按 iteration 组织结果（`iteration-1/`、`iteration-2/` 等），在该目录下，每个测试用例对应一个目录（`eval-0/`、`eval-1/` 等）。不要预先创建所有这些 —— 只需随着步骤进行创建目录。

### 步骤 1：在同一轮次中生成所有运行（with-skill 和 baseline）

对于每个测试用例，在同一轮次中生成两个 subagent —— 一个使用 skill，一个不使用。这一点很重要：不要先生成 with-skill 运行，然后再回来处理 baseline。同时启动所有任务，以便它们大致在同一时间完成。

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
- **Improving an existing skill**：旧版本。编辑前，为 skill 创建快照（`cp -r <skill-path> <workspace>/skill-snapshot/`），然后将 baseline subagent 指向该快照。保存到 `old_skill/outputs/`。

为每个测试用例编写一个 `eval_metadata.json`（assertions 暂时可以为空）。根据测试内容给每个 eval 起一个描述性名称 —— 不要只叫 "eval-0"。目录名称也使用此名称。如果本次迭代使用了新的或修改过的 eval prompts，请为每个新的 eval 目录创建这些文件 —— 不要假设它们会从之前的迭代中沿用。

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### 步骤 2：当 runs 正在进行时，起草 assertions

不要只是等待 runs 完成——你可以高效地利用这段时间。为每个 test case 起草定量的 assertions，并向用户进行解释。如果 `evals/evals.json` 中已存在 assertions，请对其进行审查并解释其检查内容。

好的 assertions 应具备客观可验证性且拥有描述性名称——它们应在 benchmark viewer 中清晰易读，以便浏览结果的人能立即理解每一项检查的内容。主观技能（如写作风格、设计质量）更适合通过定性方式进行评估——不要强行对需要人工判断的内容使用 assertions。

assertions 起草完成后，请更新 `eval_metadata.json` 文件和 `evals/evals.json`。同时向用户解释他们将在 viewer 中看到的内容——包括定性输出和定量 benchmark。

### 步骤 3：随着 runs 完成，捕获 timing data

当每个 subagent task 完成时，你会收到一个包含 `total_tokens` 和 `duration_ms` 的通知。请立即将此数据保存到 run 目录下的 `timing.json` 中：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

这是捕获此数据的唯一机会——数据通过任务通知传递，并未在其他地方持久化。请在通知到达时逐一处理，而不要尝试批量处理。

### 步骤 4：评分、聚合并启动查看器

待所有运行完成后：

1. **对每次运行进行评分** — 生成一个评分 subagent（或进行内联评分），读取 `agents/grader.md` 并根据输出评估每个断言。将结果保存到每个运行目录下的 `grading.json` 文件中。`grading.json` 的 expectations 数组必须使用 `text`、`passed` 和 `evidence` 字段（而非 `name`/`met`/`details` 或其他变体）—— 查看器依赖于这些确切的字段名称。对于可以通过编程方式检查的断言，请编写并运行脚本，而非进行目测 —— 脚本速度更快、更可靠，并且可以在多次迭代中重用。

2. **聚合为 benchmark** — 在 skill-creator 目录下运行聚合脚本：

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

这会生成 `benchmark.json` 和 `benchmark.md`，其中包含每种配置的 pass_rate、time 和 tokens，以及 mean ± stddev 和 delta。如果手动生成 benchmark.json，请参阅 `references/schemas.md` 以了解查看器所需的确切 schema。
将每个 with_skill 版本置于其对应的 baseline 版本之前。

3. **进行一轮分析师审查** —— 阅读 benchmark 数据，揭示聚合统计数据可能掩盖的模式。请参阅 `agents/analyzer.md`（“Analyzing Benchmark Results”部分）了解需要关注的内容——例如无论 skill 如何总是通过的断言、高方差评估以及 time/token 权衡。

4. **启动 viewer**，同时包含定性输出和定量数据：

```bash
nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
```

对于第 2+ 次迭代，还需传递 `--previous-workspace <workspace>/iteration-<N-1>`。

   **协作 / 无头环境：** 如果 `webbrowser.open()` 不可用或环境没有显示器，请使用 `--static <output_path>` 生成一个独立的 HTML 文件，而不是启动服务器。当用户点击 "Submit All Reviews" 时，反馈将作为 `feedback.json` 文件下载。下载后，将 `feedback.json` 复制到工作空间目录，以便下一次迭代读取。

注意：请使用 generate_review.py 创建查看器；无需编写自定义 HTML。

5. **告知用户**如下内容：“我已在浏览器中打开结果。有两个标签页 —— ‘Outputs’ 可让你点击查看每个测试用例并留下反馈，‘Benchmark’ 显示量化比较结果。完成后，请回到这里告诉我。”

### 用户在查看器中看到的内容

“Outputs” 标签页一次显示一个测试用例：
- **Prompt**：给出的任务
- **Output**：skill 生成的文件，尽可能内联渲染
- **Previous Output**（第 2+ 次迭代）：折叠部分，显示上一次迭代的输出
- **Formal Grades**（如果运行了评分）：折叠部分，显示断言通过/失败情况
- **Feedback**：文本框，输入时自动保存
- **Previous Feedback**（第 2+ 次迭代）：上次的评论，显示在文本框下方

“Benchmark” 标签页显示统计摘要：每个配置的通过率、耗时和 token 用量，以及每次评估的细分数据和分析师观察结果。

通过上一个/下一个按钮或方向键进行导航。完成后，点击 "Submit All Reviews"，将所有反馈保存到 `feedback.json`。

### 第 5 步：读取反馈

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

空反馈意味着用户认为结果没问题。重点改进用户有具体不满的测试用例。

使用完毕后终止 viewer server：

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## 改进 Skill

这是循环的核心。你已经运行了测试用例，用户也审查了结果，现在你需要根据他们的反馈改进 skill。

### 如何思考改进

1. **从反馈中归纳。** 这里的宏观目标是我们试图创建可以在数百万次（也许是字面意义上的，甚至更多）使用中跨越许多不同 prompts 的 skills。在这里，你和用户仅针对少量示例反复迭代，因为这有助于加快进度。用户对这些示例了如指掌，评估新输出对他们来说很快。但是，如果你和用户共同开发的 skill 仅适用于这些示例，那它就毫无用处。如果遇到棘手问题，与其进行繁琐的过拟合修改，或添加压抑且具有限制性的“MUST”（必须），不如尝试另辟蹊径，使用不同的隐喻，或推荐不同的工作模式。这种尝试成本相对较低，也许你会找到很棒的方案。

2. **保持 Prompt 精简。** 移除那些没有发挥作用的内容。务必阅读记录，而不仅仅是最终输出——如果看起来 skill 让模型浪费大量时间做无用功，你可以尝试删除 skill 中导致这种情况的部分，看看会发生什么。

3. **解释原因。** 尽力解释你要求模型做每件事背后的**原因**。如今的 LLM *非常聪明*。它们拥有良好的心智理论，当给予良好的引导时，它们能超越死板的指令并真正把事情做成。即使用户的反馈简短或带有挫败感，也要尝试真正理解任务，理解用户为什么这样写以及他们实际上写了什么，然后将这种理解传达至指令中。如果你发现自己用全大写字母书写 ALWAYS 或 NEVER，或使用超僵化的结构，那就是一个警示信号——如果可能，重构并解释推理过程，以便模型理解你要求的事项为何重要。这是一种更人性化、强大且有效的方法。

4. **寻找跨测试用例的重复工作。** 阅读测试运行的记录，注意 subagents 是否都独立编写了类似的 helper scripts 或对某事采取了相同的多步骤方法。如果所有 3 个测试用例都导致 subagent 编写了 `create_docx.py` 或 `build_chart.py`，这是一个强烈的信号，表明 skill 应该打包该脚本。编写一次，将其放入 `scripts/`，并告诉 skill 使用它。这能节省未来的每次调用，避免重复造轮子。

这项任务相当重要（我们要在这里创造每年数十亿美元的经济价值！），你的思考时间不是瓶颈；花点时间认真琢磨一下。我建议写一份修订草案，然后重新审视并进行改进。竭尽全力进入用户的脑海，理解他们想要和需要什么。

### 迭代循环

改进 skill 之后：

1. 将你的改进应用到 skill 中
2. 将所有测试用例重新运行到一个新的 `iteration-<N+1>/` 目录中，包括基线运行。如果你正在创建一个新的 skill，基线始终是 `without_skill`（无 skill）——这在迭代中保持不变。如果你正在改进现有的 skill，请根据判断选择合理的基线：用户最初提供的版本，还是上一次迭代。
3. 启动 reviewer，并使用 `--previous-workspace` 指向上一次迭代
4. 等待用户审查并告诉你他们已完成
5. 阅读新反馈，再次改进，重复此过程

继续进行直到：
- 用户表示满意
- 反馈全部为空（一切看起来都不错）
- 你没有取得实质性进展

---

## 高级：盲测对比

对于需要更严格地对比 skill 两个版本的情况（例如，用户问“新版本真的更好吗？”），有一个盲测对比系统。阅读 `agents/comparator.md` 和 `agents/analyzer.md` 了解详情。基本思路是：将两个输出提供给一个独立的 agent，不告诉它哪个是哪个，让其判断质量。然后分析获胜者获胜的原因。

这是可选的，需要 subagents，大多数用户不需要它。人工审查循环通常就足够了。

---

## 描述优化

SKILL.md frontmatter 中的 description 字段是决定 Claude 是否调用 skill 的主要机制。在创建或改进 skill 后，提议优化描述以提高触发准确性。

### 步骤 1：生成触发评估查询

创建 20 个 eval queries——混合应触发和不应触发的查询。保存为 JSON：

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

查询必须真实，是 Claude Code 或 Claude.ai 用户实际会输入的内容。不是抽象的请求，而是具体、详细且有相当细节的请求。例如，文件路径、关于用户工作或情况的个人背景、列名和值、公司名称、URL。一些背景故事。有些可能是小写的，或者包含缩写、拼写错误或口语化表达。使用不同长度的混合，专注于边缘情况而不是让它们过于明确（用户将有机会对它们进行确认）。

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

对于 **should-trigger** 查询（8-10条），考虑覆盖面。你需要同一意图的不同表述——有些正式，有些随意。包括用户没有明确说出技能或文件类型但显然需要它的情况。加入一些不常见的用例，以及该技能与另一个技能竞争但应该胜出的情况。

对于 **should-not-trigger** 查询（8-10条），最有价值的是那些近似命中——与技能共享关键词或概念但实际上需要不同东西的查询。考虑相邻领域、简单关键词匹配会触发但不应该触发的模糊表述，以及查询涉及技能所做的事情但在另一种工具更合适的上下文中的情况。

要避免的关键点：不要让 should-not-trigger 查询明显无关。"Write a fibonacci function" 作为 PDF 技能的负面测试太简单了——它没有测试任何东西。负面情况应该真正具有迷惑性。

### Step 2: 与用户一起审核

使用 HTML 模板向用户展示 eval set 以供审核：

1. 从 `assets/eval_review.html` 读取模板
2. 替换占位符：
   - `__EVAL_DATA_PLACEHOLDER__` → eval 项的 JSON 数组（不要加引号——这是一个 JS 变量赋值）
   - `__SKILL_NAME_PLACEHOLDER__` → 技能名称
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → 技能的当前描述
3. 写入临时文件（例如 `/tmp/eval_review_<skill-name>.html`）并打开：`open /tmp/eval_review_<skill-name>.html`
4. 用户可以编辑查询、切换 should-trigger、添加/删除条目，然后点击 "Export Eval Set"
5. 文件下载到 `~/Downloads/eval_set.json`——检查 Downloads 文件夹中的最新版本，以防有多个文件（例如 `eval_set (1).json`）

这一步很重要——糟糕的 eval 查询会导致糟糕的描述。

### Step 3: 运行优化循环

告诉用户："这需要一些时间——我会在后台运行优化循环并定期检查。"

将 eval set 保存到工作区，然后在后台运行：

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

使用系统提示词（system prompt）中的 model ID（即驱动当前会话的 ID），以便触发测试与用户的实际体验相匹配。

在运行期间，定期跟踪输出，向用户更新当前的迭代次数和分数情况。

此过程自动处理完整的优化循环。它将评估集（eval set）拆分为 60% 的训练集（train）和 40% 的留出测试集（held-out test），评估当前的描述（将每个查询运行 3 次以获得可靠的触发率），然后调用 Claude 根据失败情况提出改进建议。它会在训练集和测试集上重新评估每个新描述，最多迭代 5 次。完成后，它会在浏览器中打开一份 HTML 报告，显示每次迭代的结果，并返回包含 `best_description` 的 JSON —— 该描述是根据测试分数而非训练分数选出的，以避免过拟合（overfitting）。

### Skill 触发机制的工作原理

理解触发机制有助于设计更好的评估查询（eval queries）。Skills 会以“名称 + 描述”的形式出现在 Claude 的 `available_skills` 列表中，Claude 根据该描述决定是否使用 skill。需要了解的重要一点是，Claude 只会在遇到其自身难以独立处理的任务时才会使用 skills —— 像“读取此 PDF”这样简单的一步查询，即使描述完美匹配，也可能不会触发 skill，因为 Claude 可以使用基本工具直接处理。而当描述匹配时，复杂、多步骤或专门的查询会可靠地触发 skills。

这意味着你的评估查询应具备足够的实质性内容，让 Claude 确实能从使用 skill 中受益。像“读取文件 X”这样的简单查询属于糟糕的测试用例 —— 无论描述质量如何，它们都不会触发 skills。

### 步骤 4：应用结果

从 JSON 输出中提取 `best_description` 并更新 skill 的 SKILL.md frontmatter。向用户展示修改前后的对比并报告分数。

---

### 打包与展示（仅在 `present_files` 工具可用时）

检查你是否可以使用 `present_files` 工具。如果不能，请跳过此步骤。如果可以，请打包 skill 并向用户展示 .skill 文件：

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

打包完成后，将生成的 `.skill` 文件路径告知用户，以便他们进行安装。

---

## Claude.ai 特定说明

在 Claude.ai 中，核心 workflow 相同（草稿 → 测试 → 审查 → 改进 → 循环），但由于 Claude.ai 没有 subagents，某些机制有所变化。以下是需要调整的内容：

**运行测试用例**：没有 subagents 意味着无法并行执行。对于每个测试用例，阅读 skill 的 SKILL.md，然后按照其说明自行完成测试 prompt。逐个执行。这比独立的 subagents 不够严谨（你编写了 skill 同时也在运行它，因此你有完整的上下文），但这是一个有用的完整性检查——人工审查步骤可以弥补这一点。跳过 baseline 运行——直接使用 skill 按要求完成任务。

**审查结果**：如果无法打开 browser（例如 Claude.ai 的 VM 没有显示器，或者你在远程服务器上），完全跳过 browser 审查。改为直接在对话中展示结果。对于每个测试用例，展示 prompt 和输出。如果输出是用户需要查看的文件（如 .docx 或 .xlsx），将其保存到 filesystem 并告知用户位置，以便他们下载和检查。在线询问反馈："看起来怎么样？有什么需要修改的吗？"

**Benchmarking**：跳过定量 benchmark——它依赖于 baseline 比较，没有 subagents 时没有意义。专注于用户的定性反馈。

**迭代循环**：与之前相同——改进 skill，重新运行测试用例，询问反馈——只是中间没有 browser 审查。如果你有 filesystem，仍然可以将结果组织到迭代目录中。

**Description optimization**：此部分需要 `claude` CLI 工具（具体为 `claude -p`），该工具仅在 Claude Code 中可用。如果你在 Claude.ai 上，请跳过。

**Blind comparison**：需要 subagents。跳过。

**打包**：`package_skill.py` 脚本在任何有 Python 和 filesystem 的地方都能运行。在 Claude.ai 上，你可以运行它，用户可以下载生成的 `.skill` 文件。

**更新现有 skill**：用户可能要求你更新现有的 skill，而不是创建新的。在这种情况下：
- **保留原始名称。** 注意 skill 的目录名称和 `name` frontmatter 字段——保持不变。例如，如果安装的 skill 是 `research-helper`，输出 `research-helper.skill`（而不是 `research-helper-v2`）。
- **编辑前复制到可写位置。** 安装的 skill 路径可能是只读的。复制到 `/tmp/skill-name/`，在那里编辑，并从副本打包。
- **如果手动打包，先在 `/tmp/` 中暂存**，然后复制到输出目录——直接写入可能因权限问题失败。

---

## Cowork 特定说明

如果你使用的是 Cowork，主要需要了解的是：

- 你有 subagents，所以主要 workflow（并行生成测试用例、运行 baseline、评分等）都能正常工作。（不过，如果遇到严重的超时问题，可以串行而非并行运行测试 prompt。）
- 你没有 browser 或显示器，所以在生成 eval viewer 时，使用 `--static <output_path>` 写入一个独立的 HTML 文件，而不是启动服务器。然后提供一个链接，用户可以点击在他们的 browser 中打开 HTML。
- 无论出于什么原因，Cowork 环境似乎让 Claude 在运行测试后不太愿意生成 eval viewer，所以再次强调：无论你在 Cowork 还是 Claude Code，运行测试后，你应该始终生成 eval viewer 让人工查看示例，然后再自己修改 skill 并尝试纠正，使用 `generate_review.py`（而不是自己编写独特的 html 代码）。提前抱歉，但我要用大写了：在自己评估输入*之前*生成 EVAL VIEWER。你要尽快让它们呈现在用户面前！
- Feedback 的工作方式不同：由于没有运行中的服务器，viewer 的 "Submit All Reviews" 按钮会下载 `feedback.json` 作为文件。然后你可以从那里读取（可能需要先请求访问权限）。
- 打包可以正常工作——`package_skill.py` 只需要 Python 和 filesystem。
- Description optimization（`run_loop.py` / `run_eval.py`）在 Cowork 中应该可以正常工作，因为它通过 subprocess 使用 `claude -p`，而不是 browser，但请等到你完全完成 skill 制作且用户同意其状态良好后再进行。
- **更新现有 skill**：用户可能要求你更新现有的 skill，而不是创建新的。请遵循上面 claude.ai 部分的更新指南。

---

## 参考文件

`agents/` 目录包含专门 subagents 的说明。当你需要生成相关 subagent 时阅读它们。

- `agents/grader.md` — 如何针对输出评估断言
- `agents/comparator.md` — 如何在两个输出之间进行 blind A/B 比较
- `agents/analyzer.md` — 如何分析一个版本为何胜过另一个

`references/` 目录有额外的文档：
- `references/schemas.md` — evals.json、grading.json 等的 JSON 结构

---

再次强调核心循环：

- 弄清楚 skill 是关于什么的
- 起草或编辑 skill
- 在测试 prompt 上运行 claude-with-access-to-the-skill
- 与用户一起评估输出：
  - 创建 benchmark.json 并运行 `eval-viewer/generate_review.py` 帮助用户审查
  - 运行定量评估
- 重复直到你和用户都满意
- 打包最终的 skill 并返回给用户。

如果你有 TodoList，请将这些步骤添加进去，以确保不会遗忘。如果你在 Cowork 中，请特别将 "创建 evals JSON 并运行 `eval-viewer/generate_review.py` 以便人工审查测试用例" 放入你的 TodoList，确保这一步被执行。

祝顺利！