from unittest.mock import patch

import pytest

from app.github_api import get_repository
from app.repository_service import get_repository_summary


def test_get_repository():
    fake_repository = {
        "name": "test-repository",
        "description": "Test repository",
        "stargazers_count": 10,
        "forks_count": 5,
        "open_issues_count": 2,
        "language": "Python",
    }

    with patch(
        "app.github_api.requests.get"
    ) as mock_get:

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = fake_repository

        repo = get_repository(
            "test-user",
            "test-repository"
        )

    assert repo["name"] == "test-repository"


def test_get_invalid_repository():
    with patch(
        "app.github_api.requests.get"
    ) as mock_get:

        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = {}

        with pytest.raises(
            Exception,
            match="GitHub API error: 404"
        ):
            get_repository(
                "test-user",
                "this-repository-does-not-exist"
            )


def test_get_repository_summary():
    fake_repository = {
        "name": "test-repository",
        "description": "Test repository",
        "stargazers_count": 10,
        "forks_count": 5,
        "open_issues_count": 2,
        "language": "Python",
    }

    with patch(
        "app.github_api.requests.get"
    ) as mock_get:

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = fake_repository

        summary = get_repository_summary(
            "test-user",
            "test-repository"
        )

    assert summary["name"] == "test-repository"
    assert "stars" in summary
    assert "forks" in summary
    assert "open_issues" in summary
    assert "language" in summary