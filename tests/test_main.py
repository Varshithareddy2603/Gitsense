from app.github_api import get_repository


def test_get_repository():
    data = get_repository("Varshithareddy2603", "GitSense")

    assert data["name"] == "Gitsense"
def test_get_invalid_repository():
    try:
        get_repository("Varshithareddy2603", "this-repository-does-not-exist")
    except ValueError as e:
        assert str(e) == "Repository not found"