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


def _handle_api_error(response):
    """
    Format a descriptive error message based on GitHub status code and headers.
    """
    status = response.status_code
    if status == 401:
        return Exception("GitHub API error: 401 Unauthorized. Check your GITHUB_TOKEN in .env.")
    elif status == 403:
        rate_limit_remaining = response.headers.get("x-ratelimit-remaining", "")
        if rate_limit_remaining == "0":
            return Exception("GitHub API error: 403 Rate limit exceeded. Add a GITHUB_TOKEN in .env to increase the limit to 5,000 req/hr.")
        return Exception("GitHub API error: 403 Forbidden. Access to this repository or resource was denied.")
    elif status == 404:
        return Exception(f"GitHub API error: 404 Not Found. Repository or file does not exist, or requires authentication.")
    return Exception(f"GitHub API error: {status}")


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
        raise _handle_api_error(response)

    return response.json()


# --------------------------------
# Get Git Trees (Fast 1-Request Tree API)
# --------------------------------

def get_repository_tree(
    owner,
    repo,
    tree_sha=None,
    recursive=True
):
    """
    Retrieve the entire repository file tree in a single API call using the Git Trees API.
    Supports up to 100,000 files in 1 request.
    """
    if not tree_sha:
        # Default to HEAD to follow the default branch
        tree_sha = "HEAD"

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/git/trees/{tree_sha}"
    )

    params = {}
    if recursive:
        params["recursive"] = "1"

    response = requests.get(
        url,
        headers=HEADERS,
        params=params
    )

    if response.status_code != 200:
        raise _handle_api_error(response)

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
        raise _handle_api_error(response)

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
        # Fallback: Try downloading directly with raw media type (handles files > 1MB)
        raw_headers = dict(HEADERS)
        raw_headers["Accept"] = "application/vnd.github.v3.raw"
        raw_resp = requests.get(url, headers=raw_headers)
        if raw_resp.status_code == 200:
            return raw_resp.text
        raise _handle_api_error(response)

    data = response.json()

    # If it's a directory, return empty message
    if isinstance(data, list):
        return "Directory contents cannot be viewed as a single source file."

    encoded_content = data.get(
        "content",
        ""
    )

    # If content is omitted (e.g. file > 1MB), use download_url or raw headers
    if not encoded_content:
        download_url = data.get("download_url")
        if download_url:
            raw_response = requests.get(download_url, headers=HEADERS)
            if raw_response.status_code == 200:
                return raw_response.text
        # Fallback raw header request
        raw_headers = dict(HEADERS)
        raw_headers["Accept"] = "application/vnd.github.v3.raw"
        raw_resp = requests.get(url, headers=raw_headers)
        if raw_resp.status_code == 200:
            return raw_resp.text

        return "No content available."

    try:
        decoded_content = base64.b64decode(
            encoded_content
        ).decode(
            "utf-8",
            errors="replace"
        )
        return decoded_content
    except Exception:
        return "Unable to decode file content."


# --------------------------------
# Get Repository Branches
# --------------------------------

def get_repository_branches(
    owner,
    repo
):

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/branches"
    )

    params = {
        "per_page": 100
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params
    )

    if response.status_code != 200:
        raise _handle_api_error(response)

    return response.json()


# --------------------------------
# Get Repository Commits
# --------------------------------

def get_repository_commits(
    owner,
    repo,
    limit=10
):

    try:
        branches = get_repository_branches(
            owner,
            repo
        )
    except Exception:
        branches = []

    all_commits = {}

    # If branches fetched successfully, inspect branches, otherwise fetch default commits
    if not branches:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"per_page": limit}
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            return response.json()[:limit]
        return []

    # --------------------------------
    # Fetch commits from each branch (up to 5 branches to preserve rate limit)
    # --------------------------------

    for branch in branches[:5]:

        branch_name = branch.get(
            "name"
        )

        if not branch_name:
            continue

        url = (
            f"https://api.github.com/repos/"
            f"{owner}/{repo}/commits"
        )

        params = {
            "sha": branch_name,
            "per_page": limit
        }

        response = requests.get(
            url,
            headers=HEADERS,
            params=params
        )

        if response.status_code != 200:
            continue

        branch_commits = response.json()
        if isinstance(branch_commits, list):
            for commit in branch_commits:
                sha = commit.get("sha")
                if sha:
                    all_commits[sha] = commit

    # --------------------------------
    # Sort commits by date
    # --------------------------------

    commits = list(
        all_commits.values()
    )

    commits.sort(
        key=lambda commit: (
            commit.get(
                "commit",
                {}
            )
            .get(
                "author",
                {}
            )
            .get(
                "date",
                ""
            )
        ),
        reverse=True
    )

    return commits[:limit]