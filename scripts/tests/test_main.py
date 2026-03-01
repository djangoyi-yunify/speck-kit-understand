import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from scripts.main import FileUpdate, check_updates, translate_files
from scripts.config import Config, LLMConfig, GroupConfig, FileConfig


class TestCheckUpdates:
    @patch('scripts.main.get_file_sha')
    def test_check_updates_with_changes(self, mock_get_sha):
        """测试有更新"""
        mock_get_sha.side_effect = ["new_sha_1", "new_sha_2"]
        
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[
                GroupConfig(
                    name="test",
                    target_dir="output",
                    include_source=True,
                    files=[
                        FileConfig(source="a.md", target="a.md", last_sha="old_sha_1"),
                        FileConfig(source="b.md", target="b.md", last_sha="old_sha_2")
                    ]
                )
            ]
        )
        
        updates = check_updates(config, "token")
        assert len(updates) == 2
        assert updates[0].file_config.source == "a.md"
        assert updates[0].new_sha == "new_sha_1"

    @patch('scripts.main.get_file_sha')
    def test_check_updates_no_changes(self, mock_get_sha):
        """测试无更新"""
        mock_get_sha.side_effect = ["same_sha", "same_sha"]
        
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[
                GroupConfig(
                    name="test",
                    target_dir="output",
                    include_source=True,
                    files=[
                        FileConfig(source="a.md", target="a.md", last_sha="same_sha"),
                        FileConfig(source="b.md", target="b.md", last_sha="same_sha")
                    ]
                )
            ]
        )
        
        updates = check_updates(config, "token")
        assert len(updates) == 0

    @patch('scripts.main.get_file_sha')
    def test_check_updates_with_error(self, mock_get_sha):
        """测试 API 错误"""
        mock_get_sha.side_effect = Exception("API Error")
        
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[
                GroupConfig(
                    name="test",
                    target_dir="output",
                    include_source=True,
                    files=[FileConfig(source="a.md", target="a.md")]
                )
            ]
        )
        
        updates = check_updates(config, "token")
        assert len(updates) == 0


class TestTranslateFiles:
    @patch('scripts.main.download_file')
    @patch('scripts.main.translate_markdown')
    @patch('scripts.main.ensure_dir')
    @patch('scripts.main.write_file')
    def test_translate_files_success(self, mock_write, mock_ensure, mock_translate, mock_download):
        """测试成功翻译"""
        mock_download.return_value = Mock(sha="abc", content="# Original")
        mock_translate.return_value = "# 翻译后"
        
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[
                GroupConfig(
                    name="test",
                    target_dir="output",
                    include_source=True,
                    files=[FileConfig(source="a.md", target="a.md")]
                )
            ]
        )
        
        updates = [FileUpdate(
            group_idx=0,
            file_idx=0,
            file_config=FileConfig(source="a.md", target="a.md"),
            new_sha="new_sha"
        )]
        
        mock_client = Mock()
        results = translate_files(config, updates, mock_client, "token")
        
        assert results == {"a.md": True}
        mock_write.assert_called()

    @patch('scripts.main.download_file')
    @patch('scripts.main.ensure_dir')
    @patch('scripts.main.write_file')
    def test_translate_files_error(self, mock_write, mock_ensure, mock_download):
        """测试翻译失败"""
        mock_download.side_effect = Exception("Download failed")
        
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[
                GroupConfig(
                    name="test",
                    target_dir="output",
                    include_source=True,
                    files=[FileConfig(source="a.md", target="a.md")]
                )
            ]
        )
        
        updates = [FileUpdate(
            group_idx=0,
            file_idx=0,
            file_config=FileConfig(source="a.md", target="a.md"),
            new_sha="new_sha"
        )]
        
        mock_client = Mock()
        results = translate_files(config, updates, mock_client, "token")
        
        assert results == {"a.md": False}

    @patch('scripts.main.download_file')
    @patch('scripts.main.translate_markdown')
    @patch('scripts.main.ensure_dir')
    @patch('scripts.main.write_file')
    def test_translate_files_with_source(self, mock_write, mock_ensure, mock_translate, mock_download):
        """测试包含原文对照"""
        mock_download.return_value = Mock(sha="abc", content="# Original")
        mock_translate.return_value = "# 翻译后"
        
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[
                GroupConfig(
                    name="test",
                    target_dir="output",
                    include_source=True,
                    files=[FileConfig(source="README.md", target="README.md")]
                )
            ]
        )
        
        updates = [FileUpdate(
            group_idx=0,
            file_idx=0,
            file_config=FileConfig(source="README.md", target="README.md"),
            new_sha="new_sha"
        )]
        
        mock_client = Mock()
        translate_files(config, updates, mock_client, "token")
        
        assert mock_write.call_count == 2

    @patch('scripts.main.download_file')
    @patch('scripts.main.translate_markdown')
    @patch('scripts.main.ensure_dir')
    @patch('scripts.main.write_file')
    def test_translate_files_with_prefix_path(self, mock_write, mock_ensure, mock_translate, mock_download):
        """测试路径前缀格式"""
        mock_download.return_value = Mock(sha="abc", content="# Original")
        mock_translate.return_value = "# 翻译后"
        
        config = Config(
            source_repo="github/spec-kit",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[
                GroupConfig(
                    name="test",
                    target_dir="00-constitution",
                    include_source=True,
                    files=[FileConfig(source="a.md", target="a.cn.md")]
                )
            ]
        )
        
        updates = [FileUpdate(
            group_idx=0,
            file_idx=0,
            file_config=FileConfig(source="a.md", target="a.cn.md"),
            new_sha="new_sha"
        )]
        
        mock_client = Mock()
        translate_files(config, updates, mock_client, "token")
        
        mock_ensure.assert_called_with("github-spec-kit-main/00-constitution")

    @patch('scripts.main.download_file')
    @patch('scripts.main.translate_markdown')
    @patch('scripts.main.ensure_dir')
    @patch('scripts.main.write_file')
    def test_translate_files_without_source(self, mock_write, mock_ensure, mock_translate, mock_download):
        """测试不包含原文对照"""
        mock_download.return_value = Mock(sha="abc", content="# Original")
        mock_translate.return_value = "# 翻译后"
        
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[
                GroupConfig(
                    name="test",
                    target_dir="output",
                    include_source=False,
                    files=[FileConfig(source="README.md", target="README.md")]
                )
            ]
        )
        
        updates = [FileUpdate(
            group_idx=0,
            file_idx=0,
            file_config=FileConfig(source="README.md", target="README.md"),
            new_sha="new_sha"
        )]
        
        mock_client = Mock()
        translate_files(config, updates, mock_client, "token")
        
        assert mock_write.call_count == 1


