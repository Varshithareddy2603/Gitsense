from app.github_api import (
    get_repository,
    get_repository_contents,
    get_file_content,
    get_repository_commits
)


def get_repository_summary(owner, repo):
    repository = get_repository(owner, repo)

    return {
        "name": repository.get("name"),
        "full_name": repository.get("full_name"),
        "description": repository.get("description"),
        "language": repository.get("language"),
        "stars": repository.get("stargazers_count"),
        "forks": repository.get("forks_count"),
        "watchers": repository.get("watchers"),
        "open_issues": repository.get("open_issues_count"),
        "size": repository.get("size"),
        "default_branch": repository.get("default_branch"),
        "visibility": repository.get("visibility"),
        "created_at": repository.get("created_at"),
        "updated_at": repository.get("updated_at"),
        "html_url": repository.get("html_url"),
    }


def get_repository_files(owner, repo, path=""):
    contents = get_repository_contents(owner, repo, path)

    files = []

    for item in contents:
        files.append({
            "name": item["name"],
            "path": item["path"],
            "type": item["type"]
        })

    return files


def get_all_repository_files(owner, repo, path=""):
    contents = get_repository_contents(owner, repo, path)

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

            all_files.extend(folder_files)

    return all_files


def get_source_code(owner, repo, path):
    return get_file_content(owner, repo, path)


def get_readme(owner, repo):
    all_files = get_all_repository_files(owner, repo)

    for file in all_files:

        if file["name"].lower() == "readme.md":
            return get_file_content(
                owner,
                repo,
                file["path"]
            )

    return None


def get_recent_commits(owner, repo, limit=10):
    commits = get_repository_commits(
        owner,
        repo,
        limit
    )

    recent_commits = []

    for commit in commits:

        commit_data = commit.get(
            "commit",
            {}
        )

        author = commit_data.get(
            "author",
            {}
        )

        recent_commits.append({
            "sha": commit.get(
                "sha",
                ""
            )[:7],

            "message": commit_data.get(
                "message",
                "No commit message"
            ).split("\n")[0],

            "author": author.get(
                "name",
                "Unknown"
            ),

            "date": author.get(
                "date",
                ""
            ),

            "url": commit.get(
                "html_url",
                ""
            )
        })

    return recent_commits


def get_file_extension(filename):
    if "." not in filename:
        return "Other"

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    extension_map = {
        "py": "Python",
        "js": "JavaScript",
        "jsx": "JavaScript",
        "ts": "TypeScript",
        "tsx": "TypeScript",
        "java": "Java",
        "c": "C",
        "cpp": "C++",
        "h": "C/C++ Header",
        "hpp": "C++ Header",
        "cs": "C#",
        "html": "HTML",
        "css": "CSS",
        "json": "JSON",
        "xml": "XML",
        "sql": "SQL",
        "md": "Markdown",
        "yaml": "YAML",
        "yml": "YAML",
        "sh": "Shell",
        "bat": "Batch",
        "txt": "Text"
    }

    return extension_map.get(
        extension,
        extension.upper()
    )


def get_file_statistics(owner, repo):
    all_files = get_all_repository_files(
        owner,
        repo
    )

    statistics = {}

    for file in all_files:

        language = get_file_extension(
            file["name"]
        )

        if language not in statistics:
            statistics[language] = 0

        statistics[language] += 1

    return statistics