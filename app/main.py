from github_api import get_repository


def main():
    data = get_repository("Varshithareddy2603", "GitSense")

    print("Repository:", data["name"])
    print("Owner:", data["owner"]["login"])
    print("Stars:", data["stargazers_count"])
    print("Forks:", data["forks_count"])
    print("Open Issues:", data["open_issues_count"])
    print("Language:", data["language"])


if __name__ == "__main__":
    main()