class TestRunCheckWorkflow:
    @patch('scripts.config.load_config')
    @patch('scripts.main.check_updates')
    def test_run_check_workflow_no_updates(self, mock_check, mock_load):
        """测试无更新"""
        mock_load.return_value = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[]
        )
        mock_check.return_value = []
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            output_file = f.name
        
        try:
            env = {
                'GITHUB_TOKEN': 'test_token',
                'GITHUB_OUTPUT': output_file
            }
            with patch.dict(os.environ, env):
                from scripts.main import run_check_workflow
                run_check_workflow()
            
            with open(output_file, 'r') as f:
                content = f.read()
            assert 'has_updates=false' in content
        finally:
            os.unlink(output_file)

    @patch('scripts.config.load_config')
    @patch('scripts.main.check_updates')
    def test_run_check_workflow_with_updates(self, mock_check, mock_load):
        """测试有更新"""
        mock_load.return_value = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[GroupConfig(
                name="test",
                target_dir="output",
                include_source=True,
                files=[FileConfig(source="a.md", target="a.md")]
            )]
        )
        mock_check.return_value = [FileUpdate(
            group_idx=0,
            file_idx=0,
            file_config=FileConfig(source="a.md", target="a.md"),
            new_sha="new_sha"
        )]
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            output_file = f.name
        
        try:
            env = {
                'GITHUB_TOKEN': 'test_token',
                'GITHUB_OUTPUT': output_file
            }
            with patch.dict(os.environ, env):
                from scripts.main import run_check_workflow
                run_check_workflow()
            
            with open(output_file, 'r') as f:
                content = f.read()
            assert 'files=0:0' in content
            assert 'has_updates=true' in content
        finally:
            os.unlink(output_file)


class TestRunTranslateWorkflow:
    @patch('scripts.config.load_config')
    @patch('scripts.main.get_llm_client')
    @patch('scripts.main.translate_files')
    def test_run_translate_workflow(self, mock_translate, mock_get_client, mock_load):
        """测试翻译工作流"""
        mock_load.return_value = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[GroupConfig(
                name="test",
                target_dir="output",
                include_source=True,
                files=[FileConfig(source="a.md", target="a.md")]
            )]
        )
        mock_get_client.return_value = Mock()
        mock_translate.return_value = {"a.md": True}
        
        env = {
            'GITHUB_TOKEN': 'test_token',
            'LLM_API_KEY': 'test_key',
            'FILES': '0:0'
        }
        
        with patch.dict(os.environ, env):
            from scripts.main import run_translate_workflow
            run_translate_workflow()
