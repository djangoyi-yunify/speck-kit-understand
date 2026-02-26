# 技术详细设计

## 1. 接口定义

### 1.1 config.py

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMConfig:
    provider: str
    model: str
    base_url: Optional[str] = None

@dataclass
class FileConfig:
    source: str
    target: str
    last_sha: str = ""

@dataclass
class GroupConfig:
    name: str
    target_dir: str
    include_source: bool
    files: list[FileConfig]

@dataclass
class Config:
    source_repo: str
    source_branch: str
    llm: LLMConfig
    groups: list[GroupConfig]

def load_config(path: str) -> Config:
    """加载配置文件
    
    Args:
        path: 配置文件路径
        
    Returns:
        Config 对象
        
    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON 格式错误
        KeyError: 必要字段缺失
    """
    pass

def save_config(config: Config, path: str) -> None:
    """保存配置文件
    
    Args:
        config: Config 对象
        path: 保存路径
        
    Raises:
        PermissionError: 无写入权限
    """
    pass

def update_file_sha(config: Config, group_idx: int, file_idx: int, sha: str) -> Config:
    """更新文件的 last_sha
    
    Args:
        config: Config 对象
        group_idx: 分组索引
        file_idx: 文件索引
        sha: 新的 commit SHA
        
    Returns:
        更新后的 Config 对象（新对象，不修改原对象）
        
    Raises:
        IndexError: 索引越界
    """
    pass

def get_files_to_translate(config: Config) -> list[tuple[int, int, FileConfig]]:
    """获取所有文件的扁平列表
    
    Args:
        config: Config 对象
        
    Returns:
        [(group_idx, file_idx, FileConfig), ...]
    """
    pass
```

### 1.2 file_ops.py

```python
def ensure_dir(path: str) -> None:
    """确保目录存在，不存在则创建
    
    Args:
        path: 目录路径
    """
    pass

def write_file(path: str, content: str) -> None:
    """写入文件内容
    
    Args:
        path: 文件路径
        content: 文件内容
        
    Raises:
        FileNotFoundError: 父目录不存在
    """
    pass

def read_file(path: str) -> str:
    """读取文件内容
    
    Args:
        path: 文件路径
        
    Returns:
        文件内容
        
    Raises:
        FileNotFoundError: 文件不存在
    """
    pass

def get_source_filename(target_filename: str) -> str:
    """获取原文对照文件名
    
    Args:
        target_filename: 目标文件名，如 "README.md"
        
    Returns:
        原文文件名，如 "README.en.md"
        
    Example:
        >>> get_source_filename("README.md")
        'README.en.md'
        >>> get_source_filename("docs/guide.md")
        'docs/guide.en.md'
    """
    pass
```

### 1.3 github_api.py

```python
@dataclass
class GitHubFile:
    sha: str
    content: str

def get_file_sha(repo: str, branch: str, path: str, token: str) -> str:
    """获取文件最新 commit SHA
    
    Args:
        repo: 仓库名，格式 "owner/repo"
        branch: 分支名
        path: 文件路径
        token: GitHub token
        
    Returns:
        commit SHA
        
    Raises:
        FileNotFoundError: 文件不存在
        PermissionError: 无访问权限
    """
    pass

def download_file(repo: str, branch: str, path: str, token: str) -> GitHubFile:
    """下载文件内容
    
    Args:
        repo: 仓库名
        branch: 分支名
        path: 文件路径
        token: GitHub token
        
    Returns:
        GitHubFile 对象
        
    Raises:
        FileNotFoundError: 文件不存在
    """
    pass

def get_rate_limit(token: str) -> dict:
    """获取 API 限制信息
    
    Args:
        token: GitHub token
        
    Returns:
        {"limit": int, "remaining": int, "reset": int}
    """
    pass
```

### 1.4 translator.py

```python
from typing import Protocol

class LLMClient(Protocol):
    """LLM 客户端协议"""
    def translate(self, text: str, target_lang: str) -> str:
        ...

