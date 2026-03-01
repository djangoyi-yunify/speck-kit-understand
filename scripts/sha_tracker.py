import configparser
import os
from scripts.config import Config


def get_sha_path(config: Config) -> str:
    prefix = f"{config.source_repo}-{config.source_branch}".replace("/", "-")
    return os.path.join(prefix, "sha_tracker.ini")


def load_shas(config: Config) -> dict[str, str]:
    sha_path = get_sha_path(config)
    if not os.path.exists(sha_path):
        return {}
    
    parser = configparser.ConfigParser()
    parser.read(sha_path)
    
    if "files" not in parser:
        return {}
    
    return dict(parser["files"])


def get_sha(config: Config, source: str) -> str:
    shas = load_shas(config)
    return shas.get(source, "")


def save_sha(config: Config, source: str, sha: str) -> None:
    sha_path = get_sha_path(config)
    
    parser = configparser.ConfigParser()
    if os.path.exists(sha_path):
        parser.read(sha_path)
    
    if "files" not in parser:
        parser.add_section("files")
    
    parser.set("files", source, sha)
    
    os.makedirs(os.path.dirname(sha_path), exist_ok=True)
    with open(sha_path, "w") as f:
        parser.write(f)


def save_all_shas(config: Config, shas: dict[str, str]) -> None:
    sha_path = get_sha_path(config)
    
    parser = configparser.ConfigParser()
    parser.add_section("files")
    
    for source, sha in shas.items():
        parser.set("files", source, sha)
    
    os.makedirs(os.path.dirname(sha_path), exist_ok=True)
    with open(sha_path, "w") as f:
        parser.write(f)