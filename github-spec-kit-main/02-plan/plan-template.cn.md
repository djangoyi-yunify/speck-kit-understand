# 实施计划：[FEATURE]

**分支**：`[###-feature-name]` | **日期**：[DATE] | **规范**：[link]
**输入**：来自 `/specs/[###-feature-name]/spec.md` 的功能规范

**注意**：此模板由 `/speckit.plan` 命令填充。有关执行 Workflow，请参阅 `.specify/templates/plan-template.md`。

## 概述

[从功能规范中提取：主要需求 + 研究得出的技术路径]

## 技术背景

<!--
  需要操作：将本节内容替换为项目的技术细节。此处的结构仅供参考，旨在指导迭代过程。
-->

**语言/版本**：[例如：Python 3.11, Swift 5.9, Rust 1.75 或 待明确]  
**主要依赖**：[例如：FastAPI, UIKit, LLVM 或 待明确]  
**存储**：[如适用，例如：PostgreSQL, CoreData, files 或 N/A]  
**测试**：[例如：pytest, XCTest, cargo test 或 待明确]  
**目标平台**：[例如：Linux server, iOS 15+, WASM 或 待明确]
**项目类型**：[例如：library/cli/web-service/mobile-app/compiler/desktop-app 或 待明确]  
**性能目标**：[领域特定，例如：1000 req/s, 10k lines/sec, 60 fps 或 待明确]  
**约束条件**：[领域特定，例如：<200ms p95, <100MB memory, offline-capable 或 待明确]  
**规模/范围**：[领域特定，例如：10k users, 1M LOC, 50 screens 或 待明确]

## 规则检查

*关卡：必须在第 0 阶段研究前通过。在第 1 阶段设计后重新检查。*

[基于宪章文件确定的关卡]

## 项目结构

### 文档（此功能）```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```### 源代码（仓库根目录）
<!--
  需采取行动：将下方的占位符树替换为此功能的具体布局。
  删除未使用的选项，并使用真实路径（例如 apps/admin, packages/something）扩展所选结构。
  交付的计划中不得包含选项标签。
-->```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```**结构决策**：[记录选定的结构并引用上文捕获的真实目录]

## 复杂度跟踪

> **仅在 Constitution Check 存在违规且必须说明理由时填写**

| 违规项 | 为何需要 | 拒绝更简单替代方案的原因 |
|-----------|------------|-------------------------------------|
| [如：第4个项目] | [当前需求] | [为何3个项目不足] |
| [如：Repository 模式] | [具体问题] | [为何直接访问数据库不足] |