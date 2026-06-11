import requests
import datetime
from datetime import datetime, timezone
import json

# ─── GitHub Auth ───────────────────────────────────────────────────────────────
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("GITHUB_TOKEN")
# ─── GitHub Auth ───────────────────────────────────────────────────────────────
# Personal Access Token — authenticated requests get 5000 req/hr vs 60 unauth.
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}
def _gh():
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

# ─── URL Parser ────────────────────────────────────────────────────────────────

def extract_repo(url):
    """Accept any GitHub URL form:
       https://github.com/owner/repo
       github.com/owner/repo
       owner/repo
    """
    url = url.strip().strip("/")
    # Remove protocol prefix if present
    for prefix in ("https://", "http://", "github.com/"):
        if url.startswith(prefix):
            url = url[len(prefix):]
    # url is now something like "github.com/owner/repo" or "owner/repo"
    if url.startswith("github.com/"):
        url = url[len("github.com/"):]
    parts = url.split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError("Please enter a valid GitHub URL — e.g. https://github.com/owner/repo")
    owner = parts[0]
    repo  = parts[1]
    return owner, repo


def extract_username(input_str):
    """
    Accept a GitHub profile URL or bare username.
      https://github.com/torvalds
      github.com/torvalds
      torvalds
    Returns the username string.
    """
    s = input_str.strip().strip("/")
    for prefix in ("https://", "http://", "github.com/"):
        if s.startswith(prefix):
            s = s[len(prefix):]
    if s.startswith("github.com/"):
        s = s[len("github.com/"):]
    # Take only the first segment (ignore sub-paths)
    username = s.split("/")[0]
    if not username:
        raise ValueError("Please enter a valid GitHub username or profile URL.")
    return username


