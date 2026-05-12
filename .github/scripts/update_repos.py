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
    f"https://api.github.com/users/{USER}/repos?sort=updated&per_page=10",
    headers=headers,
    timeout=30
)

repos = response.json()

cards = []

count = 0

for repo in repos:

    if repo.get("fork"):
        continue

    name = repo["name"]

    card = f"""
<a href="https://github.com/{USER}/{name}">
  <img
    height="165"
    src="https://github-readme-stats.vercel.app/api/pin/?username={USER}&repo={name}&theme=tokyonight&hide_border=true"
  />
</a>
"""

    cards.append(card)

    count += 1

    if count >= 3:
        break

new_section = f"""
<div align="center">

{''.join(cards)}

</div>
"""

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