@dataclass
class MarkdownSection:
    type: str  # "code", "text"
    content: str
    language: Optional[str] = None  # 仅 code 类型

def get_llm_client(provider: str, model: str, base_url: Optional[str], api_key: str) -> LLMClient:
    """获取 LLM 客户端
    
    Args:
        provider: 提供商名称
        model: 模型名称
        base_url: 自定义 API 地址
        api_key: API 密钥
        
    Returns:
        LLM 客户端实例
        
    Raises:
        ValueError: 不支持的提供商
    """
    pass

def translate_text(client: LLMClient, text: str, target_lang: str = "zh") -> str:
    """翻译文本
    
    Args:
        client: LLM 客户端
        text: 待翻译文本
        target_lang: 目标语言
        
    Returns:
        翻译后的文本
    """
    pass

def split_markdown_sections(content: str) -> list[MarkdownSection]:
    """分割 Markdown 为区块
    
    Args:
        content: Markdown 内容
        
    Returns:
        区块列表
        
    Example:
        >>> sections = split_markdown_sections("# Title\\n```python\\ncode\\n```\\nText")
        >>> len(sections)
        3
        >>> sections[0].type
        'text'
        >>> sections[1].type
        'code'
    """
    pass

def merge_sections(sections: list[MarkdownSection]) -> str:
    """合并区块为 Markdown
    
    Args:
        sections: 区块列表
        
    Returns:
        合并后的 Markdown 内容
    """
    pass

def translate_markdown(client: LLMClient, content: str, target_lang: str = "zh") -> str:
    """翻译 Markdown（保留代码块不翻译）
    
    Args:
        client: LLM 客户端
        content: Markdown 内容
        target_lang: 目标语言
        
    Returns:
        翻译后的 Markdown
    """
    pass
```

### 1.5 main.py

```python
@dataclass
class FileUpdate:
    group_idx: int
    file_idx: int
    file_config: FileConfig
    new_sha: str

def check_updates(config: Config, github_token: str) -> list[FileUpdate]:
    """检测文件更新
    
    Args:
        config: 配置对象
        github_token: GitHub token
        
    Returns:
        有更新的文件列表
    """
    pass

def translate_files(
    config: Config,
    updates: list[FileUpdate],
    llm_client: LLMClient,
    github_token: str
) -> dict[str, bool]:
    """翻译文件
    
    Args:
        config: 配置对象
        updates: 待翻译文件列表
        llm_client: LLM 客户端
        github_token: GitHub token
        
    Returns:
        {"文件路径": 是否成功}
    """
    pass

def run_check_workflow() -> None:
    """检测工作流入口
    
    从环境变量读取配置，检测更新，触发翻译工作流
    """
    pass

def run_translate_workflow() -> None:
    """翻译工作流入口
    
    从环境变量读取参数，执行翻译
    """
    pass
```

## 2. 测试用例详细设计

### 2.1 test_config.py

```python
import pytest
import json
import tempfile
from scripts.config import load_config, save_config, update_file_sha, get_files_to_translate, Config

class TestLoadConfig:
    def test_load_valid_config(self, tmp_path):
        """测试加载有效配置"""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "source_repo": "owner/repo",
            "source_branch": "main",
            "llm": {"provider": "qingcloud", "model": "glm-5"},
            "groups": [{
                "name": "test",
                "target_dir": "output",
                "include_source": True,
                "files": [{"source": "README.md", "target": "README.md"}]
            }]
        }))
        
        config = load_config(str(config_file))
        assert config.source_repo == "owner/repo"
        assert len(config.groups) == 1

    def test_load_invalid_path(self):
        """测试加载不存在的文件"""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.json")

    def test_load_invalid_json(self, tmp_path):
        """测试加载无效 JSON"""
        config_file = tmp_path / "config.json"
        config_file.write_text("not valid json")
        
        with pytest.raises(json.JSONDecodeError):
            load_config(str(config_file))

    def test_load_missing_field(self, tmp_path):
        """测试缺少必要字段"""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"source_repo": "owner/repo"}))
        
        with pytest.raises(KeyError):
            load_config(str(config_file))

