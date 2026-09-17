import requests


def get_repository(owner, repository):
    url = f"https://api.github.com/repos/{owner}/{repository}"

    response = requests.get(url)

    if response.status_code == 404:
        raise ValueError("Repository not found")

    response.raise_for_status()

    return response.json()