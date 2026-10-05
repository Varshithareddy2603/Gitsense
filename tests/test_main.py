from unittest.mock import patch
import pytest

from app.github_api import (
    get_repository,
    get_repository_tree,
    get_file_content
)
from app.repository_service import (
    get_repository_summary,
    get_all_repository_files,
    get_file_extension,
    get_file_statistics
)


def test_get_repository():
    fake_repository = {
        "name": "test-repository",
        "description": "Test repository",
        "stargazers_count": 10,
        "forks_count": 5,
        "open_issues_count": 2,
        "language": "Python",
    }

    with patch("app.github_api.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = fake_repository

        repo = get_repository("test-user", "test-repository")

    assert repo["name"] == "test-repository"


def test_get_invalid_repository():
    with patch("app.github_api.requests.get") as mock_get:
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = {}

        with pytest.raises(Exception, match="404 Not Found"):
            get_repository("test-user", "this-repository-does-not-exist")


def test_get_repository_summary():
    fake_repository = {
        "name": "test-repository",
        "description": "Test repository",
        "stargazers_count": 10,
        "forks_count": 5,
        "open_issues_count": 2,
        "language": "TypeScript",
    }

    with patch("app.github_api.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = fake_repository

        summary = get_repository_summary("test-user", "test-repository")

    assert summary["name"] == "test-repository"
    assert "stars" in summary
    assert "forks" in summary
    assert "open_issues" in summary
    assert summary["language"] == "TypeScript"


def test_get_repository_tree_single_call():
    fake_tree = {
        "sha": "abc123",
        "tree": [
            {"path": "src/index.ts", "type": "blob", "size": 100},
            {"path": "src/App.tsx", "type": "blob", "size": 250},
            {"path": "package.json", "type": "blob", "size": 500},
            {"path": "src", "type": "tree"},
        ],
        "truncated": False
    }

    with patch("app.github_api.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = fake_tree

        files = get_all_repository_files("facebook", "react")

    assert len(files) == 3
    assert files[0]["path"] == "src/index.ts"
    assert files[1]["name"] == "App.tsx"


def test_file_extension_statistics():
    assert get_file_extension("main.go") == "Go"
    assert get_file_extension("App.tsx") == "TypeScript (React)"
    assert get_file_extension("lib.rs") == "Rust"
    assert get_file_extension("Server.java") == "Java"
    assert get_file_extension("Dockerfile") == "Docker"
    assert get_file_extension("script.py") == "Python"