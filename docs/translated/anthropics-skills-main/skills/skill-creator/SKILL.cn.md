---
name: skill-creator
description: 创建新 Skill，修改和改进现有 Skill，并衡量 Skill 性能。当用户希望从头创建 Skill、编辑或优化现有 Skill、运行 evals 测试 Skill、通过方差分析对比 Skill 性能，或优化 Skill 描述以提高触发准确率时使用。
---

# Skill Creator

一个用于创建新 Skill 并对其进行迭代改进的 Skill。

宏观来看，创建 Skill 的过程如下：

- 确定 Skill 的功能及其大致实现方式
- 编写 Skill 草稿
- 创建一些测试 Prompt，并对其运行 claude-with-access-to-the-skill
- 帮助用户对结果进行定性和定量评估
  - 在后台运行期间，如果没有现成的定量 evals，先起草一些（如果有，可以直接使用或根据需要进行修改）。然后向用户解释这些 evals（如果已存在，则解释现有的）
  - 使用 `eval-viewer/generate_review.py` 脚本向用户展示结果供其查看，同时让他们查看定量指标
- 根据用户对结果的评估反馈重写 Skill（如果定量 benchmark 明显暴露出缺陷，也需一并修复）
- 重复此过程直到满意
- 扩充测试集并在更大规模上再次尝试

使用此 Skill 时，你的任务是判断用户处于流程的哪个阶段，然后介入并帮助他们推进。例如，用户可能会说“我想为 X 做一个 Skill”。你可以协助明确需求、编写草稿、编写测试用例、确定评估方式、运行所有 Prompt 并重复迭代。

另一方面，如果他们已经有了 Skill 草稿，你可以直接进入循环中的评估/迭代环节。

当然，你需要保持灵活。如果用户表示“我不需要运行一堆评估，跟我凭感觉来就行”，那你就照做。

Skill 完成后（同样，顺序是灵活的），你还可以运行 Skill 描述优化器——我们有专门的脚本来优化 Skill 的触发。

明白了吗？很好。

## 与用户沟通

Skill Creator 的用户群体可能涵盖不同技术水平，对代码术语的熟悉程度也各不相同。如果你还没听说过（这也难怪，毕竟这也是最近才开始的趋势），现在有一种趋势，Claude 的强大正激励着水管工打开终端，父母祖辈去谷歌搜索“how to install npm”。另一方面，大多数用户可能都具备相当的计算机素养。

因此，请注意上下文线索来调整沟通措辞！在默认情况下，给你一些参考：

- “evaluation”和“benchmark”处于临界点，但通常可以使用
- 对于“JSON”和“assertion”，在未解释的情况下直接使用前，需要用户给出明确的信号表明他们了解这些概念

如果不确定，可以简要解释术语，如果不确定用户是否理解，也可以用简短定义澄清。

---

## 创建 Skill

### 捕捉意图

首先理解用户的意图。当前的对话可能已经包含了用户想要捕捉的 workflow（例如，他们说“把这个变成一个 Skill”）。如果是这样，先从对话历史中提取答案——使用的工具、步骤顺序、用户做的修正、观察到的输入/输出格式。用户可能需要填补空白，并应在进入下一步前进行确认。

1. 这个 Skill 应该能让 Claude 做什么？
2. 这个 Skill 何时触发？（哪些用户短语/上下文）
3. 预期的输出格式是什么？
4. 是否应该设置测试用例来验证 Skill 的有效性？具有客观可验证输出的 Skill（文件转换、数据提取、代码生成、固定 workflow 步骤）受益于测试用例。具有主观输出的 Skill（写作风格、艺术创作）通常不需要。根据 Skill 类型建议合适的默认设置，但最终由用户决定。

### 询问与研究

主动询问关于边缘情况、输入/输出格式、示例文件、成功标准和依赖项的问题。在完成这部分之前，先不要写测试 Prompt。

