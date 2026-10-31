# Sell Parameters and Take-Profit Management Algorithms (Sell Order)

> **Concept overview:** [Position management, exit algorithms and the stop-loss cascade](../../concepts/06-orders-exits-and-stops-cascade.md) · [CustomEMA and SellByCustomEMA formulas](../../concepts/05-ema-geometry-and-formulas.md)  
> **Reference navigation:** [Overview by trade phase](../parameters-by-lifecycle.md) · [Alphabetical index (TSV)](index.tsv) · [Stop losses and trailing](06-stops-and-trailing.md)

This section covers the 46 parameters of the `Sell` tab: the initial placement of the limit take-profit after the buy fills, the forced exit by filters and by the logical formula `SellByCustomEMA`, and the four algorithms for dynamic management of the `Sell` order (`PriceDown`, `SellLevel`, `SellShot`, `SellSpread`).

---

## 1. Basic take-profit settings and exit by filters/formula (Sell & SellByCustomEMA)

This group controls the calculation of the starting sell price (`SellPrice`, adjusted by `SellModifier`), the delay of the first take-profit placement on spikes (`SellDelay`) and the conditional exit from the position when market conditions deteriorate (`SellByFilters`, `SellByCustomEMA`). The exit by filters does not check the entry formula `CustomEMA` — closing the trade by formula is handled by the separate parameter `SellByCustomEMA`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`AutoSell`** | `bool · YES` | Place the `Sell` order automatically after the buy. On futures forced on (`YES`); disabling it (`NO` — leave the coins on the balance) is available only on spot (the tooltip mentions `ExpertMode`, but the current code has no such check). |
| **`SellPrice`** | `double · 0.5` | Take-profit target price in `%` from the actual buy price (adjusted by this strategy's `SellModifier`, `Delta Modifiers` tab; in `MoonShot`/`MoonHook`/`MoonStrike`/`Spread` it may be overridden by their own sell levels). |
| **`SellPriceAbsolute`** | `bool · NO` | Only for `NewListing` with `SellFromAsset = YES`: `SellPrice` is the absolute sell price of an asset already held (for example, `0.01`), not a percentage. Has no effect on a regular `NewListing` entry. |
| **`SellDelay`** | `int · 0` | Pause before placing the `Sell` order after the buy (`0..3000` ms). Needed so as not to show the take-profit volume in the first moments of the impulse. |
| **`SplitPiece`** | `int · 0` | Share of the order volume (`0..50%`) split off into a separate order by the `Split Piece` context menu command, the `SellPiece` panel or the Telegram command `SellPiece`. |
| **`UseScalpingMode`** | `bool · NO` | If `SellPrice` is not above `1%`, may raise the take-profit (up to `2%`) by placing the order below a large wall in the `ASK` side of the order book. |
| **`SellFromAsset`** | `bool · NO` | Only for `NewListing`: at the start of the listing, do not buy but immediately sell an asset already on the spot balance at the `SellPrice` price. |
| **`SellQuantity`** | `double · 0` | Only for `NewListing` with `SellFromAsset=YES`: the quantity of coins to sell (`0` — sell the whole available balance of the asset). |
| **`SellByFilters`** | `int · 0` | Timer in seconds from the moment the `Sell` order is placed (`0` — off), after which the position is closed if the market leaves the bounds of the strategy's filters (does not check `CustomEMA`). |
| **`SellByFiltersDelay`** | `double · 0` | Two-phase exit when `SellByFilters` fires: with `>= 0.1` s it first moves the limit `Sell` order once to the current price (but not below `PriceDownAllowedDrop`), and after `SellByFiltersDelay` s turns on `Panic Sell`. |
| **`SellByCustomEMA`** | `string · ''` | Exit condition formula: when it becomes true (after the `SellEMADelay` pause), the position is closed by the same path as the exit by filters — with `SellByFiltersDelay` set, the take-profit is first moved to the market, then `Panic Sell` by the strategy's stop. Works with `IgnoreFilters=YES`; requires the Autotrading module. The collector threshold `> -888` here is an always-true exit condition: with `SellEMACheckEnter=YES` (default) it will forbid buys everywhere the formula has data, with `NO` it will close the position right after entry. To disable, leave the field empty (`0` is a syntax error that blocks entries). After the trade closes, it arms `TriggerKeyProfit` / `TriggerKeyLoss`. |
| **`SellEMADelay`** | `int · 0` | Delay in seconds from the moment the `Sell` order is placed before `SellByCustomEMA` checking starts. |
| **`SellEMACheckEnter`** | `bool · YES` | Check the `SellByCustomEMA` formula before entry: if it is already true at the moment of the signal, the buy is blocked (even with `IgnoreFilters=YES`) — otherwise the position would close right after the buy. |
| **`UseMarketStop`** | `bool · NO` | Exchange-side conditional stop order — a **manual trading feature on Binance**: works only in the `Manual` strategy (and for remote control orders) with the `SM` button enabled in the main window. With a negative `MarketStopLevel`, the closing order is **immediately** placed on the exchange as a conditional stop at this level from the entry, and the exchange manages it itself — it will trigger even if the connection to the terminal is lost. A stop and a take-profit do not exist at the same time: a closing order **in the direction of the position** (above the price for a long, below for a short) is a regular limit take-profit, **against the position** (below the price for a long, above for a short) is a stop; by moving the order by hand you switch it between these roles. The order type and execution conditions depend on the exchange; the condition triggering and the full closing of the position are different events, and the terminal keeps watching: if the price broke the stop and the exchange order did not fill within a few seconds, the regular `Panic Sell` kicks in. In automatic strategies the parameter has no effect — the stop there is virtual and works while the terminal is running. |
| **`MarketStopLevel`** | `double · 0` | Initial level of the exchange stop order in `%` from the entry price (negative) with `UseMarketStop = YES` in the `Manual` strategy. `0` sets no initial stop, but with the feature enabled does not prevent turning the closing order into an exchange stop manually — by moving it against the position. |

---

## 2. Step-by-step take-profit price reduction (PriceDown)

The `PriceDown` algorithm, `PriceDownTimer` seconds after the `Sell` order is placed, starts moving the limit `Sell` order closer to the market every `PriceDownDelay` seconds, step by step, down to the `PriceDownAllowedDrop` threshold. It works independently of stop losses, trailing and `SellLevel`; fractional steps smaller than 1 tick accumulate into a whole price step. As soon as someone else moves the take-profit — the trader with the mouse on the chart, or the `SellShot` / `SellSpread` algorithms — `PriceDown` for that order stops and does not resume. `SellLevel` moves do not stop it: both algorithms move the same order at the same time, each on its own timer.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`PriceDownTimer`** | `double · 0` | Time in seconds from the `Sell` order placement to the first take-profit reduction step (`0` — algorithm off). `SellLevel` moves do not reset the countdown; when take-profit orders are joined by `JoinSellKey`, a new take-profit is created and the countdown starts over. |
| **`PriceDownDelay`** | `double · 10` | Interval in seconds between the subsequent `Sell` order price reduction steps. |
| **`PriceDownPercent`** | `double · 0.2` | Size of one `Sell` order price reduction step in `%`. |
| **`PriceDownRelative`** | `bool · NO` | Base for the `PriceDownPercent` step: with `NO` an absolute percentage of the current order price is subtracted; with `YES` — a share of the remaining distance between the current `Sell` and the buy price (with `PriceDownToAllowedDrop=NO` the order approaches the entry price asymptotically without going below it). |
| **`PriceDownToAllowedDrop`** | `bool · NO` | With `PriceDownRelative=YES`, calculate the step not from the distance to the buy price but from the distance between the current `Sell` and the `PriceDownAllowedDrop` threshold (lets the order be lowered smoothly into the negative with a negative `PriceDownAllowedDrop`). |
| **`PriceDownAllowedDrop`** | `double · 0.1` | Lower limit (in `%` from the buy price) down to which `PriceDown` (and the first phase of `SellByFiltersDelay`) may lower the `Sell` order. **Trap on Short:** with values `<= -100` the price calculation denominator becomes non-positive and blocks the reduction — set a sensible limit (for example, `-20`). |

---

<a id="3-moving-the-take-profit-to-the-high-level-or-below-a-wall-selllevel"></a>
## 3. Moving the take-profit by the trade-price extreme (SellLevel)

The `SellLevel` algorithm moves the `Sell` order to the local extreme of the trade price over the `SellLevelTime` window, adjusted by `SellLevelAdjust %`, but not below `SellLevelAllowedDrop`. **Interaction with `PriceDown`:** the timers are independent. `PriceDownTimer` runs from the take-profit placement, `SellLevel` moves do not reset it, and both algorithms may move the same order toward each other. If you enable both, separate them in time (`PriceDownTimer` noticeably greater than `SellLevelWorkTime`).

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`SellLevelDelay`** | `int · 0` | Delay in seconds from the buy to the first `SellLevel` move (`0` — algorithm off). If `SellLevelDelayNext = 0`, it also sets the interval between repeated moves. |
| **`SellLevelDelayNext`** | `int · 0` | Interval in seconds between the second and subsequent `Sell` order moves by the `SellLevel` algorithm. |
| **`SellLevelTime`** | `int · 3600` | Depth of the trade history window in seconds over which the maximum price (`MaxPrice`) is searched to calculate the sell level (`0` — off). |
| **`SellLevelAdjust`** | `double · 0.2` | Adjustment to the found high level in `%`: with `SellLevelRelative=NO` it is added to the high itself (the default `+0.2` places the take-profit **above** the high, a negative value — below it), with `YES` a share of the distance from the entry price to the high is taken. |
| **`SellLevelRelative`** | `bool · NO` | If `YES`, places the take-profit at `SellLevelAdjust %` of the difference between `MaxPrice` over `SellLevelTime` and the buy price (`BuyPrice + (MaxPrice - BuyPrice) * Adjust / 100`). |
| **`SellLevelCount`** | `int · 1` | Maximum number of take-profit moves by the `SellLevel` algorithm. Does not affect the `PriceDown` timer. |
| **`SellLevelWorkTime`** | `int · 0` | Total working time of the `SellLevel` algorithm in seconds after the buy (`0` — no limit). Must be greater than `SellLevelDelay`: the first move is allowed no earlier than `SellLevelDelay` whole seconds, so **`SellLevelWorkTime = 1` effectively disables the algorithm** — the working time expires before the first possible move. Dragging the take-profit manually with the mouse **does not disable** `SellLevel` (it stops only `PriceDown`): `SellLevel`, `SellShot` and `SellSpread` keep moving the order over the manual level until their time or move count runs out. |
| **`SellLevelAllowedDrop`** | `double · 0.1` | Move condition (in `%` from the buy price): if the calculated `SellLevel` level turns out lower, the move is postponed until a better high. |

---

## 4. Take-profit management in a dynamic corridor (SellShot)

The `SellShot` algorithm manages the `Sell` order in a dynamic corridor above the rising price by the `MoonShot` principle: while the impulse continues, the take-profit is moved higher, and when it slows or reverses, the take-profit is pulled toward the price and fills. `SellShotDelay + SellShotPriceDownDelay` s after the `Sell` order is placed, the `SellShotDistance` starts shrinking linearly at the rate of `SellShotPriceDown %/s`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`IgnoreSellShot`** | `bool · YES` | Flag disabling the `SellShot` algorithm: to activate the management, set `IgnoreSellShot = NO`. |
| **`SellShotDelay`** | `double · 0` | Delay of `SellShot` activation from the moment the `Sell` order is placed, in seconds (fractional values supported, `>= 0`). |
| **`SellShotDistance`** | `double · 0.1` | Base distance of the take-profit in `%` above the "market" — the maximum price over `SellShotCalcInterval` s (the minimum in a short). From the moment `SellShot` turns on, it overrides the base take-profit (`SellPrice`, `HookSellLevel`, the `MoonStrike` level) within `SellShotAllowedDown..Up`. Techniques from the site: a tiny distance — the take-profit at the edge of the ask; a negative distance and a negative `SellShotAllowedUp` — instant close (for emulator scouts). |
| **`SellShotCorridor`** | `int · 50` | Width of the working corridor in `%` of `SellShotDistance` (allowed range `1..99%`). With `SellShotDistance = 1%` and `SellShotCorridor = 50` the order is held within `0.5% .. 1.5%` of the price (`±SellShotCorridor %` of the distance on each side) and is moved when it leaves these bounds. |
| **`SellShotCalcInterval`** | `double · 0.6` | Window in seconds (`0.1 .. 25.0` s) for calculating the market price extreme (the maximum for Long, the minimum for Short) from which `SellShotDistance` is measured. |
| **`SellShotRaiseWait`** | `double · 0.2` | Pause in seconds (`>= 0`) before moving the take-profit further from the market (up for Long) when the price rises. |
| **`SellShotReplaceDelay`** | `double · 0.1` | Pause in seconds (`>= 0`) before moving the take-profit closer to the market (down for Long) when the price pulls back. |
| **`SellShotPriceDown`** | `double · 0` | Rate of distance shrinking over time, `%/s`, **set with a minus sign** (`-0.05` — the take-profit moves 0.05% closer to the price every second): `Dist(T) = SellShotDistance - |SellShotPriceDown| * (T - SellShotDelay - SellShotPriceDownDelay)`. A positive value is replaced by zero when saved, and no shrinking occurs. |
| **`SellShotPriceDownDelay`** | `double · 0` | Additional delay in seconds before the distance starts shrinking by `SellShotPriceDown`: counted after `SellShotDelay`, so the shrinking starts `SellShotDelay + SellShotPriceDownDelay` seconds after the `Sell` order is placed. |
| **`SellShotAllowedUp`** | `double · 10` | Upper ceiling (in `%` from the buy price) above which `SellShot` does not raise the take-profit. |
| **`SellShotAllowedDown`** | `double · -0.1` | Lower floor (in `%` from the buy price) below which `SellShot` does not lower the take-profit. |

---

## 5. Holding the take-profit inside the price spread (SellSpread)

The `SellSpread` algorithm holds the `Sell` order inside the price range of the last seconds, offset by `SellSpreadDistance` inward from its far edge, but not worse than `SellSpreadAllowedDrop`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`IgnoreSellSpread`** | `bool · YES` | Flag disabling the `SellSpread` algorithm: to activate it, set `IgnoreSellSpread = NO`. |
| **`SellSpreadMinSpread`** | `double · 0.5` | Minimum current spread in `%` (`>= 0`) at which `SellSpread` moves the take-profit. |
| **`SellSpreadDelay`** | `double · 0` | Delay of the `SellSpread` start in seconds from the moment the `Sell` order is placed (fractional values supported). |
| **`SellSpreadDistance`** | `double · -10` | Offset of the take-profit inward from the far edge of the spread in `%` of the spread width (with a `5%` spread and `-10%` the take-profit is placed at `4.5%` from the bottom of the spread). Automatically clamped to the range `[-100 .. -1]` (a positive number turns into `-1`). |
| **`SellSpreadAllowedDrop`** | `double · 0.3` | Lower limit (in `%` from the buy price) below which `SellSpread` does not lower the `Sell` order. |
| **`SellSpreadReplaceCount`** | `int · 10` | Maximum number of take-profit moves by the `SellSpread` algorithm (`0` — no repeated moves). |
