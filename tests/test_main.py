from app.github_api import get_repository


def test_get_repository():
    data = get_repository("Varshithareddy2603", "GitSense")

    assert data["name"] == "Gitsense"