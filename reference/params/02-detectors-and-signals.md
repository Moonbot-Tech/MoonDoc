# Detect algorithm parameters by strategy type (Strategy Settings)

> **Conceptual background:** [The detect pipeline and strategy families](../../concepts/02-detect-pipeline-and-signals.md) · [Spike hunting mechanics: MoonShot, MoonHook, MoonStrike](../../concepts/03-spike-hunting-mechanics.md)  
> **Reference navigation:** [Overview by trade phase](../parameters-by-lifecycle.md) · [Alphabetical index (TSV)](index.tsv) · [Filters and CustomEMA](01-filters-and-coins.md) · [Telegram, UDP, and general settings](08-ui-system-and-migrations.md)

This section contains all 196 strategy-specific parameters of the detect algorithms (No. 289..484, the `Strategy Settings` tab), split into 9 thematic strategy groups. The parameters of the `Telegram`/`UDP`/`Manual` strategies are in the [general settings section](08-ui-system-and-migrations.md), and the `EMA` strategy formulas (`CustomEMA`) are in the [filters reference](01-filters-and-coins.md).

---

## 1. MoonShot strategy — pre-emptive spike hunting

`MoonShot` places a limit `Buy` order in advance at a distance of `MShotPrice` from the price and keeps it inside the working corridor (near bound `MShotPriceMin`, far bound `MShotPrice + min(MShotPriceMin, MShotPrice − MShotPriceMin)`): if the price comes closer than `MShotPriceMin`, the order is moved deeper after `MShotReplaceDelay`; if the price moves up beyond `MShotPrice + min(MShotPriceMin, MShotPrice - MShotPriceMin)`, the order is pulled up after the market after `MShotRaiseWait`. If `MShotPriceMin > MShotPrice` is set by mistake, on saving the strategy `MShotPrice` is raised to `MShotPriceMin + 0.001%`, and the corridor turns into an ultra-thin line with continuous order re-placements.

**Formula for dynamic corridor widening by deltas (`MShotAdd*`):**
$$\Delta_{\text{add}} = \min\Big(\text{MaxModifier},\; \sum k_i \cdot \Delta_i\Big), \quad P_{\text{min}} = \text{MShotPriceMin} + \Delta_{\text{add}}, \quad P_{\text{order}} = \text{MShotPrice} + \Delta_{\text{add}} \cdot \left(1 + \frac{\text{MShotAddDistance}}{100}\right)$$
All terms are non-negative and only move the order deeper; only `MShotAddMarkDelta` depends on the order side; `MaxModifier = 0` — the sum is unlimited.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`FastShotAlgo`** | `bool · YES` | Fast `MoonShot` mode (enabled by default): with a non-zero `MShotRaiseWait`, the “current” price is the deepest trade of the latest instant rather than the last trade in the batch, and the take-profit is placed immediately on the fill. Also applies to `MoonHook` (there the “current” price is chosen this way when `HookRaiseWait > 0`). Slow down re-placements with `MShotReplaceDelay`, not by clearing the checkbox; to keep the take-profit from closing inside the same spike, use a small `SellDelay`. |
| **`MShotPriceMin`** | `double · 2` | Near bound of the corridor in `%` of the current price (`>= 0.001%`): when the price comes closer than this threshold, the order is re-placed at `MShotPrice`. |
| **`MShotPrice`** | `double · 7` | Distance from the reference price at which the order sits (in `%`; below for a long, above for a short). The far bound of the corridor is derived automatically: `MShotPrice + min(MShotPriceMin, MShotPrice − MShotPriceMin)` — with `3/2` the corridor is `2…4%`, with the default `7/2` it is `2…9%`. If `MShotPriceMin > MShotPrice`, on save `MShotPrice` is raised to `MShotPriceMin + 0.001` and the corridor degenerates into a line. |
| **`MShotMinusSatoshi`** | `bool · YES` | Do not place the limit order right at the `MShotUsePrice` reference price: for coins with a coarse price grid (step ≥ 1%), without the offset the order effectively sits at the market price. |
| **`MShotAdd3hDelta`** | `double · 0` | Corridor adjustment coefficient for each `1%` of the coin's 3-hour delta (`0 .. 1`). |
| **`MShotAddHourlyDelta`** | `double · 0.1` | Corridor adjustment coefficient for each `1%` of the coin's hourly delta (`0 .. 1`). |
| **`MShotAdd15minDelta`** | `double · 0` | Corridor adjustment coefficient for each `1%` of the coin's 15-minute delta (`0 .. 1`). |
| **`MShotAdd5minDelta`** | `double · 0` | Corridor adjustment coefficient for each `1%` of the coin's 5-minute delta (`0 .. 1`). |
| **`MShotAdd1minDelta`** | `double · 0` | Corridor adjustment coefficient for each `1%` of the coin's 1-minute delta (`0 .. 1`). |
| **`MShotAdd5sDelta`** | `double · 0` | Corridor adjustment coefficient for each `1%` of the 5-second price range (`0 .. 1`). |
| **`MShotAdd24hDelta`** | `double · 0` | Corridor adjustment coefficient for each `1%` of the coin's 24-hour delta (`0 .. 1`). |
| **`MShotAddMarketDelta`** | `double · 0` | Corridor adjustment coefficient for each `1%` of the hourly delta of the whole market (`0 .. 10`). |
| **`MShotAddBTCDelta`** | `double · 0` | Corridor adjustment coefficient for each `1%` of the hourly BTC delta (`0 .. 10`). |
| **`MShotAddBTC5mDelta`** | `double · 0` | Corridor adjustment coefficient for each `1%` of the absolute 5-minute BTC delta (`0 .. 10`). |
| **`MShotAddMarkDelta`** | `double · 0` | Adjustment coefficient from the divergence between the price and `MarkPrice` (applied only when the `MarkPrice` deviation points toward the order side). |
| **`MShotAddArbRange`** | `double · 0` | Adjustment coefficient for each `1%` of the one-minute cross-exchange price spread (`0 .. 1`). The spread is never smaller than the coin's one-minute delta, and without arbitrage price sources it equals it — then the parameter works like `MShotAdd1minDelta`. |
| **`MShotAddPriceBug`** | `double · 0.1` | Coefficient for moving the order away during exchange lag in proportion to the `PriceBug` metric (`0 .. 5`; the total contribution is capped at `30%`). |
| **`MShotAddDistance`** | `double · 0` | Percentage of extra widening of the corridor itself from the delta sum: the order (and the far bound with it) is shifted by `AddDelta * (1 + MShotAddDistance / 100)`, which lowers the re-placement frequency and saves API limits in high volatility. |
| **`MShotSellAtLastPrice`** | `bool · YES` | After the buy, the take-profit is placed at the higher of two prices — the strategy's `SellPrice` and the ask minus `MShotSellPriceAdjust`; the ask is the higher of two: the pre-spike ask (a few seconds before the strike) and the current one. The idea is to sell on the return to the price the coin was knocked down from; `SellPrice` acts as the lower bound. `NO` — a fixed take-profit in percent. |
| **`MShotSellPriceAdjust`** | `double · 0` | Adjustment in `%` (`0 .. 20%`) subtracted from the ask (the higher of the pre-spike and current ask) when calculating the take-profit with `MShotSellAtLastPrice=YES`. |
| **`MShotReplaceDelay`** | `double · 0` | Pause (s) before moving the order deeper when the price has come closer than `MShotPriceMin`. The trade-off: at zero the order manages to escape from under a fast spike; with a delay the spike fills the limit order, but a slow slide fills it more often too. The tooltip names values around `0.032–0.064` s for shots aimed at a series of strikes. The price returning into the corridor resets the countdown. |
| **`MShotRaiseWait`** | `double · 30` | Pause (s, default `30`) before pulling the order up to a price that has moved away — protection against a counter-move after a burst; at the same time the window in which the price low (high in a short) is searched for as the base of `MShotPrice`: minutes in this parameter glue the order to a bottom passed long ago. Any re-placement resets the countdown. |
| **`MShotSortBy`** | `string · 'Last2hDelta'` | Ranking metric for coins when selecting markets to work on (`Last1mDelta..24h-Delta`, `Pump5m/1h`, `Dump1h`, `DailyVol/HourlyVol/MinuteVol`, `DVolToHVolAsc/Desc`, `MaxOrder`, `Orders`, `Session`, `MaxPos`, `MarkPrice`, `Funding`, `Leverage`, `OrderBook`). |
| **`MShotSortDesc`** | `bool · YES` | Sort direction for `MShotSortBy`: `YES` — descending, `NO` — ascending. |
| **`MShotUsePrice`** | `string · 'Trade'` | Reference price of the order: `Trade` (recommended) is the worse of the latest trade price and the best bid (the ask in a short); with a stale trade feed, the order book is used; `BID` and `ASK` look only at the order book and do not see trades cutting through it. `ASK` must be in capitals, `Trade` in any case; any other spelling is read as `BID`. |
| **`MShotRepeatAfterBuy`** | `bool · NO` | A repeated shot on the same coin while the position is still open: checked in the `MShotRepeatDelay..MShotRepeatWait` window after the take-profit is placed, under the conditions `MShotRepeatIfProfit` (above entry) and `MShotRepeatIfDrop` (below — averaging down). The averaging branch is always on: with the defaults `0`/`0` the repeat is placed at almost any deviation of the price from entry; to repeat only after a rise, set `MShotRepeatIfDrop` deliberately deep. Requires the Autotrading module or the global emulator; the repeat takes the coin out of turn and does not count toward `MaxActiveOrders`. This is a repeat entry, not an exit. |
| **`MShotRepeatIfProfit`** | `double · 0` | Condition for a repeated shot on a rise: the current price must be above the entry price by more than the given `%` (`0` — at any price above entry). |
| **`MShotRepeatIfDrop`** | `double · 0` | Condition for a repeated shot to average down on a fall (`<= 0`): the price must drop below the entry price by the given `%` (`0` — at any price below entry). The branch cannot be turned off: a positive value becomes `0` on save. To avoid averaging down, set a depth the price will not reach within the repeat window. |
| **`MShotRepeatWait`** | `int · 5` | Upper bound of the window, in seconds from placing the take-profit, within which the repeated-shot condition is checked. |
| **`MShotRepeatDelay`** | `int · 0` | Lower bound of the window, in seconds from placing the take-profit, at which the check of `MShotRepeatIfProfit`/`MShotRepeatIfDrop` begins (with `MShotRepeatDelay >= MShotRepeatWait` the check window is empty). |

