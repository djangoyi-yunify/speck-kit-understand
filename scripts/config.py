import json
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
    with open(path, 'r') as f:
        data = json.load(f)
    
    llm_data = data['llm']
    llm = LLMConfig(
        provider=llm_data['provider'],
        model=llm_data['model'],
        base_url=llm_data.get('base_url')
    )
    
    groups = []
    for group_data in data['groups']:
        files = [
            FileConfig(
                source=f['source'],
                target=f['target'],
                last_sha=f.get('last_sha', '')
            )
            for f in group_data['files']
        ]
        groups.append(GroupConfig(
            name=group_data['name'],
            target_dir=group_data['target_dir'],
            include_source=group_data['include_source'],
            files=files
        ))
    
    return Config(
        source_repo=data['source_repo'],
        source_branch=data['source_branch'],
        llm=llm,
        groups=groups
    )


def save_config(config: Config, path: str) -> None:
    """保存配置文件
    
    Args:
        config: Config 对象
        path: 保存路径
        
    Raises:
        PermissionError: 无写入权限
    """
    data = {
        'source_repo': config.source_repo,
        'source_branch': config.source_branch,
        'llm': {
            'provider': config.llm.provider,
            'model': config.llm.model,
            'base_url': config.llm.base_url
        },
        'groups': [
            {
                'name': group.name,
                'target_dir': group.target_dir,
                'include_source': group.include_source,
                'files': [
                    {
                        'source': f.source,
                        'target': f.target,
                        'last_sha': f.last_sha
                    }
                    for f in group.files
                ]
            }
            for group in config.groups
        ]
    }
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


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
    import copy
    new_config = copy.deepcopy(config)
    new_config.groups[group_idx].files[file_idx].last_sha = sha
    return new_config


def get_files_to_translate(config: Config) -> list[tuple[int, int, FileConfig]]:
    """获取所有文件的扁平列表
    
    Args:
        config: Config 对象
        
    Returns:
        [(group_idx, file_idx, FileConfig), ...]
    """
    files = []
    for group_idx, group in enumerate(config.groups):
        for file_idx, file_config in enumerate(group.files):
            files.append((group_idx, file_idx, file_config))
    return files
