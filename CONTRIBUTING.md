# How to propose an improvement or a strategy template

We welcome fixes, engineering analyses and verified strategy templates from traders, quants and developers of tools for the Moonbot ecosystem.

## Language

MoonDoc is English-only. Use English for all content, filenames, code comments, screenshots, commit messages, issues, pull requests, reviews and release notes. Keep Russian source materials in the separate private working repository.

## What you can submit as a Pull Request or Issue

1. **Clarifications of mechanics and edge cases (`concepts/`, `reference/`)**
   - If you noticed a nuance in how a parameter works, an exchange error code or a formula that changed in the current Moonbot release (`v7.71+`), specify:
     - The terminal version (`v7.71+`), the exchange and the market type (`Spot` / `Futures` / `Hyperliquid DEX`).
     - The strategy block (`##Begin_Strategy ... ##End_Strategy`) or a fragment of the main log `logs/LOG_YYYY-MM-DD.log` that reproduces the behavior.

2. **Verified strategy archetypes (`examples/strategies/`)**
   - Every strategy config added to `examples/strategies/` must pass the `v7.71` validation checklist:
     - The first line after `##Begin_Strategy` is `Active=0` (strategy disabled) or `Active=-1` (enabled): this is how the terminal itself writes this field. The words `YES` / `NO` are not accepted here — the paste fails with an `Active field` format error.
     - The second line is `FVersion=12`. Without it, the terminal treats the text as a strategy of the oldest version and applies legacy format migrations to it.
     - Parameter names are case-sensitive, exactly as in [`reference/params/index.tsv`](reference/params/index.tsv) (`buyPrice`, not `BuyPrice`): a line with a wrong name is silently ignored and the field stays at its default value. A value of the wrong type (for example, `1.5M` in an integer field) is silently ignored the same way.
     - One code block — one strategy. Several strategies in one block only with `##MultiSelection` as the first line: without it, `Ctrl+V` pastes only the first one and the rest are lost without warning.
     - Explicitly written wide, non-blocking bounds (`PriceStepMax=100`, `Delta_3h_Max=1000`, `Delta_24h_Max=1000`, `Delta_BTC_Min=-100`, `Delta_BTC_Max=100`, `PenaltyTime=0`, or disabling the corresponding group via `IgnoreDelta=YES` / `IgnorePrice=YES`) for filters that should not restrict the strategy by default (zero upper bounds such as `Delta_3h_Max=0` or `PriceStepMax=0` block rising markets and a positive price step; see [`reference/AI_GUIDE.md`](reference/AI_GUIDE.md)).
     - A clear explanation of the **physical meaning**, **why the parameters are set this way**, and **where the strategy breaks (counterexamples)**.
     - A **“Checking the result”** block: the required access (the Autotrading module, PRO, spot or futures), what the user must replace, what to run, which observable event confirms it works, and how to make sure the mechanism does not fire outside its condition.

3. **Integrations and benchmarks (`examples/integrations/`, `engineering/benchmarks/`)**
   - Self-contained clients and utilities on top of [`MoonProto`](https://github.com/Moonbot-Tech/MoonProto) or the `MoonCMD` UDP protocol.
   - Reproducible speed measurement setups without external private dependencies.

## Security and privacy rules

- **Never publish API keys, key files, server IP addresses or personal account data.**
- **No trader nicknames or personal deposit amounts:** all trade breakdowns are published strictly anonymized (only the coin ticker, timeframe, percentages and milliseconds).
