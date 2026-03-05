# 快速开始指南

## 明天开始工作的步骤

### 第一步：初始化项目结构

```bash
# 在 arch-repo 目录下执行
mkdir -p scripts/tests .github/workflows
touch scripts/__init__.py scripts/tests/__init__.py
touch requirements.txt pytest.ini translation-config.json
```

### 第二步：创建依赖文件

**requirements.txt**
```
requests>=2.28.0
pytest>=7.0.0
pytest-cov>=4.0.0
```

**pytest.ini**
```ini
[pytest]
testpaths = scripts/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

**check_updates.json**
```json
{
  "config_paths": [
    "translation-config.json"
  ]
}
```

**translation-config.json**
```json
{
  "source_repo": "github/spec-kit",
  "source_branch": "main",
  "llm": {
    "provider": "qingcloud",
    "model": "glm-5"
  },
  "groups": [
    {
      "name": "core",
      "target_dir": "translated/zh/core",
      "include_source": true,
      "files": [
        {
          "source": "README.md",
          "target": "README.md"
        }
      ]
    }
  ]
}
```

### 第三步：安装依赖

```bash
pip install -r requirements.txt
```

### 第四步：开始 TDD 开发

按照以下顺序，**每个函数**都遵循：

```
写测试 → 运行测试（失败）→ 写代码 → 运行测试（通过）→ 下一个函数
```

#### 4.1 第一个函数：`load_config`

```bash
# 1. 创建测试文件
touch scripts/config.py scripts/tests/test_config.py

# 2. 在 test_config.py 中写测试
# 3. 运行测试（应失败）
pytest scripts/tests/test_config.py::TestLoadConfig::test_load_valid_config -v

# 4. 在 config.py 中实现函数
# 5. 运行测试（应通过）
pytest scripts/tests/test_config.py::TestLoadConfig::test_load_valid_config -v
```

#### 4.2 实现顺序表

| 序号 | 模块 | 函数 | 测试文件 |
|------|------|------|----------|
| 1 | config.py | load_config | test_config.py |
| 2 | config.py | save_config | test_config.py |
| 3 | config.py | get_files_to_translate | test_config.py |
| 4 | sha_tracker.py | get_sha | test_sha_tracker.py |
| 5 | sha_tracker.py | save_sha | test_sha_tracker.py |
| 6 | sha_tracker.py | load_shas | test_sha_tracker.py |
| 7 | sha_tracker.py | save_all_shas | test_sha_tracker.py |
| 8 | file_ops.py | ensure_dir | test_file_ops.py |
| 9 | file_ops.py | write_file | test_file_ops.py |
| 10 | file_ops.py | read_file | test_file_ops.py |
| 11 | github_api.py | get_file_sha | test_github_api.py |
| 12 | github_api.py | download_file | test_github_api.py |
| 13 | github_api.py | get_rate_limit | test_github_api.py |
| 14 | translator.py | split_markdown_sections | test_translator.py |
| 15 | translator.py | merge_sections | test_translator.py |
| 16 | translator.py | get_llm_client | test_translator.py |
| 17 | translator.py | translate_text | test_translator.py |
| 18 | translator.py | translate_markdown | test_translator.py |
| 19 | main.py | check_updates | test_main.py |
| 20 | main.py | translate_files | test_main.py |
| 21 | main.py | run_check_workflow | test_main.py |
| 22 | main.py | run_translate_workflow | test_main.py |

### 第五步：创建 GitHub Actions

完成所有 Python 模块后，创建工作流文件：
- `.github/workflows/check-updates.yml`
- `.github/workflows/translate-docs.yml`

---

## 文档索引

| 文档 | 内容 |
|------|------|
| `prd.md` | 产品需求文档 |
| `implementation-plan.md` | 实现计划 |
| `technical-design.md` | 技术详细设计（接口定义、测试用例） |
| `quick-start.md` | 本文档 |

## 常用命令

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest scripts/tests/test_config.py -v

# 运行单个测试用例
pytest scripts/tests/test_config.py::TestLoadConfig::test_load_valid_config -v

# 查看测试覆盖率
pytest --cov=scripts --cov-report=html
```

## 检查清单

每天开始工作前：

- [ ] 确认当前要实现的函数
- [ ] 先写测试
- [ ] 运行测试确认失败
- [ ] 实现函数
- [ ] 运行测试确认通过
- [ ] 提交代码（可选）
