import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

OWNER = "DivyamKishor"
TOKEN = os.environ["GITHUB_TOKEN"]
API = "https://api.github.com"

def get(path, params=None):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "DivyamKishor-profile-stats",
        },
    )
    with urllib.request.urlopen(req) as response:
        return json.load(response)

def search_count(query):
    data = get("/search/issues", {"q": query, "per_page": 1})
    return data.get("total_count", 0)

# GitHub search gives us a useful lifetime-facing view of authored activity.
commit_count = search_count(f"author:{OWNER}")
merged_pr_count = search_count(f"author:{OWNER} is:pr is:merged")
open_pr_count = search_count(f"author:{OWNER} is:pr is:open")
repo_count = get(f"/users/{OWNER}/repos", {"per_page": 1, "type": "owner"}) .get("total_count", 0)

# GitHub's public REST API does not expose an exact lifetime contribution total,
# so the README labels these as searchable GitHub activity rather than claiming
# they are the contribution-graph total.
stats = f"""<!-- PROFILE_STATS_START -->
<p align="center">
  <img src="https://img.shields.io/badge/{commit_count}%2B-Commits-181717?style=for-the-badge&logo=git&logoColor=white" />
  <img src="https://img.shields.io/badge/{merged_pr_count}-Merged%20PRs-6f42c1?style=for-the-badge&logo=github&logoColor=white" />
  <img src="https://img.shields.io/badge/{open_pr_count}-Open%20PRs-2ea44f?style=for-the-badge&logo=github&logoColor=white" />
  <img src="https://img.shields.io/badge/{repo_count}-Repositories-0969da?style=for-the-badge&logo=github&logoColor=white" />
</p>

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username={OWNER}&show_icons=true&include_all_commits=true&hide_border=true&rank_icon=github" />
</p>

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username={OWNER}&layout=compact&hide_border=true&langs_count=8" />
</p>
<!-- PROFILE_STATS_END -->"""

readme = Path("README.md").read_text(encoding="utf-8")
start = "<!-- PROFILE_STATS_START -->"
end = "<!-- PROFILE_STATS_END -->"
if start not in readme or end not in readme:
    raise SystemExit("Profile stats markers were not found in README.md")

before = readme.split(start, 1)[0]
after = readme.split(end, 1)[1]
Path("README.md").write_text(before + stats + after, encoding="utf-8")

print(f"Updated profile stats: {commit_count} commits, {merged_pr_count} merged PRs, {open_pr_count} open PRs, {repo_count} repos")
