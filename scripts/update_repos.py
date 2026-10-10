import json
import os
import re
import urllib.request

user = os.environ.get("GH_USER", "thilsan-coder")
url = f"https://api.github.com/users/{user}/repos?sort=pushed&per_page=20"
req = urllib.request.Request(
    url,
    headers={"Accept": "application/vnd.github+json", "User-Agent": "readme-updater"},
)
token = os.environ.get("GITHUB_TOKEN")
if token:
    req.add_header("Authorization", f"Bearer {token}")

with urllib.request.urlopen(req, timeout=30) as resp:
    repos = json.load(resp)

repos = [r for r in repos if not r["fork"] and r["name"].lower() != user.lower()][:5]

lines = ["| Repository | Description | Language | Last updated |", "|---|---|---|---|"]
for r in repos:
    desc = (r["description"] or "-").replace("|", "/")
    lang = r["language"] or "-"
    lines.append(f"| [{r['name']}]({r['html_url']}) | {desc} | {lang} | {r['pushed_at'][:10]} |")
block = "\n".join(lines)

with open("README.md", encoding="utf-8") as f:
    text = f.read()

pattern = re.compile(r"(<!--START_SECTION:repos-->)(.*?)(<!--END_SECTION:repos-->)", re.S)
if not pattern.search(text):
    raise SystemExit("Markers not found in README.md")

new_text = pattern.sub(lambda m: f"{m.group(1)}\n{block}\n{m.group(3)}", text)
if new_text != text:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_text)
print(f"Updated with {len(repos)} repos")
