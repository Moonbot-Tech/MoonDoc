# Coin list and market filter parameters (Coins & Filters)

> **Related sections:** [Market selection and filters](../../concepts/01-market-selection-and-filters.md) · [CustomEMA formulas](../../concepts/05-ema-geometry-and-formulas.md) · [Filter execution order](../filter-execution-order.md) · [Matrix by trade phase](../parameters-by-lifecycle.md) · [TSV index](index.tsv)

This reference covers the 96 market-selection parameters of Moonbot (`FVersion=12`): coin lists, check switches, and the 6 filter subgroups (`Base`, `Time`, `Price`, `Ping`, `Volume`, `Delta`).

---

## 1. Whitelists, blacklists, and dynamic coin lists (Coins & DynWL/DynBL)

Coin lists are checked **before** `IgnoreFilters` and always apply. Dynamic lists are recalculated every `Dyn_Refresh` s: coins are sorted by the selected metric and pass the strategy filters, then the first `DynBL_Count` go into the dynamic blacklist, and `DynWL_Count` of the remaining coins are selected into the dynamic whitelist.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`CoinsWhiteList`** | `string · ''` | Whitelist of tickers separated by commas or spaces. The `*` mask is allowed only at the beginning (`*PERP`) or at the end (`BTC*`). |
| **`CoinsBlackList`** | `string · ''` | Blacklist of tickers separated by commas or spaces (the `*` mask at the beginning/end). **Not disabled** by `IgnoreFilters = YES`. |
| **`DynWL_SortBy`** | `string · 'Last2hDelta'` | Metric used to sort coins for `DynWL`. |
| **`DynWL_SortDesc`** | `bool · YES` | Sort `DynWL` in descending order (`NO` — ascending). |
| **`DynWL_Count`** | `int · 0` | Number of coins (passing the filters and outside `DynBL`) for `DynWL` (`0` — off). Not disabled by `IgnoreFilters`. |
| **`DynBL_SortBy`** | `string · 'Last2hDelta'` | Metric used to sort coins for `DynBL`. |
| **`DynBL_SortDesc`** | `bool · YES` | Sort `DynBL` in descending order (`NO` — ascending). |
| **`DynBL_Count`** | `int · 0` | Number of the first coins in the selection for `DynBL` (`0` — off). Built before `DynWL`; not disabled by `IgnoreFilters`. |
| **`Dyn_Refresh`** | `int · 61` | Recalculation period of `DynWL`/`DynBL` in seconds (`>= 5` s plus `0..2` s of jitter). |

---

## 2. Global switches and base filters (Ignore* & Base)

