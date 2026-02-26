import pytest
from unittest.mock import patch, Mock
from scripts.github_api import get_file_sha, download_file, get_rate_limit, GitHubFile


class TestGetFileSha:
    @patch('requests.get')
    def test_get_file_sha_success(self, mock_get):
        """测试成功获取 SHA"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"sha": "abc123"}]
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

    @patch('requests.get')
    def test_get_file_sha_unauthorized(self, mock_get):
        """测试权限错误"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with pytest.raises(PermissionError):
            get_file_sha("owner/repo", "main", "README.md", "token")

    @patch('requests.get')
    def test_get_file_sha_no_commits(self, mock_get):
        """测试没有 commits"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        with pytest.raises(FileNotFoundError):
            get_file_sha("owner/repo", "main", "README.md", "token")

    @patch('requests.get')
    def test_get_file_sha_api_error(self, mock_get):
        """测试 API 错误"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception):
            get_file_sha("owner/repo", "main", "README.md", "token")


class TestDownloadFile:
    @patch('requests.get')
    def test_download_success(self, mock_get):
        """测试成功下载文件"""
        import base64
        content = "# Title\n"
        encoded_content = base64.b64encode(content.encode()).decode()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sha": "abc123",
            "content": encoded_content,
            "encoding": "base64"
        }
        mock_get.return_value = mock_response
        
        result = download_file("owner/repo", "main", "README.md", "token")
        assert result.sha == "abc123"
        assert result.content == "# Title\n"

    @patch('requests.get')
    def test_download_not_found(self, mock_get):
        """测试文件不存在"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(FileNotFoundError):
            download_file("owner/repo", "main", "nonexistent.md", "token")

    @patch('requests.get')
    def test_download_unauthorized(self, mock_get):
        """测试权限错误"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with pytest.raises(PermissionError):
            download_file("owner/repo", "main", "README.md", "token")

    @patch('requests.get')
    def test_download_api_error(self, mock_get):
        """测试 API 错误"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception):
            download_file("owner/repo", "main", "README.md", "token")


class TestGetRateLimit:
    @patch('requests.get')
    def test_get_rate_limit_success(self, mock_get):
        """测试成功获取限制信息"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rate": {"limit": 5000, "remaining": 4999, "reset": 1234567890}
        }
        mock_get.return_value = mock_response
        
        result = get_rate_limit("token")
        assert result["limit"] == 5000
        assert result["remaining"] == 4999
        assert result["reset"] == 1234567890

    @patch('requests.get')
    def test_get_rate_limit_api_error(self, mock_get):
        """测试 API 错误"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = get_rate_limit("token")
        assert result == {"limit": 0, "remaining": 0, "reset": 0}

    @patch('requests.get')
    def test_get_rate_limit_missing_rate(self, mock_get):
        """测试缺少 rate 字段"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        
        result = get_rate_limit("token")
        assert result == {"limit": 0, "remaining": 0, "reset": 0}