def fetch_user_repos(username, sort="stars", limit=15):
    """
    Fetch a user's public repos.
    sort: 'stars' | 'updated'
    Returns a list of dicts with card-ready fields.
    """
    url = f"https://api.github.com/users/{username}/repos?per_page=100&type=public"
    res = requests.get(url, headers=_gh())

    if res.status_code == 404:
        raise ValueError(f"User '{username}' not found on GitHub.")
    if res.status_code != 200:
        raise ValueError(f"GitHub API error {res.status_code}: {res.json().get('message', 'Unknown error')}")

    raw = res.json()
    if not raw:
        return []

    # Sort
    if sort == "stars":
        raw.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)
    else:  # updated
        raw.sort(key=lambda r: r.get("updated_at", ""), reverse=True)

    repos = []
    for r in raw[:limit]:
        updated_raw = r.get("updated_at", "")
        try:
            updated_fmt = datetime.strptime(updated_raw, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y")
        except Exception:
            updated_fmt = "N/A"
        repos.append({
            "name":        r.get("name", ""),
            "full_name":   r.get("full_name", ""),
            "description": r.get("description") or "",
            "stars":       r.get("stargazers_count", 0),
            "forks":       r.get("forks_count", 0),
            "language":    r.get("language") or "",
            "updated":     updated_fmt,
            "updated_raw": updated_raw,  # ISO string for activity filtering
            "html_url":    r.get("html_url", ""),
            "owner":       r.get("owner", {}).get("login", username),
        })
    return repos


def get_commit_activity(owner, repo_name):
    """Return last 12 weeks of commit counts as {label: count} dict."""
    import time
    url = f"https://api.github.com/repos/{owner}/{repo_name}/stats/commit_activity"
    res = requests.get(url, headers=_gh())
    if res.status_code == 202:   # GitHub is computing — wait and retry once
        time.sleep(3)
        res = requests.get(url, headers=_gh())
    if res.status_code != 200:
        return {}
    data = res.json()
    if not isinstance(data, list) or not data:
        return {}
    result = {}
    for w in data[-12:]:
        try:
            label = datetime.fromtimestamp(w["week"]).strftime("%b %d")
        except Exception:
            label = "?"
        result[label] = w.get("total", 0)
    return result


# ─── GitHub API Calls ──────────────────────────────────────────────────────────

def fetch_repodata(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=_gh())
    return response.json()


def get_code_insights(owner, repo, branch="main"):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    res = requests.get(url, headers=_gh())
    if res.status_code != 200:
        # Try master branch as fallback
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
        res = requests.get(url, headers=_gh())
        if res.status_code != 200:
            return {"files": 0, "size_kb": 0}
    data = res.json()
    files = [item for item in data.get("tree", []) if item["type"] == "blob"]
    total_files = len(files)
    total_size = sum(f.get("size", 0) for f in files)
    return {
        "files": total_files,
        "size_kb": round(total_size / 1024, 2)
    }


def has_readme(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/README.md"
    res = requests.get(url, headers=_gh())
    return res.status_code == 200


def get_languages(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    res = requests.get(url, headers=_gh())
    if res.status_code != 200:
        return {}
    data = res.json()
    total = sum(data.values()) or 1
    return {lang: round((size / total) * 100, 2) for lang, size in data.items()}


def get_commit_count(owner, repo):
    """Fetch total commit count via the contributors stats endpoint."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page=1&anon=true"
    res = requests.get(url, headers=_gh())
    if res.status_code != 200:
        return "N/A"
    url2 = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=1"
    res2 = requests.get(url2, headers=_gh())
    if res2.status_code != 200:
        return "N/A"
    link = res2.headers.get("Link", "")
    if 'rel="last"' in link:
        import re
        match = re.search(r'page=(\d+)>; rel="last"', link)
        if match:
            return int(match.group(1))
    # If no pagination header, count returned items
    data2 = res2.json()
    return len(data2) if isinstance(data2, list) else "N/A"


# ─── Data Processing ────────────────────────────────────────────────────────────

def process_data(data):
    updated_raw = data.get("updated_at")
    updated_date = datetime.strptime(updated_raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return {
        "name": data.get("name", "N/A"),
        "full_name": data.get("full_name", "N/A"),
        "description": data.get("description") or "No description provided.",
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "issues": data.get("open_issues_count", 0),
        "watchers": data.get("watchers_count", 0),
        "branch": data.get("default_branch", "main"),
        "formatted_date": updated_date.strftime("%d %B %Y"),
        "updated_datetime": updated_date,
        "html_url": data.get("html_url", ""),
        "license": data.get("license", {}).get("name", "No License") if data.get("license") else "No License",
        "visibility": data.get("visibility", "public").capitalize(),
        "created_at": datetime.strptime(data.get("created_at"), "%Y-%m-%dT%H:%M:%SZ").strftime("%d %B %Y") if data.get("created_at") else "N/A",
    }


# ─── Scoring ────────────────────────────────────────────────────────────────────

def calculate_score(stars, issues, last_updated, total_files, readme_exists):
    score = 0

    # Popularity (max 30)
    if stars > 20000:
        score += 30
    elif stars > 5000:
        score += 25
    else:
        score += 15

    # Health (max 20)
    if stars > 0:
        ratio = issues / stars
        score += 20 if ratio < 0.02 else 10
    else:
        score += 10

    # Activity (max 20)
    days = (datetime.now(timezone.utc) - last_updated).days
    score += 20 if days < 30 else 10

    # Structure (max 15)
    score += 15 if total_files > 100 else 5

    # README (max 15)
    if readme_exists:
        score += 15

    return score


def get_repo_label(score):
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Average"
    else:
        return "Needs Improvement"


def generate_summary(stars, total_files, last_updated):
    popularity = (
        "highly popular" if stars > 20000
        else "moderately popular" if stars > 5000
        else "relatively niche"
    )
    days = (datetime.now(timezone.utc) - last_updated).days
    activity = "actively maintained" if days < 30 else "less frequently updated"
    return (
        f"This is a {popularity} repository with around {total_files} files "
        f"and is {activity}."
    )


# ─── High-level Wrapper (used by Streamlit UI) ─────────────────────────────────

def analyze_repo(owner, repo):
    """
    Fetch, process, and score a GitHub repository.
    Returns a dict with all data needed by the UI.
    Raises requests.exceptions.ConnectionError / ValueError on failure.
    """
    raw = fetch_repodata(owner, repo)

    if "message" in raw:
        raise ValueError(raw["message"])

    result = process_data(raw)
    insights = get_code_insights(owner, repo, branch=result["branch"])
    readme_exists = has_readme(owner, repo)
    languages = get_languages(owner, repo)
    commit_count = get_commit_count(owner, repo)

    score = calculate_score(
        result["stars"],
        result["issues"],
        result["updated_datetime"],
        insights["files"],
        readme_exists,
    )
    label = get_repo_label(score)
    summary = generate_summary(result["stars"], insights["files"], result["updated_datetime"])

    return {
        # Identity
        "name": result["name"],
        "full_name": result["full_name"],
        "description": result["description"],
        "html_url": result["html_url"],
        "visibility": result["visibility"],
        "license": result["license"],
        "created_at": result["created_at"],
        # Metrics
        "stars": result["stars"],
        "forks": result["forks"],
        "issues": result["issues"],
        "watchers": result["watchers"],
        "branch": result["branch"],
        "last_updated": result["formatted_date"],
        "readme": "Yes ✅" if readme_exists else "No ❌",
        "readme_exists": readme_exists,
        # Code insights
        "total_files": insights["files"],
        "size_kb": insights["size_kb"],
        "commit_count": commit_count,
        # Languages
        "languages": languages,
        # Score
        "score": score,
        "label": label,
        "summary": summary,
        "days_since_update": (datetime.now(timezone.utc) - result["updated_datetime"]).days,
    }


# ─── Report Generators ──────────────────────────────────────────────────────────

def generate_json_report(data: dict) -> str:
    """Serialise analysis dict to a pretty-printed JSON string."""
    serialisable = {
        k: v for k, v in data.items()
        if not callable(v)
    }
    return json.dumps(serialisable, indent=2, default=str)


def generate_pdf_report(data: dict) -> bytes:
    """
    Generate a simple PDF report as bytes using only stdlib (no reportlab).
    Returns UTF-8 encoded plain-text wrapped in a minimal valid PDF structure.
    """
    lines = [
        "GitHub Repository Analysis Report",
        "=" * 40,
        f"Repository   : {data.get('full_name', 'N/A')}",
        f"Description  : {data.get('description', 'N/A')}",
        f"Visibility   : {data.get('visibility', 'N/A')}",
        f"License      : {data.get('license', 'N/A')}",
        f"Created      : {data.get('created_at', 'N/A')}",
        f"Last Updated : {data.get('last_updated', 'N/A')}",
        "",
        "─── Metrics ───────────────────────────────",
        f"Stars        : {data.get('stars', 0)}",
        f"Forks        : {data.get('forks', 0)}",
        f"Open Issues  : {data.get('issues', 0)}",
        f"Watchers     : {data.get('watchers', 0)}",
        f"Total Files  : {data.get('total_files', 0)}",
        f"Repo Size    : {data.get('size_kb', 0)} KB",
        f"Commits      : {data.get('commit_count', 'N/A')}",
        f"README       : {data.get('readme', 'N/A')}",
        "",
        "─── Score ──────────────────────────────────",
        f"Overall Score: {data.get('score', 0)} / 100",
        f"Status       : {data.get('label', 'N/A')}",
        "",
        "─── Summary ────────────────────────────────",
        data.get('summary', ''),
        "",
        "─── Languages ──────────────────────────────",
    ]
    for lang, pct in data.get("languages", {}).items():
        lines.append(f"  {lang}: {pct}%")

    text = "\n".join(lines)

    # Minimal PDF (text-only, no external deps)
    pdf_content = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
  /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj
<< /Length {len(text) + 100} >>
stream
BT
/F1 10 Tf
50 750 Td
14 TL
"""
    for line in lines:
        safe_line = line.replace("(", "\\(").replace(")", "\\)").replace("\\", "\\\\")
        safe_line = safe_line.encode("ascii", "replace").decode("ascii")
        pdf_content += f"({safe_line}) Tj T*\n"

    pdf_content += """ET
endstream
endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Courier >> endobj
xref
0 6
trailer << /Size 6 /Root 1 0 R >>
startxref
0
%%EOF"""

    return pdf_content.encode("latin-1", errors="replace")


# ─── CLI Entry (kept for standalone testing) ────────────────────────────────────

def main():
    url = input("Enter github repo url: ")
    owner, repo = extract_repo(url)
    data = analyze_repo(owner, repo)
    print(generate_json_report(data))


if __name__ == "__main__":
    main()
