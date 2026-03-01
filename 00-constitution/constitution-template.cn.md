# [PROJECT_NAME] 章程
<!-- 示例：Spec 章程、TaskFlow 章程等 -->

## 核心原则

### [PRINCIPLE_1_NAME]
<!-- 示例：I. Library-First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- 示例：每个功能都从独立的 Library 开始；Library 必须自包含、可独立测试、有文档记录；必须有明确目的 - 不允许仅用于组织架构的 Library -->

### [PRINCIPLE_2_NAME]
<!-- 示例：II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- 示例：每个 Library 通过 CLI 暴露功能；文本输入/输出协议：stdin/args → stdout，errors → stderr；支持 JSON + 人类可读格式 -->

### [PRINCIPLE_3_NAME]
<!-- 示例：III. Test-First (不可妥协) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- 示例：强制 TDD：编写测试 → 用户批准 → 测试失败 → 然后实现；严格执行 Red-Green-Refactor 循环 -->

### [PRINCIPLE_4_NAME]
<!-- 示例：IV. Integration Testing -->
[PRINCIPLE_4_DESCRIPTION]
<!-- 示例：需要 Integration Testing 的重点领域：新 Library 的 contract tests、Contract changes、Inter-service communication、Shared schemas -->

### [PRINCIPLE_5_NAME]
<!-- 示例：V. Observability、VI. Versioning & Breaking Changes、VII. Simplicity -->
[PRINCIPLE_5_DESCRIPTION]
<!-- 示例：文本 I/O 确保可调试性；强制要求 Structured logging；或：MAJOR.MINOR.BUILD 格式；或：Start simple，YAGNI 原则 -->

## [SECTION_2_NAME]
<!-- 示例：Additional Constraints、Security Requirements、Performance Standards 等 -->

[SECTION_2_CONTENT]
<!-- 示例：Technology stack 要求、合规标准、部署策略等 -->

## [SECTION_3_NAME]
<!-- 示例：Development Workflow、Review Process、Quality Gates 等 -->

[SECTION_3_CONTENT]
<!-- 示例：Code review 要求、Testing gates、部署批准流程等 -->

## Governance
<!-- 示例：Constitution 高于所有其他实践；修正案需要文档记录、批准、迁移计划 -->

[GOVERNANCE_RULES]
<!-- 示例：所有 PRs/reviews 必须验证合规性；复杂性必须有正当理由；使用 [GUIDANCE_FILE] 作为运行时开发指导 -->

**版本**: [CONSTITUTION_VERSION] | **批准日期**: [RATIFICATION_DATE] | **最后修订**: [LAST_AMENDED_DATE]
<!-- 示例：版本：2.1.1 | 批准日期：2025-06-13 | 最后修订：2025-07-16 -->