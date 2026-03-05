---
description: 根据现有的设计工件，为该功能生成一份可执行的、按依赖关系排序的 tasks.md。
handoffs: 
  - label: 分析一致性
    agent: speckit.analyze
    prompt: 运行项目分析以检查一致性
    send: true
  - label: 实施项目
    agent: speckit.implement
    prompt: 开始分阶段实施
    send: true
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前，你**必须**考虑用户输入（如果不为空）。

## 执行前检查

**检查扩展钩子（任务生成前）**：
- 检查项目根目录下是否存在 `.specify/extensions.yml`。
- 如果存在，读取该文件并查找 `hooks.before_tasks` 键下的条目。
- 如果 YAML 无法解析或无效，静默跳过钩子检查并正常继续。
- 仅筛选 `enabled: true` 的钩子。
- 对于每个剩余的钩子，**不要**尝试解释或评估钩子的 `condition` 表达式：
  - 如果钩子没有 `condition` 字段，或者该字段为 null/空，则将钩子视为可执行。
  - 如果钩子定义了非空的 `condition`，则跳过该钩子并将条件评估留给 HookExecutor 实现。
- 对于每个可执行的钩子，根据其 `optional` 标志输出以下内容：
  - **可选钩子**（`optional: true`）：

```
## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
```

- **强制 Hook** (`optional: false`):

```
## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    
    Wait for the result of the hook command before proceeding to the Outline.
```

- 如果未注册 hooks 或 `.specify/extensions.yml` 不存在，则静默跳过

## 大纲

1. **设置**：在仓库根目录运行 `{SCRIPT}` 并解析 FEATURE_DIR 和 AVAILABLE_DOCS 列表。所有路径必须是绝对路径。对于参数中的单引号（如 "I'm Groot"），使用转义语法：例如 'I'\''m Groot'（如果可能，使用双引号："I'm Groot"）。

2. **加载设计文档**：从 FEATURE_DIR 读取：
   - **必须**：plan.md（技术栈、库、结构），spec.md（带优先级的用户故事）
   - **可选**：data-model.md（实体），contracts/（接口契约），research.md（决策），quickstart.md（测试场景）
   - 注意：并非所有项目都包含所有文档。根据现有文档生成任务。

3. **执行任务生成 workflow**：
   - 加载 plan.md 并提取技术栈、库、项目结构
   - 加载 spec.md 并提取用户故事及其优先级（P1、P2、P3 等）
   - 如果 data-model.md 存在：提取实体并映射到用户故事
   - 如果 contracts/ 存在：将接口契约映射到用户故事
   - 如果 research.md 存在：提取决策用于 setup 任务
   - 按用户故事组织生成任务（见下方任务生成规则）
   - 生成依赖关系图，显示用户故事完成顺序
   - 为每个用户故事创建并行执行示例
   - 验证任务完整性（每个用户故事包含所有必要任务，可独立测试）

4. **生成 tasks.md**：使用 `templates/tasks-template.md` 作为结构，填充：
   - 来自 plan.md 的正确功能名称
   - 阶段 1：Setup 任务（项目初始化）
   - 阶段 2：基础任务（所有用户故事的阻塞性前置条件）
   - 阶段 3+：每个用户故事一个阶段（按 spec.md 中的优先级顺序）
   - 每个阶段包括：故事目标、独立测试标准、测试（如有要求）、实现任务
   - 最终阶段：完善与横切关注点
   - 所有任务必须遵循严格的检查表格式（见下方任务生成规则）
   - 每个任务的清晰文件路径
   - 依赖关系部分，显示故事完成顺序
   - 每个故事的并行执行示例
   - 实现策略部分（MVP 优先，增量交付）

5. **报告**：输出 tasks.md 的生成路径和摘要：
   - 任务总数
   - 每个用户故事的任务数
   - 已识别的并行机会
   - 每个故事的独立测试标准
   - 建议的 MVP 范围（通常仅为 User Story 1）
   - 格式验证：确认所有任务遵循检查表格式（复选框、ID、标签、文件路径）

