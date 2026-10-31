# Order Grids, Averaging and Joining Take-Profit Orders (MultiOrders & Join)

> **Related sections:** [Order placement, exits and the stop-loss cascade](../../concepts/06-orders-exits-and-stops-cascade.md) · [Buy parameters and volatility modifiers](03-buy-and-modifiers.md) · [Parameter matrix by trade phase](../parameters-by-lifecycle.md) · [Alphabetical TSV index](index.tsv)

This reference describes 10 parameters for building order grids (`Multiple Orders`) and automatically joining take-profit orders and exit management (`JoinSellKey`).

---

## 1. Building the order grid and the averaging step (Multiple Orders)

With `OrdersCount > 1` Moonbot creates a series of $k = 1 \dots \text{OrdersCount}$ independent orders per signal (in the `MoonShot` and `UDP` strategies the grid is forced off: `OrdersCount = 1`). The price, size and auto-cancel timer of the $k$-th grid order are determined by the selected progression mode (`Linear` or `Exponential`):

* **Price step (`BuyPriceStep`, `BuyStepKind`):**
  * `Linear` — each next order is offset by a fixed percentage of the first order's price $P_1$:
    $$P_k = P_1 \cdot \left(1 + \frac{(k - 1) \cdot \text{BuyPriceStep}}{100}\right)$$
    For `Short` the price is divided by $\left(1 + \frac{(k - 1) \cdot \text{BuyPriceStep}}{100}\right)$: the sign of the step is **not changed** — the same negative `BuyPriceStep` as in a long lays out the short legs above the price, against the position (averaging). A positive step in a short places the legs below the first price — on a falling market such sell orders cross the order book and may fill immediately. When the strategy is saved, a negative `BuyPriceStep` is clamped from below at `-99.99 / (OrdersCount - 1)` regardless of the step mode, so that the price of the last order stays strictly positive.
  * `Exponential` — for each $k$-th grid order the base `Price1` is multiplied $k$ times in succession by the step factor $\left(1 + \frac{(k - 1) \cdot \text{BuyPriceStep}}{100}\right)$ for `Long` (and divided by $\left(1 + \frac{(k - 1) \cdot \text{BuyPriceStep}}{100}\right)$ for `Short` — with the same sign of the step):
    $$P_k = P_1 \cdot \left(1 + \frac{(k - 1) \cdot \text{BuyPriceStep}}{100}\right)^k$$
    Because the offset grows quadratically-exponentially, the deep legs of the grid stretch out exponentially in a strong sell-off.
* **Size step (`OrderSizeStep`, `OrderSizeKind`):**
  * `Linear` — the size of the $k$-th order grows arithmetically from the base `OrderSize`:
    $$S_k = \text{OrderSize} \cdot \left(1 + \frac{(k - 1) \cdot \text{OrderSizeStep}}{100}\right)$$
    Equal sizes for all grid orders are achieved with **`OrderSizeStep = 0`**.
  * `Exponential` — the size of each next order is multiplied by the factor $|\text{OrderSizeStep}| / 100$:
    $$S_k = \text{OrderSize} \cdot \left(\frac{|\text{OrderSizeStep}|}{100}\right)^{k - 1}$$
    **Critical trap:** in `Exponential` mode equal order sizes are set with **`OrderSizeStep = 100`** (a multiplier of $1.0$), while with `OrderSizeStep = 0` every order from the 2nd on gets zero size and is not placed! To double each next leg (martingale $\times 2$) in `Exponential`, set `OrderSizeStep = 200`.
