# The order in which the Moonbot terminal checks filters

> **Purpose of this document:** A reference table of the sequence in which the Moonbot terminal checks a strategy's market and system conditions (`v7.71` / `FVersion=12`).  
> **Official Moonbot documentation:** [Documentation](https://moonbot.pro/documentation) | [Education](https://moonbot.pro/education)  
> **Related chapter:** [01. Market selection, the filter cascade and Filters on charts](../concepts/01-market-selection-and-filters.md)

---

## 1. Three filtering stages in the trade lifecycle

In the Moonbot terminal, checking a strategy's conditions is split into three consecutive stages:

1. **Stage 1. Background market selection:**
   * This is the stage shown by the **"Filters on charts"** window (the funnel icon on the trading pair's chart).
   * The check goes top to bottom until the first failed condition, so "Filters on charts" shows only **one** reason per running strategy — the first in order; the table below lists the main check groups, not an exhaustive list.
2. **Stage 2. The check on the signal path, before the order is placed:**
   * Runs right after the detect fires, immediately before the `Buy` order is sent to the exchange.
   * Not shown in "Filters on charts" — rejection reasons at this stage are written to the `logs/LOG_YYYY-MM-DD.log` log (in a kernel + client setup — to the kernel's log).
3. **Stage 3. Control while the buy order stands in the order book (`CheckAfterBuy`), and the exit by filters after the purchase (`SellByFilters`):**
   * While the opening `Buy` order stands in the order book, the filters are re-checked with a tolerance: the deltas are widened by `±DeltaSwitch`, the ping — by about 10 %, the minute volume `MinuteVolDelta` — by its own tolerance; the other bounds are checked as is. In `MoonShot` this check is always on.

---

## 2. Stage 1 table: the order of the background entry condition check (top to bottom)

Checks No. 1–No. 6 run **before** the `IgnoreFilters` switch and work at any value of it. With `IgnoreFilters = NO`, the six filter groups follow in turn (No. 8–No. 13: `Base`, `Time`, `Price`, `Ping`, `Volume`, `Delta`) and at the very end — the remaining checks in No. 14. With `IgnoreFilters = YES`, both the groups and the remaining checks are skipped (in `Watcher` the detect pause is checked in the detector itself and remains).

The "Module" column: "yes" — the check acts only with the Autotrading module (PRO) or in the terminal's global emulation mode; without it the condition is silently skipped, and it is pointless to look for the rejection reason among the filters.

| No. | Check | Tab | Removed by `IgnoreFilters = YES`? | Removed by its own `Ignore*`? | Module | What matters |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | **Coin session pause (`SessionPenaltyTime`)** | `Session` | **NO** | **YES** (`IgnoreSession = YES`) | yes | Checked as the first step and only when `SessionPenaltyTime ≠ 0`. |
| **2** | **System readiness and terminal pauses:** zero prices, the 30 s "market offline" pause, the 10 s pause after the terminal wakes up, the 11 min `Quantitative Rules` quarantine, the strategy pause by `sgStop` (`PreventWorkingUntil`), listing age (`OnlyNewListing`, `DontTradeListing`), the 5 s coin pause after an internal order error | System / `Base` | **NO** | **NO** | no | The "market offline" pause is shared: it is set by an exchange response that the pair is not trading now (the symbol is in delivery, trading is disabled, the contract is going into delisting, etc.). The `Quantitative Rules` quarantine — only Binance Futures with the protection enabled. The pause after an internal error does not act while an order is already standing. |
| **3** | **Triggers: `TriggerByKey`, `TriggerKeysBL` (and `SellByTriggerBL` for the exit)** | `Triggers` | **NO** | **NO** | yes | A syntax error in the key list blocks the strategy even without the module. `SellByTriggerBL` is checked only for keys that are in `TriggerKeysBL` — without them the emergency exit will not fire. |
| **4** | **`SellByCustomEMA` at entry** | `Sell` | **NO** | **NO** | yes | With `SellEMACheckEnter = YES` the exit condition is checked before the buy and while the order stands: a true exit condition forbids entry. |
| **5** | **Coin lists:** `CoinsWhiteList`, `CoinsBlackList`, the global blacklist, the temporary blacklist (`TempBL`), `DynWL`, `DynBL` | `Coins` | **NO** | **NO** | no | A coin that did not get into the dynamic whitelist at its recalculation stops here with the reason "not in dynamic whitelist" (for filter diagnostics in "Filters on charts", temporarily set `DynWL_Count = 0`). |
| **6** | **Instrument type and cross-listing, Gate pause:** `LeveragedTokens`, `ListedType`, the Gate pause by order limit | `Base` | **NO** | **NO** (`IgnoreBase` does not remove it; the Gate pause is removed by `IgnoreGatePenalty`) | no | `LeveragedTokens` is checked on Binance Spot; `ListedType` (`Ignore`, `Spot Only`, `Futures Only`, `Both`) — the presence of the pair on Binance and Bybit spot and futures. The Gate pause lasts 10 minutes after the exchange cut the order limit to the minimum; it does not act on selling or on an order already standing. |
| **7** | **The `IgnoreFilters` switch** | `Filters` | — | — | — | With `IgnoreFilters = YES` (and always for `NewListing`) the check ends here with success: groups No. 8–No. 13 and the remaining checks in No. 14 are skipped. |
| **8** | **`Base` group:** `BinanceTokenTags`, `MinLeverage` / `MaxLeverage`, `CustomEMA`, `StrategyPenalty` (in `EMA`), `MoonIntStopLevel` / `MoonIntRiskLevel`, `MarkPriceMin` / `MarkPriceMax` | `Base` | **YES** | **YES** (`IgnoreBase = YES`) | `CustomEMA` — yes | `MinLeverage` / `MaxLeverage` compare the leverage set in the terminal for the coin. A syntax error in `CustomEMA` or `SellByCustomEMA` blocks entries even without the module. While the order stands, the `CustomEMA` formula is re-checked only in `MoonShot`; in `SignalType = EMA` it is checked by the detector itself, even with `IgnoreFilters = YES`. **`MarkPriceMin` / `MarkPriceMax` belong to the `Base` group and are removed by `IgnoreBase`, not `IgnorePrice`;** here they are checked only if the strategy direction is known in advance; for bidirectional detects — at Stage 2. |
| **9** | **`Time` group:** `PenaltyTime` (3 losses), `TradePenaltyTime` (1 loss), `GlobalDetectPenalty`, `WorkingWeekTime`, `WorkingTime`, `FundingBefore` / `FundingAfter` | `Time` | **YES** | **YES** (`IgnoreTime = YES`) | no | The `PenaltyTime` and `TradePenaltyTime` loss counters are shared by all terminal strategies per coin. Funding windows are checked only on futures; on spot they are skipped. |
| **10** | **`Price` group:** `MaxBalance`, `SamePosition`, `MaxPosition`, `SessionProfitMin` / `Max`, `TotalLoss`, `WorkingPriceMin` / `Max`, `PriceStepMin` / `Max` | `Price` | **YES** | **YES** (`IgnorePrice = YES`) | no | No tolerance while the order is held. `PriceStepMax = 0` blocks trading. The coin's market session (`SessionProfitMin` / `Max`) and `TotalLoss` are checked here and work without the module. |
| **11** | **`Ping` group:** `MaxLatency`, `MaxPing`, `MinPing`, `BinancePriceBugMin`, `BinancePriceBug` | `Ping` | **YES** | **YES** (`IgnorePing = YES`) | no | While the order stands, `MaxPing` is widened by about 10 %, `MinPing` is narrowed by the same amount. `MaxPing` is checked only with **`MaxLatency > 0`**, `MinPing` — independently. A latency or ping breach pauses the strategy for 7 s. `BinancePriceBug` is compared with the exchange-wide lag and pauses the whole strategy (90 s, up to 600 s on repeats); `BinancePriceBugMin` checks the lag of the specific coin, but its failure arms the same strategy pause — do not set these thresholds together. |
| **12** | **`Volume` group:** `MinVolume` / `MaxVolume` (24 h), `MinHourlyVolume` / `MaxHourlyVolume` (1 h), `MinHourlyVolFast` / `MaxHourlyVolFast`, `MinuteVolDeltaMin` / `Max` | `Volume` | **YES** | **YES** (`IgnoreVolume = YES`) | no | While the order stands, only `MinuteVolDelta` is widened; daily and hourly volume are checked without tolerance. `0` in `MaxVolume` or `MaxHourlyVolume` is an upper limit of `0$` and blocks all coins. In `TopMarket` the upper volume bounds are not checked. |
| **13** | **`Delta` group:** `GlobalFilterPenalty`, `Delta_3h_Min` / `Max` (by the larger of the 3-hour and hourly deltas), `Delta_24h_Min` / `Max` (by the larger of the daily and hourly), `Delta2_*`, `Delta3_*`, `Delta_BTC_*`, `Delta_Market_*`, `FilterMin` / `FilterMax` | `Delta` | **YES** | **YES** (`IgnoreDelta = YES`) | no | While the order stands (`CheckAfterBuy`, in `MoonShot` always), all delta intervals are widened by `±DeltaSwitch` (no less than `0.01%`). `BTC` or the market leaving the bounds arms the `GlobalFilterPenalty` pause. |
| **14** | **Remaining checks:** the `MoonShot` pause after an internal order error, the 5 s coin pause after a liquidation, `NextDetectPenalty`, the global "Dont buy newly added coins" prohibition, order book readiness for `MShotSortBy = OrderBook` | System / `Base` | **YES** | **NO** | no | `NextDetectPenalty` sets a pause of `1 + NextDetectPenalty` s on a repeat signal for the coin; here it is checked by `Telegram`, `Combo`, `EMA`, `Spread`, `ChartWall`, `MoonHook`, `Activity`, `Watcher` (the other types — in their own detector). The global prohibition on new coins is not visible in "Filters on charts" with `IgnoreFilters = YES`, but on the signal path (Stage 2) it is checked separately and will still reject the purchase. |

---

## 3. Stage 2 table: checks on the signal path

When a strategy has produced a signal, before the `Buy` order is placed, additional checks run that are absent from the background "Filters on charts":

| No. | Check | How it runs | Where the rejection is recorded |
| :---: | :--- | :--- | :--- |
| **1** | **Re-check of the Stage 1 filters** | Verifies that the coin has not left the filters while the signal was forming. Disabled by the flag **`DontCheckBeforeBuy = YES`** | `logs/LOG_YYYY-MM-DD.log`: `FilterCheck Before Buy: market no longer meets the conditions` |
| **2** | **General terminal prohibitions** — "Dont buy newly added coins", "Dont buy delisted coins", `AutoBuy = NO` | Checked on every signal regardless of `IgnoreFilters` (for `NewListing` the new-coin prohibition does not act) | The signal line: `AutoStart: FALSE … Newly added coin!!` and the like |
| **3** | **Active order and market quotas** (`MaxOrdersPerMarket`, `MaxActiveOrders`, `MaxMarkets`, `OneOrderPerMarket`) | Before an order or a group of `MultiOrders` orders is created (in `MoonShot` the repeat shot `MShotRepeatAfterBuy` bypasses `MaxActiveOrders`) | The signal line, for example `Max active orders is …` |
| **4** | **The buy/sell balance filter `UseBV_SV_Filter`** (`BV_SV_FilterRatio .. Max`) and **`UseBV_SV_Stop` as an entry filter** (with `BV_SV_TakeProfit < 0.1`) | Over the `BV_SV_TradesN` window at the moment of the signal | `logs/LOG_YYYY-MM-DD.log` |
| **5** | **Re-check of `MarkPriceMin` / `MarkPriceMax` with the signal direction taken into account** | On futures, after a bidirectional detector (`MoonHook`, `MoonStrike`, `Spread`, `Telegram`) has determined the trade side (`Long` or `Short`), the `MarkPrice` deviation is checked again for that side | `logs/LOG_YYYY-MM-DD.log` |
| **6** | **Free balance control** | Checks that funds are sufficient for the original order size — **before** the `SessionReduceOrder` / `BuyOrderReduce` reductions, which are applied later at placement. So an order may be rejected for balance although it would have passed after the reduction; compliance with the exchange minimum lot is checked when the order is placed | `logs/LOG_YYYY-MM-DD.log`: `Free balance (...) is not enough` |