---

## 2. MoonHook strategy and manual hooks (Manual + UseHookStrategy)

`MoonHook` detects a fast spike that has already happened, with depth `HookDetectDepth` within the `HookTimeFrame` window and a pullback of `HookPriceRollBack` under way, then places a `Buy` order at `HookInitialPrice` to intercept the secondary wave (`HookInterpolate` modes `0..4`) and tracks it inside the `HookPriceDistance` corridor; in modes `0`/`1` the corridor already constrains the first placement. Important: this strategy's `DetectModifier` (the `Delta Modifiers` tab) raises the lower threshold `HookDetectDepth` but **does not move** the upper ceiling `HookDetectDepthMax` (if the lower threshold exceeds the upper one, the detect is blocked).

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`HookTimeFrame`** | `double · 2` | Spike search window in seconds (clamped to `0.4 .. 10.0` s): the spike, the pullback, and the `HookRollBackWait` wait must all fit inside it. It also sets the repeat-detect pause on the coin (roughly `HookTimeFrame` plus one second, separately for long and short) and the turnover estimation window for `BuyOrderReduce`. |
| **`HookDetectDepth`** | `double · 1` | Minimum spike depth in `%` within the `HookTimeFrame` window (raised by this strategy's `DetectModifier`). |
| **`HookDetectDepthMax`** | `double · 0` | Maximum allowed spike depth in `%` (`0` — no upper limit; not moved by `DetectModifier`). |
| **`HookDetectMinVolume`** | `double · 0` | Minimum total traded volume in USDT within the `HookTimeFrame` window (`0` — not checked; cuts off empty spikes on illiquid coins). |
| **`HookAntiPump`** | `bool · NO` | Count a spike only if, for several windows before it, the price held above the bottom by at least the detect depth (by the windows' low prices): a return to the previous level after a short upward burst does not count as a spike. |
| **`HookPriceRollBack`** | `int · 75` | Required pullback of the price from the spike bottom as a percentage of its depth (`>= 0%`), confirming the formation of the “hook”. |
| **`HookPriceRollBackMax`** | `int · 0` | Upper limit of the pullback in `%` of the spike depth (`0` — no limit). |
| **`HookRollBackWait`** | `int · 0` | Time the price must hold above the `HookPriceRollBack` level, in milliseconds (`100` ms cuts off a single tick; the whole event including the wait must fit within `HookTimeFrame`). |
| **`HookDropMin`** | `int · 0` | How far the coin had already fallen over the ~30 seconds before the spike, in `%` of the spike's own depth (`200` — the preceding drop is twice the spike); lower bound, `0` — no condition. |
| **`HookDropMax`** | `int · 0` | Ceiling of the preceding drop in `%` of the spike depth (see `HookDropMin`); `0` — no limit. |
| **`HookDirection`** | `string · 'OnlyLong'` | Direction of the spikes to track: `'OnlyLong'`, `'OnlyShort'`, or `'Both'`. |
| **`HookOppositeOrder`** | `bool · NO` | Invert the entry direction relative to the spike (for example, open a Short on a downward spike). The first order is then placed on the other side of the price; with `HookPriceDistance > 0`, in the middle of the hook corridor: in modes `0`/`1` that is one spike depth from the price, and the `HookInitialPrice` level is not used. |
| **`HookInterpolate`** | `int · 0` | Where the first order (`HookInitialPrice`) is measured from: `0` — up from the bottom by a fraction of the spike depth; `1` — down from the pullback price by the same fraction (`0` — a full depth below the pullback); in `0`/`1` with `HookPriceDistance > 0`, the first order also stays inside the hook corridor (see `HookInitialPrice`); `2` — like `0`, but the corridor is fitted to the order, and with `HookPriceDistance > 0` the signal is skipped if the level is not below the current price (so `HookInitialPrice` sets the minimum pullback); `3` — down from the current price on an inverted scale by `(100 − HookInitialPrice)%` of the depth; `4` — the same, but as a fraction of the pullback. In `3`/`4`, the smaller the number, the deeper the order. |
| **`HookInitialPrice`** | `int · 10` | Level of the **first** placement of the `Buy` order in `%` (`-500 .. 200%`); what it is measured from is set by `HookInterpolate`: with `0` and `2` — up from the spike bottom by a fraction of the depth; with `1` — down from the pullback price by the same fraction; with `3` and `4` — on an inverted scale from the current price (down for `Long`, up for `Short`) by `(100 − HookInitialPrice)%` of the spike depth (`3`) or of the pullback height (`4`): `100` — right at the price, `0` — a full depth / the whole pullback, negative values — deeper still. In modes `0`/`1` with `HookPriceDistance > 0` (default `25`) the first order stays inside the corridor: no closer than `(100 − HookPriceDistance)%` and no farther than `(100 + HookPriceDistance)%` of the spike depth from the current price. A spike `110 → 100`, a pullback to `105`, `HookInterpolate = 0`, `HookInitialPrice = 25`, `HookPriceDistance = 25`: instead of `102.5` the order lands near `97.8`. It lands exactly at `HookInitialPrice` only with `HookPriceDistance = 0` or a wide corridor. |
| **`HookPriceDistance`** | `int · 25` | Width of the order-tracking corridor: in modes `0`/`1`, in `%` of the spike depth (after a re-placement the order sits one depth away from the price: a `5%` spike and `10` → corridor `4.5…5.5%`), and this corridor already constrains the first placement (see `HookInitialPrice`); in modes `3`/`4`, in `%` of the order-to-price distance; in mode `2` the corridor is fitted to the order — roughly from half to one and a half order-to-price distances, but no deeper than `(100 + HookPriceDistance)%` of the spike depth: here the parameter only bounds the corridor and enables tracking; for manual hooks, in `%` of the click depth. `0` — the order does not move. Without a width, a manual hook does not work. |
| **`HookSellLevel`** | `int · 50` | The hook's take-profit as a share of the spike depth: with `HookSellFixed = NO`, the share of the path from the calculated entry price to the top of the spike (`100` — the top), and this percentage is added to the actual entry price; with `YES`, `HookSellLevel %` of the depth is added to the actual entry price regardless of where the fill happened. |
| **`HookSellFixed`** | `bool · NO` | With `YES`, always adds the fixed amount `HookSellLevel * Depth` to the actual buy price, regardless of the level inside the spike at which the `Buy` filled. |
| **`HookReplaceDelay`** | `double · 0` | Delay in seconds (`>= 0`) before moving the `Buy` order deeper on a new impulse against the position. |
| **`HookRaiseWait`** | `double · 30` | Pause (s, default `30`) before pulling the order closer to the price; at the same time the extreme search window — the initial `30` seconds keep the order under the old bottom. |
| **`HookPartFilledDelay`** | `int · 0` | Delay before canceling a partially filled `Buy` order, in milliseconds (`0` — the remainder is canceled immediately). |
| **`HookRepeatIfProfit`** | `double · 0` | Re-arm threshold with `HookRepeatAfterSell = YES`: the closed trade's profit must be strictly greater (`0` — any profitable trade; zero and losing trades do not produce a repeat). With an order grid, a single order is re-placed. |
| **`HookRepeatAfterSell`** | `bool · NO` | Automatically place a repeated `MoonHook` order after the take-profit closes (subject to `HookRepeatIfProfit`). |
| **`UseHookStrategy`** | `string · ''` | In the `Manual` strategy (`Strategy settings` tab): the name of the slave `MoonHook` that tracks the manual order inside the corridor, sets the take-profit from the click depth, and re-arms the hook. On save, the slave is switched to slave mode: `AutoBuy` is enabled, `OrderSize` is zeroed, and the start checkbox is cleared. |

---

## 3. MoonStrike strategy — instant entry on a breakout

`MoonStrike` fires inside the spike — on the trade that broke through the bid reference line deeper than `MStrikeDepth` with a strike sell volume of at least `MStrikeVolume` (mirrored in a short) — and immediately sends a limit order into the tail of the spike: after `MStrikeBuyDelay`, or, with `MStrikeWaitDip = YES`, after the first trade priced above the previous one. This is a race against other bots; the fill is not guaranteed. Without `AutoBuy = YES` and `OrderSize > 0` there is no detect at all, not even a notification. The `MaxActiveOrders` limit for all active `MoonStrike` strategies is counted in total across the whole terminal (`0` — no limit).

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`MStrikeDepth`** | `double · 10` | Depth of the breakout through the bid reference line in `%`, with the `MStrikeAdd*` distance adjustments; on save, at least `0.1%` on spot and `0.01%` on futures. Without `AutoBuy = YES` and `OrderSize > 0` there is no `MoonStrike` detect at all. |
| **`MStrikeVolume`** | `double · 0.2` | Monetary volume of market sells (buys in a short) at the moment of the strike, in the quote currency; on save, at least `0.01` on spot and `1` on futures (there the default `0.2` becomes `1`). The default is a legacy of `BTC` pairs; on USDT pairs set a realistic amount. |
| **`MStrikeLastBidEMA`** | `int · 10` | Reserved smoothing parameter (not used in the calculation in current versions). |
| **`MStrikeDirection`** | `string · 'OnlyLong'` | Futures only: direction of spike hunting (`'OnlyLong'`, `'OnlyShort'`, or `'Both'`). |
| **`MStrikeAddHourlyDelta`** | `double · 0` | Adjustment in `%` to the `MStrikeDepth` threshold for each `1%` of the coin's hourly delta (`<= 1`). |
| **`MStrikeAdd15minDelta`** | `double · 0.1` | Adjustment in `%` to the `MStrikeDepth` threshold for each `1%` of the coin's 15-minute delta (`<= 1`). |
| **`MStrikeAddMarketDelta`** | `double · 1` | Adjustment in `%` to the `MStrikeDepth` threshold for each `1%` of the hourly market delta (`<= 20`). |
| **`MStrikeAddBTCDelta`** | `double · 0.5` | Adjustment in `%` to the `MStrikeDepth` threshold for each `1%` of the hourly BTC delta (`<= 10`). |
| **`MStrikeBuyDelay`** | `int · 0` | Pause before sending the `Buy` order (`0 .. 3000` ms), during which the terminal keeps measuring how far the spike extends downward. |
| **`MStrikeBuyLevel`** | `double · 0` | Level at which the `Buy` order is placed, in `%`: with `MStrikeBuyRelative=YES` it is measured upward from the spike bottom as a fraction of its depth (`0` — at the bottom, `50` — at the middle); with `NO`, **with a minus sign** from the pre-spike price (`-5` — 5% below the pre-spike price). In `NO` mode, zero and positive values put the order at the level where the spike started, that is, above the price that has already flown past — such an order crosses the order book and will most likely fill immediately at post-spike market prices rather than on the pullback. |
| **`MStrikeBuyRelative`** | `bool · YES` | Reference mode for `MStrikeBuyLevel`: `YES` — in `%` of the recorded spike depth from its bottom; `NO` — in absolute `%` of the pre-spike price (a negative value). |
| **`MStrikeWaitDip`** | `bool · NO` | Wait (up to 9 s) for the first trade priced above the previous one (below in a short) before sending the `Buy` order: this is a sign that the extreme has stopped updating, not a confirmed reversal. If no such trade appears within 9 s, the entry is canceled with the log entry `Strike waited too much`; this is normal. |
| **`MStrikeSellLevel`** | `double · 80` | Take-profit level in `%` of the spike depth, measured from the spike's lowest point. |
| **`MStrikeSellAdjust`** | `bool · NO` | With `YES`, measures the take-profit from the lowest of three prices (the spike bottom, the calculated entry price, and the actual buy price) — useful on short `1..3%` spikes. |

---

## 4. Spread and Activity strategies — trading inside the spread and trade feed bursts

The `Spread` strategy divides the `TimeInterval` window into `PriceIntervals` equal slices and requires that on each slice the price range exceeds `PriceSpread` (with more than five slices, one is allowed to miss the threshold) and that the trade feed was continuous for at least `TradesDensity` percent of the window time. The `Activity` strategy looks for the algorithmic footprint of a market maker: over the `MMTimeFrame` window it groups trades of size `MMOrderMin..MMOrderMax` into bins of width `MMOrderStep` and fires when repeating order sizes concentrate in a narrow group (low entropy). The trade feed density filters (`TradesDensity`, `TradesDensityPrev`, `TradesCountMin`) belong to `Spread`; `Activity` has its own measure. MM detection works only on a machine with two or more cores.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`TimeInterval`** | `double · 5` | Length of the trade feed analysis window in seconds (`0.5 .. 30.0` s). |
| **`TradesDensity`** | `int · 80` | Minimum share of time within `TimeInterval` during which trades at different prices were happening (`%`) — how continuous the trade feed is. **Trap:** on save it is forcibly clamped to `10 .. 100` (a value of `0` does not disable the filter; it becomes `10%`). |
| **`TradesDensityPrev`** | `int · 20` | Minimum trade feed continuity before the detect window (`0 .. 100%`): cuts off coins that were flat just before; to catch the start of a pump from the bottom, set `0`. With `TimeInterval` longer than ~15 s the check reaches inside the window itself and loses its meaning. |
| **`TradesCountMin`** | `int · 0` | Minimum number of trades in each short slice of the detect window where trades occurred (`0` — off): cuts off a feed of sparse single prints. |
| **`PriceIntervals`** | `int · 10` | How many equal sub-slices (`1 .. 100`) to divide `TimeInterval` into for checking the minimum spread `PriceSpread` on each of them; with more than five slices, one is allowed to miss the threshold. |
| **`PriceIntervalShift`** | `int · 0` | Number of extra checks of the window shifted back by fractions of a second (`0 .. 5`): requires the spread conditions to hold on all shifted windows to filter out isolated spikes. |
| **`PriceSpread`** | `double · 0.3` | Minimum price range (`>= 0.01%`) on each of the `PriceIntervals` sub-slices of the window (with more than five slices, one is allowed to miss the threshold); the range of the whole window must also be at least three price steps. |
| **`PriceSpreadMax`** | `double · 0` | Maximum allowed total price range over the whole `TimeInterval` window in `%` (`0` — no upper limit). |
| **`IntervalsForBuySpread`** | `int · 3` | How many of the last `PriceIntervals` sub-slices to use for calculating the spread bounds when placing the order (`0` — use the whole `TimeInterval`). |
| **`BuyPriceInSpread`** | `int · 20` | Position of the base buy price inside the detected spread in `%` (for Long it is measured upward from the bottom of the spread, for Short downward from the top; the general `buyPrice` is applied on top of it). |
| **`SellPriceInSpread`** | `int · 80` | Target sell level inside the spread in `%` of its width: the final take-profit is whichever of `SellPrice` and this level is farther in the direction of the trade. |
| **`BuyOrderReduce`** | `int · 100` | Window in milliseconds for estimating the allowed order size from the average turnover of the trade feed: estimate = turnover of the detect window × `BuyOrderReduce` / window length in ms (in `Spread` the window is `TimeInterval`, in `MoonHook` it is `HookTimeFrame`). |
| **`MinReducedSize`** | `double · 0` | Minimum threshold of the estimated size in USDT with `BuyOrderReduce > 0`: if the turnover estimate gives a size below the threshold, there is no detect (`Spread` logs `Reduced order would be too small`, `MoonHook` silently skips the signal). In both strategies the order itself is reduced to the estimated size (not below the exchange minimum); the exception is a manual hook, whose size is left untouched. |
| **`SpreadFlat`** | `bool · YES` | Look for the spread in a horizontal price channel without a pronounced trend. |
| **`Spread_BV_SV_Time`** | `int · 3000` | Window in milliseconds (`0 .. 30000` ms, `0` — off) for calculating the buy-to-sell volume ratio filter (`BV/SV` for Long, `SV/BV` for Short). |
| **`Spread_BV_SV_Max`** | `double · 0` | Upper limit of the `BV/SV` ratio over the `Spread_BV_SV_Time` window (`0` — off). |
| **`Spread_BV_SV_Min`** | `double · 0` | Lower limit of the `BV/SV` ratio over the `Spread_BV_SV_Time` window (`0` — off). |
| **`SpreadPolarityMin`** | `int · -100` | Lower bound of the spread polarity (direction vector; `-100 .. +100`, calculated over the last 5 seconds of the window). |
| **`SpreadPolarityMax`** | `int · 100` | Upper bound of the polarity (`-100 .. +100`): the sign is tied to the chart and is not inverted for a short — “only downward spikes” is `SpreadPolarityMax = 0`. |
| **`SpreadRepeatIfProfit`** | `int · 0` | Repeat entry in the first seconds after the sell order is placed if the price has covered more than the given `%` of the distance toward the take-profit; the repeat is also placed when a profitable sell filled within those same first seconds (`0 .. 100`, `0` — off; at `100` only the repeat after a profitable sell remains; no more than five repeats; requires the Autotrading module). |
| **`MMTimeFrame`** | `int · 45` | `Activity`: window for analyzing the concentration of equal market-maker trade sizes, in seconds (`15 .. 60` s). |
| **`MMOrderMin`** | `int · 100` | `Activity`: lower bound of the size of the MM orders being searched for, in USD (`>= 100$`, `<= MMOrderMax - 10`). |
| **`MMOrderMax`** | `int · 1000` | `Activity`: upper bound of the size of the MM orders being searched for, in USD (`120 .. 200000$`). |
| **`MMOrderStep`** | `int · 1` | `Activity`: width of the bin (grid step) by which trade sizes are grouped, in USD (`1 .. (MMOrderMax - MMOrderMin) div 10`). |

---

## 5. DropsDetection and PumpsDetection strategies — sell-offs and pumps

`DropsDetection` tracks a gradual or stepwise price drop of `DropsPriceDelta %` over the `DropsMaxTime` window on a grid of 2-second ticks. `PumpsDetection` catches a fast impulse rise of `PumpPriceRaise %` over `PumpPriceInterval`, backed by the trade frequency `PumpBuysPerSec` and the volume `PumpVolPerSec`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`DropsMaxTime`** | `int · 0` | Drop analysis window in seconds (`<= 2000`); zero blocks the detect. |
| **`DropsPriceMA`** | `int · 0` | Smoothing of past prices in seconds (`< 2` — no averaging). Keep it small (`0..2`): with a large value the past peak is counted in a weakened form, and a noticeably deeper sell-off than specified is needed to fire. |
| **`DropsLastPriceMA`** | `int · 0` | Number of 2-second ticks for averaging the final (lowest) price of the sell-off (`0` — no averaging; reacts to fast spikes). |
| **`DropsPriceDelta`** | `double · 0` | Required drop depth in `%` over `DropsMaxTime` (raised by `DetectModifier`). Zero does not disable the detect but prevents it from firing — fill in both `DropsPriceDelta` and `DropsMaxTime`. |
| **`DropsPriceIsLow`** | `bool · NO` | Require that the current price at the moment of the detect also sets a new hourly low for the coin. |
| **`DropsUseLastPrice`** | `bool · NO` | Measure `buyPrice` from the final (lowest) price of the sell-off averaged over `DropsLastPriceMA` instead of the current order book price. |
| **`PumpPriceInterval`** | `string · '30s'` | Window for measuring the price rise impulse in `PumpsDetection`: `'4s'`, `'15s'`, `'30s'`, or `'60s'`. |
| **`PumpPriceRaise`** | `double · 7` | The price rise over `PumpPriceInterval`, in `%`, measured from the lowest bid price within the window rather than from the price at its start, must exceed the threshold (the threshold is raised by `DetectModifier`). Only the topmost enabled `PumpsDetection` strategy in the terminal works. |
| **`PumpBuysPerSec`** | `int · 15` | The number of buys over the `PumpVolEMA` window (no shorter than two seconds) must exceed the threshold: with the defaults, more than fifteen buys in two seconds, not in one (the tooltip says “per second”). |
| **`PumpVolPerSec`** | `double · 0.8` | The buy volume over the same window must exceed the threshold (in the market's quote currency). |
| **`PumpVolEMA`** | `double · 2` | Exponential smoothing window for the per-second buy volume, in seconds (`>= 1` s). |
| **`PumpMoveTimer`** | `int · 0` | How many seconds after the take-profit is placed (`0` — off) to move the take-profit once toward the pump peak by `PumpMovePersent`. The countdown starts from placing the take-profit, not from the detect as the `PumpMovePersent` tooltip says. |
| **`PumpMovePersent`** | `double · 0.5` | Offset from the peak in `%` of the “entry → peak” path: after `PumpMoveTimer` seconds the take-profit is moved once to `entry + (peak − entry) × (1 − PumpMovePersent/100)`, where the peak is the higher of the post-detect price maximum and the current `ASK`, but not below breakeven including the fee. `50` — halfway between entry and peak; the default `0.5` — almost at the peak itself. If the pump fell short of the original take-profit, the take-profit is lowered toward the peak — this is an earlier exit, not a later one. |
| **`PumpUsePrevBuyPrice`** | `bool · YES` | Measure the buy price from the price 2 seconds old (unless `Use30SecOldASK` is enabled), protecting against entering at the very top of the tick. |

---

## 6. WallsDetection and ChartWall strategies — order book walls

These are two different strategies with different parameters. **`WallsDetection`** looks for a large cluster of limit orders (a wall) on the `BID` side of the order book with volume `WallBuyVolume` (and at least `WallBuyVolToDailyVol %` of the daily volume) with no comparable opposing wall on the `ASK` side, after the price has been flat for some time; checked at the close of five-minute candles. **`ChartWall`** is an experimental detect, hidden by default (enabled with the `Use_sk_ChartWall` key in the `[Special]` section of `MoonBot.ini`): it sums **all** the volume on one side of the order book within a band of `WallSpread %` from the best price and fires when the sum exceeds `WallSize`; checked on every order book update of an open chart. After the detect the order is placed in the usual way — `ChartWall` has no tracking of the order “at the wall” and no cancellation when the wall gets eaten.

`WallsDetection` parameters:

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`WallsMaxTime`** | `int · 0` | Time in seconds during which the price in front of the wall must hold within the narrow `WallsPriceDelta` range. |
| **`WallsPriceDelta`** | `double · 0` | Maximum allowed difference between the five-minute candle lows over `WallsMaxTime` in `%` — the price sits on a shelf. The comparison is strict: zero (the default) does not disable the detect but blocks it. |
| **`WallBuyVolDeep`** | `double · 0` | Depth of the search for supporting bids in the order book in `%` — down from the lower wick of the shelf, not from the current price. |
| **`WallBuyVolume`** | `int · 0` | Threshold of the total `BID` volume in the order book — from the best price down to the `WallBuyVolDeep` depth below the shelf — in the quote currency; the sum must exceed the threshold. |
| **`WallBuyVolToDailyVol`** | `double · 0` | The same total `BID` volume (see `WallBuyVolume`) must exceed this `%` of the coin's daily trading volume. |
| **`WallSellVolToBuy`** | `double · 0` | Ceiling of the total `ASK` volume in the order book (up to the `WallSellVolDeep` height) in `%` of the found `BID` volume. The comparison is strict: zero (the default) does not disable the detect but blocks it. |
| **`WallSellVolDeep`** | `double · 0` | Height of the `ASK` side scan in `%` — up from the upper edge of the shelf (the highest of the candle lows), not from the current price; the `ASK` volume up to this height is compared via `WallSellVolToBuy`. |

`ChartWall` parameters:

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`WallSize`** | `double · 0` | Threshold of the total order book volume (in the quote currency) within the `WallSpread` band from the best price: the detect fires when the volume exceeds the threshold. |
| **`WallSpread`** | `double · 0` | Width of the order book band from the best price in `%` within which the volume is summed. |
| **`RedWall`** | `bool · NO` | Which side of the order book to sum: `YES` — `ASK` (red wall), `NO` — `BID` (green wall). The trade direction is set separately by the `Short` parameter and by what the market allows — the order book side does not determine it. |

---

## 7. Volumes, VolumesLite, Waves, and Delta strategies — volume and wave analysis

Four classic families compare volume and price dynamics across a series of intervals:
- **`Volumes`** compares a burst of buys over the short window `VolShortInterval` with the background long window `VolLongInterval` and the `BID/ASK` balance of the order book. The background volume excludes trades in the short window.
- **`VolumesLite`** and **`Waves`** divide the history into 4 consecutive intervals in time from left to right: **`T0` — the quiet base in the past**, then `T1`, `T2`, and **`T3` — the most recent window, which ends at the last trade**. `P1`/`V1` compare the average price/volume of `T1` with the `T0` base, `P2`/`V2` — `T2` with `T1`, `P3`/`V3` — the recent `T3` with `T2`; `Delta0` is the price range inside the `T0` base window (in `Waves`, a positive threshold requires a range above it, a negative threshold requires a range below its absolute value, and `0` skips the check). The defaults suggest the geometry: a long base `T0 = 300` s and short run-up windows.
- **`Delta`** compares volume and price on the short slice `DeltaShortInterval` against the long base `DeltaInterval`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`VolShortInterval`** | `int · 45` | `Volumes`: duration of the short (signal) window in seconds (`4 .. VolLongInterval div 2`). |
| **`VolShortPriseRaise`** | `double · 1` | `Volumes`: minimum price range (high to low, without direction) over the short interval in `%`; the comparison is strict — zero does not disable the condition, the range still has to be greater than zero. |
| **`VolLongInterval`** | `int · 300` | `Volumes`: duration of the long (background) window in seconds (`120 .. 3600` s). |
| **`VolBvShortToLong`** | `double · 0.2` | `Volumes`: how many times the buy volume (`BV`) over the short window must exceed the average per-minute background volume over the long window, excluding the short window. |
| **`VolBvLongToHourlyMin`** | `double · 0.2` | `Volumes`: minimum ratio of the long window's normalized volume to the coin's hourly volume. |
| **`VolBvLongToHourlyMax`** | `double · 2` | `Volumes`: maximum ratio of the long window's normalized volume to the coin's hourly volume. |
| **`VolBvLongToDailyMin`** | `double · 0.2` | `Volumes`: minimum ratio of the long window's normalized volume to the coin's daily volume. |
| **`VolBvLongToDailyMax`** | `double · 2` | `Volumes`: maximum ratio of the long window's normalized volume to the coin's daily volume. |
| **`VolBvToSvShort`** | `double · 2` | `Volumes`: minimum buy-to-sell volume ratio (`BV/SV`) over the short interval. |
| **`VolBvShort`** | `double · 0.5` | `Volumes`: minimum absolute buy volume (`BV`) over the short interval in the quote currency. |
| **`VolSvLong`** | `double · 4` | `Volumes`: maximum allowed sell volume (`SV`) over the long interval excluding the short window, in the quote currency. |
| **`VolTakeLongMaxP`** | `bool · NO` | `Volumes`: use the long interval's maximum price (protects against a false signal on a bounce from the bottom). |
| **`VolAtMinP`** | `double · 0.5` | `Volumes`: minimum total `BID` volume in the order book above the short interval's minimum price. |
| **`VolAtMaxP`** | `double · 0.1` | `Volumes`: minimum total `BID` volume in the order book above the short interval's maximum price (the long interval's with `VolTakeLongMaxP = YES`). |
| **`VolDeltaAtMaxP`** | `double · 0.1` | `Volumes`: required increase of the total `BID` volume above the short interval's high during order book confirmation (several re-reads) before the order is placed; if it did not grow, there is no signal. No more than 15 coins are in confirmation at the same time; extra signals are dropped silently. |
| **`VolDeltaAtMinP`** | `double · 0.2` | `Volumes`: required increase of the total `BID` volume above the short interval's low over the same time. |
| **`volBidsDeep`** | `double · 3` | `Volumes`: depth of the `BID` side scan in `%` of the current `ASK` price. |
| **`volBids`** | `double · 0.5` | `Volumes`: minimum total `BID` volume within the `volBidsDeep` depth. |
| **`volAsksDeep`** | `double · 4` | `Volumes`: height of the `ASK` side scan in `%` of the current `ASK` price. |
| **`volBidsToAsks`** | `double · 1.5` | `Volumes`: minimum ratio of the `BID` sum (within the `volBidsDeep` depth) to the `ASK` sum (within the `volAsksDeep` height). |
| **`VLiteT0`** | `int · 300` | `VolumesLite`: duration of the `T0` base window — the oldest, “quiet” segment before the run-up, in seconds. |
| **`VLiteT1`** | `int · 180` | `VolumesLite`: duration of window `T1` — the first run-up segment after the `T0` base, in seconds. |
| **`VLiteT2`** | `int · 180` | `VolumesLite`: duration of window `T2` — the second run-up segment, in seconds. |
| **`VLiteT3`** | `int · 180` | `VolumesLite`: duration of the most recent window `T3`, which ends at the last trade, in seconds. |
| **`VLiteP1`** | `double · 1` | `VolumesLite`: minimum rise of the average price from the `T0` base to the next window `T1` in `%`. |
| **`VLiteP2`** | `double · 1` | `VolumesLite`: minimum rise of the average price from `T1` to `T2` in `%`. |
| **`VLiteP3`** | `double · 1` | `VolumesLite`: minimum rise of the average price from `T2` to the recent `T3` in `%`. |
| **`VLiteMaxP`** | `double · 5` | `VolumesLite`: maximum allowed price rise on each of the `P1..P3` transitions in `%`. |
| **`VLitePDelta1`** | `double · 0` | `VolumesLite`: by how many percent the price growth rate of the second transition (`P2`) exceeds the first (`P1`) — relative acceleration, strict comparison: rates of `1%` and `1.5%` give `50`, not `0.5`; at `0` the second rate simply has to be higher than the first. |
| **`VLitePDelta2`** | `double · 0` | `VolumesLite`: the same for the third transition (`P3`) versus the second (`P2`). |
| **`VLiteDelta0`** | `double · 2` | `VolumesLite`: maximum allowed price range (`Max - Min`) inside the `T0` base window in `%` — the requirement that “the coin was quiet before the run-up”. |
| **`VLiteMaxSpike`** | `double · 7` | `VolumesLite`: maximum allowed excess of the peak price over the interval's average price in `%` (cuts off isolated spikes). |
| **`VLiteV1`** | `double · 1` | `VolumesLite`: minimum volume increase from the `T0` base to window `T1` in `%`. |
| **`VLiteV2`** | `double · 1` | `VolumesLite`: minimum volume increase from `T1` to `T2` in `%`. |
| **`VLiteV3`** | `double · 1` | `VolumesLite`: minimum volume increase from `T2` to the recent `T3` in `%`. |
| **`VLiteWeightedAvg`** | `bool · YES` | `VolumesLite`: method of calculating the interval average prices (`YES` — volume-weighted average, VWAP; `NO` — average by trade count). |
| **`VLiteReducedVolumes`** | `bool · NO` | `VolumesLite`: with `YES` compares per-minute volumes, with `NO` the full volume sums per interval. |
| **`WavesT0`** | `int · 300` | `Waves`: duration of the `T0` base window — the oldest segment before the waves, in seconds. |
| **`WavesT1`** | `int · 180` | `Waves`: duration of wave window `T1` — the first after the `T0` base, in seconds. |
| **`WavesT2`** | `int · 180` | `Waves`: duration of wave window `T2` — the second after the base, in seconds. |
| **`WavesT3`** | `int · 180` | `Waves`: duration of the most recent wave window `T3`, which ends at the last trade, in seconds. |
| **`WavesP1`** | `double · 1` | `Waves`: change of the average price from the `T0` base to window `T1` in `%` (`> 0` — a rise of at least this much, `< 0` — a drop of at least this much, `0` — not checked). |
| **`WavesP2`** | `double · -1` | `Waves`: change of the average price from `T1` to `T2` in `%` (`> 0` — rise, `< 0` — pullback/drop, `0` — not checked). The defaults `+1 / −1 / +1` describe a wave: a rise, a pullback, a new rise toward the last trade. |
| **`WavesP3`** | `double · 1` | `Waves`: change of the average price from `T2` to the recent `T3` in `%` (`> 0` — rise, `< 0` — drop, `0` — not checked). |
| **`WavesDelta0`** | `double · 2` | `Waves`: price range in the `T0` base window in `%` (`> 0` — the range exceeds the threshold, `< 0` — a flat with fluctuation below `|WavesDelta0|%`, `0` — off). |
| **`WavesMaxSpike`** | `double · 7` | `Waves`: maximum deviation of the price peak from the interval's average price in `%` (spike filter). |
| **`WavesV1`** | `double · 1` | `Waves`: volume change from the `T0` base to window `T1` in `%` (`> 0` — volume rise, `< 0` — volume decline, `0` — off). |
| **`WavesV2`** | `double · 0` | `Waves`: volume change from `T1` to `T2` in `%` (`> 0` — rise, `< 0` — decline, `0` — off). |
| **`WavesV3`** | `double · 1` | `Waves`: volume change from `T2` to the recent `T3` in `%` (`> 0` — rise, `< 0` — decline, `0` — off). |
| **`WavesWeightedAvg`** | `bool · YES` | `Waves`: calculate the volume-weighted average price (`YES`) or a simple average over trades (`NO`). |
| **`WavesReducedVolumes`** | `bool · NO` | `Waves`: with `YES` normalizes interval volumes to one minute, with `NO` takes the full interval volume. |
| **`DeltaInterval`** | `int · 600` | `Delta`: long interval for analyzing price and volume changes, in seconds. |
| **`DeltaShortInterval`** | `int · 5` | `Delta`: short interval for averaging the price and measuring the current impulse, in seconds. |
| **`DeltaPrice`** | `double · 2` | `Delta`: minimum price range over two `DeltaInterval` intervals in `%` — between the high and low of prices averaged over `DeltaShortInterval` slices; up or down, the direction is set by `DeltaLastPrice`; the threshold is raised by `DetectModifier`. |
| **`DeltaVol`** | `double · 5` | `Delta`: minimum total volume (`BV + SV`) over `DeltaInterval` in the quote currency. |
| **`DeltaVolRaise`** | `double · 100` | `Delta`: minimum volume increase on the current `DeltaInterval` compared with the previous interval of the same length, in `%`. |
| **`DeltaVolSec`** | `double · 0.1` | `Delta`: minimum weighted per-second volume before the detect (`0` — off). |
| **`DeltaLastPrice`** | `double · 0.3` | `Delta`: deviation of the last short interval's average price from the long interval's average price in `%` (`> 0` — rise, `< 0` — drop, `0` — off). |

---

## 8. Liquidations, Combo, TopMarket, and Alerts strategies

`Liquidations` is available in PRO on futures markets with a liquidation feed supported by the terminal, including Binance and Bybit; the detect needs at least two liquidations in the coin's history.

The group brings together specialized detectors: catching cascades of forced liquidations (`Liquidations`), linking two strategies that fired one after another on the same coin (`Combo`), entering on the leader by 15-minute range (`TopMarket`), and firing on chart alert lines (`Alerts`).

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`LiqTime`** | `int · 15` | `Liquidations`: window for counting the liquidation cascade, in seconds. |
| **`LiqCount`** | `int · 5` | `Liquidations`: minimum number of liquidations in the `LiqTime` window (`0` — not checked). |
| **`LiqVolumeMin`** | `int · 10000` | `Liquidations`: minimum total liquidation volume over `LiqTime` in USDT; the comparison is strict — zero still requires a non-zero volume. |
| **`LiqVolumeMax`** | `int · 0` | `Liquidations`: maximum total liquidation volume over `LiqTime` in USDT (`0` — no upper limit). |
| **`LiqWaitTime`** | `int · 0` | `Liquidations`: minimum quiet pause after the last liquidation, in milliseconds, before entering (`0` — off). |
| **`LiqWithinTime`** | `int · 5000` | `Liquidations`: maximum time in milliseconds since the last liquidation during which the signal stays valid (`0` — off). |
| **`LiqDirection`** | `string · 'Both'` | `Liquidations`: filter by window direction. All liquidations in the `LiqTime` window count toward `LiqCount` and the volume, and the window's direction is the side whose liquidations have the larger volume: `'Both'` — any window, `'OnlyLong'` — only windows dominated by long liquidations, `'OnlyShort'` — by short liquidations, `'Combo'` — two detects in a row with opposite directions, `'Twice'` — two in a row with the same direction (at least `NextDetectPenalty` between detects). |
| **`LiqSameDirection`** | `bool · YES` | `Liquidations`: a “long liquidation” is a forcibly closed long, that is, a market sell into the sell-off. `YES` (the default) opens a position **in the same direction as the liquidated positions**: after a cascade of long liquidations (`LiqDirection = OnlyLong`), a long to buy the sell-off. `NO` reverses the entry — a short along with the cascade. Verified on Binance and Bybit; for Gate, OKX, and Hyperliquid the side was not checked separately. |
| **`Liq_BV_SV_Time`** | `int · 1500` | `Liquidations`: window in milliseconds for calculating the `BV/SV` entry filter (`0` — the filter is off). |
| **`Liq_BV_SV_Filter`** | `double · 0.5` | `Liquidations`: the ratio of the trade feed's counter-flow volume to the volume along the cascade over `Liq_BV_SV_Time` (after long liquidations — buys to sells, after short liquidations — the reverse) must exceed the threshold. The default `0.5` does not yet mean the counter-flow dominates — dominance starts at a threshold above `1`; if the ratio is below the threshold at the moment of the cascade, the terminal waits for it to recover while the other conditions still hold. |
| **`ComboStart`** | `string · ''` | `Combo`: name of the first (starting) strategy of the link (case-insensitive lookup). `MoonShot` and `MoonStrike` cannot be links; a link with `AutoBuy = NO` does not show its own signal. |
| **`ComboEnd`** | `string · ''` | `Combo`: name of the second (closing) strategy of the link. |
| **`ComboDelayMin`** | `int · 0` | `Combo`: minimum time in seconds between the `ComboStart` and `ComboEnd` triggers. |
| **`ComboDelayMax`** | `int · 600` | `Combo`: maximum time in seconds between the `ComboStart` and `ComboEnd` triggers. |
| **`DeltaMin`** | `double · 0` | `TopMarket`: minimum 15-minute range (`Last15mDelta`) of the market-leading coin in `%` (among coins that passed `PriceStepMax`; a repeat signal is issued only after the leader changes). |
| **`TMSameDirection`** | `bool · YES` | `TopMarket`: enter in the direction of the leader's smoothed price deviation from its hourly average (`YES`: above the average — long, below — short) or against it (`NO`). |
| **`AlertByTrades`** | `bool · NO` | `Alerts`: check the crossing of the user's alert line by actual trades (`YES`) or by the smoothed average price (`NO`). |

---

## 9. Watcher strategy — tracking large Hyperliquid wallets

The `Watcher` strategy subscribes to the trades of specified on-chain addresses (`0x...`) on Hyperliquid and opens a position in sync with the large player or against them. How it works:
1. The subscription is to the address's own fills, not to a coin: the coin is taken from each incoming trade, so its chart does not need to be open — it is enough for the coin to be in the terminal's Coins table. The address book is assembled from all running `Watcher` strategies and is updated when a strategy is saved and on `Start`.
2. In a kernel + client setup, the detect of the marked strategies runs on the kernel regardless of `AutoBuy`; the client only displays the trades of the watched addresses on the chart. The strategy is available in the PRO version and on Hyperliquid in MoonBonus mode.
3. Trades of one address on one coin that arrive as a batch are summed by volume: the batch volume is compared against `WatchMinVolume`, while the absolute starting position plus volume is compared against `WatchMinPosition`; the check may run for individual fills inside the batch — each with its own starting position.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`WatchAddress`** | `string · ''` | List of watched Hyperliquid addresses (`0x...`) separated by spaces or commas — the strategy's address book. Applied when the strategy is saved and on `Start`; the coin is determined from the address's trade itself, so an open chart is not needed. |
| **`WatchDirection`** | `string · 'Both'` | Which wallet operations to react to: `'Both'` (any trades), `'OnlyOpen'` (only opening/building a position), `'OnlyClose'` (only closing). |
| **`WatchSameDirection`** | `bool · YES` | Entry direction relative to the watched address's **position**, not its last trade: `YES` — in the direction of its position, `NO` — against it. If you catch closes (`WatchDirection = OnlyClose`), this is not copying the exit: on a whale's partial close of a long, with `YES` the terminal opens a long. |
| **`WatchPriceDeviation`** | `double · 0` | Pulls the order price toward the address's trade price, in `%` (`0` — off). Before exchange price rounding, the terminal compares its calculated entry price with the watched fill price multiplied by `(1 + WatchPriceDeviation / 100)` for a long, or divided by the same factor for a short. It chooses the higher price for a long and the lower price for a short. The parameter does not cap the price — it keeps the limit order from falling behind a market that has moved after the whale, that is, it raises the chance of a fill at the cost of a more expensive entry. |
| **`WatchMinVolume`** | `int · 0` | Minimum total volume of a batch of the watched address's trades on the coin, in USD; the batch must exceed the threshold. |
| **`WatchMinPosition`** | `int · 0` | Minimum position of the address in USD. What is compared is not the remainder after the trade but the address's starting position on the coin plus the volume of the trade or batch: `|position before the fill| + volume`; inside a batch the check may run per individual fill. When building a position this is roughly its size after the trade; when closing, the old position plus the volume being closed (closing `9,000` out of a `10,000` position gives `19,000`, not the remainder of `1,000`). The threshold cuts off small addresses but does not tell a partial close from a full one. |
