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

search_response = requests.get(
    f"https://api.github.com/search/repositories?q=user:{USER}",
    headers=headers,
    timeout=30
)

search_data = search_response.json()

collab_lines = []

count = 0

for repo in search_data.get("items", []):

    owner = repo["owner"]["login"]

    # Skip your own repositories
    if owner.lower() == USER.lower():
        continue

    name = repo["name"]

    description = repo.get("description") or "No description"

    language = repo.get("language") or "Unknown"

    stars = repo.get("stargazers_count", 0)

    line = (
        f"- 🤝 [{owner}/{name}]({repo['html_url']}) "
        f"• {language} \n"
        f"  - {description}"
    )

    collab_lines.append(line)

    count += 1

    if count >= 5:
        break

if not collab_lines:

    collab_lines.append(
        "- No public collaborator repositories found."
    )

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
