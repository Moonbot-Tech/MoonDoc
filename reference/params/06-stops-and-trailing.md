# Stop-Loss, Breakeven and Trailing Parameters (Stops)

> **Concept overview:** [The stop-loss cascade, trailing and Panic Sell mechanics](../../concepts/06-orders-exits-and-stops-cascade.md)  
> **Reference navigation:** [Overview by trade phase](../parameters-by-lifecycle.md) · [Alphabetical index (TSV)](index.tsv) · [Take-profit and sell algorithms](05-sell-and-take-profit.md)

This section describes the 35 parameters of the `Stops` tab: setting up the main stop loss and the emergency exit algorithm `Panic Sell`, switching to breakeven by timer and price (`StopLoss 2` and `StopLoss 3`), protecting profit with a trailing stop (`Trailing`) and the dynamic exit by the trade feed (`BV/SV Stop`).

---

## 1. Main stop loss, liquidation protection and Panic Sell (StopLoss 1)

When the `StopLoss` level is broken, the `Panic Sell` algorithm starts (or a market order is sent with `UseMarketOrder=YES`), which moves the limit `Sell` order step by step deeper into the order book: the initial offset is `StopLossSpread`, the limit is `AllowedDrop`. The `StopLossDelay` delay blocks `Stop 1/2/3` and `Trailing` from triggering in the first seconds after entry, but the `TimeToSwitch2Stop`/`TimeToSwitchStop3` timers are already ticking during it, and `UseBV_SV_Stop` starts working right after entry regardless of `StopLossDelay`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`UseSignalStops`** | `bool · NO` | Only for `Telegram` strategies: take the stop-loss levels from the signal text (if the signal has no stop, the strategy settings apply). |
| **`UseStopLoss`** | `bool · YES` | Enable the main stop loss. A disabled stop creates no fallback limit: if the position is closed by filters, by the `SellByCustomEMA` formula or by the `Panic Sell` button, how far the price is chased is set only by the strategy's `AllowedDrop`. **The second and third stops and pulling the stop toward liquidation (`StopAboveLiq`) are moves of the main stop, not separate stops: with `UseStopLoss = NO` they do not turn on** (the second role of `StopAboveLiq` — a limit for `PriceDown` — does not depend on the stop). If you need only breakeven, keep `UseStopLoss = YES` with a far initial `StopLoss`. |
| **`StopLossFixed`** | `bool · NO` | Do not recalculate the absolute stop-loss price when orders are merged (`JoinSellKey`) or a grid fills (the stop level of the first order is kept). |
| **`FastStopLoss`** | `bool · NO` | Faster stop check on trade and order book prices, without waiting for the smoothed average: the exit on a sharp break of the level happens earlier. Does not guarantee triggering on the first single spike and does not set a fixed reaction time. Not recommended in `MoonShot`, where a repeated spike will immediately knock the trade out by the stop. |
| **`UseMarketOrder`** | `bool · NO` | On any `Panic Sell` of this order — by stop loss, trailing, `BV/SV` stop, exit by filters, formula or key, delisting, manual button — close with a market order instead of the limit cascade. Supported on Binance, Bybit, Gate and Bitget (spot and futures); not applied to a short on spot and on other exchanges — there the limit cascade is always used. If the exchange did not fill the market order, the terminal tries to close with a limit order at the current price and then runs `Panic Sell` by `StopLossSpread` / `AllowedDrop`; closing then depends on the market and is not guaranteed. |
| **`StopLossEMA`** | `int · 0` | Price smoothing for the stop-loss check (`0` — off, modes `3`, `5`, `10`), so that a single spike does not knock out the stop. Applied in the **long** check with `FastStopLoss = NO`; in the current **short** path these modes do not enable similar smoothing of the `ASK` price — do not count on filtering a single price spike in a short. Smoothing does not guarantee the result in a long either. |
| **`StopLossDelay`** | `double · 0` | Delay of `StopLoss 1/2/3` and `Trailing` activation in seconds (fractional values supported) from the moment the `Sell` order is placed. The `Stop 2`/`Stop 3` switch timers count in parallel with `StopLossDelay`. |
| **`StopLoss`** | `double · -5` | Level of the main stop loss in `%` from the buy price (set with a minus sign; adjusted by this strategy's `StopLossModifier`, `Delta Modifiers` tab). |
| **`StopLossSpread`** | `double · 1` | Initial offset of the `Panic Sell` closing order (in `%`, range `0.1 .. 10%`) from the lower of the current prices — the best bid and the last trades (mirrored in a short); the offset grows with each move. The site recommends `0.4 .. 1.5`. |
| **`StopSpreadAdd1mDelta`** | `double · 0.01` | Coefficient for widening `StopLossSpread` by the coin's 1-minute volatility: adds the coin's 1-minute delta multiplied by `StopSpreadAdd1mDelta` (without `PriceBug`). |
| **`AllowedDrop`** | `double · -99` | Limit (in `%` from the entry price) down to which `Panic Sell` may chase the price with the closing limit order after the stop triggers or after an exit by filters / `SellByCustomEMA`. This is **not a loss level**: `StopLoss` sets the level at which the exit starts, `AllowedDrop` — the allowed price of the closing order; the actual result depends on execution on the exchange. The actual floor is another `StopLossSpread` below the set value. Values `< -98` (including the default `-99`) mean "no floor": the order follows the price down to any level the exchange accepts. Too tight an `AllowedDrop` on a squeeze may leave the closing order below the market, and the position will not close — especially dangerous in a short. With `UseMarketOrder = YES` the market order goes out without regard to `AllowedDrop`. |
| **`DontSellBelowLiq`** | `bool · NO` | Only for isolated margin with leverage above one: forbids `Panic Sell` from placing the closing order worse than the calculated liquidation price (in the log: `Stop level (...) is below than liq level`). In the emulator and in a backtest this protection may hold the virtual exit — disable it for the duration of tests. The `UseMarketOrder` market order ignores this protection. |
| **`StopAboveLiq`** | `double · 0` | Offset in `%` from the exchange liquidation price, with two roles: pulls the main stop toward liquidation (this requires `UseStopLoss = YES`) and limits the take-profit lowering by the `PriceDown` algorithm on futures — this limit works even with the stop disabled. `0` — not applied. |
| **`PanicSellDelisted`** | `bool · NO` | Automatically close an open position by the stop when a delisting notice for the coin arrives from the `@MoonInt` system channel (requires consent to share statistics to be enabled). |

---

## 2. Cascade of the second and third stop losses (StopLoss 2 & StopLoss 3)

The cascade lets you move the trade to breakeven or tighten the stop after a set time. The time (`TimeToSwitch*`) and price (`PriceToSwitch*`) conditions are checked by a strict logical **`AND`** and only as long as the main stop has not yet triggered. **Two important traps:**
1. The second stop turns on when, at the same time, `TimeToSwitch2Stop` has passed, the trade has its stop loss enabled, and the price is on the favorable side of the `PriceToSwitch2Stop` threshold from the entry: for a long the best `Bid` is above the "entry + threshold" level, for a short — below the mirrored level (entry `100`, threshold `-10` → a long waits for a price above `90`, a short — below about `111.1`). With the default `0%` it will not turn on in a drawdown; if you want a time-based switch in the negative as well, set a negative threshold (with `-10` the stop will not switch only deeper than `-10%`).
2. If `Stop 2` is configured for a later time, or triggered later than an already active `Stop 3`, it **overwrites** the `Stop 3` level with its `SecondStopLoss` value.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`UseSecondStop`** | `bool · NO` | Move the main stop to the `SecondStopLoss` level when `TimeToSwitch2Stop` and `PriceToSwitch2Stop` are met at the same time. Works only with `UseStopLoss = YES`: this is a move of the stop, not a separate stop. |
| **`TimeToSwitch2Stop`** | `int · 60` | Time in seconds from the moment the `Sell` order is placed, starting from which switching to `SecondStopLoss` is allowed. |
| **`PriceToSwitch2Stop`** | `double · 0` | Price threshold (in `%` from the buy price) for enabling the second stop: the price must be on the favorable side — for a long the best `Bid` above the "entry + threshold" level, for a short below the mirrored level. Additionally requires an expired `TimeToSwitch2Stop` and an enabled stop loss. For the stop to switch in the negative zone as well, set a negative value (for example, `-10`). |
| **`SecondStopLoss`** | `double · 0` | New stop-loss level (in `%` from the buy price) after `StopLoss 2` activates. This is a move of the main stop: does not work without `UseStopLoss = YES`; the chase floor after the second stop is the main `AllowedDrop`. |
| **`UseStopLoss3`** | `bool · NO` | Move the stop to the `StopLoss3` level when `TimeToSwitchStop3` and `PriceToSwitchStop3` are met at the same time. Works only with `UseStopLoss = YES`. |
| **`TimeToSwitchStop3`** | `int · 60` | Time in seconds from the moment the `Sell` order is placed until switching to `StopLoss3` is allowed. |
| **`PriceToSwitchStop3`** | `double · -10` | Price threshold (in `%` from the buy price) for switching to `StopLoss3`: the price must be on the favorable side — for a long above the "entry + threshold" level, for a short below the mirrored level. |
| **`StopLoss3`** | `double · 0` | Level of the third stop loss (in `%` from the buy price). |
| **`AllowedDrop3`** | `double · -99` | Chase limit of the closing order (in `%` from the buy price, `>= -99%`) after the **third** stop triggers (the second uses the main `AllowedDrop`). If after triggering the price fell below the initial stop, the deeper of the two limits is allowed. |

---

## 3. Trailing stop and locking in profit on an impulse (Trailing & TakeProfit)

Trailing watches the peak price after entry (with `TrailingEMA > 0` — the smoothed price) and triggers when the price pulls back from the peak by `|TrailingPercent|`. With `UseTakeProfit = YES` triggering is allowed only while the price stays above the `TakeProfit` level — both by the average trade price and by the last trade; in practice the peak must rise above `TakeProfit` by the pullback amount as well (as a ratio of prices, not a simple sum). At the moment of triggering, the chase floor is raised to the `TakeProfit` level (actually `StopLossSpread` below it), and then the regular `Panic Sell` works with the `TrailingSpread` spread — the closing price depends on the market, the `TakeProfit` level is not guaranteed.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`UseTrailing`** | `bool · YES` | Enable managing the position with a sliding trailing stop. |
| **`TrailingPercent`** | `double · -3` | Pullback distance from the peak price in `%` at which closing by trailing turns on (automatically forced to a negative sign). The main window's global slider "Add … to trailing per each % of price" also changes the trailing of strategy orders. |
| **`TrailingSpread`** | `double · 0.5` | `Panic Sell` step in `%` (`0.1 .. 5.0%`) when trailing and the `BV/SV` stop trigger. An attempt to set `<= 0` is automatically normalized to `0.1%` when the strategy is loaded. |
| **`TrailingEMA`** | `int · 0` | Number of ticks (`0` — off) for smoothing the peak price, so that a single upward spike does not pull the trailing line into an empty `ASK` side of the order book. |
| **`UseTakeProfit`** | `bool · YES` | Allow trailing to trigger only above the `TakeProfit` level (by the average trade price and by the last trade) and, on triggering, raise the chase floor to the `TakeProfit` level (`StopLossSpread` below it). Without trailing the parameter has no meaning. |
| **`TakeProfit`** | `double · 1` | Base level of protected profit in `%` from the buy price for activating trailing with `UseTakeProfit=YES`. |

---

## 4. Stop loss by the buy/sell volume imbalance (BV/SV Stop)

The `BV/SV Stop` algorithm analyzes the ratio of market buy volume (`Buy Volume`) to sell volume (`Sell Volume`) over the last `N` trades or seconds (on Short it is automatically inverted to `SV/BV`). It starts working right after the take-profit is placed, without waiting for `StopLossDelay`, and is in effect while the smoothed bid and the last trade are **on the favorable side** of the `BV_SV_TakeProfit` threshold (above for a long, below for a short). The condition is re-checked every time: once the price went back behind the threshold, the stop is inactive until it crosses it again.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`UseBV_SV_Stop`** | `bool · NO` | Enable closing the position by the ratio of flows in the trade feed over the last `BV_SV_TradesN` trades or **seconds** (by `BV_SV_Kind`): for a long — buys to sells, for a short — sells to buys; exit when the ratio falls below `BV_SV_Ratio`. The stop is in effect while the smoothed bid and the last trade are above the `BV_SV_TakeProfit` threshold from the entry (below in a short); the threshold may be negative (default `-1`), then the stop also works in the negative. With `BV_SV_Reverse = YES` the numerator and denominator swap places — see `BV_SV_Reverse`. **Interaction:** if `BV_SV_TakeProfit < 0.1`, the `BV_SV_Ratio` threshold also works as an entry filter before the buy. |
| **`BV_SV_Kind`** | `string · 'TradesCount'` | Unit of the `BV/SV` ratio calculation window: `'TradesCount'` (over the last `N` trades) or `'Time'` (over the last `N` seconds). |
| **`BV_SV_TradesN`** | `int · 100` | Size of the `BV/SV` calculation window: the number of trades or seconds depending on `BV_SV_Kind`. |
| **`BV_SV_Ratio`** | `double · 0.75` | Threshold `BV/SV` ratio for the stop exit (and for the preliminary entry filter with `BV_SV_TakeProfit < 0.1`). |
| **`BV_SV_TakeProfit`** | `double · -1` | Lower price threshold of `BV/SV Stop` activity in `%` from the entry: with a negative value (for example, `-1%`) the stop works while the drawdown is not deeper than `-1%`, and with a positive one (for example, `+1%`) it works **only while the price is above `+1%`** to protect accumulated profit. With a value `< 0.1` it also enables the entry filter by `BV_SV_Ratio`. |
| **`BV_SV_Reverse`** | `bool · NO` | Swap the numerator and denominator of the `BV/SV` stop fraction: for a long, instead of "buys to sells", "sells to buys" is calculated (the reverse for a short), and the exit happens when this fraction falls below the same `BV_SV_Ratio` — that is, when the flow is going your way (locking in at the climax). **The threshold is set as the reciprocal:** if you want to exit a long when buys outweigh sells twofold, set `BV_SV_Ratio = 0.5`, not `2` (`2` will exit almost immediately). Does not affect the `UseBV_SV_Filter` entry filter. |