The `Ignore*` flags disable individual tabs or all 6 filter subgroups. Market type filters (`LeveragedTokens`, `ListedType`), listing age filters (`OnlyNewListing`, `DontTradeListing`), coin lists, triggers, and sessions are checked **before** `IgnoreFilters` and work even with `IgnoreFilters = YES`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`IgnoreFilters`** | `bool · NO` | Skips all 6 filter subgroups (`Base..Delta`) (including `CustomEMA` for all strategies except `SignalType = EMA`, where the detector itself checks the formula). **Does not disable:** coin lists, `Session`, `Triggers`, `OnlyNewListing`, `DontTradeListing`, `LeveragedTokens`, `ListedType`, `PreventWorkingUntil`, `SellByCustomEMA`, and the Quantitative rules. |
| **`IgnoreBase`** | `bool · NO` | Disables the `Base` filter subgroup entirely. |
| **`IgnoreTime`** | `bool · NO` | Disables the `Time` filter subgroup entirely. |
| **`IgnorePrice`** | `bool · NO` | Disables the `Price` filter subgroup entirely. |
| **`IgnorePing`** | `bool · NO` | Disables the `Ping` filter subgroup entirely. |
| **`IgnoreVolume`** | `bool · NO` | Disables the `Volume` filter subgroup entirely. |
| **`IgnoreDelta`** | `bool · NO` | Disables the `Delta` filter subgroup entirely. |
| **`CheckAfterBuy`** | `bool · NO` | Continuously rechecks the filters while the `Buy` order is in place and cancels it when a value goes out of bounds (tolerance: deltas `±DeltaSwitch`, ping `+10%`). Always enabled in `MoonShot`. |
| **`DontCheckBeforeBuy`** | `bool · NO` | Disables the filter recheck immediately before the `Buy` order is sent (leaving only the check on the detect). |
| **`NextDetectPenalty`** | `int · 30` | Strategy pause before a repeat detect of the same coin: `1 + NextDetectPenalty` s (`0` — off). For `Telegram`, `Combo`, `EMA`, `Spread`, `ChartWall`, `MoonHook`, and `Activity` it is disabled by `IgnoreFilters = YES`; for `Watcher` the pause is checked inside the detect itself and cannot be disabled. |
| **`GlobalDetectPenalty`** | `int · 0` | Shared per-coin pause (s) for strategies with `GlobalDetectPenalty > 0` after any detect. An active `ChartWall` continuously extends this pause on every order book tick. |
| **`PreventWorkingUntil`** | `int64 · 0` | Unix timestamp of the strategy pause (the `sgStop` command). Checked before `IgnoreFilters`. |
| **`CustomEMA`** | `string · ''` | Formula (`EMA`, `Avg`, `MAX`, `MIN`, `Vol`, `BTC`, `MAvg`, `Arb`; `AND`/`OR` connectors, no grouping parentheses; windows `1s..300s`, `2m..90m`, `1h..48h` — hourly data actually goes back to ~41h). Checked on the detect and before the buy, and in `MoonShot` also while the order is in place. Collector thresholds (`> -888`, `< 888`, for `Vol` — `> 0`) skip the comparison but require data: a formula made only of collectors is not checked before the buy and writes its values to the report, while a collector appended with `AND` cuts off coins without data. A syntax error blocks entries while the `Base` filters are enabled. Requires the Autotrading module (or the global emulator); disabled by `IgnoreFilters = YES` or `IgnoreBase = YES` (in `SignalType = EMA` the detector itself checks the formula, but then `NextDetectPenalty` and `StrategyPenalty` stop working). |
| **`BinanceTokenTags`** | `string · ''` | Space-separated tags combined with `AND` (`Monitoring`, `Fan`, `Seed`, `Launch`, `Gaming`, `New`, `BNB`, `Alpha`, `OICapped`, `TradFi`; `!` — exclusion: `Fan !Monitoring`). Requires the special tags API; `Monitoring` also works on Bybit and Gate. |
| **`MinLeverage`** | `int · 1` | Minimum leverage set in the terminal for the coin (`>= 1`). |
| **`MaxLeverage`** | `int · 0` | Maximum leverage set in the terminal for the coin (`0` — off). |
| **`MoonIntRiskLevel`** | `int · 2` | Risk level (`1..3`) from `@MoonInt` at which the coin is blocked (`4` — ignore; requires Telegram). |
| **`MoonIntStopLevel`** | `int · 4` | Risk level (`1..3`) from `@MoonInt` that stops the whole strategy: the strategy stops when the coin's level is not below the threshold. The default `4` ignores the regular levels `1..3`, but the `AdminStop` signal (level `10`) stops it anyway; `0` stops the strategy at any level `>= 1`. |
| **`MarkPriceMin`** | `double · 0` | Lower threshold of the `MarkPrice` deviation from the futures price in `%` (`> 0` — in the direction of the position, `< 0` — against it; on `Short` the signs are inverted). **A value of `0` disables the bound** (for zero, set `-0.001`). Disabled by `IgnoreBase = YES`. |
| **`MarkPriceMax`** | `double · 1` | Upper threshold of the `MarkPrice` deviation in `%` (`1.0%` protects against entering near liquidation; `0` — off). Disabled by `IgnoreBase = YES`. |
| **`LeveragedTokens`** | `bool · NO` | Allows leveraged spot tokens (checked on Binance Spot **before** `IgnoreFilters`). |
| **`ListedType`** | `string · 'Ignore'` | Cross-listing of the coin on Binance and Bybit: `Ignore`, `Spot Only`, `Futures Only`, `Both`. Checked **before** `IgnoreFilters`. |
| **`OnlyNewListing`** | `int · 0` | Work only for the first `N` s after the pair appears (`0` — off). Checked **before** `IgnoreFilters`. |
| **`DontTradeListing`** | `int · 0` | Do not trade the pair for the first `N` s after listing (`0..345600` s, up to 4 days; only for listings noticed by a running terminal). Checked **before** `IgnoreFilters`. |
| **`IgnoreGatePenalty`** | `bool · NO` | Do not stop the strategy on Gate.io during the global order-limit penalty. |
| **`StrategyPenalty`** | `int · 2` | Pause of the strategy itself (s) on all coins after it fires anywhere — exists only for the `EMA` type (`Base` group, lifted by `IgnoreBase`/`IgnoreFilters`); for the other types the only all-markets pause is `GlobalFilterPenalty`. |
| **`MultiTokens`** | `bool · NO` | Buy all tickers from one signal (recommended for `MoonNews`; otherwise only the first coin is taken). |