检查可用的 MCP——如果有助于研究（搜索文档、查找相似 Skill、查询最佳实践），若条件允许可通过 subagent 并行研究，否则就在当前会话中进行。准备好上下文以减轻用户的负担。

### 编写 SKILL.md

根据用户的访谈，填写以下组件：

- **name**：Skill 标识符
- **description**：触发时机及功能。这是主要的触发机制——既要包含 Skill 的功能，也要包含何时使用的具体上下文。所有“何时使用”的信息都应放在这里，而非正文。注意：目前 Claude 倾向于“触发不足”（undertrigger）——即在 Skill 有用时却不使用。为了解决这个问题，请让 Skill 描述稍微“激进”一点。例如，与其写“如何构建一个简单快速的仪表板来显示内部 Anthropic 数据”，不如写“如何构建一个简单快速的仪表板来显示内部 Anthropic 数据。只要用户提到仪表板、数据可视化、内部指标，或想显示任何类型的公司数据，即使他们没有明确要求‘仪表板’，也要务必使用此 Skill。”
- **compatibility**：所需工具、依赖项（可选，很少需要）
- **the rest of the skill :)**：Skill 的其余内容 :)

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

#### Progressive Disclosure

Skills 使用三级加载系统：
1. **Metadata** (name + description) - 始终位于上下文中（约 100 词）
2. **SKILL.md body** - 每当 Skill 触发时位于上下文中（理想情况 <500 行）
3. **Bundled resources** - 按需加载（无限制，Scripts 可在不加载的情况下执行）

这些字数仅为近似值，如有需要可适当延长。

**关键模式：**
- 将 SKILL.md 保持在 500 行以内；若接近此限制，请增加额外的层级结构，并包含明确指引，告知使用该 Skill 的 Model 接下来应前往何处继续执行。
- 在 SKILL.md 中清晰引用文件，并提供关于何时读取这些文件的指导
- 对于大型引用文件（>300 行），需包含目录

**领域组织**：当一个 Skill 支持多个领域/框架时，按变体进行组织：

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

这一点不言而喻，但 skills 绝不能包含恶意软件、漏洞利用代码或任何可能危及系统安全的内容。如果对 skills 的内容进行描述，其意图不应让用户感到意外。不要配合创建具有误导性的 skills，或旨在协助未经授权访问、数据窃取或其他恶意活动的 skills。不过，像“扮演 XYZ”之类的情况是可以的。

#### 编写模式

在指令中优先使用祈使语气。

**定义输出格式** - 可以这样做：

```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**示例模式** - 包含示例很有用。您可以按如下格式编排（但如果示例中包含 "Input" 和 "Output"，您可能需要稍作变通）：

```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### 写作风格

尝试向模型解释事物之所以重要的原因，而非使用生硬、陈旧的强制性要求。运用心智理论，尝试使技能具有通用性，而非仅仅局限于特定的具体示例。首先撰写草稿，然后以全新的视角审视并加以改进。

### 测试用例

编写完技能草稿后，设想 2-3 个现实的测试提示词——即真实用户实际上会提出的请求。将其分享给用户：[不必完全照搬这段话] “这里有几个我想尝试的测试用例。它们看起来合适吗？还是你想添加更多？” 然后运行这些用例。

将测试用例保存到 `evals/evals.json`。暂且不要编写断言——仅包含提示词。稍后在运行过程中，你将起草断言。

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

请参阅 `references/schemas.md` 查看完整的 schema（包括你稍后会添加的 `assertions` 字段）。

## 运行和评估测试用例

本节是一个连续的流程——请勿中途停止。切勿使用 `/skill-test` 或任何其他测试技能。

将结果存放在 `<skill-name>-workspace/` 中，该目录与 skill 目录同级。在工作区内，按迭代组织结果（`iteration-1/`、`iteration-2/` 等），并在该目录下为每个测试用例创建一个目录（`eval-0/`、`eval-1/` 等）。不要预先创建所有目录——只需在过程中按需创建。

### 步骤 1：在同一轮中生成所有运行（with-skill 和 baseline）

