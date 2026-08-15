from __future__ import annotations

import json
import re
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


USER = "LoganthP"
OUT = Path("data/contributions.json")


class ContributionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.days: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in {"td", "tool-tip"}:
            return
        data = {key: value or "" for key, value in attrs}
        day = data.get("data-date")
        level = data.get("data-level")
        count = data.get("data-count")
        if day:
            self.days.append(
                {
                    "date": day,
                    "count": int(count or 0),
                    "level": int(level or 0),
                }
            )


def fetch_html() -> str:
    url = f"https://github.com/users/{USER}/contributions"
    request = Request(url, headers={"User-Agent": "LoganthP profile README renderer"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_days(html: str) -> list[dict[str, object]]:
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        days = []
        for node in soup.select("[data-date]"):
            count = node.get("data-count") or "0"
            level = node.get("data-level") or "0"
            days.append({"date": node["data-date"], "count": int(count), "level": int(level)})
        if days:
            return days
    except Exception:
        pass

    parser = ContributionParser()
    parser.feed(html)
    if parser.days:
        return parser.days

    days = []
    pattern = re.compile(r'data-date="([^"]+)".*?data-level="(\d+)".*?data-count="(\d+)"', re.S)
    for day, level, count in pattern.findall(html):
        days.append({"date": day, "count": int(count), "level": int(level)})
    return days


def compute_stats(days: list[dict[str, object]]) -> dict[str, object]:
    by_date = {str(item["date"]): int(item.get("count", 0)) for item in days}
    today = date.today()
    current = 0
    cursor = today
    while by_date.get(cursor.isoformat(), 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    longest = 0
    active = 0
    for key in sorted(by_date):
        if by_date[key] > 0:
            active += 1
            longest = max(longest, active)
        else:
            active = 0

    monthly: dict[str, int] = {}
    for key, count in by_date.items():
        monthly[key[:7]] = monthly.get(key[:7], 0) + count

    return {
        "total": sum(by_date.values()),
        "current_streak": current,
        "longest_streak": longest,
        "monthly_totals": monthly,
    }


def main() -> None:
    html = fetch_html()
    days = parse_days(html)
    payload = {
        "user": USER,
        "generated_at": date.today().isoformat(),
        "days": days,
        "stats": compute_stats(days),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} with {len(days)} days.")


if __name__ == "__main__":
    main()
