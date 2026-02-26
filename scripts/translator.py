import re
import os
from typing import Protocol, Optional
from dataclasses import dataclass


_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")


def load_system_prompt(filename: str = "translate_system.txt") -> str:
    """Load system prompt from file.
    
    Args:
        filename: Name of the prompt file in the prompts directory.
        
    Returns:
        The content of the prompt file.
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist.
    """
    prompt_path = os.path.join(_PROMPT_DIR, filename)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


class LLMClient(Protocol):
    """LLM 客户端协议"""
    def translate(self, text: str) -> str:
        ...


@dataclass
class MarkdownSection:
    type: str  # "code", "text"
    content: str
    language: Optional[str] = None  # 仅 code 类型


class QingCloudClient:
    """青云 AI 客户端 (OpenAI 兼容格式)"""
    def __init__(self, model: str, api_key: str, base_url: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url or "https://api.qingcloud.com/v1"
        self._system_prompt = load_system_prompt()
    
    def translate(self, text: str) -> str:
        import requests
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": text}
            ]
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class OpenAIClient:
    """OpenAI 客户端"""
    def __init__(self, model: str, api_key: str, base_url: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self._system_prompt = load_system_prompt()
    
    def translate(self, text: str) -> str:
        import requests
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": text}
            ]
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class AnthropicClient:
    """Anthropic Claude 客户端"""
    def __init__(self, model: str, api_key: str, base_url: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url or "https://api.anthropic.com"
        self._system_prompt = load_system_prompt()
    
    def translate(self, text: str) -> str:
        import requests
        url = f"{self.base_url}/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": self.model,
            "max_tokens": 4096,
            "system": self._system_prompt,
            "messages": [
                {"role": "user", "content": text}
            ]
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()["content"][0]["text"]


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
    providers = {
        "qingcloud": QingCloudClient,
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
    }
    
    if provider not in providers:
        raise ValueError(f"Unsupported provider: {provider}. Supported: {list(providers.keys())}")
    
    return providers[provider](model=model, api_key=api_key, base_url=base_url)


def split_markdown_sections(content: str) -> list[MarkdownSection]:
    """分割 Markdown 为区块
    
    Args:
        content: Markdown 内容
        
    Returns:
        区块列表
    """
    sections = []
    pattern = r'```(\w*)\n(.*?)```'
    
    last_end = 0
    for match in re.finditer(pattern, content, flags=re.DOTALL):
        text_before = content[last_end:match.start()]
        if text_before.strip():
            sections.append(MarkdownSection(type="text", content=text_before))
        
        language = match.group(1) or None
        code_content = match.group(2).strip()
        sections.append(MarkdownSection(type="code", content=code_content, language=language))
        last_end = match.end()
    
    text_after = content[last_end:]
    if text_after.strip():
        sections.append(MarkdownSection(type="text", content=text_after))
    
    if not sections:
        sections.append(MarkdownSection(type="text", content=content))
    
    return sections


def merge_sections(sections: list[MarkdownSection]) -> str:
    """合并区块为 Markdown
    
    Args:
        sections: 区块列表
        
    Returns:
        合并后的 Markdown 内容
    """
    result = []
    for section in sections:
        if section.type == "code":
            lang = section.language or ""
            result.append(f"```{lang}\n{section.content}\n```")
        else:
            result.append(section.content)
    return "".join(result)


def translate_text(client: LLMClient, text: str) -> str:
    """翻译文本
    
    Args:
        client: LLM 客户端
        text: 待翻译文本
        
    Returns:
        翻译后的文本
    """
    if not text.strip():
        return text
    return client.translate(text)


def translate_markdown(client: LLMClient, content: str) -> str:
    """翻译 Markdown（保留代码块不翻译）
    
    Args:
        client: LLM 客户端
        content: Markdown 内容
        
    Returns:
        翻译后的 Markdown
    """
    sections = split_markdown_sections(content)
    translated_sections = []
    
    for section in sections:
        if section.type == "code":
            translated_sections.append(section)
        else:
            translated_content = translate_text(client, section.content)
            translated_sections.append(MarkdownSection(type="text", content=translated_content))
    
    return merge_sections(translated_sections)
