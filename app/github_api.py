import requests


def get_repository(owner, repository):
    url = f"https://api.github.com/repos/{owner}/{repository}"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(
            f"GitHub API request failed: {response.status_code}"
        )

    return response.json()