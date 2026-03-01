import pytest
import os
import tempfile
import shutil
from scripts.sha_tracker import get_sha_path, load_shas, get_sha, save_sha, save_all_shas
from scripts.config import Config, LLMConfig, GroupConfig, FileConfig


class TestShaTracker:
    def test_get_sha_path(self):
        config = Config(
            source_repo="github/spec-kit",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[]
        )
        path = get_sha_path(config)
        assert path == "github-spec-kit-main/sha_tracker.ini"
    
    def test_get_sha_path_with_slashes(self):
        config = Config(
            source_repo="owner/repo",
            source_branch="develop",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[]
        )
        path = get_sha_path(config)
        assert path == "owner-repo-develop/sha_tracker.ini"
    
    def test_save_and_get_sha(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            config = Config(
                source_repo="owner/repo",
                source_branch="main",
                llm=LLMConfig(provider="qingcloud", model="glm-5"),
                groups=[]
            )
            
            save_sha(config, "test/file.md", "abc123")
            
            sha = get_sha(config, "test/file.md")
            assert sha == "abc123"
    
    def test_get_sha_not_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            config = Config(
                source_repo="owner/repo",
                source_branch="main",
                llm=LLMConfig(provider="qingcloud", model="glm-5"),
                groups=[]
            )
            
            sha = get_sha(config, "nonexistent.md")
            assert sha == ""
    
    def test_save_all_shas(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            config = Config(
                source_repo="owner/repo",
                source_branch="main",
                llm=LLMConfig(provider="qingcloud", model="glm-5"),
                groups=[]
            )
            
            shas = {
                "file1.md": "sha1",
                "file2.md": "sha2"
            }
            
            save_all_shas(config, shas)
            
            assert get_sha(config, "file1.md") == "sha1"
            assert get_sha(config, "file2.md") == "sha2"
    
    def test_update_sha(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            config = Config(
                source_repo="owner/repo",
                source_branch="main",
                llm=LLMConfig(provider="qingcloud", model="glm-5"),
                groups=[]
            )
            
            save_sha(config, "test.md", "old_sha")
            assert get_sha(config, "test.md") == "old_sha"
            
            save_sha(config, "test.md", "new_sha")
            assert get_sha(config, "test.md") == "new_sha"
    
    def test_ini_file_format(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            config = Config(
                source_repo="owner/repo",
                source_branch="main",
                llm=LLMConfig(provider="qingcloud", model="glm-5"),
                groups=[]
            )
            
            save_sha(config, "test/file.md", "abc123")
            
            with open("owner-repo-main/sha_tracker.ini", "r") as f:
                content = f.read()
            
            assert "[files]" in content
            assert "test/file.md = abc123" in content