对于每个测试用例，在同一轮中生成两个子代理——一个带有 skill，一个不带。这一点很重要：不要先生成 with-skill 运行，稍后再回来处理 baseline。一次性启动所有任务，以便它们能在大致相同的时间完成。

**With-skill 运行：**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**基线运行**（相同的 prompt，但 baseline 依赖于上下文）：
- **创建新 skill**：完全没有 skill。相同的 prompt，无 skill path，保存到 `without_skill/outputs/`。
- **改进现有 skill**：旧版本。编辑前，对 skill 进行快照（`cp -r <skill-path> <workspace>/skill-snapshot/`），然后将 baseline subagent 指向该快照。保存到 `old_skill/outputs/`。

为每个测试用例编写一个 `eval_metadata.json`（assertions 暂时可以为空）。根据测试内容为每个 eval 赋予一个描述性名称——不要仅使用 "eval-0"。也使用该名称作为目录名。如果本次迭代使用了新的或修改过的 eval prompts，请为每个新的 eval 目录创建这些文件——不要假设它们会从之前的迭代中沿用。

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### 步骤 2：当运行正在进行时，编写断言

不要只是等待运行结束——您可以充分利用这段时间。为每个测试用例编写定量断言，并向用户解释这些断言。如果 `evals/evals.json` 中已存在断言，请审查它们并解释它们检查的内容。

好的断言是客观可验证的，并且具有描述性的名称——它们在基准测试查看器中应清晰易读，以便浏览结果的人能立即理解每个断言检查的内容。主观技能（写作风格、设计质量）更适合进行定性评估——不要强行对需要人工判断的内容设定断言。

断言编写完成后，更新 `eval_metadata.json` 文件和 `evals/evals.json`。同时向用户解释他们将在查看器中看到的内容——包括定性输出和定量基准测试。

### 步骤 3：当运行完成时，捕获计时数据

当每个 subagent 任务完成时，您会收到一个包含 `total_tokens` 和 `duration_ms` 的通知。立即将此数据保存到运行目录中的 `timing.json`：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

这是捕获此数据的唯一机会——它通过任务通知传递，并未持久化到其他地方。请在每个通知到达时进行处理，而不是尝试批量处理。

### 步骤 4：评分、聚合并启动查看器

一旦所有运行完成：

1. **对每次运行进行评分** —— 生成一个评分子代理（或内联评分），读取 `agents/grader.md` 并根据输出评估每个断言。将结果保存到每个运行目录下的 `grading.json` 中。grading.json 的 expectations 数组必须使用字段 `text`、`passed` 和 `evidence`（而不是 `name`/`met`/`details` 或其他变体）—— 查看器依赖于这些确切的字段名称。对于可以通过编程方式检查的断言，请编写并运行脚本，而不是通过肉眼检查 —— 脚本更快、更可靠，并且可以在迭代中重用。

2. **聚合为基准测试** —— 从 skill-creator 目录运行聚合脚本：

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

这会生成 `benchmark.json` 和 `benchmark.md`，包含每种配置的 `pass_rate`、`time` 和 `tokens`，以及 mean ± stddev 和 delta。如果手动生成 `benchmark.json`，请参阅 `references/schemas.md` 查看 viewer 所期望的确切 schema。
将每个 `with_skill` 版本排在其对应的 baseline 版本之前。

3. **执行 analyst pass** —— 阅读 benchmark 数据，揭示 aggregate stats 可能隐藏的模式。请参阅 `agents/analyzer.md`（“Analyzing Benchmark Results”章节）了解需要关注的内容——例如无论 skill 如何总是通过的断言、高方差的 evals（可能 flaky），以及 time/token tradeoffs。

4. **启动 viewer**，同时加载定性输出 和定量数据：

```bash
nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
```

对于第 2 次及以后的迭代，还需传入 `--previous-workspace <workspace>/iteration-<N-1>`。