6. **检查 extension hooks**：tasks.md 生成后，检查项目根目录下是否存在 `.specify/extensions.yml`。
   - 如果存在，读取文件并查找 `hooks.after_tasks` 键下的条目
   - 如果 YAML 无法解析或无效，静默跳过 hook 检查并正常继续
   - 筛选出 `enabled: true` 的 hooks
   - 对于每个剩余的 hook，**不要**尝试解释或评估 hook 的 `condition` 表达式：
     - 如果 hook 没有 `condition` 字段，或者为 null/空，则将 hook 视为可执行
     - 如果 hook 定义了非空 `condition`，跳过该 hook 并将条件评估留给 HookExecutor 实现
   - 对于每个可执行的 hook，根据其 `optional` 标志输出以下内容：
     - **Optional hook** (`optional: true`)：

```
## Extension Hooks

       **Optional Hook**: {extension}
       Command: `/{command}`
       Description: {description}

       Prompt: {prompt}
       To execute: `/{command}`
```

- **强制 Hook** (`optional: false`):

```
## Extension Hooks

       **Automatic Hook**: {extension}
       Executing: `/{command}`
       EXECUTE_COMMAND: {command}
```

- 如果没有注册 hooks 或 `.specify/extensions.yml` 不存在，则静默跳过

任务生成上下文：{ARGS}

tasks.md 应可直接执行 —— 每个任务必须足够具体，以便 LLM 无需额外上下文即可完成。

## 任务生成规则

**关键**：任务必须按 user story 组织，以便能够独立实施和测试。

**测试为可选项**：仅在功能规范中明确要求或用户请求 TDD 方法时才生成测试任务。

### 清单格式（必填）

每个任务必须严格遵循以下格式：

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**格式组成**：

1. **Checkbox**：必须以 `- [ ]` 开头
2. **Task ID**：按执行顺序排列的序号（T001, T002, T003...）
3. **[P] marker**：仅当任务可并行化时包含（不同文件、不依赖未完成任务）
4. **[Story] label**：仅用户故事阶段任务需要
   - 格式：[US1], [US2], [US3] 等（映射到 spec.md 中的用户故事）
   - Setup 阶段：无 story label
   - Foundational 阶段：无 story label
   - User Story 阶段：必须包含 story label
   - Polish 阶段：无 story label
5. **Description**：清晰的操作描述及精确的文件路径

**示例**：

- ✅ 正确：`- [ ] T001 Create project structure per implementation plan`
- ✅ 正确：`- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ 正确：`- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ 正确：`- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ 错误：`- [ ] Create User model`（缺少 ID 和 Story label）
- ❌ 错误：`T001 [US1] Create model`（缺少 checkbox）
- ❌ 错误：`- [ ] [US1] Create User model`（缺少 Task ID）
- ❌ 错误：`- [ ] T001 [US1] Create model`（缺少文件路径）

### 任务组织

1. **源自 User Stories (spec.md)** - 主要组织方式：
   - 每个用户故事（P1, P2, P3...）拥有独立的阶段
   - 将所有相关组件映射到其对应的故事：
     - 该故事所需的 Models
     - 该故事所需的 Services
     - 该故事所需的 Interfaces/UI
     - 如果请求了测试：该故事特定的测试
   - 标记故事依赖关系（大多数故事应是独立的）

2. **源自 Contracts**：
   - 将每个接口契约映射 → 到其服务的用户故事
   - 如果请求了测试：每个接口契约 → 在该故事阶段实现前的契约测试任务 [P]

3. **源自 Data Model**：
   - 将每个实体映射到需要它的用户故事
   - 如果实体服务于多个故事：放入最早的故事或 Setup 阶段
   - 关系 → 适当故事阶段中的服务层任务

4. **源自 Setup/Infrastructure**：
   - 共享基础设施 → Setup 阶段（阶段 1）
   - Foundational/阻塞任务 → Foundational 阶段（阶段 2）
   - 特定故事的设置 → 在该故事的阶段内

### 阶段结构

- **Phase 1**：Setup（项目初始化）
- **Phase 2**：Foundational（阻塞性前置条件 - 必须在用户故事前完成）
- **Phase 3+**：User Stories 按优先级排序（P1, P2, P3...）
  - 在每个故事内：Tests（如有要求）→ Models → Services → Endpoints → Integration
  - 每个阶段应是一个完整、可独立测试的增量
- **Final Phase**：Polish & Cross-Cutting Concerns