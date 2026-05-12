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

    name = repo.get("name", "Unknown")

    description = repo.get("description") or "No description"

    language = repo.get("language") or "Unknown"

    stars = repo.get("stargazers_count", 0)

    line = (
        f"- 🚀 [{name}](https://github.com/{USER}/{name}) "
        f"• {language} \n"
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

start_marker = "<!--START_SECTION:recent_repos-->"
end_marker = "<!--END_SECTION:recent_repos-->"

pattern = re.compile(
    f"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
    re.DOTALL
)

replacement = (
    f"{start_marker}\n"
    f"{new_section}\n"
    f"{end_marker}"
)

updated_content = pattern.sub(replacement, content)

with open("README.md", "w", encoding="utf-8") as file:
    file.write(updated_content)

print("README updated successfully")
