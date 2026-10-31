# Buy Parameters and Volatility Modifiers (Buy & Delta Modifiers)

> **Related sections:** [Order placement, exits and the stop-loss cascade](../../concepts/06-orders-exits-and-stops-cascade.md) · [The detect and signal pipeline](../../concepts/02-detect-pipeline-and-signals.md) · [Order grids and joining take-profit orders](04-multiorders-and-scales.md) · [Parameter matrix by trade phase](../parameters-by-lifecycle.md) · [Alphabetical TSV index](index.tsv)

This reference describes 45 parameters for placing the opening order (`Buy`) and for dynamically scaling the detect threshold, entry price, take-profit and stop loss by the current market volatility (`Delta Modifiers`).

---

## 1. Direction, size and price of the buy order (Buy Order)

The parameters in this block define whether the strategy places a real order on a signal (`AutoBuy`), in which direction the trade opens (`Long` or `Short`), what type of order is created (`Buy`, `BuyStop`, `BuyLimit`) and from which base price the entry level is calculated.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`AutoBuy`** | `bool · NO` | Allows the `Buy` order to be placed automatically when a detect fires. With `NO` the strategy only gives the signal (alert, trigger, mark on the chart) — an assistant for manual trading. In a kernel + client setup, the detects of checked strategies run on the kernel regardless of `AutoBuy`; there is no need to enable buying "so that the strategy works on the kernel". |
| **`Short`** | `bool · NO` | On futures, opens a short position (`Short`). On spot, sells a token already held on the balance, without borrowed funds (with `OrderSize = 0` the whole available balance of the coin is sold). Auto-borrow on a Binance margin account is a separate terminal setting, available with MoonBonus. |
| **`OrderSize`** | `double · 0` | Order size in the quote currency (`0` — take the order size from the general settings in the main window of the terminal). |
| **`BuyType`** | `string · 'Buy'` | Type of the opening order: `Buy` — a real limit order in the order book; `BuyStop` and `BuyLimit` — conditional pending orders held in the terminal's memory which, once the level is broken both by the order book and by the average trade price, place a real limit order (after triggering, the real order lives 3 seconds regardless of `AutoCancelBuy` — a pending order catches the moment, it does not wait in the queue). In `MoonShot`, `MoonHook`, `Spread`, `MoonStrike` and `UDP` the type is forced to `Buy`. |
| **`PendingOrderSpread`** | `double · 0.1` | Extra price margin in `%` when a conditional `BuyStop` or `BuyLimit` order activates (the real limit order is placed `PendingOrderSpread %` deeper into the market so that it fills with higher probability; the sign sets the side of the offset). |
| **`buyPrice`** | `double · 0` | Offset of the buy price in `%` from the base market price at the moment of the signal (a negative value — below the market, a positive one — above). |
| **`buyPriceAbsolute`** | `bool · NO` | Treat `buyPrice` as the exact absolute price of the coin (for example, `0.015`) rather than a percentage offset from the market. Works only in the `NewListing` strategy. |
| **`buyPriceLastTrade`** | `bool · NO` | Calculate `buyPrice` from the last trade price (with `NO` the base is the current best `ASK` price). |
| **`Use30SecOldASK`** | `bool · NO` | Calculate `buyPrice` from the minimum `ASK` price over the last 30 seconds instead of the current price. |
| **`UseOldPrice`** | `int · 0` | Calculate `buyPrice` from the price as it was `N` seconds ago (`0` — use the current price). |
| **`BuyDelay`** | `int · 0` | Pause before sending the `Buy` order after a detect, in milliseconds (`0..3000` ms). Lets you skip the first tick of the impulse. |

---

## 2. Cancel timers, active order limits and entry protection

