from app.github_api import (
    get_repository,
    get_repository_contents,
    get_file_content
)


def get_repository_summary(owner, repo):

    repository = get_repository(
        owner,
        repo
    )

    return {
        "name": repository.get("name"),
        "full_name": repository.get("full_name"),
        "description": repository.get("description"),
        "language": repository.get("language"),
        "stars": repository.get("stargazers_count"),
        "forks": repository.get("forks_count"),
        "watchers": repository.get("watchers_count"),
        "open_issues": repository.get("open_issues_count"),
        "size": repository.get("size"),
        "default_branch": repository.get("default_branch"),
        "visibility": repository.get("visibility"),
        "created_at": repository.get("created_at"),
        "updated_at": repository.get("updated_at"),
        "html_url": repository.get("html_url"),
    }


def get_repository_files(owner, repo, path=""):

    contents = get_repository_contents(
        owner,
        repo,
        path
    )

    files = []

    for item in contents:

        files.append({
            "name": item["name"],
            "path": item["path"],
            "type": item["type"]
        })

    return files


def get_all_repository_files(
    owner,
    repo,
    path=""
):

    contents = get_repository_contents(
        owner,
        repo,
        path
    )

    all_files = []

    for item in contents:

        if item["type"] == "file":

            all_files.append({
                "name": item["name"],
                "path": item["path"],
                "type": "file"
            })

        elif item["type"] == "dir":

            folder_files = get_all_repository_files(
                owner,
                repo,
                item["path"]
            )

            all_files.extend(
                folder_files
            )

    return all_files


def get_source_code(owner, repo, path):

    return get_file_content(
        owner,
        repo,
        path
    )