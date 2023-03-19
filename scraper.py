import argparse
import shutil
import stat
import requests
import os
from git import Repo

# defining a function that force removes read only documents
def removeReadOnly(func, path, excinfo):
    # Using os.chmod with stat.S_IWRITE to allow write permissions
    os.chmod(path, stat.S_IWRITE)
    func(path)

class GitHubStats:
    def __init__(self, repo_url, token=None):
        self.owner, self.repo = repo_url.split("/")[-2:]
        self.token = token
        self.repo = self.repo.split('.git')[0]

    def fetch_repo_info(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            repo_info = response.json()
            print(f"Repository name: {repo_info['name']}")
            print(f"Repository owner: {repo_info['owner']['login']}")
            print(f"Repository description: {repo_info['description']}")
            print(f"Repository created at: {repo_info['created_at']}")
        else:
            print("Failed to fetch repository information.",response.json())

    def fetch_contributors(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contributors"
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            contributors = response.json()
            for contributor in contributors:
                print(f"{contributor['login']}: {contributor['contributions']} contributions")
        else:
            print("Failed to fetch contributor information.")

    def fetch_issues_and_pull_requests(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues"
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        params = {
            "state": "all",
            "per_page": 1,
            "page": 1
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            issues = response.json()
            num_issues = issues[0]['number'] if len(issues) > 0 else 0
            print(f"Number of issues: {num_issues}")

            params = {
                "state": "all",
                "per_page": 1,
                "page": 1,
                "pull_request": "all"
            }
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                pull_requests = response.json()
                num_pull_requests = pull_requests[0]['number'] if len(pull_requests) > 0 else 0
                print(f"Number of pull requests: {num_pull_requests}")
            else:
                print("Failed to fetch pull request information.")
        else:
            print("Failed to fetch issue information.")

    def fetch_commit_history(self):
        repo_url = f"https://github.com/{self.owner}/{self.repo+'.git'}"
        repo_dir =  "temp_repo\\"+self.repo
        try:
            print("Repo Cloning operation locally initiated !!!!")
            Repo.clone_from(repo_url,repo_dir)
        except:
            print("Repo present in the local already !!!")
        repo = Repo(repo_dir,search_parent_directories=True)
        commits = list(repo.iter_commits())
        print(f"Number of commits: {len(commits)}")
        # path = os.path.join(os.getcwd(), repo_dir)
        # print(path)
        # shutil.rmtree(path,onerror=removeReadOnly)
        # os.remove(path)



    def run(self):
        print("=" * 60)
        self.fetch_repo_info()
        print("=" * 60)
        self.fetch_contributors()
        print("=" * 60)
        self.fetch_issues_and_pull_requests()
        print("=" * 60)
        self.fetch_commit_history()
        print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch GitHub repository statistics and insights.")
    parser.add_argument("repo_url", help="URL of the GitHub repository.")
    parser.add_argument("--token", help="GitHub personal access token.")

    args = parser.parse_args()

    gh_stats = GitHubStats(args.repo_url, args.token)
    gh_stats.run()
