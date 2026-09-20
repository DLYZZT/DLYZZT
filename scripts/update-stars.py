#!/usr/bin/env python3
"""Render GitHub star cards using public repository data and the Python stdlib."""

import argparse
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def fetch_repositories(username):
    repositories = []
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-star-card"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    page = 1
    while True:
        query = urlencode({"type": "owner", "per_page": 100, "page": page})
        request = Request(f"https://api.github.com/users/{username}/repos?{query}", headers=headers)
        with urlopen(request, timeout=30) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError("Expected a repository list from GitHub")
        repositories.extend(batch)
        if len(batch) < 100:
            return repositories
        page += 1


def summarize(repositories, username):
    owned = {
        repo["id"]: repo
        for repo in repositories
        if not repo["private"] and repo["owner"]["login"].casefold() == username.casefold()
    }
    ordered = sorted(owned.values(), key=lambda repo: (-repo["stargazers_count"], repo["name"].casefold()))
    return {
        "total": sum(repo["stargazers_count"] for repo in ordered),
        "repositories": len(ordered),
        "starred": sum(repo["stargazers_count"] > 0 for repo in ordered),
        "top": [repo for repo in ordered if repo["stargazers_count"] > 0][:2],
    }


def render(stats, username, updated, dark=False):
    bg, fg, muted, border, panel, accent = (
        ("#0d1117", "#e6edf3", "#a0acc0", "#30363d", "#161b22", "#a5b4fc")
        if dark else
        ("#ffffff", "#17213b", "#5c6a85", "#dce3f2", "#f1f3fc", "#6366f1")
    )
    rows = []
    largest = stats["top"][0]["stargazers_count"] if stats["top"] else 1
    for index, repo in enumerate(stats["top"]):
        y = 90 + index * 43
        name = escape(repo["name"] if len(repo["name"]) <= 32 else repo["name"][:29] + "…")
        count = repo["stargazers_count"]
        rows.append(f'''<text x="390" y="{y}" fill="{fg}" font-size="15">{name}</text>
<text x="860" y="{y}" fill="{accent}" text-anchor="end" font-size="15" font-weight="600">{count:,}</text>
<rect x="390" y="{y + 10}" width="470" height="5" rx="2.5" fill="{panel}"/>
<rect x="390" y="{y + 10}" width="{470 * count / largest:.2f}" height="5" rx="2.5" fill="url(#accent)"/>''')
    if not rows:
        rows.append(f'<text x="390" y="135" fill="{muted}" font-size="16">Every project starts with an idea.</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="204" viewBox="0 0 900 204" role="img" aria-labelledby="title desc">
<title id="title">{escape(username)} · GitHub Stars</title>
<desc id="desc">{stats['total']:,} stars received across {stats['repositories']} public repositories. {stats['starred']} repositories have stars. Updated {escape(updated)}.</desc>
<defs><linearGradient id="accent"><stop stop-color="#38bdf8"/><stop offset="1" stop-color="#818cf8"/></linearGradient></defs>
<rect x=".5" y=".5" width="899" height="203" rx="16" fill="{bg}" stroke="{border}"/>
<g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Arial, sans-serif">
<text x="32" y="41" fill="{accent}" font-size="15" font-weight="600" letter-spacing="1.5">★ GITHUB STARS</text>
<text x="32" y="135" fill="{fg}" font-size="72" font-weight="700" letter-spacing="-3">{stats['total']:,}</text>
<path d="M352 66V148" stroke="{border}"/>
<text x="390" y="41" fill="{muted}" font-size="12" letter-spacing="1.5">MOST STARRED</text>
{''.join(rows)}
<path d="M32 168H868" stroke="{border}"/>
<text x="32" y="190" fill="{muted}" font-size="11">@{escape(username)} · PUBLIC REPOSITORIES</text>
<text x="868" y="190" fill="{muted}" font-size="11" text-anchor="end">UPDATED {escape(updated)}</text>
</g></svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="DLYZZT")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "assets")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", args.username):
        parser.error("Invalid GitHub username")
    stats = summarize(fetch_repositories(args.username), args.username)
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # Fetch everything successfully before replacing either card.
    cards = {
        "github-stars-light.svg": render(stats, args.username, updated),
        "github-stars-dark.svg": render(stats, args.username, updated, dark=True),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in cards.items():
        path = args.output_dir / filename
        temporary = path.with_suffix(".svg.tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)
    print(json.dumps({"total_stars": stats["total"], "public_repositories": stats["repositories"], "updated": updated}))


if __name__ == "__main__":
    main()
