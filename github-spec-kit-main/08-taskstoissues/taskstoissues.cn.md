---
description: 基于现有的设计产物，将现有任务转换为针对该功能的可执行、按依赖关系排序的 GitHub issues。
tools: ['github/github-mcp-server/issue_write']
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前，你 **必须** 考虑用户输入（如果非空）。

## 大纲

1. 从 repo 根目录运行 `{SCRIPT}` 并解析 FEATURE_DIR 和 AVAILABLE_DOCS 列表。所有路径必须是绝对路径。对于参数中的单引号（如 "I'm Groot"），请使用转义语法：例如 'I'\''m Groot'（或者如果可能，使用双引号："I'm Groot"）。
1. 从执行的脚本中，提取 **tasks** 的路径。
1. 通过运行以下命令获取 Git remote：

```bash
git config --get remote.origin.url
```

> [!CAUTION]
> 仅当 remote 为 GitHub URL 时，才继续执行后续步骤

1. 对于列表中的每个任务，使用 GitHub MCP server 在代表 Git remote 的 repository 中创建一个新的 issue。

> [!CAUTION]
> 严禁在与 remote URL 不匹配的 repository 中创建 issue