---

## 3. Time, pause, and funding filters (Filters / Time)

Control the strategy's working schedule, pauses after losses, and windows around funding settlement. Disabled by `IgnoreFilters = YES` or `IgnoreTime = YES`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`PenaltyTime`** | `int · 300` | Per-coin pause (s) after 3 consecutive trades with an unfavorable exit price (average sell price worse than average buy price, fee not counted), a manual cancel, or a click on the chart. In `MoonShot` it also raises the coin's priority if a profitable trade closed on it less than `PenaltyTime` s ago. |
| **`TradePenaltyTime`** | `int · 0` | Per-coin pause (s) after any trade whose exit price is worse than the entry price (by average prices, fee not counted; `0` — off). |
| **`WorkingTime`** | `string · ''` | Working schedule: `HH:MM-HH:MM` (an interval within the day) or `MM-MM` without a colon (a repeating interval of minutes `0..59` within **every hour**, for example `05-10` — from the 5th to the 10th minute of every hour). |
| **`WorkingWeekTime`** | `string · ''` | A continuous weekly range (`1` = Mon .. `7` = Sun, for example `1-5`, `7.23:05-5.23:55`, `1-5.21:00` — from the start of Monday to Friday 21:00; combined with `WorkingTime` it works as an `AND` intersection). |
| **`FundingBefore`** | `int · 0` | Seconds **before** funding settlement (checked **only on futures**, skipped on spot): `> 0` — work only during the last `N` s before funding; `< 0` — pause for `|N|` s before funding (`0` — off). |
| **`FundingAfter`** | `int · 0` | Seconds **after** funding settlement (checked **only on futures**, skipped on spot): `> 0` — work only during the first `N` s after funding; `< 0` — pause for the first `|N|` s after funding (`0` — off). |

---

## 4. Price, order book step, and position limit filters (Filters / Price)

Limit the coin price, the order book tick step in `%`, the balance in use, the position size, and the coin's profit per session. Disabled by `IgnoreFilters = YES` or `IgnorePrice = YES`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`WorkingPriceMin`** | `double · 0` | Minimum coin price (`0` — off). |
| **`WorkingPriceMax`** | `double · 0` | Maximum coin price (`0` — off). |
| **`PriceStepMin`** | `double · 0` | Minimum order book price step in `%` (checked directly, without the `DeltaSwitch` extension). |
| **`PriceStepMax`** | `double · 0.5` | Maximum order book price step in `%` (checked without `DeltaSwitch`; **trap:** a value of `0` blocks all pairs). |
| **`UseBTCPriceStep`** | `bool · NO` | Calculate `PriceStepMin`/`Max` from the corresponding `BTC` pair. |
| **`MaxBalance`** | `double · 0` | Limit on the total balance in all orders of the terminal, including the new `OrderSize` (`0` — off). |
| **`MaxPosition`** | `double · 0` | Limit on the coin's position in the terminal (active `Buy` orders + `Sell` remainders + `OrderSize`); with `CheckAfterBuy = YES` it cancels resting `Buy` orders. |
| **`SamePosition`** | `bool · NO` | Do not open orders against the coin's open position (`MoonShot`, `Telegram`, `MoonHook`). |
| **`SessionProfitMin`** | `int · 0` | Lower limit of the coin's total profit for the terminal session in `$` (`0` — off; the `Filters / Price` tab, not `Session`). |
| **`SessionProfitMax`** | `int · 0` | Upper limit of the coin's total profit for the terminal session in `$` (`0` — off). |
| **`TotalLoss`** | `double · 0` | Filter by report result: while the total loss over the whole report for the interval from the `AutoStart` tab exceeds `TotalLoss` (a positive number in the report currency), the strategy does not enter new trades. This is not a stop switch: the strategy stays running, open trades, triggers, and signals keep working, and entries resume when the result improves. Checked in the `Price` group, so `IgnorePrice` / `IgnoreFilters` bypass it. `0` — off. |