**协同工作 / 无头环境：** 如果 `webbrowser.open()` 不可用或环境没有显示器，请使用 `--static <output_path>` 写入一个独立的 HTML 文件，而不是启动服务器。当用户点击 "Submit All Reviews" 时，反馈将作为 `feedback.json` 文件下载。下载后，将 `feedback.json` 复制到工作空间目录中，供下一次迭代读取。

注意：请使用 generate_review.py 创建查看器；无需编写自定义 HTML。

5. **告知用户** 类似如下内容：“我已经在您的浏览器中打开了结果。有两个标签页 — 'Outputs' 允许您点击查看每个测试用例并留下反馈，'Benchmark' 显示量化对比。完成后，请回到这里告诉我。”

### 用户在查看器中看到的内容

"Outputs" 标签页一次显示一个测试用例：
- **Prompt**：给定的任务
- **Output**：技能生成的文件，在可能的情况下内嵌渲染
- **Previous Output**（迭代 2+）：显示上一次迭代输出的折叠区域
- **Formal Grades**（如果运行了评分）：显示断言通过/失败的折叠区域
- **Feedback**：一个随输入自动保存的文本框
- **Previous Feedback**（迭代 2+）：上次的评论，显示在文本框下方

"Benchmark" 标签页显示统计摘要：每种配置的通过率、耗时和 Token 用量，以及单次评估的细分详情和分析观察。

导航通过 prev/next 按钮或方向键进行。完成后，他们点击 "Submit All Reviews"，这将所有反馈保存到 `feedback.json`。

### Step 5：读取反馈

当用户告诉您他们已完成时，读取 `feedback.json`：

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

反馈为空意味着用户认为没问题。请将改进重点放在用户提出具体问题的测试用例上。

使用完毕后，请终止 Viewer server：

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## 改进技能

这是循环的核心。你已经运行了测试用例，用户已经审查了结果，现在你需要根据他们的反馈让技能变得更好。

### 如何思考改进

1. **从反馈中泛化。** 这里的宏观图景是，我们正在尝试创建可以在许多不同的 prompts 中使用数百万次（也许是字面意义上的，甚至更多，谁知道呢）的技能。在这里，你和用户只在几个示例上反复迭代，因为这有助于加快速度。用户对这些示例了如指掌，评估新输出对他们来说很快。但是，如果你和用户共同开发的技能仅适用于这些示例，它就毫无用处。与其做一些琐碎的过拟合修改，或添加过于严苛的 MUST 约束，如果遇到顽固问题，你不妨尝试扩展思路，使用不同的隐喻，或推荐不同的工作模式。尝试的成本相对较低，也许你会找到很棒的方案。

2. **保持 prompt 精简。** 删除那些没有发挥作用的内容。确保阅读 transcripts，而不仅仅是最终输出——如果技能似乎让模型浪费时间做一些无效的事情，你可以尝试删除技能中导致这种情况的部分，看看会发生什么。

3. **解释原因。** 努力解释你要求模型做的每件事背后的**原因**。今天的 LLMs 非常*聪明*。它们具有良好的心智理论能力，当给予良好的引导时，能够超越死板的指令，真正把事情做成。即使用户的反馈简短或带有挫败感，也要试着真正理解任务，理解用户为什么这样写，以及他们实际写了什么，然后将这种理解传递到指令中。如果你发现自己用全大写写 ALWAYS 或 NEVER，或者使用过于僵化的结构，这是一个警示信号——如果可能的话，重新组织语言并解释原因，让模型理解你要求的事情为什么重要。这是一种更人性化、更强大、更有效的方法。

4. **寻找跨测试用例的重复工作。** 阅读测试运行的 transcripts，注意 subagents 是否都独立编写了相似的辅助脚本，或对某事采取了相同的多步骤方法。如果所有 3 个测试用例都导致 subagent 编写了 `create_docx.py` 或 `build_chart.py`，这是一个强烈的信号，表明技能应该打包该脚本。编写一次，放入 `scripts/`，并告诉技能使用它。这能让每次未来的调用都不必重复造轮子。

