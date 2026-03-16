> **注意：** 本仓库包含 Anthropic 为 Claude 实现的 Skills。有关 Agent Skills 标准的信息，请参阅 [agentskills.io](http://agentskills.io)。

# Skills
Skills 是包含指令、脚本和资源的文件夹，Claude 可以动态加载这些内容以提升在专业任务上的表现。Skills 教会 Claude 如何以可重复的方式完成特定任务，无论是根据公司品牌指南创建文档、使用组织特定的 Workflow 分析数据，还是自动化个人任务。

欲了解更多信息，请查看：
- [什么是 Skills？](https://support.claude.com/en/articles/12512176-what-are-skills)
- [在 Claude 中使用 Skills](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [如何创建自定义 Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [使用 Agent Skills 为 Agent 装备应对真实世界的能力](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

# 关于本仓库

本仓库包含的 Skills 展示了 Claude 的 Skills 系统所能实现的功能。这些 Skills 涵盖了从创意应用（艺术、音乐、设计）到技术任务（测试 Web 应用、MCP 服务器生成），再到企业 Workflow（通信、品牌推广等）。

每个 Skill 都独立包含在自己的文件夹中，并带有一个 `SKILL.md` 文件，其中包含 Claude 使用的指令和元数据。浏览这些 Skills 可为您自己的 Skills 寻找灵感，或了解不同的模式和方法。

本仓库中的许多 Skills 都是开源的（Apache 2.0）。我们还在 [`skills/docx`](./skills/docx)、[`skills/pdf`](./skills/pdf)、[`skills/pptx`](./skills/pptx) 和 [`skills/xlsx`](./skills/xlsx) 子文件夹中包含了支持 [Claude 文档功能](https://www.anthropic.com/news/create-files) 的文档创建和编辑 Skills。这些 Skills 是源码可用的，而非开源，但我们希望与开发者分享这些内容，作为在生产级 AI 应用中实际使用的更复杂 Skills 的参考。

## 免责声明

**这些 Skills 仅供演示和教育目的。** 虽然 Claude 中可能提供某些功能，但您从 Claude 获得的实现和行为可能与这些 Skills 中展示的有所不同。这些 Skills 旨在说明模式和可能性。在依赖它们执行关键任务之前，请务必在您自己的环境中进行全面测试。

# Skill Sets
- [./skills](./skills): 创意与设计、开发与技术、企业与通信以及文档 Skills 的示例
- [./spec](./spec): Agent Skills 规范
- [./template](./template): Skill 模板

# 在 Claude Code、Claude.ai 和 API 中试用

## Claude Code
您可以通过在 Claude Code 中运行以下命令，将此仓库注册为 Claude Code Plugin marketplace：

```
/plugin marketplace add anthropics/skills
```

然后，安装特定的技能集：
1. 选择 `Browse and install plugins`
2. 选择 `anthropic-agent-skills`
3. 选择 `document-skills` 或 `example-skills`
4. 选择 `Install now`

或者，通过以下方式直接安装任一 Plugin：

```
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

安装插件后，只需提及即可使用该技能。例如，如果您从市场安装了 `document-skills` 插件，可以让 Claude Code 执行如下操作：“使用 PDF 技能从 `path/to/some-file.pdf` 提取表单字段”

## Claude.ai

这些示例技能已向 Claude.ai 的付费计划用户开放。

要使用本仓库中的任何技能或上传自定义技能，请按照 [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude#h_a4222fa77b) 中的说明操作。

## Claude API

您可以通过 Claude API 使用 Anthropic 的预构建技能，并上传自定义技能。更多信息请参阅 [Skills API Quickstart](https://docs.claude.com/en/api/skills-guide#creating-a-skill)。

# 创建基础技能

创建技能非常简单——只需一个包含 `SKILL.md` 文件的文件夹，该文件包含 YAML frontmatter 和指令。您可以将本仓库中的 **template-skill** 用作起点：

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Add your instructions here that Claude will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

Frontmatter 仅需两个字段：
- `name` - Skill 的唯一标识符（小写，空格用连字符代替）
- `description` - 关于 Skill 功能及其使用时机的完整描述

下方的 Markdown 内容包含 Claude 将遵循的指令、示例和指南。更多详情请参阅 [如何创建自定义 Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)。

# 合作伙伴 Skills

Skills 是教导 Claude 如何更好地使用特定软件的极佳方式。当我们看到合作伙伴提供的出色示例 Skills 时，可能会在此重点介绍部分内容：

- **Notion** - [Notion Skills for Claude](https://www.notion.so/notiondevs/Notion-Skills-for-Claude-28da4445d27180c7af1df7d8615723d0)