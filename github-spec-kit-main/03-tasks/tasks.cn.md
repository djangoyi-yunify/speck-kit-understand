---
description: 根据可用的设计产物，为该功能生成一份可执行的、按依赖关系排序的 tasks.md。
handoffs: 
  - label: 一致性分析
    agent: speckit.analyze
    prompt: 运行项目一致性分析
    send: true
  - label: 实现项目
    agent: speckit.implement
    prompt: 分阶段开始实现
    send: true
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## 用户输入```text
$ARGUMENTS
```在继续之前，你**必须**考虑用户输入（如果非空）。

## 大纲

1. **设置**：从仓库根目录运行 `{SCRIPT}` 并解析 FEATURE_DIR 和 AVAILABLE_DOCS 列表。所有路径必须为绝对路径。对于参数中的单引号，例如 "I'm Groot"，请使用转义语法：例如 'I'\''m Groot'（或者如果可能，使用双引号："I'm Groot"）。

2. **加载设计文档**：从 FEATURE_DIR 读取：
   - **必需**：plan.md（技术栈、库、结构），spec.md（用户故事及其优先级）
   - **可选**：data-model.md（实体），contracts/（接口契约），research.md（决策），quickstart.md（测试场景）
   - 注意：并非所有项目都包含所有文档。请根据现有内容生成任务。

3. **执行任务生成工作流**：
   - 加载 plan.md 并提取技术栈、库、项目结构
   - 加载 spec.md 并提取用户故事及其优先级（P1、P2、P3 等）
   - 如果 data-model.md 存在：提取实体并映射到用户故事
   - 如果 contracts/ 存在：将接口契约映射到用户故事
   - 如果 research.md 存在：提取决策用于设置任务
   - 生成按用户故事组织的任务（见下文任务生成规则）
   - 生成依赖关系图，显示用户故事完成顺序
   - 创建每个用户故事的并行执行示例
   - 验证任务完整性（每个用户故事包含所有必要任务，且可独立测试）

4. **生成 tasks.md**：使用 `templates/tasks-template.md` 作为结构，填充以下内容：
   - 来自 plan.md 的正确功能名称
   - 阶段 1：设置任务（项目初始化）
   - 阶段 2：基础任务（所有用户故事的阻塞式前置条件）
   - 阶段 3+：每个用户故事一个阶段（按 spec.md 中的优先级顺序）
   - 每个阶段包括：故事目标、独立测试标准、测试（如请求）、实现任务
   - 最终阶段：润色与横切关注点
   - 所有任务必须遵循严格的清单格式（见下文任务生成规则）
   - 每个任务的清晰文件路径
   - 依赖关系部分，显示故事完成顺序
   - 每个故事的并行执行示例
   - 实现策略部分（MVP 优先，增量交付）

5. **报告**：输出所生成 tasks.md 的路径及摘要：
   - 总任务数
   - 每个用户故事的任务数
   - 已识别的并行机会
   - 每个故事的独立测试标准
   - 建议的 MVP 范围（通常仅为用户故事 1）
   - 格式验证：确认所有任务遵循清单格式（复选框、ID、标签、文件路径）

任务生成上下文：{ARGS}

tasks.md 应当立即可执行——每个任务必须足够具体，以便 LLM 无需额外上下文即可完成。

## 任务生成规则

**关键**：任务必须按用户故事组织，以实现独立的实现和测试。

**测试是可选的**：仅在功能规范中明确要求或用户请求 TDD 方法时才生成测试任务。

### 清单格式（必需）

每个任务必须严格遵循此格式：```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```**格式组成部分**：

1. **Checkbox**：始终以 `- [ ]` 开头（Markdown 复选框）
2. **Task ID**：按执行顺序排列的顺序编号（T001, T002, T003...）
3. **[P] marker**：仅当任务可并行时包含（不同文件，无未完成任务依赖）
4. **[Story] label**：仅 User Story 阶段的任务需要
   - 格式：[US1], [US2], [US3] 等（映射到 spec.md 中的 user stories）
   - Setup 阶段：无 story 标签
   - Foundational 阶段：无 story 标签
   - User Story 阶段：必须有 story 标签
   - Polish 阶段：无 story 标签
5. **Description**：包含确切文件路径的清晰动作

**示例**：

- ✅ 正确：`- [ ] T001 Create project structure per implementation plan`
- ✅ 正确：`- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ 正确：`- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ 正确：`- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ 错误：`- [ ] Create User model`（缺少 ID 和 Story 标签）
- ❌ 错误：`T001 [US1] Create model`（缺少 Checkbox）
- ❌ 错误：`- [ ] [US1] Create User model`（缺少 Task ID）
- ❌ 错误：`- [ ] T001 [US1] Create model`（缺少文件路径）

### 任务组织

1. **源自 User Stories (spec.md)** - 主要组织方式：
   - 每个 user story (P1, P2, P3...) 拥有各自的阶段
   - 将所有相关组件映射到其所属的 story：
     - 该 story 所需的 Models
     - 该 story 所需的 Services
     - 该 story 所需的 Interfaces/UI
     - 如果请求了测试：针对该 story 的测试
   - 标记 story 依赖关系（大多数 story 应相互独立）

2. **源自 Contracts**：
   - 将每个 interface contract 映射 → 到其服务的 user story
   - 如果请求了测试：每个 interface contract → 在该 story 阶段实现之前的 contract test task [P]

3. **源自 Data Model**：
   - 将每个 entity 映射到需要它的 user story/stories
   - 如果 entity 服务于多个 stories：放入最早的 story 或 Setup 阶段
   - Relationships → 适当 story 阶段中的 service layer tasks

4. **源自 Setup/Infrastructure**：
   - Shared infrastructure → Setup 阶段 (Phase 1)
   - Foundational/blocking tasks → Foundational 阶段 (Phase 2)
   - Story-specific setup → 在该 story 的阶段内

### 阶段结构

- **Phase 1**：Setup（项目初始化）
- **Phase 2**：Foundational（阻塞性前置条件 - 必须在 user stories 之前完成）
- **Phase 3+**：按优先级排序的 User Stories (P1, P2, P3...)
  - 在每个 story 内：Tests（如需）→ Models → Services → Endpoints → Integration
  - 每个阶段应是一个完整、可独立测试的增量
- **Final Phase**：Polish & Cross-Cutting Concerns