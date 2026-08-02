#!/usr/bin/env python3
"""
Scrape the public contribution calendar for GITHUB_USERNAME and write
data/contributions.json with raw days plus derived stats (current streak,
longest streak, best day, monthly totals).

No GitHub token needed -- this hits the same public HTML fragment endpoint
GitHub's own profile page uses: https://github.com/users/<user>/contributions
"""
import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_PROFILE_USERNAME", "SSShogunn")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def fetch_days():
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day[data-date]")
    if not cells:
        raise RuntimeError(
            "No contribution cells found -- GitHub may have changed markup, "
            "or the username has no public calendar."
        )

    days = []
    for cell in cells:
        d = cell.get("data-date")
        level = int(cell.get("data-level", 0))
        days.append({"date": d, "level": level})

    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days):
    total = sum(1 for d in days if d["level"] > 0)

    # streaks (level > 0 counts as a contribution day)
    current_streak = 0
    longest_streak = 0
    running = 0
    today = date.today().isoformat()
    for d in days:
        if d["level"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    # current streak counts back from the most recent day with data
    for d in reversed(days):
        if d["date"] > today:
            continue
        if d["level"] > 0:
            current_streak += 1
        else:
            break

    monthly = defaultdict(int)
    for d in days:
        if d["level"] > 0:
            month_key = d["date"][:7]  # YYYY-MM
            monthly[month_key] += 1

    best_day = max(days, key=lambda x: x["level"]) if days else None

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day["date"] if best_day and best_day["level"] > 0 else None,
        "monthly_totals": dict(sorted(monthly.items())),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    days = fetch_days()
    stats = derive_stats(days)
    payload = {"username": USERNAME, "days": days, "stats": stats}

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote {len(days)} days ({stats['total_contributions']} contributions) -> {OUT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"fetch_contributions.py failed: {e}", file=sys.stderr)
        sys.exit(1)
