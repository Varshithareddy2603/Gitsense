import pytest

from app.github_api import get_repository
from app.repository_service import get_repository_summary


def test_get_repository():
    repo = get_repository("Varshithareddy2603", "Gitsense")

    assert repo["name"] == "Gitsense"


def test_get_invalid_repository():
    with pytest.raises(ValueError, match="Repository not found"):
        get_repository(
            "Varshithareddy2603",
            "this-repository-does-not-exist"
        )


def test_get_repository_summary():
    summary = get_repository_summary(
        "Varshithareddy2603",
        "Gitsense"
    )

    assert summary["name"] == "Gitsense"
    assert "stars" in summary
    assert "forks" in summary
    assert "open_issues" in summary
    assert "language" in summary