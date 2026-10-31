# 05. CustomEMA formulas: the state of a coin and the market through moving averages, extremes, volumes and prices on other exchanges

> **Official Moonbot documentation:** [EMA Strategy and Its Parameters](https://moonbot.pro/documentation/advanced-strategy-parameters/ema-strategy-and-its-parameters) | ["Filters → Base" Tab](https://moonbot.pro/documentation/filters-tab/filters-base-tab) | ["Autotrading" Extension](https://moonbot.pro/moonbot-pro/modules/autotrading) | ["Arbitrage Prices" Extension](https://moonbot.pro/moonbot-pro/modules/arbitrage)  
> **Related sections:** [01. Coin selection and filters](01-market-selection-and-filters.md) | [02. Detects and signals](02-detect-pipeline-and-signals.md) | [06. Orders, take-profits and stops](06-orders-exits-and-stops-cascade.md) | [08. Testing and debugging](08-testing-debugging-and-analytics.md) | [Reference: filters and coins](../reference/params/01-filters-and-coins.md) | [Reference: selling](../reference/params/05-sell-and-take-profit.md) | [Archetype 01. Diagnostic rulers](../examples/strategies/01-ema-rulers-and-data-collector.md) | [Archetype 06. Deep bounce](../examples/strategies/06-deep-bounce-and-hl-watcher.md)

---

## 1. Why formulas: a market state that a single number cannot describe

Ordinary filters answer the question "where to trade": volume, price step, deltas ([chapter 01](01-market-selection-and-filters.md)). They do not see the **shape** of a move. A trading idea almost always is a shape: a coin has been sliding gently for a quarter of an hour and has just started to bounce; the price sits right at the low of the last hour; the five-second turnover is ten times the usual; on the leading exchange the coin has already taken off, but not here yet. Such a picture cannot be set with a single threshold; it is set by comparing price and volume with their own past.

For this, Moonbot has the `CustomEMA` formula language: one line describes the geometry of price, volumes, extremes and the cross-exchange divergence. It is used in four roles:

1. **Entry filter of any strategy** — the `CustomEMA` field on the `Filters → Base` tab: while the formula is false, the strategy does not enter on this coin.
2. **The standalone `EMA` strategy** (`SignalType = EMA`): its detector uses the formula to produce signals while it is true.
3. **Exit condition for a position** — the `SellByCustomEMA` field on the `Sell` tab: when the formula becomes true, the position is closed by the `Panic Sell` rules.
4. **Telemetry**: the values of the formulas at the moment of the trade are written to the report and help to pick thresholds on a real sample.

> [!IMPORTANT]
> **Formulas are part of the Autotrading module.** `CustomEMA`, `SellByCustomEMA` and the `EMA` strategy are checked only with the module active or in the terminal's global emulation mode (Menu → Emulation mode); the `EmulatorMode = YES` checkbox in the strategy itself does not replace this condition. Without the module the formula is **silently not checked**: a strategy with the `BTC(5m, 1s) > -0.8` protection on a live account will enter as if the `CustomEMA` field did not exist, and the exit by `SellByCustomEMA` will not fire. The only thing that works without the module is a syntax error in the formula: it blocks the entry. The `Arb(...)` function additionally requires the Arbitrage Prices module.

---

## 2. How to read a formula: two points in time and the percentage between them

All price functions — `EMA`, `Avg`, `MAX`, `MIN`, `BTC`, `MAvg` — have the form `Func(X, Y) > A` or `Func(X, Y) < A` and answer one question: **by what percentage the price at point `Y` differs from the price at point `X`**:

$$\text{Func}(X, Y) = \left(\frac{P_Y}{P_X} - 1\right) \times 100\%$$

Hence the only ordering rule: **the first argument is further in the past, the second is closer to the present**; `1s` (or just `1`) is the current price.

- `EMA(5m, 1s) < -2.5` — the price now is more than `2.5%` below where it was five minutes ago: a fall.
- `EMA(10s, 1s) > 1.2` — over ten seconds the price has risen by more than `1.2%`: an impulse.
- `EMA(15m, 3s) < -3 AND EMA(5s, 1s) > 0.3` — a "hump": over a quarter of an hour the coin has fallen by more than `3%`, and in the last seconds it is already bouncing by at least `0.3%`.

Swap the arguments — `EMA(1s, 5m) < -2.5` — and the formula starts looking for a rise instead of a fall: the current price ends up in the denominator. This is the most common mistake, and the parser will not catch it: the notation is syntactically valid.

**What "the current price" is.** Formulas are calculated not from the last trade and not from the order book, but from the **average trade price line** (on the chart — `Avg Price` in the menu of the "Show Spot trades\OrderBook" button). So the value in the report may not match the price of the trade mark you see on the chart; this is normal. In the same menu of that button (to the left of "Filters on charts"), the `Show EMA`, `Show MinMax`, `Market Avg` checkboxes draw exactly the points the formulas are calculated from; this is not an indicator but a hint, and the lines have gaps at the joints between scales.

---

## 3. Three time scales and what stands behind them

Arguments are given as a number with a letter: **`s`** — seconds (`1s..300s`; a number without a letter is read as seconds), **`m`** — minutes (`2m..90m`; for one minute write `60s`), **`h`** — hours (`1h..48h`; there is no `d` suffix). Behind each scale stands **its own nature of the value**, and this matters more than the ranges themselves:

| Scale | What the value is | What it shows the trader |
| :--- | :--- | :--- |
| **Seconds `EMA(Ns)`** | The smoothed price of the last seconds: the larger `N`, the stronger the smoothing and the inertia. `N` is a nominal memory length, not an exact period | Impulse and bounce right now: `EMA(5s, 1s) > 0.3` — the price has broken away upward from its second-scale average |
| **Minutes `EMA(Nm)`** | **The average price of the single minute that was `N` minutes ago** — not a window "from now to `N` minutes back" | The local trend of the last hour and a half: `EMA(15m, 1s) < -3` — now `3%` lower than a quarter of an hour ago |
| **Hours `EMA(Nh)`** | **The average price of the hour that was `N` hours ago**, from five-minute candles; `1h` is the hour from the 60th to the 120th minute back; the last hour is not included in the hourly values | Position relative to the day's levels: `EMA(4h, 1s) > 8` — the coin is overheated over several hours |

This way one formula can describe the state of a coin on three levels: where it was going for hours, what it did in the last minutes and what is happening in these seconds. For the market context, the same three scales are available for Bitcoin and for the average altcoin (section 5).

**While there is no history, the formula does not work.** After the terminal starts, the second and minute series fill up gradually, the hourly ones are assembled from the loaded candles; a just-listed coin has no history at all. Until filled, the formula shows `EMAFilter(90 m): no data` and **does not let the entry through** (and `SellByCustomEMA` in this state never fires). Hourly values are actually available up to about `41h` — that is how many candles the terminal loads; the parser accepts `42h..48h`, but they stay in `no data`. If `no data` persists on long hourly windows after a long run, the terminal has not received some candles from the exchange; a restart helps.

### A history point without smoothing: `Avg`

`Avg(X, Y)` is written the same way as `EMA`, but takes **the point of the average price line `X` ago without smoothing over a window**. The difference shows on sharp price spikes: if there was a peak four seconds ago, `EMA(4s, 1s)` smooths it out, while `Avg(4s, 1s)` compares with it directly. That makes `Avg` the tool for second-scale reversals and for a fast exit by `SellByCustomEMA`. `Avg(2s, 1s)` is almost always near zero (the previous point is almost equal to the current one); a meaningful window starts at `3s`.

> [!WARNING]
> **`Avg` has a short memory.** The history of the average price line is kept for a limited time: in VDS mode and on the kernel — a few minutes, on an ordinary PC — longer, up to tens of minutes depending on the machine's memory. If the window is longer than the stored history, the terminal **silently compares with the oldest available point**: `Avg(30m, 1s) < -5` on the kernel actually catches a fall over a few minutes, and hourly `Avg(1h, …)` never reaches its window in any configuration. For windows longer than a few minutes use `EMA(Xm)` and `EMA(Xh)`.

---

## 4. Extremes: `MAX` and `MIN` — a new high, a new low, the zone near the bottom

`MAX(X, Y)` and `MIN(X, Y)` compare **the maximum or minimum of the price over window `X`** (in the denominator) with **the `EMA(Y)` price** (in the numerator). This is the language of levels: entry on a breakout, picking up at support, catching a bounce off the bottom ([archetype 06](../examples/strategies/06-deep-bounce-and-hl-watcher.md)).

**Sign.** While the price is below the maximum, `MAX` is negative; while above the minimum, `MIN` is positive. Hence the main trap: **`MAX(60m, 1s) < 5` without a minus is true for almost any coin** (everyone that has not risen more than `5%` above the maximum) and will buy up the whole market; a pullback from the maximum is always written as a negative threshold.
- `MAX(60m, 1s) < -5` — the price is `5%` or more below the maximum of the last hour: a pullback.
- `MAX(60m, 1s) > 0.2` — the price has broken the hour's maximum upward by `0.2%`: a new high.
- `MIN(60m, 1s) > -0.2 AND MIN(60m, 1s) < 0.3` — a narrow zone near the hour's minimum: from `0.2%` below to `0.3%` above.

**Window `X`.** Minutes — from `5m` to `90m` in five-minute steps: `2m..7m` round to `5m`, `1m` is an error, and seconds in the first argument **silently turn into minutes** (`MAX(10s, 1s)` is read as `MAX(10m, 1s)`). Hours — `1h..48h` (data up to `~41h`). The second argument `Y` is any from section 3: `1s..300s`, `2m..90m`, `1h..48h`.

**The window does not include the last segment — on purpose.** Minute extremes are calculated without the last minute, hourly ones without the last hour: `MAX(1h)` is the maximum from the 60th to the 120th minute back, `MAX(2h)` — over the two hours that ended an hour ago. Thanks to this, the current price can turn out to be **above** the maximum, and the formula can express a new high; otherwise `MAX(…) > 0` would be impossible. Hence the practical rule: **the level of the last hour is `MAX(60m, 1s)`, not `MAX(1h, 1s)`**; the notation with `1h` describes the hour before last. Hourly levels update when a new five-minute candle appears, minute levels with a small lag.

---

## 5. Market context: `BTC` and `MAvg`

- **`BTC(X, Y)`** — the same `EMA`, but for the venue's bellwether: Bitcoin on crypto exchanges, the base index on Hyperliquid index markets. `BTC(5m, 1s) > -0.8` in `CustomEMA` forbids longs while Bitcoin has dropped more than `0.8%` over five minutes; the same condition with the opposite sign in `SellByCustomEMA` is an evacuation from longs when the bellwether collapses. These are the same questions the `Delta_BTC` filters solve ([chapter 01, section 4](01-market-selection-and-filters.md)), but in any windows and in any combination with conditions on the coin.
- **`MAvg(X, Y)`** — the change in the average price of all traded altcoins of the exchange. This is how a coin's own move is separated from the general one: `EMA(5m, 1s) < -3 AND MAvg(5m, 1s) > -0.5` — the coin has fallen while the market stands still, so this is its own event. Two terminal settings affect the calculation: "Black List" + "Exclude from delta" (Settings → Main) remove the coins of the global black list from the average; `Weighted mAvg` (Settings → Advanced → Engine settings) weights each coin by its daily volume so that illiquid coins do not distort the picture.

---

## 6. Volume: `Vol(X, Y)` — how many times louder than usual

Price without volume proves nothing: a shift of an empty order book looks like an impulse. `Vol(X, Y)` answers whether a flow of trades stands behind the move. The function is unsigned and returns the **ratio** of the turnover in window `Y` to the turnover in window `X`, with both windows normalized to **turnover per minute**, so windows of any length can be compared:

- `Vol(1h, 5s) > 10` — turnover over the last five seconds, converted to a per-minute rate, is more than ten times the average per-minute turnover over the past hour: a burst.
- `Vol(1h, 1m) > 2` — the current minute is twice as loud as the hour's average minute (example from the site: `120,000` per hour → `2000` per minute; `4000` per minute → `2`).

The windows are fixed: `0`, `5s`, `15s`, `30s`, `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `3h`, `24h`; other values are a formula error.

**Absolute turnover.** A zero in the first argument removes the comparison: `Vol(0, Y) > N` is the turnover of window `Y` converted to per-minute, in the quote currency of the pair (on a `USDT` market — in `USDT`). The conversion is a simple proportion: `10,000` in five seconds is `120,000` per minute, `15,000` in fifteen seconds is `60,000`, `1,000,000` in five minutes is `200,000`. Hence the notations `Vol(0, 5s) > 120000` ("more than ten thousand in five seconds") and `Vol(0, 1m) > 100000` ("more than a hundred thousand in a minute").

> [!WARNING]
> **Zero volume is "no data", not zero.** If there was not a single trade in the window, the function does not return `0` but counts as not computed, and the condition is false. So an "exit when volume has died down" formula like `Vol(0, 5s) < 1000` will not catch a coin dying out completely, and the collector threshold `Vol(…) > 0` (section 10) requires at least one trade.

---

## 7. Price on other exchanges: `Arb(Exchange)`

On a spike, news or an Asian pump, the price on one venue runs ahead of the others. `Arb(Exchange)` compares the coin's price on an external exchange with the price on yours:

$$\text{Arb}(\text{Exchange}) = \left(\frac{P_{\text{external}}}{P_{\text{yours}}} - 1\right) \times 100\%$$

- `Arb(BinanceF) > 2.5` — on Binance futures the coin is `2.5%` or more dearer than on yours: the bellwether has gone ahead — a catch-up buy or picking up a local downward spike.
- `Arb(BinanceF) < -2.5` — it is cheaper there: a short signal or an evacuation condition from a long in `SellByCustomEMA`.

**What is needed for this to work.** The Arbitrage Prices module (activated in the Moon Credits window) and **ticked exchanges** in the price and order book settings (the menu of the "Show Spot trades\OrderBook" button, the `Arbitrage` zone); by default none is ticked: the formula is written correctly, but the chart shows `Arb(...): no arb data` and there are no signals. Quotes older than a few seconds are not taken into account; exchanges where deposits or withdrawals of the coin are closed (a lock icon on the chart) are excluded from the formulas: the price of an isolated venue detaches from the world market and means nothing. If data from the needed exchange has not arrived, the condition is simply false: **a formula can detect a divergence, but cannot assert that there is no divergence.**

**Exchange codes** — exactly as in the terminal's arbitrage settings, case-insensitive, with no arbitrary abbreviations: `BinanceS`, `BinanceF`, `BinanceQ`, `BybitS`, `BybitF`, `OkxS`, `OkxF`, `GateS`, `GateF`, `BitgetS`, `BitgetF`, `HtxS`, `HL_S`, `HL_F` and Hyperliquid venues of the form `HL_<dex>` (`HL_xyz`, `HL_para`, `HL_mkts`, `HL_io`), `UpBit`, `BinAlpha`. The list of sources is not guaranteed to stay constant. The `Forex` code is visible on the chart, but in a formula it currently breaks the parsing entirely (the letters `or` inside the name are read as the `OR` connective) — do not use it in `CustomEMA`.

**The `Arb(*)` mask** — "at least one exchange": with the `>` sign the most expensive of the external divergences is checked, with `<` the cheapest. So the "fork" `Arb(*) > 2 AND Arb(*) < 30` does not bound a corridor: the two halves look at different exchanges and can be true at the same time. A corridor is set per specific venue: `Arb(BinanceF) > 2 AND Arb(BinanceF) < 30`. For autotrading the site directly recommends a coin white list and specific exchanges instead of `*`: another venue may list a token with the same name and a different price (`PEPE` and `PePe`), and the mask will produce a false detect.

---

## 8. The `AND` / `OR` connectives, notation and errors

Conditions are joined with the words `AND` and `OR`; **all `AND`s are evaluated first, then `OR`**: `A AND B OR C AND D` reads as `(A AND B) OR (C AND D)` — two entry scenarios in one line, for example `EMA(5m, 1s) < -2 AND Avg(5s, 1s) > 0.3 OR EMA(15m, 1s) < -4 AND Avg(10s, 1s) > 0.5`.

**Notation.** There are no grouping parentheses: round brackets are allowed only around function arguments. The threshold `A` is a number in percent **without the `%` sign**, with a decimal point (`-2.5`, not `-2,5%`); the comparison signs are only `>` and `<`, no `>=`, `<=` or `=`; to the right of the sign only a number: two functions cannot be compared with each other (`EMA(5m,1s) > EMA(15m,1s)`); the `k` and `m` abbreviations do not work in the threshold (`100000`, not `100k`). Function names, the `s/m/h` letters and the connectives are read case-insensitively; spaces are optional. Connectives are searched for as substrings, so any name inside the formula that contains `or` or `and` destroys the parsing (that is how `Forex` breaks).

**An error in the formula does not "disable the filter" — it blocks the strategy.** While the `Base` filters are enabled, a strategy with an erroneous `CustomEMA` or `SellByCustomEMA` does not enter on any coin, and "Filters on charts" shows the reason with the line `EMA Filters: CustomEMA: …`:

| What the terminal shows | Cause | Fix |
| :--- | :--- | :--- |
| `Not a EMA (…)` | Function name not recognized: a Cyrillic letter, a different encoding, a typo | Retype in the English keyboard layout |
| `Wrong EMA parameter (…)` | The time letter is not a Latin `s`/`m`/`h` | `5m` in Latin letters |
| `Wrong EMA formula (…)` / `(no comma)` | No round brackets (for example, square ones); arguments separated by a period | `EMA(5m,1)`, not `EMA[5m,1]` and not `EMA(5m.1)` |
| `Wrong EMA range (1 minutes, must be [2 .. 90])` | Window out of range: `1m`, `400s`, `0` in a price function | `60s` instead of `1m`; `1s` for the current price |
| `Wrong EMA comparision part (…)` | The sign is `=`, `>=`, `<=` or missing | Only `>` or `<` |
| `Wrong EMA comparision value (…)` | The threshold is not a number: the letter `O` instead of zero, `100k`, `1%`, a comma, a typo in `AND` | A number with a point, no `%` and no suffixes; the `AND` connective in Latin letters |
| `Wrong Vol time parameters` / `Unknown Arb exchange "…"` | `Vol` window not in the fixed list; venue code not from the arbitrage settings | `5s..24h` from the list in section 6; the exact name, for example `OkxF` |
| `EMAFilter(90 m): no data` | No history yet (start, listing, candles not loaded) — not a notation error | Wait; on long windows — restart |

If the `Base` filters are disabled (`IgnoreFilters` or `IgnoreBase`), the `CustomEMA` entry filter is not checked — neither a correct nor an erroneous one. This does not apply to `SellByCustomEMA` and the `SellEMACheckEnter` check (they work even with `IgnoreFilters`) or to the `EMA` strategy, where the detector checks the formula and an error stops the signals under any flags.

---

## 9. Where the formula lives in a trade

**Entry filter.** It is checked when the strategy decides on an entry: on the detect and once more before placing the order. For `MoonShot`, which keeps its order in the order book in advance, the formula is also re-checked the whole time the order stands: once it stops holding, the order is cancelled. For the other strategies the formula is not part of the re-check of a standing order (`CheckAfterBuy`). `IgnoreFilters = YES` and `IgnoreBase = YES` disable `CustomEMA` together with the `Base` group — do not set them in a strategy where the formula is the entry condition; disable only the unneeded neighboring groups ([chapter 01, section 6](01-market-selection-and-filters.md)).

**The `EMA` strategy.** The formula is the signal: while it is true, the strategy will enter again and again; only pauses and order limits restrain it. So `NextDetectPenalty` (a pause on the coin after a signal), `StrategyPenalty` (a pause of the strategy itself after any signal) and a limit on simultaneous orders are mandatory for it. A peculiarity: `IgnoreFilters = YES` disables the common filter groups for it, but its detector checks the formula itself and keeps checking it — while both pauses **stop acting**, and the strategy enters on every pass. Formula values are calculated from trade prices, so the trade-feed latency filter (`MaxLatency`) is a necessity for the `EMA` strategy, not an option.

**Exit by formula.** `SellByCustomEMA` is checked after the buy (with a pause of `SellEMADelay` seconds) and, when true, closes the position by the same mechanism as the exit by filters ([chapter 06](06-orders-exits-and-stops-cascade.md)): if `SellByFiltersDelay` is set, the take-profit is first moved once to the current price (not lower than `PriceDownAllowedDrop` from the entry) and a countdown starts; when it expires — `Panic Sell`; without a delay — `Panic Sell` at once. The exit by formula does not depend on the value of `SellByFilters`. `SellEMACheckEnter = YES` (enabled by default) does not let the strategy buy if the exit condition already holds at the moment of entry — otherwise the position would close right after the buy. To disable the exit by formula, leave the field **empty**; a `0` in the text field is a syntax error that will block entries. From this also follows the site's technique for emulator scouts, which only need to leave a trace in the report and light a trigger ([chapter 04](04-triggers-and-master-slave.md)): `SellByCustomEMA = EMA(5m,1) > -1000`, `SellEMADelay = 0`, `SellEMACheckEnter = NO` — an always-true condition closes the virtual position right after the buy. In a working strategy the same thing will dump every trade at market, and with `SellEMACheckEnter = YES` it will forbid buys wherever the formula has data.

---

## 10. Telemetry: formula values in the report and on the chart

To pick thresholds, you need to know what `EMA`, `MAX`, `Vol`, `BTC` were in the second of real entries. For this there are **collector thresholds**: for price functions — `> -888` (a threshold of `-888` or lower with the `>` sign) or `< 888`, for `Vol` — only `> 0`. For such a condition the comparison is not performed, but the presence of data is still checked. An example of a collector line: `EMA(5s,1s)>-888 AND EMA(5m,1s)>-888 AND MAX(60m,1s)>-888 AND MIN(60m,1s)>-888 AND Vol(1h,5s)>0 AND Vol(0,1m)>0 AND BTC(5m,1s)>-888`.

- If the **whole** `CustomEMA` line consists of collectors, it is not checked before the buy and does not block the entry. At the moment the buy order is placed, the terminal calculates all the listed values and writes them to the `logs/LOG_YYYY-MM-DD.log` log (the `EMAFilter:` line) and to the `Comment` column of the Reports window — for all strategy types except `EMA` (for it — only to the log). The accumulated sample is read by the MoonTerminal strategy tuner ([chapter 08](08-testing-debugging-and-analytics.md)).
- If collectors are appended via `AND` to working conditions, each of them **requires data**: with no trades in the `Vol` window, no quote for `Arb`, no accumulated history, the condition is false and the coin is cut off. It is safer to keep the collector in a separate emulator copy of the strategy.
- In the `EMA` strategy a line of collectors alone is a buy signal on every coin that has data; in `SellByCustomEMA` a collector is an always-true exit condition (section 9). Telemetry is built into strategies of other types and only into `CustomEMA`.

**A ruler on the chart.** To see the current formula values live, create an auxiliary strategy with `AutoBuy = NO` and a deliberately **unattainable** threshold (`EMA(15m, 1s) < -1000`, `Vol(0, 1m) > 999999999`): no coin will ever pass it, and "Filters on charts" will show the current value as the reason for refusal. Three conditions for the ruler to work: the strategy is ticked and running; the coin's chart is open **in full screen** — on small charts the terminal saves CPU and writes only `EMA filter not passed. Open full screen chart to see more info`; the formula's turn has come — the checks that stand before it (coin lists, sessions, triggers, token tags) have not cut off the coin. In an `AND` chain "Filters on charts" shows only the first failed condition; join the ruler's conditions with `OR` — then the terminal checks each branch and prints the values of all formulas in one line ([archetype 01](../examples/strategies/01-ema-rulers-and-data-collector.md)).
