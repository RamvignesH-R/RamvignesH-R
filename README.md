name: Update Recent Repos in Profile README

on:
  schedule:
    - cron: "0 */12 * * *"
  workflow_dispatch:
  push:
    branches:
      - main
      - master

permissions:
  contents: write

jobs:
  update-recent-repos:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout profile repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Update recent repos section
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_USER: ${{ github.repository_owner }}

        run: |
          python <<'EOF'
          import os
          import re
          import requests

          user = os.getenv("GITHUB_USER")
          token = os.getenv("GITHUB_TOKEN")

          headers = {
              "Authorization": f"Bearer {token}",
              "Accept": "application/vnd.github+json"
          }

          response = requests.get(
              f"https://api.github.com/users/{user}/repos?sort=updated&per_page=3",
              headers=headers
          )

          repos = response.json()

          cards = []

          for repo in repos:

              if repo.get("fork"):
                  continue

              name = repo["name"]

              card = f'''
<a href="https://github.com/{user}/{name}">
  <img src="https://github-readme-stats.vercel.app/api/pin/?username={user}&repo={name}&theme=tokyonight&hide_border=true"/>
</a>
'''

              cards.append(card)

          new_block = f"""
<div align="center">

{''.join(cards)}

</div>
"""

          with open("README.md", "r", encoding="utf-8") as f:
              content = f.read()

          pattern = r"(<!--START_SECTION:recent_repos-->
<div align="center"><a href="https://github.com/RamvignesH-R/RamvignesH-R" target="_blank"><img src="https://github-readme-stats.vercel.app/api/pin/?username=RamvignesH-R&repo=RamvignesH-R&theme=tokyonight&hide_border=true&border_radius=15&show_icons=true&cache_seconds=86400" alt="RamvignesH-R repo card"/></a><a href="https://github.com/RamvignesH-R/Circuit-Verification-Using-Resolution" target="_blank"><img src="https://github-readme-stats.vercel.app/api/pin/?username=RamvignesH-R&repo=Circuit-Verification-Using-Resolution&theme=tokyonight&hide_border=true&border_radius=15&show_icons=true&cache_seconds=86400" alt="Circuit-Verification-Using-Resolution repo card"/></a><a href="https://github.com/RamvignesH-R/Privacy_Guard_AI_Chat_System" target="_blank"><img src="https://github-readme-stats.vercel.app/api/pin/?username=RamvignesH-R&repo=Privacy_Guard_AI_Chat_System&theme=tokyonight&hide_border=true&border_radius=15&show_icons=true&cache_seconds=86400" alt="Privacy_Guard_AI_Chat_System repo card"/></a></div><br><div align="center"><sub>• <b>RamvignesH-R</b> (Unknown) ⭐ 0<br>Config files for my GitHub profile.</sub><br><br><sub>• <b>Circuit-Verification-Using-Resolution</b> (Jupyter Notebook) ⭐ 0<br>An Artificial Intelligence exercise implementing propositional logic resolution and CNF-based reasoning using Python. The notebook demonstrates automated theorem proving, logical equivalence verification, and resolution refutation concepts in a practical learning-oriented workflow.</sub><br><br><sub>• <b>Privacy_Guard_AI_Chat_System</b> (Python) ⭐ 0<br>AI-powered privacy protection system that masks sensitive personal information from chats and documents before cloud AI processing using FastAPI, React, OCR, BiLSTM, and Transformer-based NLP models.</sub><br><br></div>
<!--END_SECTION:recent_repos-->)"

          updated = re.sub(
              pattern,
              r"\\1\n" + new_block + r"\n\\3",
              content,
              flags=re.DOTALL
          )

          with open("README.md", "w", encoding="utf-8") as f:
              f.write(updated)

          print("README updated successfully")

          EOF

      - name: Commit and push changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add README.md

          git diff --cached --quiet || git commit -m "chore: update recent repos"

          git push