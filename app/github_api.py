import requests
import base64
import os

from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


# Get GitHub token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# GitHub request headers
HEADERS = {
    "Accept": "application/vnd.github+json"
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def get_repository(owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(
        url,
        headers=HEADERS
    )

    if response.status_code != 200:
        raise Exception(
            f"GitHub API error: {response.status_code}"
        )

    return response.json()


def get_repository_contents(owner, repo, path=""):

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    response = requests.get(
        url,
        headers=HEADERS
    )

    if response.status_code != 200:
        raise Exception(
            f"GitHub API error: {response.status_code}"
        )

    return response.json()


def get_file_content(owner, repo, path):

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    response = requests.get(
        url,
        headers=HEADERS
    )

    if response.status_code != 200:
        raise Exception(
            f"GitHub API error: {response.status_code}"
        )

    data = response.json()

    encoded_content = data.get("content", "")

    if not encoded_content:
        return "No content available."

    decoded_content = base64.b64decode(
        encoded_content
    ).decode(
        "utf-8",
        errors="replace"
    )

    return decoded_content