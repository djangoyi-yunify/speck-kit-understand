import pytest
import json
import tempfile
from scripts.config import (
    load_config, save_config, update_file_sha, get_files_to_translate,
    Config, LLMConfig, GroupConfig, FileConfig
)


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
        assert config.groups[0].name == "test"
        assert len(config.groups[0].files) == 1

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

    def test_load_config_with_base_url(self, tmp_path):
        """测试加载带 base_url 的配置"""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "source_repo": "owner/repo",
            "source_branch": "main",
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "base_url": "https://proxy.example.com/v1"
            },
            "groups": []
        }))
        
        config = load_config(str(config_file))
        assert config.llm.base_url == "https://proxy.example.com/v1"

    def test_load_config_with_last_sha(self, tmp_path):
        """测试加载带 last_sha 的配置"""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "source_repo": "owner/repo",
            "source_branch": "main",
            "llm": {"provider": "qingcloud", "model": "glm-5"},
            "groups": [{
                "name": "test",
                "target_dir": "output",
                "include_source": True,
                "files": [{"source": "README.md", "target": "README.md", "last_sha": "abc123"}]
            }]
        }))
        
        config = load_config(str(config_file))
        assert config.groups[0].files[0].last_sha == "abc123"


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
        assert data["llm"]["provider"] == "qingcloud"

    def test_save_config_with_groups(self, tmp_path):
        """测试保存带分组的配置"""
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[
                GroupConfig(
                    name="core",
                    target_dir="translated/core",
                    include_source=True,
                    files=[FileConfig(source="README.md", target="README.md", last_sha="xyz789")]
                )
            ]
        )
        
        config_file = tmp_path / "config.json"
        save_config(config, str(config_file))
        
        data = json.loads(config_file.read_text())
        assert len(data["groups"]) == 1
        assert data["groups"][0]["name"] == "core"
        assert data["groups"][0]["files"][0]["last_sha"] == "xyz789"

    def test_save_config_with_null_base_url(self, tmp_path):
        """测试保存 base_url 为 null 的配置"""
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5", base_url=None),
            groups=[]
        )
        
        config_file = tmp_path / "config.json"
        save_config(config, str(config_file))
        
        data = json.loads(config_file.read_text())
        assert data["llm"]["base_url"] is None


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

    def test_update_invalid_file_index(self):
        """测试文件索引越界"""
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[GroupConfig(
                name="test",
                target_dir="output",
                include_source=True,
                files=[FileConfig(source="README.md", target="README.md")]
            )]
        )
        
        with pytest.raises(IndexError):
            update_file_sha(config, 0, 1, "new_sha")


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
        assert files[0] == (0, 0, FileConfig(source="a.md", target="a.md", last_sha=""))
        assert files[1] == (1, 0, FileConfig(source="b.md", target="b.md", last_sha=""))

    def test_get_files_empty_groups(self):
        """测试空分组"""
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[]
        )
        
        files = get_files_to_translate(config)
        assert len(files) == 0

    def test_get_files_multiple_files_per_group(self):
        """测试每组多个文件"""
        config = Config(
            source_repo="owner/repo",
            source_branch="main",
            llm=LLMConfig(provider="qingcloud", model="glm-5"),
            groups=[
                GroupConfig(
                    name="g1",
                    target_dir="out1",
                    include_source=True,
                    files=[
                        FileConfig(source="a.md", target="a.md"),
                        FileConfig(source="b.md", target="b.md"),
                        FileConfig(source="c.md", target="c.md")
                    ]
                )
            ]
        )
        
        files = get_files_to_translate(config)
        assert len(files) == 3
        assert files[0][2].source == "a.md"
        assert files[1][2].source == "b.md"
        assert files[2][2].source == "c.md"
