from app.github_api import get_repository


def get_repository_summary(owner, repository):
    repo = get_repository(owner, repository)

    return {
        "name": repo["name"],
        "description": repo["description"],
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "open_issues": repo["open_issues_count"],
        "watchers": repo["watchers_count"],
        "language": repo["language"],
        "created_at": repo["created_at"],
        "updated_at": repo["updated_at"],
        "size": repo["size"]
    }