这项任务相当重要（我们正试图每年创造数十亿美元的经济价值！），你的思考时间不是瓶颈；慢慢来，认真思考。我建议先写一个修订草案，然后重新审视并改进。真正尽力进入用户的思维，理解他们想要和需要什么。

### 迭代循环

改进技能后：

1. 将你的改进应用到技能
2. 将所有测试用例重新运行到一个新的 `iteration-<N+1>/` 目录，包括 baseline 运行。如果你在创建新技能，baseline 始终是 `without_skill`（无技能）——这在各次迭代中保持不变。如果你在改进现有技能，根据你的判断选择合理的 baseline：用户带来的原始版本，或上一次迭代。
3. 启动 reviewer，用 `--previous-workspace` 指向上一次迭代
4. 等待用户审查并告诉你他们完成了
5. 阅读新反馈，再次改进，重复

持续进行直到：
- 用户表示满意
- 反馈全部为空（一切看起来都很好）
- 你没有取得实质性进展

---

## 高级：盲比较

对于需要更严格比较两个技能版本的情况（例如，用户问"新版本真的更好吗？"），有一个盲比较系统。阅读 `agents/comparator.md` 和 `agents/analyzer.md` 了解详情。基本思路是：将两个输出提供给一个独立的 agent，不告诉它哪个是哪个，让它评判质量。然后分析获胜者为什么获胜。

这是可选的，需要 subagents，大多数用户不需要它。人工审查循环通常就足够了。

---

## 描述优化

SKILL.md frontmatter 中的 description 字段是决定 Claude 是否调用技能的主要机制。创建或改进技能后，提议优化描述以提高触发准确性。

### 步骤 1：生成触发评估查询

创建 20 个评估查询——混合 should-trigger 和 should-not-trigger。保存为 JSON：

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

查询必须真实，是 Claude Code 或 Claude.ai 用户实际会输入的内容。不要抽象的请求，而是具体、详细、包含大量细节的请求。例如：文件路径、关于用户工作或情况的个人背景、列名和值、公司名称、URL。还要有一些背景故事。有些可能是小写的，或者包含缩写、拼写错误或口语化表达。使用不同长度的混合，重点关注边缘情况而不是过于明确的情况（用户有机会确认它们）。

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok 所以我老板刚发给我一个 xlsx 文件（在我的 downloads 文件夹里，名字好像是 'Q4 sales final FINAL v2.xlsx'），她想让我加一列显示利润率百分比。收入在 C 列，成本在 D 列，我记得"`

对于 **should-trigger** 查询（8-10 条），要考虑覆盖范围。你需要同一意图的不同表达方式——有些正式，有些随意。包括用户没有明确说出技能或文件类型但明显需要它的情况。加入一些不常见的用例，以及这个技能与另一个技能竞争但应该胜出的情况。

对于 **should-not-trigger** 查询（8-10 条），最有价值的是那些几乎命中但实际上未命中的情况——与技能共享关键词或概念但实际上需要其他东西的查询。想想相邻领域、模糊的表达（简单的关键词匹配会触发但不应该触发），以及查询涉及技能所做的事情但在另一个工具更合适的上下文中的情况。

要避免的关键点：不要让 should-not-trigger 查询明显无关。用 "Write a fibonacci function" 作为 PDF 技能的负面测试太简单了——它测试不了任何东西。负面案例应该真正具有欺骗性。

### Step 2: 与用户一起审查

使用 HTML 模板向用户展示评估集以供审查：

1. 从 `assets/eval_review.html` 读取模板
2. 替换占位符：
   - `__EVAL_DATA_PLACEHOLDER__` → eval 项目的 JSON 数组（不要加引号——这是一个 JS 变量赋值）
   - `__SKILL_NAME_PLACEHOLDER__` → 技能名称
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → 技能的当前描述
3. 写入临时文件（例如 `/tmp/eval_review_<skill-name>.html`）并打开它：`open /tmp/eval_review_<skill-name>.html`
4. 用户可以编辑查询、切换 should-trigger、添加/删除条目，然后点击 "Export Eval Set"
5. 文件下载到 `~/Downloads/eval_set.json` — 检查 Downloads 文件夹获取最新版本，以防有多个文件（例如 `eval_set (1).json`）

