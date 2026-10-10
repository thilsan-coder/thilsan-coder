import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

MAX_REPOS = 30  # change this number to show fewer or more projects

user = os.environ.get("GH_USER", "thilsan-coder")

# language -> (badge color, simple-icons logo, logo color)
LANGS = {
    "PHP": ("777BB4", "php", "white"),
    "JavaScript": ("F7DF1E", "javascript", "black"),
    "TypeScript": ("3178C6", "typescript", "white"),
    "Dart": ("0175C2", "dart", "white"),
    "Blade": ("FF2D20", "laravel", "white"),
    "HTML": ("E34F26", "html5", "white"),
    "CSS": ("1572B6", "css3", "white"),
    "Python": ("3776AB", "python", "white"),
    "C#": ("512BD4", "csharp", "white"),
    "Vue": ("4FC08D", "vuedotjs", "white"),
    "Kotlin": ("7F52FF", "kotlin", "white"),
}


def lang_badge(lang):
    if not lang:
        return "-"
    color, logo, logo_color = LANGS.get(lang, ("555555", "", "white"))
    name = urllib.parse.quote(lang, safe="")
    url = f"https://img.shields.io/badge/{name}-{color}?style=flat-square&labelColor=0d1117"
    if logo:
        url += f"&logo={logo}&logoColor={logo_color}"
    return f"![{lang}]({url})"


req = urllib.request.Request(
    f"https://api.github.com/users/{user}/repos?sort=pushed&per_page=100",
    headers={"Accept": "application/vnd.github+json", "User-Agent": "readme-updater"},
)
token = os.environ.get("GITHUB_TOKEN")
if token:
    req.add_header("Authorization", f"Bearer {token}")

with urllib.request.urlopen(req, timeout=30) as resp:
    all_repos = json.load(resp)

repos = [r for r in all_repos if not r["fork"] and r["name"].lower() != user.lower()]
total = len(repos)
repos = repos[:MAX_REPOS]

now = datetime.now(timezone.utc)
lines = [
    f"> 📦 **{total} projects** · 🔄 auto-updated daily · 🔥 = updated in the last 7 days",
    "",
    "| # | Project | Description | Tech | Last updated |",
    "|:-:|---|---|:-:|:-:|",
]
for i, r in enumerate(repos, 1):
    pushed = datetime.strptime(r["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    fire = " 🔥" if (now - pushed).days <= 7 else ""
    desc = (r["description"] or "—").replace("|", "/")
    date = pushed.strftime("%d %b %Y")
    lines.append(
        f"| {i} | 📁 **[{r['name']}]({r['html_url']})**{fire} | {desc} | {lang_badge(r['language'])} | {date} |"
    )
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
print(f"Updated: showing {len(repos)} of {total} projects")