This group controls the lifetime of an unfilled order, the quotas on simultaneous trades per strategy and per coin, the exchange execution flags (`UsePostOnly`, `HFT`), the free balance check, and protection against an inflated price in Telegram and Trust Management signals.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`AutoCancelBuy`** | `double · 300` | Auto-cancel timer for an unfilled `Buy` order, in seconds (fractional values supported; `0` — do not cancel). In `MoonShot` forced to at least `15` s; in other strategies, moving the order restarts the timer. For pending `BuyStop`/`BuyLimit` orders the countdown starts when the pending order is placed, not when it triggers: the default `300` s removes the pending order after 5 minutes of waiting — for levels that wait for the price for hours, set `0`. |
| **`AutoCancelLowerBuy`** | `int · 0` | Auto-cancel timer for the `Buy` order (s) in `Telegram` strategies, if the purchase was placed at the lower price from the signal text (`TlgBuyDipPrice`). |
| **`CancelBuyAfterSell`** | `bool · NO` | Cancels the remaining `Buy` orders on the coin right after a `Sell` order of the same strategy fills (or an order with the same non-zero `JoinSellKey`). |
| **`MaxActiveOrders`** | `int · 10` | Maximum number of simultaneously active orders (`Buy` and `Sell`) for this strategy (`0` — no limit). In `MoonStrike` strategies the limit is counted across all strike strategies of the terminal. |
| **`MaxOrdersPerMarket`** | `int · 1` | Maximum number of simultaneous orders of this strategy on one coin (`0` — no limit). |
| **`MaxMarkets`** | `int · 0` | Maximum number of different coins on which the strategy can hold orders at the same time (`0` — no limit; not applied to `MoonStrike`). |
| **`OneOrderPerMarket`** | `bool · NO` | Strict single-order-per-market mode: forbids entry if the coin already has an active trade, disables the grid (`OrdersCount = 1`) and `JoinSellKey` merging. |
| **`UsePostOnly`** | `bool · NO` | Sends the `Buy` order with the exchange flag `PostOnly` (maker only): if the order would cross the spread and fill as a taker, the exchange rejects it automatically. |
| **`HFT`** | `int · 0` | Request validity window `recvWindow` in milliseconds for opening `Buy` orders (on the Bybit WS API also for selling and `Amend` modifications; `0` — the standard window). If network latency exceeds `HFT` ms, the exchange rejects the late order without penalty against API limits. The window is counted from a timestamp that the terminal itself aligns to the exchange clock; a rejection by `HFT` is a normal event during a ping spike ([chapter 07](../../concepts/07-kernel-vps-and-infrastructure.md)). |
| **`CheckFreeBalance`** | `bool · NO` | Before the signal fires, check that the free balance is enough to place the whole `OrdersCount` grid. |
| **`MinFreeBalance`** | `double · 0` | Minimum free balance in the quote currency below which the strategy does not place new orders (`0` — off). |
| **`TlgUseBuyDipWords`** | `bool · NO` | For `Telegram` strategies: if the signal text contains stop words about buying on a pullback, use the `TlgBuyDipPrice` price instead of the regular `buyPrice`. |
| **`TlgBuyDipPrice`** | `double · 0` | Offset of the buy price in `%` to the market when `TlgUseBuyDipWords = YES` fires. |
| **`TMBuyPriceLimit`** | `double · 500` | Trust Management (TM) protection: the maximum allowed excess of the buy price over the current market price in `%`, above which the external command is ignored. |

---

## 3. Volatility coefficients and the resulting modifiers (Delta Modifiers)

The modifiers automatically widen the detect threshold, shift the buy/sell price and widen the stop loss in proportion to the current volatility. First, a weighted sum of the active deltas is computed — a measure of the current volatility. Each delta is prepared beforehand by its own rule (market deltas and `BTC` deltas are taken in absolute value; the mark price deviation participates only on futures, with direction taken into account and without the negative part), then the absolute value of the **whole sum** is taken, and `MaxModifier` caps the result from above:

$$\text{SumDelta} = \min\!\Big(\Big|\sum_i \text{Add}_i \cdot \text{Delta}_i\Big|,\; \text{MaxModifier}\Big) \ge 0$$