这一步很重要 — 糟糕的 eval 查询会导致糟糕的描述。

### Step 3: 运行优化循环

告诉用户："这需要一些时间 — 我会在后台运行优化循环并定期检查。"

将 eval 集保存到工作区，然后在后台运行：

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

使用系统 prompt 中的 model ID（即驱动当前会话的那个），这样触发测试才能匹配用户的实际体验。

运行期间，定期查看输出，向用户更新当前迭代次数和分数情况。

这会自动处理完整的优化循环。它将 eval 集划分为 60% 的训练集和 40% 的保留测试集，评估当前的 description（每个 query 运行 3 次以获得可靠的触发率），然后调用 Claude 根据失败情况提出改进建议。它会在训练集和测试集上重新评估每个新的 description，最多迭代 5 次。完成后，它会在浏览器中打开 HTML 报告，显示每次迭代的结果，并返回包含 `best_description` 的 JSON——该 description 根据测试集分数而非训练集分数选择，以避免过拟合。

### Skill 触发机制

理解触发机制有助于设计更好的 eval query。Skill 会以名称 + description 的形式出现在 Claude 的 `available_skills` 列表中，Claude 根据 description 决定是否调用 skill。重要的是要知道，Claude 只会为它无法独自轻松处理的任务调用 skill——像"read this PDF"这样简单的一步查询可能不会触发 skill，即使 description 完全匹配，因为 Claude 可以直接用基础工具处理。复杂、多步骤或专业化的查询在 description 匹配时会可靠地触发 skill。

这意味着你的 eval query 应该足够有实质内容，让 Claude 确实能从调用 skill 中受益。像"read file X"这样的简单查询是糟糕的测试用例——无论 description 质量如何，它们都不会触发 skill。

### 步骤 4：应用结果

从 JSON 输出中获取 `best_description`，更新 skill 的 SKILL.md frontmatter。向用户展示修改前后的对比并报告分数。

---

### 打包和展示（仅在 `present_files` 工具可用时）

检查你是否有 `present_files` 工具的访问权限。如果没有，跳过此步骤。如果有，打包 skill 并向用户展示 .skill 文件：

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

打包完成后，引导用户找到生成的 `.skill` 文件路径，以便他们进行安装。

---

## Claude.ai 特定说明

在 Claude.ai 中，核心工作流程相同（起草 → 测试 → 审查 → 改进 → 循环），但由于 Claude.ai 没有 subagents，某些机制需要调整。以下是需要适配的内容：

**运行测试用例**：没有 subagents 意味着无法并行执行。对于每个测试用例，读取 skill 的 SKILL.md，然后按照其说明自行完成测试提示。逐个执行。这比独立的 subagents 不够严格（你编写了 skill，同时也在运行它，因此你拥有完整的上下文），但这是一种有用的完整性检查——人工审查步骤可以弥补这一点。跳过基线运行——直接使用 skill 按要求完成任务。

**审查结果**：如果你无法打开浏览器（例如 Claude.ai 的 VM 没有显示器，或者你在远程服务器上），则完全跳过浏览器审查。改为直接在对话中展示结果。对于每个测试用例，显示提示和输出。如果输出是用户需要查看的文件（如 .docx 或 .xlsx），将其保存到文件系统并告知用户位置，以便他们下载和检查。内联询问反馈："看起来怎么样？有什么需要修改的吗？"

**基准测试**：跳过定量基准测试——它依赖于基线比较，没有 subagents 时没有意义。专注于用户的定性反馈。

**迭代循环**：与之前相同——改进 skill，重新运行测试用例，询问反馈——只是中间没有浏览器审查。如果有的话，你仍然可以将结果组织到文件系统上的迭代目录中。

