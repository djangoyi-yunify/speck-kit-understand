import pytest
from scripts.file_ops import ensure_dir, write_file, read_file, get_source_filename


class TestEnsureDir:
    def test_create_dir(self, tmp_path):
        """测试创建新目录"""
        new_dir = tmp_path / "new_dir"
        ensure_dir(str(new_dir))
        assert new_dir.exists()

    def test_existing_dir(self, tmp_path):
        """测试已存在的目录"""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        ensure_dir(str(existing_dir))  # 不应报错
        assert existing_dir.exists()

    def test_nested_dir(self, tmp_path):
        """测试创建嵌套目录"""
        nested_dir = tmp_path / "a" / "b" / "c"
        ensure_dir(str(nested_dir))
        assert nested_dir.exists()


class TestWriteFile:
    def test_write_file(self, tmp_path):
        """测试写入文件"""
        file_path = tmp_path / "test.txt"
        write_file(str(file_path), "hello")
        assert file_path.read_text() == "hello"

    def test_write_to_nonexistent_dir(self):
        """测试写入不存在的目录"""
        with pytest.raises(FileNotFoundError):
            write_file("/nonexistent/dir/file.txt", "content")

    def test_write_chinese_content(self, tmp_path):
        """测试写入中文内容"""
        file_path = tmp_path / "test.txt"
        write_file(str(file_path), "你好世界")
        assert file_path.read_text() == "你好世界"


class TestReadFile:
    def test_read_file(self, tmp_path):
        """测试读取文件"""
        file_path = tmp_path / "test.txt"
        file_path.write_text("hello")
        assert read_file(str(file_path)) == "hello"

    def test_read_nonexistent_file(self):
        """测试读取不存在的文件"""
        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/file.txt")

    def test_read_chinese_content(self, tmp_path):
        """测试读取中文内容"""
        file_path = tmp_path / "test.txt"
        file_path.write_text("你好世界")
        assert read_file(str(file_path)) == "你好世界"


class TestGetSourceFilename:
    def test_simple_filename(self):
        """测试简单文件名"""
        assert get_source_filename("README.md") == "README.en.md"

    def test_path_with_dir(self):
        """测试带路径的文件名"""
        assert get_source_filename("docs/guide.md") == "docs/guide.en.md"

    def test_nested_path(self):
        """测试嵌套路径"""
        assert get_source_filename("a/b/c/file.md") == "a/b/c/file.en.md"

    def test_no_extension(self):
        """测试无扩展名文件"""
        assert get_source_filename("README") == "README.en"

    def test_multiple_dots(self):
        """测试多个点的文件名"""
        assert get_source_filename("file.test.md") == "file.test.en.md"

    def test_empty_string(self):
        """测试空字符串"""
        assert get_source_filename("") == ".en"
