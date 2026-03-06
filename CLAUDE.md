# tech-research-101 - GitHub Action 文档翻译系统

自动化将 GitHub 仓库中的 Markdown 文档翻译成中文的项目，通过 GitHub Action 实现定时检测更新和自动翻译。

## 项目结构

```
tech-research-101/
├── .github/workflows/          # GitHub Actions 工作流
│   ├── check-updates.yml      # 每日检测文件更新
│   ├── translate-docs.yml      # 翻译工作流
│   └── force-translate.yml     # 手动强制翻译工作流
├── scripts/                    # 核心 Python 模块
│   ├── main.py                # 工作流入口函数
│   ├── config.py              # 配置管理
│   ├── github_api.py          # GitHub API 集成
│   ├── translator.py          # LLM 翻译客户端
│   ├── sha_tracker.py         # SHA 状态追踪
│   ├── file_ops.py            # 文件操作工具
│   ├── prompts/
│   │   └── translate_system.txt  # 翻译系统提示词
│   └── tests/                 # 单元测试
├── demo.json                   # 示例翻译配置
├── check_updates.json          # 多配置文件路径列表
├── requirements.txt            # Python 依赖
├── docs/                       # 前端文档查看器
│   ├── index.html              # 文档对比查看器页面
│   ├── app.js                  # 前端逻辑（支持 Markdown 渲染）
│   ├── styles.css              # 样式
│   └── translated/             # 翻译输出目录
│       ├── djangoyi-yunify-tech-research-101-main/  # demo.json 翻译结果
│       ├── github-spec-kit-main/       # github/spec-kit 翻译结果
│       └── anthropics-skills-main/     # anthropics/skills 翻译结果
```

## 核心功能

### 1. 三工作流设计

- **check-updates.yml**: 每日定时检测源仓库文件 SHA 变化，触发翻译
- **translate-docs.yml**: 下载文件 → 分离代码块 → 翻译文本 → 保存结果
- **force-translate.yml**: 手动强制翻译指定配置文件中的所有源文件（忽略 SHA 检查）

### 2. 增量更新

通过 SHA 追踪机制（`sha_tracker.ini`），只翻译发生变化的文件，避免重复翻译。

### 3. Git 冲突处理策略

工作流采用以下策略处理并发推送冲突：

```
翻译前: git pull --rebase origin main  # 获取最新代码，减少冲突
翻译...
git commit
git fetch origin
git rebase origin/main                  # 将本地提交变基到远程最新之上
git push origin main
```

### 4. 文档查看器

在 `docs/` 目录下提供了文档对比查看器，支持：
- 选择仓库和文档进行对比
- Markdown 渲染
- 原文与译文并排显示

使用方式：部署 `docs/` 目录到 GitHub Pages，然后在浏览器中打开 `index.html`。

### 5. 多 LLM 提供商支持

- QingCloud (青云AI) ✅
- OpenAI ✅
- Anthropic Claude ✅
- DeepSeek (计划中)
- Zhipu 智谱 (计划中)
- OpenRouter (计划中)
- Ollama 本地 (计划中)

## 配置文件格式

```json
{
  "source_repo": "owner/repo",
  "source_branch": "main",
  "llm": {
    "provider": "qingcloud",
    "model": "GLM-5",
    "base_url": "https://api.example.com/v1"
  },
  "groups": [{
    "name": "core",
    "target_dir": "translated/zh",
    "include_source": true,
    "files": [
      {"source": "README.md", "target": "README.cn.md"}
    ]
  }]
}
```

## 开发指南

### 运行测试

```bash
pytest
```

### 本地测试翻译

```python
from scripts.config import load_config
from scripts.translator import get_llm_client, translate_markdown

config = load_config("demo.json")
client = get_llm_client(
    provider=config.llm.provider,
    model=config.llm.model,
    base_url=config.llm.base_url,
    api_key="your-api-key"
)
result = translate_markdown(client, "# Hello World\n\nThis is a test.")
```

### 添加新的 LLM 提供商

1. 在 `scripts/translator.py` 中创建新的客户端类
2. 实现 `LLMClient` Protocol 的 `translate(text: str) -> str` 方法
3. 在 `get_llm_client()` 函数中注册新提供商

## 翻译策略

- 代码块（```）内容保持原样不翻译
- 技术术语（API、SDK、CLI 等）保持英文
- Markdown 格式标记保持不变
- 输出符合中文表达习惯的流畅译文

## GitHub Secrets 配置

- `PAT_TOKEN`: GitHub Personal Access Token（用于 API 访问）
- `QINGCLOUD_API_KEY`: 青云 AI API Key
- `OPENAI_API_KEY`: OpenAI API Key
- `ANTHROPIC_API_KEY`: Anthropic API Key

## 手动触发翻译

使用 `gh` 命令行工具手动触发强制翻译：

```bash
# 翻译 demo.json 配置的文件（测试用）
gh workflow run force-translate.yml -f config_path=demo.json

# 查看工作流运行状态
gh run list --workflow=force-translate.yml --limit 3
```

或在 GitHub 仓库页面：Actions → Force Translate → Run workflow → 输入配置文件路径