class TestSaveConfig:
    def test_save_config(self, tmp_path):
        """测试保存配置"""
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[]
        )
        
        config_file = tmp_path / "config.json"
        save_config(config, str(config_file))
        
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["source_repo"] == "owner/repo"

class TestUpdateFileSha:
    def test_update_file_sha(self):
        """测试更新 SHA"""
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[GroupConfig(
                name="test",
                target_dir="output",
                include_source=True,
                files=[FileConfig(source="README.md", target="README.md", last_sha="old")]
            )]
        )
        
        new_config = update_file_sha(config, 0, 0, "new_sha")
        assert new_config.groups[0].files[0].last_sha == "new_sha"
        assert config.groups[0].files[0].last_sha == "old"  # 原对象不变

    def test_update_invalid_index(self):
        """测试索引越界"""
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[]
        )
        
        with pytest.raises(IndexError):
            update_file_sha(config, 0, 0, "new_sha")

class TestGetFilesToTranslate:
    def test_get_files(self):
        """测试获取文件列表"""
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[
                GroupConfig(name="g1", target_dir="out1", include_source=True, 
                           files=[FileConfig(source="a.md", target="a.md")]),
                GroupConfig(name="g2", target_dir="out2", include_source=False,
                           files=[FileConfig(source="b.md", target="b.md")])
            ]
        )
        
        files = get_files_to_translate(config)
        assert len(files) == 2
        assert files[0] == (0, 0, FileConfig(source="a.md", target="a.md"))
```

### 2.2 test_file_ops.py

```python
import pytest
from scripts.file_ops import ensure_dir, write_file, read_file, get_source_filename

class TestEnsureDir:
    def test_create_dir(self, tmp_path):
        """测试创建新目录"""
        new_dir = tmp_path / "new_dir"
        ensure_dir(str(new_dir))
        assert new_dir.exists()

    def test_existing_dir(self, tmp_path):
        """测试已存在的目录"""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        ensure_dir(str(existing_dir))  # 不应报错
        assert existing_dir.exists()

class TestWriteFile:
    def test_write_file(self, tmp_path):
        """测试写入文件"""
        file_path = tmp_path / "test.txt"
        write_file(str(file_path), "hello")
        assert file_path.read_text() == "hello"

    def test_write_to_nonexistent_dir(self):
        """测试写入不存在的目录"""
        with pytest.raises(FileNotFoundError):
            write_file("/nonexistent/dir/file.txt", "content")

class TestReadFile:
    def test_read_file(self, tmp_path):
        """测试读取文件"""
        file_path = tmp_path / "test.txt"
        file_path.write_text("hello")
        assert read_file(str(file_path)) == "hello"

    def test_read_nonexistent_file(self):
        """测试读取不存在的文件"""
        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/file.txt")

class TestGetSourceFilename:
    def test_simple_filename(self):
        """测试简单文件名"""
        assert get_source_filename("README.md") == "README.en.md"

    def test_path_with_dir(self):
        """测试带路径的文件名"""
        assert get_source_filename("docs/guide.md") == "docs/guide.en.md"

    def test_nested_path(self):
        """测试嵌套路径"""
        assert get_source_filename("a/b/c/file.md") == "a/b/c/file.en.md"
```

### 2.3 test_github_api.py

```python
import pytest
from unittest.mock import patch, Mock
from scripts.github_api import get_file_sha, download_file, get_rate_limit

class TestGetFileSha:
    @patch('requests.get')
    def test_get_file_sha_success(self, mock_get):
        """测试成功获取 SHA"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sha": "abc123"}
        mock_get.return_value = mock_response
        
        sha = get_file_sha("owner/repo", "main", "README.md", "token")
        assert sha == "abc123"

    @patch('requests.get')
    def test_get_file_sha_not_found(self, mock_get):
        """测试文件不存在"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(FileNotFoundError):
            get_file_sha("owner/repo", "main", "nonexistent.md", "token")

