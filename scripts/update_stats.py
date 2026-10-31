#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""
Automatic update of the Moonbot public statistics and the trade screenshot from Telegram.
Fetches the public JSON from https://stat.moonbot.pro/ and updates:
  - assets/stats-current-month.svg
  - stats/YYYY-MM.md and stats/README.md
  - assets/featured-trade.jpg (from https://t.me/s/MoonBot_Profit)
  - README.md (between the <!-- STATS:START --> and <!-- STATS:END --> markers)
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
STATS_DIR = ROOT / "stats"

MONTH_MAP = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

# Month name forms used in the generated text: (heading, in date phrases, short label)
MONTH_RU = {
    "January": ("January", "January", "Jan"),
    "February": ("February", "February", "Feb"),
    "March": ("March", "March", "Mar"),
    "April": ("April", "April", "Apr"),
    "May": ("May", "May", "May"),
    "June": ("June", "June", "Jun"),
    "July": ("July", "July", "Jul"),
    "August": ("August", "August", "Aug"),
    "September": ("September", "September", "Sep"),
    "October": ("October", "October", "Oct"),
    "November": ("November", "November", "Nov"),
    "December": ("December", "December", "Dec"),
}


def fetch_json(url: str):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Moonbot-GitHub-Stats-Updater/1.0 (+https://moonbot.pro)"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_int(val) -> int:
    if isinstance(val, (int, float)):
        return int(round(val))
    return int(re.sub(r"[^\d-]", "", str(val)) or "0")


def fmt_spaced(n: int) -> str:
    sign = "-" if n < 0 else ""
    s = f"{abs(n):,}".replace(",", " ")
    return f"{sign}{s}"


def fmt_signed_usd(n: int) -> str:
    abs_s = fmt_spaced(abs(n))
    if n >= 0:
        return f"+${abs_s}"
    return f"−${abs_s}"


def fmt_month_ru(raw_d: str) -> str:
    parts = raw_d.strip().split()
    if len(parts) == 2 and parts[1] in MONTH_RU:
        return f"{MONTH_RU[parts[1]][0]} {parts[0]}"
    return raw_d


def parse_day_entry(raw_d: str) -> tuple[int, str, int] | None:
    m = re.match(r"^(\d{4})\s+(\d+)(?:st|nd|rd|th)\s+([A-Za-z]+)$", raw_d.strip())
    if not m:
        return None
    return int(m.group(1)), m.group(3), int(m.group(2))


def render_daily_svg(year: int, month_name: str, daily_rows: list[tuple[int, float]]) -> str:
    width, height = 720, 220
    pad_l, pad_r, pad_t, pad_b = 58, 14, 18, 28
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    vals = [v for _, v in daily_rows] or [0.0]
    max_v = max(max(vals), 10000.0)
    min_v = min(min(vals), -10000.0)
    span = (max_v - min_v) or 1.0
    zero_y = pad_t + (max_v / span) * plot_h

    n = max(len(daily_rows), 1)
    step = plot_w / n
    bar_w = max(6.0, min(16.0, step * 0.68))
    ru_nom, _, ru_short = MONTH_RU.get(month_name, (month_name, month_name, month_name[:3]))

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="Daily net result of Moonbot users for {ru_nom} {year}, USD">',
        "  <style>",
        '    .axis { stroke: #8b949e; stroke-opacity: 0.35; stroke-width: 1; }',
        '    .grid { stroke: #8b949e; stroke-opacity: 0.16; stroke-width: 1; stroke-dasharray: 3 3; }',
        '    .lbl { fill: #6e7781; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 11px; }',
        '    .pos { fill: #2da44e; }',
        '    .neg { fill: #cf222e; }',
        "  </style>",
        f'  <line class="grid" x1="{pad_l}" y1="{pad_t:.1f}" x2="{width - pad_r}" y2="{pad_t:.1f}"/>',
        f'  <line class="axis" x1="{pad_l}" y1="{zero_y:.1f}" x2="{width - pad_r}" y2="{zero_y:.1f}"/>',
        f'  <line class="grid" x1="{pad_l}" y1="{pad_t + plot_h:.1f}" x2="{width - pad_r}" y2="{pad_t + plot_h:.1f}"/>',
        f'  <text class="lbl" x="{pad_l - 6}" y="{pad_t + 4:.1f}" text-anchor="end">+${int(round(max_v / 1000))}k</text>',
        f'  <text class="lbl" x="{pad_l - 6}" y="{zero_y + 4:.1f}" text-anchor="end">$0</text>',
        f'  <text class="lbl" x="{pad_l - 6}" y="{pad_t + plot_h + 4:.1f}" text-anchor="end">−${abs(int(round(min_v / 1000)))}k</text>',
    ]

    for idx, (day_num, val) in enumerate(daily_rows):
        x = pad_l + idx * step + (step - bar_w) * 0.5
        h = max(2.0, abs(val) / span * plot_h)
        y = (zero_y - h) if val >= 0 else zero_y
        cls = "pos" if val >= 0 else "neg"
        sign_str = fmt_signed_usd(int(round(val)))
        lines.append(
            f'  <rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="2">'
            f"<title>{ru_short} {day_num}: {sign_str}</title></rect>"
        )
        if day_num == 1 or day_num % 5 == 0 or idx == len(daily_rows) - 1:
            cx = x + bar_w * 0.5
            lines.append(
                f'  <text class="lbl" x="{cx:.1f}" y="{height - 8}" text-anchor="middle">{day_num}</text>'
            )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def update_featured_trade() -> None:
    try:
        req = urllib.request.Request(
            "https://t.me/s/MoonBot_Profit",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="ignore")
        blocks = html.split("tgme_widget_message_wrap")
        for block in reversed(blocks[1:]):
            img_m = re.search(r"background-image:url\('(https://cdn[^']+)'\)", block)
            if img_m:
                img_url = img_m.group(1)
                out_img = ASSETS_DIR / "featured-trade.jpg"
                if not out_img.exists():
                    img_req = urllib.request.Request(
                        img_url, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    out_img.write_bytes(urllib.request.urlopen(img_req, timeout=20).read())
                return
    except Exception:
        return


def replace_section(text: str, marker: str, new_body: str) -> str:
    pattern = re.compile(
        rf"(<!--\s*{re.escape(marker)}:START\s*-->).*?(<!--\s*{re.escape(marker)}:END\s*-->)",
        re.S,
    )
    return pattern.sub(rf"\1\n{new_body.strip()}\n\2", text)


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    STATS_DIR.mkdir(parents=True, exist_ok=True)

    volumes = fetch_json("https://stat.moonbot.pro/getVolumes")
    top_days = fetch_json("https://stat.moonbot.pro/getTopDays")

    total_vol = sum(parse_int(r["v"]) for r in volumes)
    total_orders = sum(parse_int(r["o"]) for r in volumes)

    latest = volumes[0]
    m_parts = latest["d"].strip().split()
    year = int(m_parts[0])
    month_name = m_parts[1]
    month_num = MONTH_MAP[month_name]
    month_slug = f"{year:04d}-{month_num:02d}"
    ru_nom, ru_gen, _ = MONTH_RU[month_name]

    latest_vol = parse_int(latest["v"])
    latest_orders = parse_int(latest["o"])
    latest_markets = parse_int(latest.get("m", 0))

    daily_rows: list[tuple[int, float]] = []
    for row in top_days:
        parsed = parse_day_entry(row["d"])
        if parsed and parsed[0] == year and parsed[1] == month_name:
            daily_rows.append((parsed[2], float(row["p"])))
    daily_rows.sort(key=lambda x: x[0])

    days_count = len(daily_rows)
    first_day = daily_rows[0][0] if daily_rows else 1
    last_day = daily_rows[-1][0] if daily_rows else 1
    net_total = int(round(sum(v for _, v in daily_rows)))
    pos_days = sum(1 for _, v in daily_rows if v >= 0)
    neg_days = sum(1 for _, v in daily_rows if v < 0)
    best_day, best_val = max(daily_rows, key=lambda x: x[1]) if daily_rows else (1, 0.0)
    worst_day, worst_val = min(daily_rows, key=lambda x: x[1]) if daily_rows else (1, 0.0)

    # 1. Write the SVG chart
    svg_path = ASSETS_DIR / "stats-current-month.svg"
    svg_path.write_text(render_daily_svg(year, month_name, daily_rows), encoding="utf-8")

    # 2. Write stats/YYYY-MM.md
    month_md_lines = [
        f"# Moonbot public trading statistics — {ru_nom} {year}",
        "",
        "Source: [`stat.moonbot.pro`](https://stat.moonbot.pro/) (voluntary anonymized telemetry from rating participants with statistics sending enabled).",
        "",
        "## Monthly summary",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Period | {ru_gen} {first_day}–{last_day}, {year} ({days_count} days) |",
        f"| Trading volume (USDT equivalent) | `${fmt_spaced(latest_vol)}` |",
        f"| Filled orders | `{fmt_spaced(latest_orders)}` |",
        f"| Active markets | `{latest_markets}` |",
        f"| Net result of rating participants | `{fmt_signed_usd(net_total)}` |",
        f"| Positive days / negative days | `{pos_days} / {neg_days}` |",
        f"| Best day | `{fmt_signed_usd(int(round(best_val)))}` ({ru_gen} {best_day}) |",
        f"| Worst day | `{fmt_signed_usd(int(round(worst_val)))}` ({ru_gen} {worst_day}) |",
        "",
        "## Daily results",
        "",
        "| Date | Net result of rating participants, USD |",
        "| --- | --- |",
    ]
    for d_num, val in reversed(daily_rows):
        month_md_lines.append(f"| {year}-{month_num:02d}-{d_num:02d} | `{fmt_signed_usd(int(round(val)))}` |")
    (STATS_DIR / f"{month_slug}.md").write_text("\n".join(month_md_lines) + "\n", encoding="utf-8")

    # 3. Write stats/README.md
    stats_readme = [
        "# Moonbot public trading statistics archive",
        "",
        "Aggregated anonymized trading telemetry from [`stat.moonbot.pro`](https://stat.moonbot.pro/) since March 2019 (statistics sent voluntarily by participants of the public rating).",
        "",
        f"- **Total tracked volume (March 2019 – {ru_nom} {year}):** `${fmt_spaced(total_vol)}` (`${total_vol / 1e9:.2f} billion`)",
        f"- **Total filled orders:** `{fmt_spaced(total_orders)}` (`{total_orders / 1e6:.2f} million`)",
        f"- **Current monthly snapshot:** [`stats/{month_slug}.md`]({month_slug}.md)",
        "",
        "> The month file `stats/YYYY-MM.md` is updated while the month is current. After the month changes it is no longer appended and stays as of its last update: the last days of the month may be missing from it. The table below re-reads the monthly totals from [`stat.moonbot.pro`](https://stat.moonbot.pro/) on every update; the full daily data is there as well.",
        "",
        "![Daily result of the current month](../assets/stats-current-month.svg)",
        "",
        "## Last 12 months",
        "",
        "| Month | Trading volume, $ | Filled orders | Active markets |",
        "| --- | --- | --- | --- |",
    ]
    for r in volumes[:12]:
        stats_readme.append(
            f"| {fmt_month_ru(r['d'])} | `${fmt_spaced(parse_int(r['v']))}` | `{fmt_spaced(parse_int(r['o']))}` | `{r.get('m', '—')}` |"
        )
    (STATS_DIR / "README.md").write_text("\n".join(stats_readme) + "\n", encoding="utf-8")

    # 4. Update the block in README.md
    six_rows_ru = "\n".join(
        f"| {fmt_month_ru(r['d'])}{'*' if i == 0 else ''} | ${fmt_spaced(parse_int(r['v']))} | {fmt_spaced(parse_int(r['o']))} |"
        for i, r in enumerate(volumes[:6])
    )
    ru_block = f"""### {ru_nom} {year} ({ru_gen} {first_day}–{last_day})

| Value | Metric |
| :--- | :--- |
| **${fmt_spaced(latest_vol)}** | trading volume in USDT equivalent |
| **{fmt_spaced(latest_orders)}** | filled orders on {latest_markets} active markets |
| **{fmt_signed_usd(net_total)}** | total net result of rating participants over {days_count} days |
| **{pos_days} / {neg_days}** | positive days / negative days |
| **{fmt_signed_usd(int(round(best_val)))}** | best day, {ru_gen} {best_day} |
| **{fmt_signed_usd(int(round(worst_val)))}** | worst day, {ru_gen} {worst_day} |

<p align="center">
  <img src="assets/stats-current-month.svg" width="720" alt="Daily result of Moonbot users for {ru_nom} {year}, USD">
</p>

<sub>Daily net result of public statistics participants, $, {ru_gen} {first_day}–{last_day}, {year}. Source: <a href="https://stat.moonbot.pro/">stat.moonbot.pro</a> (voluntary anonymized telemetry from terminals with statistics sending enabled). Full daily table: <a href="stats/{month_slug}.md"><code>stats/{month_slug}.md</code></a>.</sub>

<details>
<summary><b>Volume and trades over the last 6 months (total since March 2019: ${total_vol / 1e9:.1f} billion+ · {total_orders / 1e6:.1f} million+ orders)</b></summary>

| Month | Trading volume, $ | Filled orders |
| :--- | ---: | ---: |
{six_rows_ru}

<sub>* The month is still in progress. Full archive since March 2019: <a href="stats/README.md"><code>stats/README.md</code></a> and <a href="https://stat.moonbot.pro/">stat.moonbot.pro</a>.</sub>
</details>"""

    readme_path = ROOT / "README.md"
    if readme_path.exists():
        readme_path.write_text(
            replace_section(readme_path.read_text(encoding="utf-8"), "STATS", ru_block),
            encoding="utf-8",
        )

    update_featured_trade()
    print(
        f"Updated stats: {month_slug} | Vol=${fmt_spaced(latest_vol)} | Orders={fmt_spaced(latest_orders)} | Total=${total_vol / 1e9:.2f}B"
    )


if __name__ == "__main__":
    main()
