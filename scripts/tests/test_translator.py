import pytest
from unittest.mock import Mock
from scripts.translator import (
    split_markdown_sections, merge_sections, translate_markdown,
    MarkdownSection, get_llm_client
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
        assert sections[1].content == "print('hello')"
        assert sections[2].type == "text"

    def test_multiple_code_blocks(self):
        """测试多个代码块"""
        content = "Text\n```\ncode1\n```\nMore text\n```\ncode2\n```"
        sections = split_markdown_sections(content)
        assert len(sections) == 4
        assert sections[0].type == "text"
        assert sections[1].type == "code"
        assert sections[2].type == "text"
        assert sections[3].type == "code"

    def test_code_block_no_language(self):
        """测试无语言代码块"""
        content = "```\ncode\n```"
        sections = split_markdown_sections(content)
        assert len(sections) == 1
        assert sections[0].type == "code"
        assert sections[0].language is None

    def test_empty_content(self):
        """测试空内容"""
        sections = split_markdown_sections("")
        assert len(sections) == 1
        assert sections[0].type == "text"
        assert sections[0].content == ""

    def test_only_code_block(self):
        """测试只有代码块"""
        content = "```javascript\nfunction() {}\n```"
        sections = split_markdown_sections(content)
        assert len(sections) == 1
        assert sections[0].type == "code"
        assert sections[0].language == "javascript"


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

    def test_merge_empty(self):
        """测试合并空列表"""
        result = merge_sections([])
        assert result == ""

    def test_merge_multiple_text(self):
        """测试合并多个文本"""
        sections = [
            MarkdownSection(type="text", content="Hello "),
            MarkdownSection(type="text", content="World")
        ]
        assert merge_sections(sections) == "Hello World"


class TestTranslateMarkdown:
    def test_translate_preserves_code(self):
        """测试代码块不被翻译"""
        mock_client = Mock()
        mock_client.translate.side_effect = lambda text: "翻译后的文本"
        
        content = "Hello\n```python\ncode\n```\nWorld"
        result = translate_markdown(mock_client, content)
        
        assert "```python" in result
        assert "code" in result
        assert "```" in result

    def test_translate_text_sections(self):
        """测试文本部分被翻译"""
        mock_client = Mock()
        mock_client.translate.return_value = "Translated"
        
        content = "Hello World"
        result = translate_markdown(mock_client, content)
        
        assert result == "Translated"
        mock_client.translate.assert_called_once()

    def test_translate_mixed_content(self):
        """测试混合内容"""
        mock_client = Mock()
        mock_client.translate.side_effect = ["翻译 1", "翻译 2"]
        
        content = "Text1\n```python\ncode\n```\nText2"
        result = translate_markdown(mock_client, content)
        
        assert "翻译 1" in result
        assert "翻译 2" in result
        assert "```python" in result
        assert "code" in result


class TestGetLlmClient:
    def test_get_qingcloud_client(self):
        """测试获取青云客户端"""
        client = get_llm_client("qingcloud", "glm-5", None, "test_key")
        assert client.__class__.__name__ == "QingCloudClient"

    def test_get_openai_client(self):
        """测试获取 OpenAI 客户端"""
        client = get_llm_client("openai", "gpt-4", None, "test_key")
        assert client.__class__.__name__ == "OpenAIClient"

    def test_get_anthropic_client(self):
        """测试获取 Anthropic 客户端"""
        client = get_llm_client("anthropic", "claude-3", None, "test_key")
        assert client.__class__.__name__ == "AnthropicClient"

    def test_get_client_with_base_url(self):
        """测试带自定义 base_url"""
        client = get_llm_client("openai", "gpt-4", "https://proxy.com/v1", "test_key")
        assert client.base_url == "https://proxy.com/v1"

    def test_unsupported_provider(self):
        """测试不支持的提供商"""
        with pytest.raises(ValueError) as exc_info:
            get_llm_client("unsupported", "model", None, "key")
        assert "Unsupported provider" in str(exc_info.value)