---

## 5. Ping, stream latency, and price lag filters (Filters / Ping)

Protect against entries during network lag and chart delay. Disabled by `IgnoreFilters = YES` or `IgnorePing = YES`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`MaxPing`** | `int · 0` | Upper ping limit in ms (`0` — off). **Trap:** checked **only when `MaxLatency > 0`**. While an order is held (`CheckAfterBuy`) it is widened by `+10%`. |
| **`MinPing`** | `int · 0` | Lower ping limit in ms (`0` — off; works independently of `MaxLatency`; while an order is held it is reduced by `-10%`). |
| **`MaxLatency`** | `int · 0` | Max. latency of the trade/order stream in ms (`0` — off). When exceeded, it sets a 7-second strategy-level pause and enables the `MaxPing` check. |
| **`BinancePriceBug`** | `double · 0` | Threshold of the **exchange-wide** price lag in `%` (the largest lag among liquid pairs). When exceeded, **the whole strategy** — on all coins — is paused (90 s, longer on repeated peaks, up to 600 s). This is a kill switch for an exchange malfunction, not a coin filter. |
| **`BinancePriceBugMin`** | `double · 0` | Lower threshold of the price lag of a **specific coin** in `%` (`0` — off): take into work only coins whose lag is currently above the threshold — a spike radar. **Do not combine with `BinancePriceBug` in one strategy:** every `Min` rejection on a quiet coin arms the same strategy pause as `BinancePriceBug`, and a strategy with both thresholds hardly trades. |

---

## 6. Volume and buy/sell ratio filters (Filters / Volume)

Filter coins by daily, hourly, and minute volume and by the `BV/SV` balance. In `MaxVolume` and `MaxHourlyVolume` a value of `0` **blocks the strategy** (it means a ceiling of `0`).

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`MinVolume`** | `int64 · 100` | Min. daily trading volume of the coin. |
| **`MaxVolume`** | `int64 · 100000` | Max. daily trading volume of the coin (`0` blocks the strategy). |
| **`MinHourlyVolume`** | `int64 · 10` | Min. hourly trading volume of the coin. |
| **`MaxHourlyVolume`** | `int64 · 10000` | Max. hourly trading volume of the coin (`0` blocks the strategy). |
| **`MinHourlyVolFast`** | `int · 0` | Min. fast-updated hourly volume (`0` — off). |
| **`MaxHourlyVolFast`** | `int64 · 0` | Max. fast-updated hourly volume (`0` — off). |
| **`MinuteVolDeltaMin`** | `double · 0` | Min. ratio of the minute volume to the reference average minute volume (`1.0` = equal to the reference; `0` — off). |
| **`MinuteVolDeltaMax`** | `double · 0` | Max. ratio of the minute volume to the reference average minute volume (`0` — off). |
| **`UseBV_SV_Filter`** | `bool · NO` | Enables the buy-to-sell volume ratio filter (`BV/SV`) over the `BV_SV_TradesN` window (`Stops` tab). |
| **`BV_SV_FilterRatio`** | `double · 1` | Minimum `BV/SV` ratio for entry. |
| **`BV_SV_FilterRatioMax`** | `double · 0` | Maximum `BV/SV` ratio (`0` — off). |

