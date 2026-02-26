# GitHub Action 文档翻译系统 - PRD

## 项目目标

将 GitHub 仓库（如 https://github.com/github/spec-kit）中的文档自动翻译成中文，并通过 GitHub Action 实现自动化管理。

## 功能需求

### 1. 双工作流设计

#### 1.1 检测更新工作流 (`check-updates.yml`)

- **触发条件**
  - 定时触发：每天自动检测
  - 手动触发：`workflow_dispatch`

- **功能逻辑**
  1. 读取全局配置文件 `translation-config.json`
  2. 遍历每个分组中的每个文件
  3. 获取该文件在源仓库的最新 commit SHA
  4. 对比配置中记录的 `last_sha`
  5. 有变化 → 加入待翻译列表
  6. 如果有待翻译文件，触发 `translate-docs.yml` 工作流
  7. 更新配置文件中的 `last_sha`

#### 1.2 翻译工作流 (`translate-docs.yml`)

- **触发条件**
  - 工作流调用：`workflow_call`（被 `check-updates.yml` 调用）
  - 手动触发：`workflow_dispatch`（独立测试）

- **输入参数**
  - `files`: 待翻译文件列表
  - `config`: 配置信息

- **功能逻辑**
  1. 接收配置参数和待翻译文件列表
  2. 下载变更的源文件
  3. 调用 LLM API 进行翻译
  4. 写入目标路径
  5. 如配置 `include_source: true`，同时保存原文对照文件
  6. 提交更改到仓库

### 2. 分组翻译

- 支持将文档分组管理
- 每个分组可指定独立的目标目录
- 每个分组可选择是否包含原文对照

### 3. 多 LLM 提供商支持

| Provider | 说明 | 需要的 Secret |
|----------|------|---------------|
| `qingcloud` | 青云 AI（默认） | `QINGCLOUD_API_KEY` |
| `openai` | OpenAI | `OPENAI_API_KEY` |
| `anthropic` | Anthropic Claude | `ANTHROPIC_API_KEY` |
| `deepseek` | DeepSeek | `DEEPSEEK_API_KEY` |
| `zhipu` | 智谱 | `ZHIPU_API_KEY` |
| `openrouter` | OpenRouter | `OPENROUTER_API_KEY` |
| `ollama` | 本地 Ollama | 无需 Secret |

### 4. 文件级别增量更新

- 只翻译发生变更的文件
- 通过 commit SHA 追踪文件变化
- 减少不必要的 API 调用

## 配置文件设计

### 文件位置

```
.github/
└── workflows/
    ├── check-updates.yml      # 检测更新工作流
    └── translate-docs.yml     # 翻译工作流
scripts/
└── translate.py               # 翻译脚本
translation-config.json        # 全局配置文件
```

### 配置文件格式 (`translation-config.json`)

```json
{
  "source_repo": "github/spec-kit",
  "source_branch": "main",
  "llm": {
    "provider": "qingcloud",
    "model": "glm-5",
    "base_url": null
  },
  "groups": [
    {
      "name": "core",
      "target_dir": "translated/zh/core",
      "include_source": true,
      "files": [
        {
          "source": "README.md",
          "target": "README.md",
          "last_sha": ""
        },
        {
          "source": "spec-driven.md",
          "target": "spec-driven.md",
          "last_sha": ""
        }
      ]
    },
    {
      "name": "guides",
      "target_dir": "translated/zh/docs",
      "include_source": true,
      "files": [
        {
          "source": "docs/upgrade.md",
          "target": "upgrade.md",
          "last_sha": ""
        }
      ]
    }
  ]
}
```

### 配置字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `source_repo` | string | 源仓库地址（owner/repo 格式） |
| `source_branch` | string | 源仓库分支 |
| `llm.provider` | string | LLM 提供商名称 |
| `llm.model` | string | 模型名称 |
| `llm.base_url` | string? | 可选，自定义 API 地址（用于代理/私有部署） |
| `groups` | array | 分组列表 |
| `groups[].name` | string | 分组名称 |
| `groups[].target_dir` | string | 该组翻译输出目录 |
| `groups[].include_source` | boolean | 是否包含原文对照文件（`.en.md` 后缀） |
| `groups[].files` | array | 文件列表 |
| `groups[].files[].source` | string | 源文件路径（相对源仓库根目录） |
| `groups[].files[].target` | string | 目标文件名 |
| `groups[].files[].last_sha` | string | 上次翻译时的 SHA（自动维护） |

### 输出目录结构示例

```
translated/zh/
├── core/
│   ├── README.md           # 翻译版
│   ├── README.en.md        # 原文对照
│   ├── spec-driven.md
│   └── spec-driven.en.md
└── docs/
    ├── upgrade.md
    └── upgrade.en.md
```

## Secrets 配置

需要根据选择的 LLM 提供商配置对应的 API Key：

```
QINGCLOUD_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
ANTHROPIC_API_KEY=your_api_key_here
DEEPSEEK_API_KEY=your_api_key_here
ZHIPU_API_KEY=your_api_key_here
OPENROUTER_API_KEY=your_api_key_here
```

## 使用示例

### 示例 1：使用青云 AI（默认）

```json
{
  "llm": {
    "provider": "qingcloud",
    "model": "glm-5"
  }
}
```

### 示例 2：使用 DeepSeek

```json
{
  "llm": {
    "provider": "deepseek",
    "model": "deepseek-chat"
  }
}
```

### 示例 3：使用 OpenAI 代理

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "base_url": "https://your-proxy.com/v1"
  }
}
```

### 示例 4：使用本地 Ollama

```json
{
  "llm": {
    "provider": "ollama",
    "model": "qwen2:7b",
    "base_url": "http://localhost:11434"
  }
}
```

## 非功能需求

1. **性能**：只翻译变更文件，减少 API 调用
2. **可靠性**：支持重试机制，处理 API 限流
3. **可维护性**：配置驱动，无需修改代码即可调整翻译目标
4. **兼容性**：保留 Markdown 格式，不翻译代码块

## 实现清单

| 文件 | 说明 |
|------|------|
| `.github/workflows/check-updates.yml` | 检测更新工作流 |
| `.github/workflows/translate-docs.yml` | 翻译工作流 |
| `scripts/translate.py` | 翻译脚本（多 LLM 支持） |
| `translation-config.json` | 全局配置文件 |
