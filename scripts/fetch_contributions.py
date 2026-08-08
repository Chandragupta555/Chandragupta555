import json
import os
import re
import sys
import requests
from bs4 import BeautifulSoup


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "Chandragupta555"
    output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join("data", "contributions.json")

    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    print(f"Fetching GitHub contribution calendar for '{username}'...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error: Failed to fetch contributions from '{url}': {e}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")

    # Find day elements in the contribution grid table
    cells = soup.find_all(
        ["td", "rect"],
        class_=lambda c: c and "ContributionCalendar-day" in c
    )

    if not cells:
        print("Error: Could not find any contribution calendar day cells in the response HTML.", file=sys.stderr)
        sys.exit(1)

    days = []
    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue

        try:
            level = int(cell.get("data-level", 0))
        except ValueError:
            level = 0

        # Determine contribution count from data-count, tooltip, or aria/title attributes
        count = 0
        if cell.get("data-count") is not None:
            try:
                count = int(cell.get("data-count"))
            except ValueError:
                count = 0
        else:
            cell_id = cell.get("id")
            tooltip = soup.find("tool-tip", attrs={"for": cell_id}) if cell_id else None
            text_to_search = ""
            if tooltip and tooltip.text:
                text_to_search = tooltip.text.strip()
            elif cell.get("aria-label"):
                text_to_search = cell.get("aria-label").strip()
            elif cell.get("title"):
                text_to_search = cell.get("title").strip()

            if text_to_search:
                match = re.search(r"(\d+)\s+contribution", text_to_search)
                if match:
                    count = int(match.group(1))

        days.append({
            "date": date,
            "count": count,
            "level": level
        })

    if not days:
        print("Error: No valid day records parsed from contribution calendar.", file=sys.stderr)
        sys.exit(1)

    # Sort days chronologically
    days.sort(key=lambda d: d["date"])

    # Compute statistics
    total = sum(d["count"] for d in days)

    # Longest streak calculation
    longest_streak = 0
    current_count = 0
    for d in days:
        if d["count"] > 0:
            current_count += 1
            if current_count > longest_streak:
                longest_streak = current_count
        else:
            current_count = 0

    # Current streak calculation (backwards from latest date)
    current_streak = 0
    idx = len(days) - 1
    if days[idx]["count"] == 0 and idx > 0 and days[idx - 1]["count"] > 0:
        idx -= 1

    while idx >= 0 and days[idx]["count"] > 0:
        current_streak += 1
        idx -= 1

    # Best day
    best_day_record = max(days, key=lambda d: d["count"])
    best_day = {
        "date": best_day_record["date"],
        "count": best_day_record["count"]
    }

    # Monthly totals
    monthly_totals = {}
    for d in days:
        month_key = d["date"][:7]
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + d["count"]

    result = {
        "days": days,
        "stats": {
            "total": total,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "best_day": best_day,
            "monthly_totals": monthly_totals
        }
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"Writing contributions data to '{output_path}'...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Successfully processed {len(days)} days (Total contributions: {total}).")


if __name__ == "__main__":
    main()
