import requests
from dataclasses import dataclass
import base64


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
    url = f"https://api.github.com/repos/{repo}/commits"
    params = {
        'path': path,
        'sha': branch,
        'per_page': 1
    }
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 404:
        raise FileNotFoundError(f"File not found: {path} in {repo}/{branch}")
    elif response.status_code == 401:
        raise PermissionError("Invalid GitHub token")
    elif response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
    
    commits = response.json()
    if not commits:
        raise FileNotFoundError(f"No commits found for file: {path}")
    
    return commits[0]['sha']


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
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    params = {'ref': branch}
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 404:
        raise FileNotFoundError(f"File not found: {path} in {repo}/{branch}")
    elif response.status_code == 401:
        raise PermissionError("Invalid GitHub token")
    elif response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
    
    data = response.json()
    content = base64.b64decode(data['content']).decode('utf-8')
    
    return GitHubFile(sha=data['sha'], content=content)


def get_rate_limit(token: str) -> dict:
    """获取 API 限制信息
    
    Args:
        token: GitHub token
        
    Returns:
        {"limit": int, "remaining": int, "reset": int}
    """
    url = "https://api.github.com/rate_limit"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return {"limit": 0, "remaining": 0, "reset": 0}
    
    data = response.json()
    rate = data.get('rate', {})
    
    return {
        "limit": rate.get('limit', 0),
        "remaining": rate.get('remaining', 0),
        "reset": rate.get('reset', 0)
    }
