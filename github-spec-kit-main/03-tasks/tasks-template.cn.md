---

description: "功能实现任务列表模板"
---

# 任务：[FEATURE NAME]

**输入**：来自 `/specs/[###-feature-name]/` 的设计文档
**前置条件**：plan.md（必需），spec.md（用户故事必需），research.md，data-model.md，contracts/

**测试**：以下示例包含测试任务。测试是可选的——仅在功能规范中明确要求时才包含。

**组织方式**：任务按用户故事分组，以便对每个故事进行独立的实现和测试。

## 格式：`[ID] [P?] [Story] 描述`

- **[P]**：可并行运行（不同文件，无依赖）
- **[Story]**：此任务所属的用户故事（例如：US1, US2, US3）
- 描述中需包含准确的文件路径

## 路径约定

- **单体项目**：仓库根目录下的 `src/`、`tests/`
- **Web 应用**：`backend/src/`、`frontend/src/`
- **移动应用**：`api/src/`、`ios/src/` 或 `android/src/`
- 下方显示的路径假设为单体项目——请根据 plan.md 结构进行调整

<!-- 
  ============================================================================
  重要：以下任务是仅用于说明的示例任务。
  
  /speckit.tasks 命令必须根据以下内容替换这些任务：
  - 来自 spec.md 的用户故事（及其优先级 P1, P2, P3...）
  - 来自 plan.md 的功能需求
  - 来自 data-model.md 的实体
  - 来自 contracts/ 的端点
  
  任务必须按用户故事组织，以便每个故事可以：
  - 独立实现
  - 独立测试
  - 作为 MVP 增量交付
  
  切勿在生成的 tasks.md 文件中保留这些示例任务。
  ============================================================================
-->

## 阶段 1：设置（共享基础设施）

**目的**：项目初始化和基础结构

- [ ] T001 根据实现计划创建项目结构
- [ ] T002 使用 [framework] 依赖初始化 [language] 项目
- [ ] T003 [P] 配置 linting 和格式化工具

---

## 阶段 2：基础（阻塞性前置条件）

**目的**：必须在任何用户故事实现之前完成的核心基础设施

**⚠️ 关键**：此阶段完成前，不得开始任何用户故事工作

基础任务示例（根据您的项目进行调整）：

- [ ] T004 设置数据库 schema 和迁移框架
- [ ] T005 [P] 实现认证/授权框架
- [ ] T006 [P] 设置 API 路由和中间件结构
- [ ] T007 创建所有故事依赖的基础模型/实体
- [ ] T008 配置错误处理和日志基础设施
- [ ] T009 设置环境配置管理

**检查点**：基础已就绪——用户故事实现现在可以并行开始

---

## 阶段 3：用户故事 1 - [Title]（优先级：P1）🎯 MVP

**目标**：[关于此故事交付内容的简要描述]

**独立测试**：[如何独立验证此故事是否正常工作]

### 用户故事 1 的测试（可选——仅在要求测试时） ⚠️

> **注意：首先编写这些测试，确保实现前它们处于失败状态**

- [ ] T010 [P] [US1] 在 tests/contract/test_[name].py 中为 [endpoint] 编写契约测试
- [ ] T011 [P] [US1] 在 tests/integration/test_[name].py 中为 [user journey] 编写集成测试

### 用户故事 1 的实现

- [ ] T012 [P] [US1] 在 src/models/[entity1].py 中创建 [Entity1] 模型
- [ ] T013 [P] [US1] 在 src/models/[entity2].py 中创建 [Entity2] 模型
- [ ] T014 [US1] 在 src/services/[service].py 中实现 [Service]（依赖于 T012, T013）
- [ ] T015 [US1] 在 src/[location]/[file].py 中实现 [endpoint/feature]
- [ ] T016 [US1] 添加验证和错误处理
- [ ] T017 [US1] 为用户故事 1 的操作添加日志记录

**检查点**：此时，用户故事 1 应完全可用并可独立测试

---

## 阶段 4：用户故事 2 - [Title]（优先级：P2）

**目标**：[关于此故事交付内容的简要描述]

**独立测试**：[如何独立验证此故事是否正常工作]

### 用户故事 2 的测试（可选——仅在要求测试时） ⚠️

- [ ] T018 [P] [US2] 在 tests/contract/test_[name].py 中为 [endpoint] 编写契约测试
- [ ] T019 [P] [US2] 在 tests/integration/test_[name].py 中为 [user journey] 编写集成测试

### 用户故事 2 的实现

