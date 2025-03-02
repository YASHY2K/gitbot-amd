import requests
import os
import subprocess
import json

# GitHub API Details
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Make sure to set this in your environment
GITHUB_ORG = "RuchaKhairnar"  # Replace with your actual org
REPO_NAME = "Hack_cu"  # Replace with your actual repo name
GITHUB_API = f"https://api.github.com/repos/{GITHUB_ORG}/{REPO_NAME}"


def github_request(url):
    """Makes a GitHub API request and handles errors."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": f"HTTP {response.status_code}: {response.text}"}

    return response.json()


# 📌 1️⃣ Repository Info
repo_info = github_request(GITHUB_API)
repo_data = {
    "name": repo_info.get("name", "Unknown"),
    "description": repo_info.get("description", "No description"),
    "default_branch": repo_info.get("default_branch", "Unknown"),
    "url": repo_info.get("html_url", "No URL")
}

# 📌 2️⃣ Active Branches + Ahead/Behind Status
branches = github_request(f"{GITHUB_API}/branches")
branch_data = []
if isinstance(branches, list):
    for branch in branches:
        branch_name = branch.get("name", "Unknown")
        compare_url = f"{GITHUB_API}/compare/{branch_name}...origin/{branch_name}"
        compare_data = github_request(compare_url)

        branch_data.append({
            "name": branch_name,
            "ahead_by": compare_data.get("ahead_by", 0),
            "behind_by": compare_data.get("behind_by", 0)
        })

# 📌 3️⃣ Recent Commits
commits = github_request(f"{GITHUB_API}/commits?per_page=5")
commit_data = []
if isinstance(commits, list):
    for commit in commits:
        commit_data.append({
            "sha": commit.get("sha", "Unknown")[:7],
            "message": commit.get("commit", {}).get("message", "No message"),
            "author": commit.get("commit", {}).get("author", {}).get("name", "Unknown Author")
        })

# 📌 4️⃣ Local Changes
try:
    modified_files = subprocess.check_output(["git", "status", "--porcelain"]).decode().strip().split("\n")
    modified_files = [line[3:] for line in modified_files if line]
except:
    modified_files = ["Error fetching local changes"]

# 📌 5️⃣ Open Pull Requests
pull_requests = github_request(f"{GITHUB_API}/pulls?state=open")
pr_data = []
if isinstance(pull_requests, list):
    for pr in pull_requests:
        pr_data.append({
            "id": pr.get("number", "Unknown"),
            "title": pr.get("title", "No Title"),
            "author": pr.get("user", {}).get("login", "Unknown")
        })

# 📌 6️⃣ Recent Contributor Activity
contributors = github_request(f"{GITHUB_API}/contributors")
contributor_data = []
if isinstance(contributors, list):
    for contributor in contributors[:5]:  # Show top 5 contributors
        contributor_data.append({
            "name": contributor.get("login", "Unknown User"),
            "contributions": contributor.get("contributions", 0)
        })

# 📌 7️⃣ Open Issues
issues = github_request(f"{GITHUB_API}/issues?state=open")
issue_data = []
if isinstance(issues, list):
    for issue in issues[:5]:  # Show top 5 issues
        issue_data.append({
            "id": issue.get("number", "Unknown"),
            "title": issue.get("title", "No Title"),
            "assignee": issue.get("assignee", {}).get("login", "Unassigned")
        })

# 📌 Combine All Data
repo_context = {
    "repository": repo_data,
    "branches": branch_data,
    "recent_commits": commit_data,
    "local_changes": modified_files,
    "pull_requests": pr_data,
    "contributors": contributor_data,
    "open_issues": issue_data
}

# 📌 Print JSON Output
print(json.dumps(repo_context, indent=4))

json_filename = f"{REPO_NAME}_context.json"
with open(json_filename, "w", encoding="utf-8") as json_file:
    json.dump(repo_context, json_file, indent=4)
