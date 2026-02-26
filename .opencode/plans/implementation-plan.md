# 实现计划 - TDD 方式

## 开发原则

1. 采用测试驱动开发（TDD）
2. 大功能拆分成多个可测试的函数/过程
3. 一次实现一个函数或过程

## 模块划分

### 模块 1：配置管理 (`config.py`)

| 函数 | 功能 | 测试用例 |
|------|------|----------|
| `load_config(path)` | 加载配置文件 | 有效配置、无效路径、格式错误 |
| `save_config(config, path)` | 保存配置文件 | 保存成功、路径不存在 |
| `update_file_sha(config, group_idx, file_idx, sha)` | 更新文件 SHA | 更新成功、索引越界 |
| `get_files_to_translate(config)` | 获取所有文件列表 | 返回正确列表 |

### 模块 2：GitHub API (`github_api.py`)

| 函数 | 功能 | 测试用例 |
|------|------|----------|
| `get_file_sha(repo, branch, path, token)` | 获取文件最新 SHA | 成功获取、文件不存在、权限错误 |
| `download_file(repo, branch, path, token)` | 下载文件内容 | 成功下载、文件不存在 |
| `get_rate_limit(token)` | 获取 API 限制 | 成功获取 |

### 模块 3：LLM 翻译 (`translator.py`)

| 函数 | 功能 | 测试用例 |
|------|------|----------|
| `get_llm_client(provider, model, base_url, api_key)` | 获取 LLM 客户端 | 各提供商初始化 |
| `translate_text(client, text, target_lang)` | 翻译文本 | 简单文本、Markdown、代码块 |
| `split_markdown_sections(content)` | 分割 Markdown 区块 | 标题、代码块、普通段落 |
| `merge_sections(sections)` | 合并翻译后的区块 | 正确合并 |
| `translate_markdown(client, content)` | 翻译 Markdown（保留代码块） | 代码块不翻译、表格保留 |

### 模块 4：文件操作 (`file_ops.py`)

| 函数 | 功能 | 测试用例 |
|------|------|----------|
| `ensure_dir(path)` | 确保目录存在 | 创建成功、已存在 |
| `write_file(path, content)` | 写入文件 | 成功写入、目录不存在 |
| `read_file(path)` | 读取文件 | 成功读取、文件不存在 |
| `get_source_filename(target_filename)` | 获取原文对照文件名 | `README.md` → `README.en.md` |

### 模块 5：主流程 (`main.py`)

| 函数 | 功能 | 测试用例 |
|------|------|----------|
| `check_updates(config, github_token)` | 检测更新 | 有更新、无更新、API 错误 |
| `translate_files(config, files, llm_client, github_token)` | 翻译文件 | 成功翻译、部分失败 |
| `run_check_workflow()` | 检测工作流入口 | 集成测试 |
| `run_translate_workflow()` | 翻译工作流入口 | 集成测试 |

## 实现顺序

### 第一阶段：基础模块

```
1. config.py
   ├── test_load_config()
   ├── load_config()
   ├── test_save_config()
   ├── save_config()
   ├── test_update_file_sha()
   ├── update_file_sha()
   ├── test_get_files_to_translate()
   └── get_files_to_translate()

2. file_ops.py
   ├── test_ensure_dir()
   ├── ensure_dir()
   ├── test_write_file()
   ├── write_file()
   ├── test_read_file()
   ├── read_file()
   ├── test_get_source_filename()
   └── get_source_filename()
```

### 第二阶段：外部接口

```
3. github_api.py
   ├── test_get_file_sha()
   ├── get_file_sha()
   ├── test_download_file()
   ├── download_file()
   ├── test_get_rate_limit()
   └── get_rate_limit()

4. translator.py
   ├── test_split_markdown_sections()
   ├── split_markdown_sections()
   ├── test_merge_sections()
   ├── merge_sections()
   ├── test_get_llm_client()
   ├── get_llm_client()
   ├── test_translate_text()
   ├── translate_text()
   ├── test_translate_markdown()
   └── translate_markdown()
```

### 第三阶段：业务流程

```
5. main.py
   ├── test_check_updates()
   ├── check_updates()
   ├── test_translate_files()
   ├── translate_files()
   ├── test_run_check_workflow()
   ├── run_check_workflow()
   ├── test_run_translate_workflow()
   └── run_translate_workflow()
```

### 第四阶段：GitHub Action

```
6. check-updates.yml
7. translate-docs.yml
```

## 文件结构

```
scripts/
├── __init__.py
├── config.py
├── file_ops.py
├── github_api.py
├── translator.py
├── main.py
└── tests/
    ├── __init__.py
    ├── test_config.py
    ├── test_file_ops.py
    ├── test_github_api.py
    ├── test_translator.py
    └── test_main.py

.github/
└── workflows/
    ├── check-updates.yml
    └── translate-docs.yml

translation-config.json
requirements.txt
pytest.ini
```

## 测试数据

准备 mock 数据用于测试：
- 示例配置文件
- 示例 Markdown 文件（含代码块、表格）
- Mock GitHub API 响应
- Mock LLM API 响应
