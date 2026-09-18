import requests
import base64
import os

from dotenv import load_dotenv


# --------------------------------
# Load Environment Variables
# --------------------------------

load_dotenv()


# --------------------------------
# GitHub Token
# --------------------------------

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN"
)


# --------------------------------
# GitHub Request Headers
# --------------------------------

HEADERS = {
    "Accept": "application/vnd.github+json"
}

if GITHUB_TOKEN:

    HEADERS["Authorization"] = (
        f"Bearer {GITHUB_TOKEN}"
    )


# --------------------------------
# Get Repository
# --------------------------------

def get_repository(owner, repo):

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}"
    )

    response = requests.get(
        url,
        headers=HEADERS
    )

    if response.status_code != 200:

        raise Exception(
            f"GitHub API error: "
            f"{response.status_code}"
        )

    return response.json()


# --------------------------------
# Get Repository Contents
# --------------------------------

def get_repository_contents(
    owner,
    repo,
    path=""
):

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/contents/{path}"
    )

    response = requests.get(
        url,
        headers=HEADERS
    )

    if response.status_code != 200:

        raise Exception(
            f"GitHub API error: "
            f"{response.status_code}"
        )

    return response.json()


# --------------------------------
# Get File Content
# --------------------------------

def get_file_content(
    owner,
    repo,
    path
):

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/contents/{path}"
    )

    response = requests.get(
        url,
        headers=HEADERS
    )

    if response.status_code != 200:

        raise Exception(
            f"GitHub API error: "
            f"{response.status_code}"
        )

    data = response.json()

    encoded_content = data.get(
        "content",
        ""
    )

    if not encoded_content:

        return "No content available."

    decoded_content = base64.b64decode(
        encoded_content
    ).decode(
        "utf-8",
        errors="replace"
    )

    return decoded_content


# --------------------------------
# Get Repository Commits
# --------------------------------

def get_repository_commits(
    owner,
    repo,
    limit=10
):

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/commits"
    )

    params = {
        "per_page": limit
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params
    )

    if response.status_code != 200:

        raise Exception(
            f"GitHub API error: "
            f"{response.status_code}"
        )

    return response.json()