**描述优化**：此部分需要 `claude` CLI 工具（具体为 `claude -p`），该工具仅在 Claude Code 中可用。如果你在 Claude.ai 上，请跳过。

**盲比较**：需要 subagents。跳过。

**打包**：`package_skill.py` 脚本可在任何有 Python 和文件系统的地方运行。在 Claude.ai 上，你可以运行它，用户可以下载生成的 `.skill` 文件。

**更新现有 skill**：用户可能要求你更新现有的 skill，而不是创建新的。在这种情况下：
- **保留原始名称。** 记录 skill 的目录名和 `name` frontmatter 字段——保持不变。例如，如果安装的 skill 是 `research-helper`，则输出 `research-helper.skill`（而不是 `research-helper-v2`）。
- **编辑前复制到可写位置。** 安装的 skill 路径可能是只读的。复制到 `/tmp/skill-name/`，在那里编辑，并从副本打包。
- **如果手动打包，先暂存到 `/tmp/`**，然后复制到输出目录——直接写入可能因权限问题而失败。

---

## Cowork 特定说明

如果你在 Cowork 中，主要需要了解的是：

- 你有 subagents，所以主要工作流程（并行生成测试用例、运行基线、评分等）都能正常工作。（但是，如果遇到严重的超时问题，可以改为串行运行测试提示而非并行。）
- 你没有浏览器或显示器，所以在生成 eval viewer 时，使用 `--static <output_path>` 写入一个独立的 HTML 文件，而不是启动服务器。然后提供一个链接，用户可以点击在浏览器中打开 HTML。
- 无论出于什么原因，Cowork 环境似乎会让 Claude 在运行测试后不愿意生成 eval viewer，所以再次强调：无论你在 Cowork 还是 Claude Code，运行测试后，你应该始终使用 `generate_review.py` 生成 eval viewer 供人工查看示例，然后再自己修改 skill 并尝试纠正（不要自己编写独特的 html 代码）。提前抱歉，但我要用全大写了：在自己评估输入之前**先生成 EVAL VIEWER**。你想尽快把它们展示给人工！
- 反馈机制不同：由于没有运行中的服务器，查看器的"Submit All Reviews"按钮会将 `feedback.json` 作为文件下载。然后你可以从中读取（可能需要先请求访问权限）。
- 打包可以正常工作——`package_skill.py` 只需要 Python 和文件系统。
- 描述优化（`run_loop.py` / `run_eval.py`）在 Cowork 中应该可以正常工作，因为它通过 subprocess 使用 `claude -p`，而不是浏览器，但请在完全完成 skill 制作且用户认可其状态良好之后再进行。
- **更新现有 skill**：用户可能要求你更新现有的 skill，而不是创建新的。请遵循上方 claude.ai 部分的更新指导。

---

## 参考文件

agents/ 目录包含专门 subagents 的说明。需要生成相关 subagent 时请阅读它们。

- `agents/grader.md` — 如何对输出评估断言
- `agents/comparator.md` — 如何在两个输出之间进行盲 A/B 比较
- `agents/analyzer.md` — 如何分析一个版本为何优于另一个

references/ 目录包含额外文档：
- `references/schemas.md` — evals.json、grading.json 等的 JSON 结构

---

再次重复核心循环以强调：

- 弄清楚 skill 的用途
- 起草或编辑 skill
- 使用可访问 skill 的 claude 运行测试提示
- 与用户一起评估输出：
  - 创建 benchmark.json 并运行 `eval-viewer/generate_review.py` 帮助用户审查
  - 运行定量评估
- 循环直到你和用户都满意
- 打包最终 skill 并返回给用户。

如果有 TodoList，请将步骤添加到其中，以确保不会遗忘。如果你在 Cowork 中，请务必将"创建 evals JSON 并运行 `eval-viewer/generate_review.py` 以便人工审查测试用例"放入 TodoList，以确保其被执行。

祝好运！