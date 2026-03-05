# [PROJECT_NAME] 章程
<!-- 示例：Spec Constitution, TaskFlow Constitution 等 -->

## 核心原则

### [PRINCIPLE_1_NAME]
<!-- 示例：I. Library-First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- 示例：每个功能都作为独立的 Library 启动；Library 必须自包含、可独立测试、有文档记录；需要明确的目的——不存在仅用于组织管理的 Library -->

### [PRINCIPLE_2_NAME]
<!-- 示例：II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- 示例：每个 Library 通过 CLI 暴露功能；文本输入/输出协议：stdin/args → stdout，errors → stderr；支持 JSON + 人类可读格式 -->

### [PRINCIPLE_3_NAME]
<!-- 示例：III. Test-First (不可协商) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- 示例：强制 TDD：编写测试 → 用户批准 → 测试失败 → 然后实现；严格执行 Red-Green-Refactor 循环 -->

### [PRINCIPLE_4_NAME]
<!-- 示例：IV. Integration Testing -->
[PRINCIPLE_4_DESCRIPTION]
<!-- 示例：需要集成测试的重点领域：新 Library 契约测试、契约变更、服务间通信、共享 Schema -->

### [PRINCIPLE_5_NAME]
<!-- 示例：V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
[PRINCIPLE_5_DESCRIPTION]
<!-- 示例：文本 I/O 确保可调试性；要求结构化日志；或：MAJOR.MINOR.BUILD 格式；或：从简单开始，遵循 YAGNI 原则 -->

## [SECTION_2_NAME]
<!-- 示例：附加约束、安全要求、性能标准等 -->

[SECTION_2_CONTENT]
<!-- 示例：技术栈要求、合规标准、部署策略等 -->

## [SECTION_3_NAME]
<!-- 示例：开发 Workflow、评审流程、质量门禁等 -->

[SECTION_3_CONTENT]
<!-- 示例：代码审查要求、测试门禁、部署审批流程等 -->

## 治理
<!-- 示例：本章程凌驾于所有其他实践之上；修订需要文档记录、批准和迁移计划 -->

[GOVERNANCE_RULES]
<!-- 示例：所有 PR/Review 必须验证合规性；复杂性必须有正当理由；使用 [GUIDANCE_FILE] 获取运行时开发指导 -->

**版本**：[CONSTITUTION_VERSION] | **批准日期**：[RATIFICATION_DATE] | **最后修订日期**：[LAST_AMENDED_DATE]
<!-- 示例：版本：2.1.1 | 批准日期：2025-06-13 | 最后修订日期：2025-07-16 -->