---

## 7. Volatility and price delta filters (Filters / Delta)

Limit the amplitude of movement of the coin, `BTC`, and the altcoin market. With `CheckAfterBuy = YES` (and in `MoonShot`) the bounds are widened by `±DeltaSwitch`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`Delta_3h_Min`** | `double · 0` | Min. price range of the coin over 3 h in `%` (`>= 0`). |
| **`Delta_3h_Max`** | `double · 20` | Max. 3-hour delta of the coin in `%`. **Actually checks `Max(Delta_3h, Delta_1h)`.** |
| **`Delta_24h_Min`** | `double · 0` | Min. price range of the coin over 24 h in `%`. |
| **`Delta_24h_Max`** | `double · 100` | Max. 24-hour delta of the coin in `%`. **Actually checks `Max(Delta_24h, Delta_1h)`.** |
| **`Delta2_Type`** | `string · '1h'` | First additional delta: `1h`, `2h`, `30m`, `15m`, `5m`, `1m`, `Pump5m`, `Pump1h`, `Dump1h` (all `>= 0`). |
| **`Delta2_Min`** | `double · 0` | Lower bound of `Delta2_Type` in `%`. |
| **`Delta2_Max`** | `double · 20` | Upper bound of `Delta2_Type` in `%`. |
| **`Delta3_Type`** | `string · '1m'` | Second additional delta (`1h`, `2h`, `30m`, `15m`, `5m`, `1m`, `Pump5m`, `Pump1h`, `Dump1h`). |
| **`Delta3_Min`** | `double · 0` | Lower bound of `Delta3_Type` in `%`. |
| **`Delta3_Max`** | `double · 1000` | Upper bound of `Delta3_Type` in `%`. |
| **`Delta_BTC_Min`** | `double · -5` | Min. `BTC` change over 1 h in `%` (signed). |
| **`Delta_BTC_Max`** | `double · 5` | Max. `BTC` change over 1 h in `%`. |
| **`Delta_BTC_24_Min`** | `double · -10` | Min. deviation of `BTC` from its 24-hour average in `%`. |
| **`Delta_BTC_24_Max`** | `double · 10` | Max. deviation of `BTC` from its 24-hour average in `%`. |
| **`Delta_BTC_5m_Min`** | `double · 0` | Min. `BTC` range over 5 min in `%` (`>= 0`). |
| **`Delta_BTC_5m_Max`** | `double · 10` | Max. `BTC` range over 5 min in `%`. |
| **`Delta_BTC_1m_Min`** | `double · 0` | Min. `BTC` range over 1 min in `%` (`>= 0`). |
| **`Delta_BTC_1m_Max`** | `double · 100` | Max. `BTC` range over 1 min in `%`. |
| **`Delta_Market_Min`** | `double · -5` | Min. average hourly altcoin delta in `%` (signed). |
| **`Delta_Market_Max`** | `double · 10` | Max. average hourly altcoin delta in `%`. |
| **`Delta_Market_24_Min`** | `double · -10` | Min. average 24-hour altcoin delta in `%` (signed). |
| **`Delta_Market_24_Max`** | `double · 10` | Max. average 24-hour altcoin delta in `%`. |
| **`FilterBy`** | `string · 'Last2hDelta'` | Market metric for the universal filter. |
| **`FilterMin`** | `double · 0` | Lower bound of `FilterBy` (`0` — off). |
| **`FilterMax`** | `double · 0` | Upper bound of `FilterBy` (`0` — off). |
| **`GlobalFilterPenalty`** | `int · 0` | Pause for the whole strategy (s) when the `BTC` or market delta goes out of bounds (`0` — off). |
| **`DeltaSwitch`** | `double · 0` | Delta hysteresis in `%` (min. `0.01%`) with `CheckAfterBuy = YES` and in `MoonShot`: widens the corridor `[X .. Y]` to `[X - DeltaSwitch .. Y + DeltaSwitch]` after the order is placed. |
