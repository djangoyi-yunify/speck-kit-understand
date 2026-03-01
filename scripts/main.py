import os
from dataclasses import dataclass
from typing import Optional

from scripts.config import Config, get_files_to_translate, FileConfig
from scripts.github_api import get_file_sha, download_file, GitHubFile
from scripts.file_ops import ensure_dir, write_file, read_file
from scripts.translator import LLMClient, translate_markdown, get_llm_client
from scripts.sha_tracker import get_sha, save_sha


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
    updates = []
    files = get_files_to_translate(config)
    
    for group_idx, file_idx, file_config in files:
        try:
            current_sha = get_file_sha(
                config.source_repo,
                config.source_branch,
                file_config.source,
                github_token
            )
            
            last_sha = get_sha(config, file_config.source)
            if current_sha != last_sha:
                updates.append(FileUpdate(
                    group_idx=group_idx,
                    file_idx=file_idx,
                    file_config=file_config,
                    new_sha=current_sha
                ))
        except Exception as e:
            print(f"Error checking {file_config.source}: {e}")
            continue
    
    return updates


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
    results = {}
    
    prefix = f"{config.source_repo}-{config.source_branch}".replace("/", "-")
    
    for update in updates:
        group = config.groups[update.group_idx]
        target_dir = os.path.join(prefix, group.target_dir)
        
        try:
            github_file = download_file(
                config.source_repo,
                config.source_branch,
                update.file_config.source,
                github_token
            )
            
            translated_content = translate_markdown(
                llm_client,
                github_file.content
            )
            
            ensure_dir(target_dir)
            target_path = os.path.join(target_dir, update.file_config.target)
            write_file(target_path, translated_content)
            
            if group.include_source:
                source_filename = os.path.basename(update.file_config.source)
                source_path = os.path.join(target_dir, source_filename)
                write_file(source_path, github_file.content)
            
            results[update.file_config.source] = True
            
        except Exception as e:
            print(f"Error translating {update.file_config.source}: {e}")
            results[update.file_config.source] = False
    
    return results


def run_check_workflow() -> None:
    """检测工作流入口
    
    从环境变量读取配置，检测更新，触发翻译工作流
    """
    config_path = os.environ.get('CONFIG_PATH', 'translation-config.json')
    github_token = os.environ.get('GITHUB_TOKEN')
    
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    from scripts.config import load_config
    config = load_config(config_path)
    
    updates = check_updates(config, github_token)
    
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        if updates:
            print(f"Found {len(updates)} files to translate:")
            for update in updates:
                print(f"  - {update.file_config.source}")
            
            files_json = ','.join([
                f'{u.group_idx}:{u.file_idx}'
                for u in updates
            ])
            f.write(f"files={files_json}\n")
            f.write("has_updates=true\n")
        else:
            print("No files need translation")
            f.write("has_updates=false\n")


def run_translate_workflow() -> None:
    """翻译工作流入口
    
    从环境变量读取参数，执行翻译
    """
    config_path = os.environ.get('CONFIG_PATH', 'translation-config.json')
    github_token = os.environ.get('GITHUB_TOKEN')
    llm_api_key = os.environ.get('LLM_API_KEY')
    files_input = os.environ.get('FILES', '')
    
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    if not llm_api_key:
        raise ValueError("LLM_API_KEY environment variable is required")
    
    from scripts.config import load_config
    config = load_config(config_path)
    
    llm_client = get_llm_client(
        provider=config.llm.provider,
        model=config.llm.model,
        base_url=config.llm.base_url,
        api_key=llm_api_key
    )
    
    updates = []
    if files_input:
        for item in files_input.split(','):
            if ':' in item:
                group_idx, file_idx = map(int, item.split(':'))
                group = config.groups[group_idx]
                file_config = group.files[file_idx]
                updates.append(FileUpdate(
                    group_idx=group_idx,
                    file_idx=file_idx,
                    file_config=file_config,
                    new_sha=""
                ))
    
    if updates:
        results = translate_files(config, updates, llm_client, github_token)
        
        for update in updates:
            if results.get(update.file_config.source, False):
                save_sha(config, update.file_config.source, update.new_sha)
        
        print(f"Translation completed. Results: {results}")
    else:
        print("No files to translate")
