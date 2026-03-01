# [PROJECT_NAME] 章程
<!-- 示例：Spec Constitution, TaskFlow Constitution 等 -->

## 核心原则

### [PRINCIPLE_1_NAME]
<!-- 示例：I. Library-First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- 示例：每个功能都始于一个独立的 library；Libraries 必须是自包含的、可独立测试的、有文档记录的；必须有明确的目的——不存在仅用于组织架构的 libraries -->

### [PRINCIPLE_2_NAME]
<!-- 示例：II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- 示例：每个 library 都通过 CLI 暴露功能；文本输入/输出协议：stdin/args → stdout, errors → stderr；支持 JSON + 人类可读格式 -->

### [PRINCIPLE_3_NAME]
<!-- 示例：III. Test-First (不可妥协) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- 示例：强制执行 TDD：编写测试 → 用户批准 → 测试失败 → 然后实现；严格遵循 Red-Green-Refactor 循环 -->

### [PRINCIPLE_4_NAME]
<!-- 示例：IV. Integration Testing -->
[PRINCIPLE_4_DESCRIPTION]
<!-- 示例：需要集成测试的重点领域：新的 library 契约测试、契约变更、服务间通信、共享 schemas -->

### [PRINCIPLE_5_NAME]
<!-- 示例：V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
[PRINCIPLE_5_DESCRIPTION]
<!-- 示例：文本 I/O 确保可调试性；需要结构化日志；或：MAJOR.MINOR.BUILD 格式；或：起步要简单，遵循 YAGNI 原则 -->

## [SECTION_2_NAME]
<!-- 示例：Additional Constraints, Security Requirements, Performance Standards 等 -->

[SECTION_2_CONTENT]
<!-- 示例：技术栈要求、合规标准、部署策略等 -->

## [SECTION_3_NAME]
<!-- 示例：Development Workflow, Review Process, Quality Gates 等 -->

[SECTION_3_CONTENT]
<!-- 示例：代码审查要求、测试关卡、部署审批流程等 -->

## 治理
<!-- 示例：章程优于所有其他实践；修正案需要文档记录、批准、迁移计划 -->

[GOVERNANCE_RULES]
<!-- 示例：所有 PRs/reviews 必须验证合规性；复杂性必须有正当理由；使用 [GUIDANCE_FILE] 获取运行时开发指导 -->

**版本**：[CONSTITUTION_VERSION] | **批准日期**：[RATIFICATION_DATE] | **最后修订**：[LAST_AMENDED_DATE]
<!-- 示例：版本：2.1.1 | 批准日期：2025-06-13 | 最后修订：2025-07-16 -->