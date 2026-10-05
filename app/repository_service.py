from pathlib import Path
from app.github_api import (
    get_repository,
    get_repository_contents,
    get_repository_tree,
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

    if not isinstance(contents, list):
        if isinstance(contents, dict) and contents.get("type") == "file":
            return [{
                "name": contents["name"],
                "path": contents["path"],
                "type": "file"
            }]
        return []

    files = []
    for item in contents:
        files.append({
            "name": item.get("name", ""),
            "path": item.get("path", ""),
            "type": item.get("type", "file")
        })

    return files


def get_all_repository_files(owner, repo, path=""):
    """
    Retrieve all files in a repository.
    Uses the Git Trees API for fast single-call retrieval (up to 100k files in 1 request).
    Falls back to recursive contents API if tree lookup fails or specific subdirectory is requested.
    """
    if not path:
        try:
            tree_data = get_repository_tree(owner, repo, recursive=True)
            tree_items = tree_data.get("tree", [])

            if tree_items:
                all_files = []
                for item in tree_items:
                    # In Git Trees API: type 'blob' is a file, 'tree' is a directory
                    if item.get("type") == "blob":
                        item_path = item.get("path", "")
                        all_files.append({
                            "name": Path(item_path).name,
                            "path": item_path,
                            "type": "file"
                        })
                return all_files
        except Exception:
            # Fallback to recursive contents API if tree lookup is not supported or failed
            pass

    # Recursive fallback
    try:
        contents = get_repository_contents(owner, repo, path)
    except Exception:
        return []

    if not isinstance(contents, list):
        if isinstance(contents, dict) and contents.get("type") == "file":
            return [{
                "name": contents["name"],
                "path": contents["path"],
                "type": "file"
            }]
        return []

    all_files = []

    for item in contents:
        if item.get("type") == "file":
            all_files.append({
                "name": item["name"],
                "path": item["path"],
                "type": "file"
            })
        elif item.get("type") == "dir":
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
    try:
        # Check standard README locations directly
        for candidate in ["README.md", "readme.md", "README", "readme.markdown", "docs/README.md"]:
            try:
                content = get_file_content(owner, repo, candidate)
                if content and not content.startswith("Directory contents") and content != "No content available.":
                    return content
            except Exception:
                continue
    except Exception:
        pass

    all_files = get_all_repository_files(owner, repo)

    for file in all_files:
        if file["name"].lower().startswith("readme"):
            try:
                return get_file_content(
                    owner,
                    repo,
                    file["path"]
                )
            except Exception:
                pass

    return None


def get_recent_commits(owner, repo, limit=10):
    try:
        commits = get_repository_commits(
            owner,
            repo,
            limit
        )
    except Exception:
        return []

    recent_commits = []

    for commit in commits:
        if not isinstance(commit, dict):
            continue

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
    if not filename:
        return "Other"

    # Special file names
    lower_name = filename.lower()
    if lower_name in ("dockerfile", "containerfile"):
        return "Docker"
    if lower_name in ("makefile", "gnumakefile"):
        return "Makefile"
    if lower_name == "cmakelists.txt":
        return "CMake"

    if "." not in filename:
        return "Other"

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    extension_map = {
        # Python
        "py": "Python",
        "pyi": "Python",
        "ipynb": "Jupyter Notebook",
        # JavaScript / TypeScript
        "js": "JavaScript",
        "jsx": "JavaScript (React)",
        "mjs": "JavaScript",
        "cjs": "JavaScript",
        "ts": "TypeScript",
        "tsx": "TypeScript (React)",
        # Web & Styling
        "html": "HTML",
        "htm": "HTML",
        "css": "CSS",
        "scss": "SCSS",
        "sass": "Sass",
        "less": "Less",
        "vue": "Vue",
        "svelte": "Svelte",
        # Systems & Compiled
        "c": "C",
        "cpp": "C++",
        "cc": "C++",
        "cxx": "C++",
        "h": "C/C++ Header",
        "hpp": "C++ Header",
        "cs": "C#",
        "go": "Go",
        "rs": "Rust",
        "java": "Java",
        "kt": "Kotlin",
        "kts": "Kotlin",
        "scala": "Scala",
        "swift": "Swift",
        "m": "Objective-C",
        # Scripting & Dynamic
        "rb": "Ruby",
        "php": "PHP",
        "sh": "Shell",
        "bash": "Shell",
        "zsh": "Shell",
        "ps1": "PowerShell",
        "bat": "Batch",
        "cmd": "Batch",
        "lua": "Lua",
        "r": "R",
        "dart": "Dart",
        # Data & Config
        "json": "JSON",
        "yaml": "YAML",
        "yml": "YAML",
        "toml": "TOML",
        "xml": "XML",
        "sql": "SQL",
        "graphql": "GraphQL",
        "proto": "Protocol Buffers",
        "env": "Config",
        "ini": "Config",
        # Docs
        "md": "Markdown",
        "rst": "reStructuredText",
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
            file.get("name", "")
        )

        if language not in statistics:
            statistics[language] = 0

        statistics[language] += 1

    return statistics