class TestDownloadFile:
    @patch('requests.get')
    def test_download_success(self, mock_get):
        """测试成功下载文件"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sha": "abc123",
            "content": "IyBUaXRsZQo=",  # base64 "# Title\n"
            "encoding": "base64"
        }
        mock_get.return_value = mock_response
        
        result = download_file("owner/repo", "main", "README.md", "token")
        assert result.sha == "abc123"
        assert "# Title" in result.content

class TestGetRateLimit:
    @patch('requests.get')
    def test_get_rate_limit(self, mock_get):
        """测试获取限制"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rate": {"limit": 5000, "remaining": 4999, "reset": 1234567890}
        }
        mock_get.return_value = mock_response
        
        result = get_rate_limit("token")
        assert result["limit"] == 5000
```

### 2.4 test_translator.py

```python
import pytest
from unittest.mock import Mock
from scripts.translator import (
    split_markdown_sections, merge_sections, translate_markdown,
    MarkdownSection
)

class TestSplitMarkdownSections:
    def test_simple_text(self):
        """测试纯文本"""
        sections = split_markdown_sections("Hello World")
        assert len(sections) == 1
        assert sections[0].type == "text"
        assert sections[0].content == "Hello World"

    def test_code_block(self):
        """测试代码块"""
        content = "# Title\n```python\nprint('hello')\n```\nText after"
        sections = split_markdown_sections(content)
        
        assert len(sections) == 3
        assert sections[0].type == "text"
        assert sections[1].type == "code"
        assert sections[1].language == "python"
        assert sections[2].type == "text"

    def test_multiple_code_blocks(self):
        """测试多个代码块"""
        content = "Text\n```\ncode1\n```\nMore text\n```\ncode2\n```"
        sections = split_markdown_sections(content)
        assert len(sections) == 4

class TestMergeSections:
    def test_merge_text(self):
        """测试合并文本"""
        sections = [MarkdownSection(type="text", content="Hello")]
        assert merge_sections(sections) == "Hello"

    def test_merge_code(self):
        """测试合并代码块"""
        sections = [
            MarkdownSection(type="text", content="Before\n"),
            MarkdownSection(type="code", content="code", language="python"),
            MarkdownSection(type="text", content="\nAfter")
        ]
        result = merge_sections(sections)
        assert "```python" in result
        assert "code" in result
        assert "```" in result

class TestTranslateMarkdown:
    def test_translate_preserves_code(self):
        """测试代码块不被翻译"""
        mock_client = Mock()
        mock_client.translate.side_effect = lambda text, lang: "翻译后的文本"
        
        content = "Hello\n```python\ncode\n```\nWorld"
        result = translate_markdown(mock_client, content)
        
        # 代码块应保留
        assert "```python" in result
        assert "code" in result
```

## 3. 依赖库

### requirements.txt

```
requests>=2.28.0
openai>=1.0.0
anthropic>=0.18.0
pytest>=7.0.0
pytest-cov>=4.0.0
```

### pytest.ini

```ini
[pytest]
testpaths = scripts/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

## 4. 项目初始化步骤

```bash
# 1. 创建目录结构
mkdir -p scripts/tests .github/workflows

# 2. 创建 __init__.py
touch scripts/__init__.py scripts/tests/__init__.py

# 3. 创建配置文件
touch translation-config.json requirements.txt pytest.ini

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行测试
pytest

# 6. 开始 TDD 开发
# 按顺序实现每个模块
```

## 5. 环境变量

```bash
# GitHub Token
GITHUB_TOKEN=ghp_xxx

# LLM API Key（根据使用的提供商配置）
QINGCLOUD_API_KEY=xxx
OPENAI_API_KEY=xxx
DEEPSEEK_API_KEY=xxx
# ...
```
