import os
import re
import requests

USER = os.getenv("GITHUB_USER")
TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# =========================================================
# OWN RECENT REPOSITORIES
# =========================================================

response = requests.get(
    f"https://api.github.com/users/{USER}/repos?sort=updated&per_page=20",
    headers=headers,
    timeout=30
)

repos = response.json()

repo_lines = []

count = 0

for repo in repos:

    if repo.get("fork"):
        continue

    name = repo.get("name", "Unknown")

    description = repo.get("description") or "No description"

    language = repo.get("language") or "Config"

    stars = repo.get("stargazers_count", 0)

    line = (
        f"- 🚀 [{name}]({repo['html_url']}) "
        f"• {language} \n"
        f"  - {description}"
    )

    repo_lines.append(line)

    count += 1

    if count >= 5:
        break

recent_section = (
    "<div align=\"left\">\n\n"
    + "\n\n".join(repo_lines)
    + "\n\n</div>"
)

# =========================================================
# COLLABORATOR REPOSITORIES
# =========================================================

events_response = requests.get(
    f"https://api.github.com/users/{USER}/events/public",
    headers=headers,
    timeout=30
)

events = events_response.json()

collab_lines = []

seen = set()

count = 0

for event in events:

    repo_data = event.get("repo")

    if not repo_data:
        continue

    repo_name = repo_data.get("name")

    if not repo_name:
        continue

    owner = repo_name.split("/")[0]

    if owner.lower() == USER.lower():
        continue

    if repo_name in seen:
        continue

    seen.add(repo_name)

    repo_response = requests.get(
        f"https://api.github.com/repos/{repo_name}",
        headers=headers,
        timeout=30
    )

    if repo_response.status_code != 200:
        continue

    repo = repo_response.json()

    description = repo.get("description") or "No description"

    language = repo.get("language") or "Config"

    stars = repo.get("stargazers_count", 0)

    line = (
        f"- 🤝 [{repo_name}]({repo['html_url']}) "
        f"• {language}\n"
        f"  - {description}"
    )

    collab_lines.append(line)

    count += 1

    if count >= 5:
        break

collab_section = (
    "<div align=\"left\">\n\n"
    + "\n\n".join(collab_lines)
    + "\n\n</div>"
)

# =========================================================
# UPDATE README
# =========================================================

with open("README.md", "r", encoding="utf-8") as file:
    content = file.read()

# RECENT REPOS
recent_pattern = re.compile(
    r"<!--START_SECTION:recent_repos-->.*?<!--END_SECTION:recent_repos-->",
    re.DOTALL
)

recent_replacement = (
    "<!--START_SECTION:recent_repos-->\n"
    + recent_section +
    "\n<!--END_SECTION:recent_repos-->"
)

content = recent_pattern.sub(recent_replacement, content)

# COLLAB REPOS
collab_pattern = re.compile(
    r"<!--START_SECTION:collab_repos-->.*?<!--END_SECTION:collab_repos-->",
    re.DOTALL
)

collab_replacement = (
    "<!--START_SECTION:collab_repos-->\n"
    + collab_section +
    "\n<!--END_SECTION:collab_repos-->"
)

content = collab_pattern.sub(collab_replacement, content)

with open("README.md", "w", encoding="utf-8") as file:
    file.write(content)

print("README updated successfully")
