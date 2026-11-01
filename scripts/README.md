# Scripts

## `update_stats.py` — public statistics

Fetches the public JSON from [stat.moonbot.pro](https://stat.moonbot.pro/) and updates:

- `assets/stats-current-month.svg` — the daily result chart for the last completed calendar month;
- `stats/YYYY-MM.md` and `stats/README.md` — the monthly snapshot and the 12-month summary;
- `assets/featured-trade.jpg` — downloads a trade screenshot from the [@MoonBot_Profit](https://t.me/s/MoonBot_Profit) channel only if the file is missing; an existing screenshot is kept;
- the block between the `<!-- STATS:START -->` and `<!-- STATS:END -->` markers in the root `README.md`.

Run: `python3 scripts/update_stats.py` from the repository root (Python 3.12, no dependencies or keys; only network access is needed — without it the script exits before writing any files).

Run automatically by GitHub Actions ([`.github/workflows/`](../.github/workflows/)): on Mondays at 06:00 UTC, on the 1st of every month at 06:15 UTC, and manually via `workflow_dispatch`; changes are committed as `github-actions[bot]`.

The month is selected by the UTC calendar. The chart, monthly file and summary tables exclude the current partial month. If the previous month's totals or any daily results are missing, the script exits before changing the published statistics; the next scheduled run retries.

Checks: `python3 -m unittest discover -s scripts -p 'test_*.py'`.
