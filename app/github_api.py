import requests


def get_repository(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(url)

    print("Repository API:", response.status_code)

    if response.status_code != 200:
        raise Exception(
            f"GitHub API error: {response.status_code}"
        )

    return response.json()


def get_repository_contents(owner, repo, path=""):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    print("Contents API URL:", url)

    response = requests.get(url)

    print("Contents API Status:", response.status_code)

    if response.status_code != 200:
        raise Exception(
            f"GitHub API error: {response.status_code}"
        )

    data = response.json()

    print("Contents returned:")

    for item in data:
        print(
            item.get("name"),
            "->",
            item.get("type"),
            "->",
            item.get("path")
        )

    return data