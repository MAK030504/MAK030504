#!/usr/bin/env python3
"""Save the public GitHub contribution calendar. No token and no GraphQL."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"
USER = os.environ.get("GITHUB_USER", "MAK030504")


def parse_calendar(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    days: list[dict] = []
    for cell in soup.select("td.ContributionCalendar-day"):
        day = cell.get("data-date")
        if not day:
            continue
        level = int(cell.get("data-level") or 0)
        tip = soup.find("tool-tip", attrs={"for": cell.get("id")})
        days.append(
            {
                "date": day,
                "count": _count_from_tip(tip.get_text(" ", strip=True) if tip else ""),
                "level": level,
            }
        )
    days.sort(key=lambda item: item["date"])
    return days


def _count_from_tip(text: str) -> int:
    lowered = text.lower()
    if not text or lowered.startswith("no contribution"):
        return 0
    match = re.match(r"([\d,]+)", text.strip())
    if not match:
        return 0
    return int(match.group(1).replace(",", ""))


def streak_stats(days: list[dict], today: date | None = None) -> dict:
    today = today or datetime.now(timezone.utc).date()
    parsed = [(date.fromisoformat(item["date"]), item["count"]) for item in days]
    longest = 0
    run = 0
    previous: date | None = None
    for day, count in parsed:
        if count > 0 and previous is not None and day == previous + timedelta(days=1):
            run += 1
        elif count > 0:
            run = 1
        else:
            run = 0
        longest = max(longest, run)
        previous = day

    current = 0
    for day, count in reversed(parsed):
        if count > 0:
            current += 1
            continue
        # An empty today (or a still-empty yesterday while today has not posted)
        # does not break a streak that ended on the previous active day.
        if current == 0 and day >= today - timedelta(days=1):
            continue
        break

    best = max(days, key=lambda item: item["count"]) if days else None
    return {
        "total": sum(item["count"] for item in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best["date"] if best else None,
        "best_count": best["count"] if best else 0,
    }


def heading_total(html: str) -> int | None:
    soup = BeautifulSoup(html, "html.parser")
    node = soup.select_one("h2")
    if node is None:
        return None
    match = re.search(r"([\d,]+)\s+contributions", node.get_text(" ", strip=True))
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def fetch_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (profile-readme)"},
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def build_payload(html: str, username: str) -> dict:
    days = parse_calendar(html)
    stats = streak_stats(days)
    reported = heading_total(html)
    return {
        "username": username,
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "reported_total": reported,
        **stats,
        "days": days,
    }


def main() -> None:
    html_path = sys.argv[1] if len(sys.argv) > 1 else ""
    html = Path(html_path).read_text(encoding="utf-8") if html_path else fetch_html(USER)
    payload = build_payload(html, USER)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"wrote {OUT} days={len(payload['days'])} total={payload['total']} "
        f"streak={payload['current_streak']} longest={payload['longest_streak']}"
    )


if __name__ == "__main__":
    main()