* **Cancel timer of the $k$-th level (`CancelBuyStep`):** with `AutoCancelBuy > 0` the lifetime of the $k$-th order is:
  $$T_k = \text{AutoCancelBuy} + (k - 1) \cdot \text{CancelBuyStep}$$

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`OrdersCount`** | `int · 1` | Number of orders the strategy places per signal. In the Free version it is capped by the global setting for the maximum number of grid orders. In `MoonShot`, `UDP` and with `OneOrderPerMarket = YES` it is forced to `1`. |
| **`BuyPriceStep`** | `double · -1.5` | Price step between grid levels in `%`. A negative step lays out the grid **against the position** both in a long and in a short: in a long the legs are below, in a short — above the first order (the terminal mirrors the direction itself, no need to change the sign). A positive step lays out the grid in the direction of the position (breakout); in a short the legs will stand below the first price and on a falling market may fill immediately. When saved, a negative step is clamped from below at `-99.99 / (OrdersCount - 1)` regardless of the mode. |
| **`BuyStepKind`** | `string · 'Linear'` | Law for the distance between price levels in the grid: `Linear` (uniform step in `%` from the first price) or `Exponential` (multiplier `(1 + BuyPriceStep * (k - 1) / 100)^k` from `Price1` for the `k`-th order). |
| **`OrderSizeStep`** | `double · 25` | Step of the grid order size change in `%`. For equal size of all orders set **`0`** with `OrderSizeKind = Linear` and **`100`** with `OrderSizeKind = Exponential`. |
| **`OrderSizeKind`** | `string · 'Linear'` | Law for the grid order size: `Linear` — adds `OrderSizeStep %` of the first order at each step; `Exponential` — multiplies the previous order's size by `|OrderSizeStep| / 100`. |
| **`CancelBuyStep`** | `int · 0` | Extra lifetime (in seconds) for each next grid order on top of the base `AutoCancelBuy`. Has no effect with `AutoCancelBuy = 0`. |
| **`IgnoreCancelBuy`** | `bool · NO` | Disables the auto-cancel timer (`AutoCancelBuy`) for all remaining waiting `Buy` orders of the grid as soon as the **first in order** has filled (including a partial fill with the unfilled remainder cancelled). Lets you hold a deep averaging grid until the position closes. |
| **`AutoSplitBuy`** | `bool · NO` | Manual trading only (`Manual`) with `OrdersCount = 1`: automatically splits a large `Buy` order into parts when it exceeds the exchange's maximum order size limit. |

---

<a id="2-automatic-position-merging-joinsellkey"></a>

## 2. Automatic joining of take-profit orders (JoinSellKey)

The `JoinSellKey` mechanism joins exits for filled entries on the same coin and in the same direction (`Long`/`Short`). Moonbot cancels the separate `Sell` orders, combines the remaining quantities and manages their exit together using a common average entry price. This can reduce the number of small take-profits and the API requests needed to manage them when a grid or a cascade of strategies fires.

**Merging rules and parameter inheritance with `JoinSellKey > 0`:**
1. **Owner strategy search from top to bottom:** the merged order is assigned to the **first running strategy in the list (started with the "Start" button)** with the same `JoinSellKey` value. From it the merged order inherits the strategy name in reports, the take-profit parameters (`SellPrice`), price reduction (`PriceDown`) and the stop-loss cascade (`StopLoss`, `Trailing`).
2. **Fallback — a checked strategy:** if there is no running strategy with this `JoinSellKey` (for example, the bot is stopped), Moonbot takes **the first strategy in the list with the checkbox ticked** — even if it is not running right now or is switched to `EmulatorMode = YES`. The checkbox is the same mark that the `Active=-1` / `Active=0` line stores in the strategy text.
3. **Recalculation of the take-profit price (`JoinPriceFixed`):**
   * With `JoinPriceFixed = NO` (default) the merged take-profit target is calculated from the combined (position-weighted) entry price using the **average current percentage** of the `Sell` orders being merged — a simple average, not weighted by order size. The resulting price may be adjusted to the current market. Neither the total profit in money nor the first order's percentage is preserved: with different order sizes and targets, the common take-profit will not land where a trader counting on either of these rules expects.
   * With `JoinPriceFixed = YES` the merged take-profit is placed at the positive calculated `SellPrice` percentage of the owner strategy from the new average entry price. For strategies with a dynamic take-profit — `MoonHook` and `MoonStrike` — this fixing is not applied: their merged order is calculated by the common path, as with `NO`.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`JoinSellKey`** | `int · 0` | Group number for automatic merging of `Sell` orders (`0` — auto-merging off; manual orders follow the global merging settings). Joins the real `Sell` orders of the same coin and direction with the same key into a common exit, inheriting the sell and stop-loss parameters from the first running strategy in the list with this `JoinSellKey` (and if none is running — from the first checked one). Not applied in `Spread` strategies and with `OneOrderPerMarket = YES`. |
| **`JoinPriceFixed`** | `bool · NO` | How the merged take-profit price is calculated: with `YES` — the positive calculated `SellPrice` percentage of the owner strategy from the new average entry price (not applied to `MoonHook` and `MoonStrike` — they use the common path); with `NO` — the arithmetic mean of the current percentages of the `Sell` orders being merged (not weighted by size) from the same entry price, with a possible market adjustment. The money target and the first order's percentage are not preserved. |
