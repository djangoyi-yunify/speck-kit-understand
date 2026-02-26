import os


def ensure_dir(path: str) -> None:
    """确保目录存在，不存在则创建
    
    Args:
        path: 目录路径
    """
    os.makedirs(path, exist_ok=True)


def write_file(path: str, content: str) -> None:
    """写入文件内容
    
    Args:
        path: 文件路径
        content: 文件内容
        
    Raises:
        FileNotFoundError: 父目录不存在
    """
    with open(path, 'w') as f:
        f.write(content)


def read_file(path: str) -> str:
    """读取文件内容
    
    Args:
        path: 文件路径
        
    Returns:
        文件内容
        
    Raises:
        FileNotFoundError: 文件不存在
    """
    with open(path, 'r') as f:
        return f.read()


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
    dir_name = os.path.dirname(target_filename)
    base_name = os.path.basename(target_filename)
    
    if '.' in base_name:
        name_parts = base_name.rsplit('.', 1)
        source_name = f"{name_parts[0]}.en.{name_parts[1]}"
    else:
        source_name = f"{base_name}.en"
    
    if dir_name:
        return os.path.join(dir_name, source_name)
    return source_name