- [ ] T020 [P] [US2] 在 src/models/[entity].py 中创建 [Entity] 模型
- [ ] T021 [US2] 在 src/services/[service].py 中实现 [Service]
- [ ] T022 [US2] 在 src/[location]/[file].py 中实现 [endpoint/feature]
- [ ] T023 [US2] 与用户故事 1 组件集成（如需要）

**检查点**：此时，用户故事 1 和 2 应均能独立工作

---

## 阶段 5：用户故事 3 - [Title]（优先级：P3）

**目标**：[关于此故事交付内容的简要描述]

**独立测试**：[如何独立验证此故事是否正常工作]

### 用户故事 3 的测试（可选——仅在要求测试时） ⚠️

- [ ] T024 [P] [US3] 在 tests/contract/test_[name].py 中为 [endpoint] 编写契约测试
- [ ] T025 [P] [US3] 在 tests/integration/test_[name].py 中为 [user journey] 编写集成测试

### 用户故事 3 的实现

- [ ] T026 [P] [US3] 在 src/models/[entity].py 中创建 [Entity] 模型
- [ ] T027 [US3] 在 src/services/[service].py 中实现 [Service]
- [ ] T028 [US3] 在 src/[location]/[file].py 中实现 [endpoint/feature]

**检查点**：所有用户故事此时应能独立运行

---

[根据需要添加更多用户故事阶段，遵循相同模式]

---

## 阶段 N：完善与横切关注点

**目的**：影响多个用户故事的改进

- [ ] TXXX [P] 更新 docs/ 中的文档
- [ ] TXXX 代码清理和重构
- [ ] TXXX 跨所有故事的性能优化
- [ ] TXXX [P] 在 tests/unit/ 中添加额外的单元测试（如已要求）
- [ ] TXXX 安全加固
- [ ] TXXX 运行 quickstart.md 验证

---

## 依赖关系与执行顺序

### 阶段依赖

- **设置（阶段 1）**：无依赖——可立即开始
- **基础（阶段 2）**：依赖设置阶段的完成——阻塞所有用户故事
- **用户故事（阶段 3+）**：全部依赖基础阶段的完成
  - 用户故事随后可并行进行（如有人员配置）
  - 或按优先级顺序进行（P1 → P2 → P3）
- **完善（最终阶段）**：依赖所有预期用户故事的完成

### 用户故事依赖

- **用户故事 1 (P1)**：可在基础阶段（阶段 2）后开始——不依赖其他故事
- **用户故事 2 (P2)**：可在基础阶段（阶段 2）后开始——可能与 US1 集成，但应可独立测试
- **用户故事 3 (P3)**：可在基础阶段（阶段 2）后开始——可能与 US1/US2 集成，但应可独立测试

### 在每个用户故事内部

- 测试（如果包含）必须在实现前编写并处于失败状态
- 先模型后服务
- 先服务后端点
- 先核心实现后集成
- 故事完成后再移至下一优先级

### 并行机会

- 所有标记为 [P] 的设置任务可并行运行
- 所有标记为 [P] 的基础任务可并行运行（在阶段 2 内）
- 基础阶段完成后，所有用户故事可并行开始（如果团队产能允许）
- 用户故事中所有标记为 [P] 的测试可并行运行
- 故事中标记为 [P] 的模型可并行运行
- 不同用户故事可由不同团队成员并行处理

---

## 并行示例：用户故事 1```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```---

## 实施策略

### MVP 优先（仅 User Story 1）

1. 完成 Phase 1：Setup
2. 完成 Phase 2：Foundational（CRITICAL - 阻塞所有 Story）
3. 完成 Phase 3：User Story 1
4. **停止并验证**：独立测试 User Story 1
5. 准备好后部署/演示

### 增量交付

1. 完成 Setup + Foundational → 基础就绪
2. 添加 User Story 1 → 独立测试 → 部署/演示（MVP！）
3. 添加 User Story 2 → 独立测试 → 部署/演示
4. 添加 User Story 3 → 独立测试 → 部署/演示
5. 每个 Story 都能增加价值，且不破坏之前的 Story

### 并行团队策略

有多个开发人员时：

1. 团队共同完成 Setup + Foundational
2. Foundational 完成后：
   - Developer A：User Story 1
   - Developer B：User Story 2
   - Developer C：User Story 3
3. Story 独立完成并集成

---

## 注意事项

- [P] 任务 = 不同文件，无依赖
- [Story] 标签将任务映射到特定 User Story，以便追溯
- 每个 User Story 应独立可完成且可测试
- 实现前验证测试失败
- 每个任务或逻辑组完成后提交
- 在任何检查点停止，以独立验证 Story
- 避免：任务描述模糊、同一文件冲突、破坏独立性的跨 Story 依赖