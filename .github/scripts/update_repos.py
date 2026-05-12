import os
import re
import requests

USER = os.getenv("GITHUB_USER")
TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

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

    name = repo["name"]

    description = repo.get("description") or "No description"

    language = repo.get("language") or "Unknown"

    stars = repo.get("stargazers_count", 0)

    line = (
        f"- 🚀 [{name}](https://github.com/{USER}/{name}) "
        f"• {language} • ⭐ {stars}\n"
        f"  - {description}"
    )

    repo_lines.append(line)

    count += 1

    if count >= 5:
        break

new_section = (
    "<div align=\"left\">\n\n"
    + "\n\n".join(repo_lines)
    + "\n\n</div>"
)

with open("README.md", "r", encoding="utf-8") as file:
    content = file.read()

pattern = r"(<!--START_SECTION:recent_repos-->)(.*?)(<!--END_SECTION:recent_repos-->)"

updated = re.sub(
    pattern,
    r"\1\n" + new_section + r"\n\3",
    content,
    flags=re.DOTALL
)

with open("README.md", "w", encoding="utf-8") as file:
    file.write(updated)

print("README updated successfully")