(if `MaxModifier = 0`, no cap is applied). Therefore a negative weight does not make the adjustment negative — it is only subtracted inside the sum before the absolute value is taken. This is the common formula for the strategy modifiers; `MoonShot` has its own distance adjustments `MShotAdd*`, which are calculated separately. `SumDelta` is then multiplied by four target coefficients and shifts the corresponding level. The sign is set by the coefficient, not by the delta: a negative `BuyModifier` lowers the buy price on a volatile market, a positive `SellModifier` raises the take-profit, a positive `StopLossModifier` **moves the stop further** from the entry (the value is subtracted from the stop level), and a negative one tightens the stop and, in strong volatility, may close the trade earlier than intended. The modifier affects only the main stop.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`Add3hDelta`** | `double · 0` | Weight of the coin's 3-hour delta in the total `SumDelta`. |
| **`AddHourlyDelta`** | `double · 0` | Weight of the coin's hourly delta in `SumDelta`. |
| **`Add15minDelta`** | `double · 0` | Weight of the coin's 15-minute delta in `SumDelta`. |
| **`Add5minDelta`** | `double · 0` | Weight of the coin's 5-minute delta in `SumDelta`. |
| **`Add1minDelta`** | `double · 0` | Weight of the coin's 1-minute delta in `SumDelta`. |
| **`Add24hDelta`** | `double · 0` | Weight of the coin's daily (24h) delta in `SumDelta`. |
| **`AddMarketDelta`** | `double · 0` | Weight of the hourly delta of the whole market (taken **in absolute value**, always `>= 0`) in `SumDelta`. |
| **`AddMarket24Delta`** | `double · 0` | Weight of the 24-hour delta of the whole market (taken **in absolute value**, always `>= 0`) in `SumDelta`. |
| **`AddBTCDelta`** | `double · 0` | Weight of the hourly `BTC` delta in `SumDelta` (taken **in absolute value**, like the other `BTC` deltas). |
| **`AddBTC5mDelta`** | `double · 0` | Weight of the 5-minute `BTC` delta in `SumDelta`. |
| **`AddBTC1mDelta`** | `double · 0` | Weight of the 1-minute `BTC` delta in `SumDelta`. |
| **`AddMarkDelta`** | `double · 0` | Weight of the mark price (`MarkPrice`) deviation in `SumDelta`. |
| **`AddPriceBug`** | `double · 0.1` | Weight of the current per-coin price lag `PriceBug` (including `Latency`) in `SumDelta`. Lets you move the buy order deeper during exchange lags (in `MoonShot` a separate parameter `MShotAddPriceBug` is used). |
| **`AddPump1h`** | `double · 0` | Weight of the hourly rise `Pump1h` (from the price an hour ago to the hour's high) in `SumDelta`. |
| **`AddDump1h`** | `double · 0` | Weight of the hourly fall `Dump1h` (from the price an hour ago to the hour's low) in `SumDelta`. |
| **`MaxModifier`** | `double · 0` | Upper cap on the total adjustment `SumDelta` (`0` — no cap). There is no lower cap: the sum is non-negative by construction. |
| **`DetectModifier`** | `double · 0.5` | Multiplier for adding `SumDelta` to the detect threshold (`Threshold + SumDelta * DetectModifier`). **Trap in `MoonHook`:** it raises the lower threshold `HookDetectDepth` but does not shift the upper ceiling `HookDetectDepthMax` — once the upper limit is exceeded, the detect stops firing. |
| **`BuyModifier`** | `double · 0` | Multiplier for adding `SumDelta` to the buy price (`buyPrice + SumDelta * BuyModifier`; a negative value places the order lower on a volatile market). |
| **`SellModifier`** | `double · 0` | Multiplier for adding `SumDelta` to the take-profit price (`SellPrice + SumDelta * SellModifier`). |
| **`StopLossModifier`** | `double · 0` | Multiplier for the `SumDelta` adjustment of the main stop-loss level: a positive value **moves** the stop further from the entry by `SumDelta × StopLossModifier` percent (for example, `StopLoss = -1` and an adjustment of `9.75` give a stop of `-10.75`), a negative one tightens it. The actual shift is visible in the log in the `StopLoss adjusted [...]` line. |
