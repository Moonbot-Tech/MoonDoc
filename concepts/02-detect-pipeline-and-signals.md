# 02. Finding trading situations: detects and external signals

> **Official Moonbot documentation:** [What Detectors Are and Why They Matter](https://moonbot.pro/begin/detect-settings/what-detectors-are-and-why-they-matter) | [Working with the Detectors Interface](https://moonbot.pro/begin/detect-settings/working-with-the-detectors-interface) | [Strategy Types](https://moonbot.pro/documentation/strategy-usage/strategy-types) | [“HMap” Button](https://moonbot.pro/documentation/main-terminal-window-with-advanced-settings/hmap-button) | [Telegram Strategy and Its Parameters](https://moonbot.pro/documentation/advanced-strategy-parameters/telegram-strategy-and-its-parameters)  
> **Related sections:** [01. Coin selection and the filter system](01-market-selection-and-filters.md) | [03. Spike hunting: MoonShot, MoonHook and MoonStrike](03-spike-hunting-mechanics.md) | [04. Triggers and Master → Slave links](04-triggers-and-master-slave.md) | [05. CustomEMA formulas](05-ema-geometry-and-formulas.md) | [Reference: detector parameters](../reference/params/02-detectors-and-signals.md) | [Navigator: which strategy to choose](../reference/strategy-selection-guide.md)

---

## 1. What a detect is and what it gives the trader

Candle analysis sees a move when the candle has closed — for scalping that is late: by the close of the first one-minute candle the impulse has often already played out. A detect in Moonbot is a condition on the **live stream**: on every trade in the feed, on an order book change, on a forced liquidation, on a trade by a specific Hyperliquid wallet, on a news item or a Telegram message. Feed detects react to every trade without waiting for the candle to close; order book and candle detects (`Volumes`, `WallsDetection`) are slower by design. The terminal scans all pairs of the strategy's working list simultaneously — something a human cannot do on three hundred charts.

A detect firing is a **signal**, and it has two independent halves:

- **Show the coin to the trader:** a sound and a button with the ticker on the main screen (`SoundAlert`), a chart in a separate window (`AddToChart = 1..N`, available with MoonBonus), a message to your own Telegram channel (`ReportToTelegram`). This is the “detect as an assistant” mode — the site recommends starting any strategy with it.
- **Run the automation:** light the `TriggerKey` trigger key on the coin for other strategies ([chapter 04](04-triggers-and-master-slave.md)) and, if `AutoBuy = YES`, place an order by the rules of the `Buy` / `Sell` tabs.

The key is lit **regardless of `AutoBuy`** — the standard master strategy of a link is exactly a detect with `AutoBuy = NO` and a key. `AutoBuy` decides one thing: whether to place an order. Two exceptions to this scheme: `MoonShot` gives no signal at all (its “detect” is the fill of a limit order standing in advance, [chapter 03](03-spike-hunting-mechanics.md)), and `MoonStrike` without `AutoBuy = YES` is completely silent.

**A trick for manual trading.** A detect with `AutoBuy = YES` and a far entry price (for example, `buyPrice = -3`) places a limit order deliberately below the market: when the chart opens, the order is already in the order book, and the trader only has to pull it up to the spread with the mouse rather than spend seconds placing it.

**“There was a signal, there is no order.”** The sound, button and chart arrive even when the order was cut — by the filter re-check, a busy coin, the order limit, the balance. The reason is written on the coin's chart as the line `AutoStart: FALSE ...` and to the log `logs/LOG_YYYY-MM-DD.log`. If there is no signal either, look at “Filters on charts” ([chapter 01, section 6](01-market-selection-and-filters.md)).

---

## 2. What a detect sees: the feed, the order book, the map of large trades

The working screen is built around the **tick chart**: every point is a real trade, green is a market buy (the aggressor took volume from the sellers), red is a market sell. So that a storm of thousands of small prints does not turn the chart into a blot, neighboring trades of the same direction and the same price that arrived at the same instant are glued into one point — the volume is preserved in full, and detects see the honest turnover. Old history is compressed into five-second bars to save memory. The rest about reading the order book and the feed is on the site, [here](https://moonbot.pro/documentation/main-terminal-window-with-advanced-settings/order-books-buy-and-sell).

**The `HMap` map of large trades** is a strip below the volumes where a point is a participant's order from `$100`, assembled from all of its fills. A horizontal chain of points at one volume level is the signature of an algorithm hitting the market in equal portions; on Hyperliquid every address has its own color, and a series of one color gives away a large participant. The map receives no data when Moon Streamer is enabled, and on futures it is built from the spot of the same coin ([site](https://moonbot.pro/documentation/main-terminal-window-with-advanced-settings/hmap-button)).

**After a restart, detects are silent until they accumulate history.** `Volumes` waits for a full `VolLongInterval`, `VolumesLite` and `Waves` for the sum of the `T0..T3` windows (about 14 minutes at the default values), `Delta` for two long intervals (about 20 minutes by default). This is not a breakage: there is nothing yet to compare “now” with.

---

## 3. Detect map: which strategy type catches what

The full parameter tables of each type are in the [reference](../reference/params/02-detectors-and-signals.md); choosing a type for a task is in the [navigator](../reference/strategy-selection-guide.md).

| What we want to notice | Strategy type (`SignalType`) | Where in detail |
| :--- | :--- | :--- |
| A sharp rise on buys | `PumpsDetection` | section 4 |
| A deep sell-off over tens of seconds | `DropsDetection` | section 4 |
| Feed acceleration in either direction | `Delta` | section 4 |
| Hidden position building by volume | `Volumes`, `VolumesLite`, `Waves` | section 4 |
| Price oscillations in a widened spread | `Spread` | section 5 |
| A market maker's algorithm with identical orders | `Activity` | section 5 |
| Buy-side liquidity below the price | `WallsDetection`, `ChartWall` | section 5 |
| A cascade of forced liquidations | `Liquidations` | section 6 |
| Trades of specific Hyperliquid wallets | `Watcher` | section 7 |
| A signal from Telegram, a news item, TradingView, your own script | `Telegram`, `UDP`, `Combo`, `Alerts`, `Manual`, `NewListing`, `TopMarket` | section 8 |
| A one-second price spike | `MoonShot`, `MoonHook`, `MoonStrike` | [chapter 03](03-spike-hunting-mechanics.md) |
| A condition on indicators by formula | `EMA` | [chapter 05](05-ema-geometry-and-formulas.md) |

---

## 4. Feed detects: impulse, sell-off, volume

### `PumpsDetection`: the start of a run-up

The detector looks for a fast rise on buys: the price rose by no less than `PumpPriceRaise` percent over the `PumpPriceInterval` window (`60`, `30`, `15` or `4` seconds), and this is confirmed by the frequency and volume of buys (`PumpBuysPerSec`, `PumpVolPerSec`). Two peculiarities not visible from the names:

- The rise is measured from the **lowest** bid price over the window, not from the price at its start: a coin that dropped within half a minute and came back gives the same “rise” as one that started rising.
- Buys and their volume are counted over the `PumpVolEMA` smoothing window, but no shorter than two seconds: at the default value, the threshold `PumpBuysPerSec = 15` means fifteen buys in two seconds, not in one.

**Only one** `PumpsDetection` strategy works in the terminal — the topmost of the enabled ones; the others of the same type will never fire, even when the top one is asleep by schedule. If you need different thresholds at different times, change the parameters of the one strategy.

So as not to buy at the very top of the spike, `PumpUsePrevBuyPrice = YES` (default) takes the price from two seconds ago as the entry anchor, and a negative `buyPrice` places the limit order on a pullback inside the impulse. After the buy, `PumpMoveTimer` and `PumpMovePersent` once move the take-profit to the peak reached, with an offset of `PumpMovePersent` percent of the way from the entry: `50` is the midpoint between entry and peak (entry `1000`, peak `1200` → take-profit `1100`), `0.5` is almost at the peak. If the pump did not reach the original take-profit, the take-profit **drops** to the peak — this is an earlier exit, not a later one.

### `DropsDetection`: a sell-off that can be bought back

Looks for a price fall of `DropsPriceDelta` percent over a window of `DropsMaxTime` seconds — a sustained shift, not a single spike, so it suits the search for coins ready for a corrective bounce. `DropsPriceMA` averages past prices, `DropsLastPriceMA` the current one: with `DropsLastPriceMA = 0` the detector also reacts to an instant spike with a return. Keep `DropsPriceMA` small (`0..2`): at a large value the past peak is counted attenuated, and firing needs a noticeably deeper sell-off than set. Zeros in `DropsPriceDelta` and `DropsMaxTime` (the default values) do not disable the detector but keep it from ever firing — fill in both.

### `Delta`: feed acceleration

`DeltaPrice` requires that over two long `DeltaInterval` intervals the price moved noticeably at all — up or down, the detector does not know direction. Direction is set by the sign of `DeltaLastPrice`: plus — the average price of the last short interval is above the long one's average, minus — below. Volume: `DeltaVol` is the turnover over the long interval, `DeltaVolRaise` its growth against the previous one of the same length, `DeltaVolSec` the turnover rate, smoothed so that one large second does not inflate it. This is a universal detector for manual scalping and for the master strategy of a link; it is also available in the Free version.

### `Volumes`, `VolumesLite`, `Waves`: hidden position building

A large participant rarely takes volume in one blow — it accumulates in a series, trying not to push the price up. Three detectors look for this trace.

**`Volumes`** compares buys in the short `VolShortInterval` window with the calm background `VolLongInterval`, requires buys to outweigh sells (`VolBvToSvShort`) and a price move (`VolShortPriseRaise`; zero does not disable the condition — the range must still be greater than zero), and then waits for confirmation from the order book: the sum of bids above the short window's low and high must grow (`volBidsToAsks`, `VolDeltaAt*`). Confirmation takes several re-reads of the order book; if it did not grow, there is no signal. No more than `15` coins are in confirmation at the same time; extra ones are dropped silently. The profile is long-only.

**`VolumesLite` and `Waves`** cut the history into four time windows from left to right: `T0` is the base in the past, `T1`, `T2`, `T3` are the run-up segments, `T3` ends at the last trade. `P1` compares the average price of `T1` with the `T0` base, `P3` the fresh `T3` with `T2`; `V1..V3` do the same for volume; the averages can be weighted by money turnover (`VLiteWeightedAvg`, `WavesWeightedAvg`). `VLitePDelta1/2` is the relative acceleration of the pace: paces of `1 %` and `1.5 %` give `50`, not half a percent. The difference between them is in the base and in the shape: `VLiteDelta0` is a **ceiling** on the base's range (a calm shelf before the run-up), while for `WavesDelta0` the meaning is set by the sign — a positive value requires the base to have moved **more** than the threshold, a negative one — no more. `Waves`, by alternating the signs of `WavesP1..P3`, describes the three-wave pattern “impulse → pullback → continuation”.

### What `Short` does in detects

`Pump`, `Drops`, `Volumes`, `VolumesLite` see the same geometry; `Short = YES` flips only the trade. In `Waves` the wave shape is set by the signs of the thresholds and the trade side by `Short`. In `Spread` a short enters from the upper boundary of the corridor, the buys-to-sells ratio is flipped, the polarity is not. `Delta` catches both rise and fall by the sign of `DeltaLastPrice`. `Liquidations`, `TopMarket`, `MoonStrike` and `Watcher` have no `Short` parameter — direction is set by their own switch (`LiqSameDirection`, `TMSameDirection`, `WatchSameDirection`).

---

## 5. Order book and microstructure detects: `Spread`, `Activity`, walls

### `Spread`: trading oscillations in a widened spread

After a news item or an impulse, the order book near the price thins out, and trades start darting between the boundaries — on the tick chart this appears as rapid back-and-forth price moves. `Spread` trades this oscillation: it buys at the lower boundary of the corridor and sells at the upper one. The strategy is available with the Autotrading module and carries high risk — the site advises running it first without auto-buy, as a detect.

The detect conditions in the trader's terms:

- `TimeInterval` — the analysis window in seconds (`0.5 .. 30`).
- `TradesDensity` — what share of the window the price really darted, that is, trades went at different prices: `100` — continuous oscillation, `50` — for half the window trading stood still or went at one price. Zero does not disable the filter — the minimum is `10`.
- `TradesDensityPrev` — the same density **before** the window: it cuts off coins that were just lying flat. To catch the start of a pump from the bottom, set `0`. Works with a short `TimeInterval`: with a window longer than about 15 seconds the check goes inside the window itself and loses its meaning.
- `TradesCountMin` — the feed must not thin out at any moment of the window; even small values leave only coins with very frequent trades.
- `PriceIntervals` and `PriceSpread` — the window is cut into pieces, and in each the price must travel at least `PriceSpread`. This is how oscillation (many moves) is distinguished from one candle (one move); with `PriceIntervals` above five, one segment is allowed to fall short of the threshold. The range of the whole window is at the same time no less than three price steps.
- `PriceIntervalShift` — the check is repeated with the piece boundaries shifted, and the worst result counts: a range that rested on one candle at the junction of pieces will be exposed by the shift. The larger, the stricter.
- `PriceSpreadMax` — a ceiling on the range for the whole window; needed to assign oscillations of different widths to different strategies.
- `SpreadFlat` — the corridor stands horizontal; a staircase up or down does not count as an oscillation within a horizontal corridor.
- `SpreadPolarityMin / Max` — which way the price shoots out of its average in the last seconds of the window: `+100` — only up, `-100` — only down. The sign is tied to the chart and is not flipped for a short: “only downward spikes” is `SpreadPolarityMax = 0`.
- `Spread_BV_SV_Min / Max` — the ratio of market buys to sells over the last `Spread_BV_SV_Time` milliseconds (for a short — sells to buys).

Orders are placed inside the corridor found: the boundaries are taken from the last `IntervalsForBuySpread` pieces, the entry is at `BuyPriceInSpread` percent of the width from the lower boundary (for a short — from the upper), with `buyPrice` applied on top; the take-profit is the farther, in the trade's direction, of `SellPrice` and the `SellPriceInSpread` level. `BuyOrderReduce` limits the entry size to the feed's average turnover over the specified milliseconds, and an estimate below `MinReducedSize` cancels the detect altogether. `SpreadRepeatIfProfit` allows a repeat entry in the first seconds after the sell is placed, if the price has traveled the set percent (no more than five repeats; requires the module). For `Spread` the `MaxLatency` latency filters are especially important ([chapter 01](01-market-selection-and-filters.md)): a detect on late trades places an order at a price that has already left.

### `Activity`: the signature of a market maker's algorithm

Order-slicing algorithms hit the market with a series of orders of one size. `Activity` looks for this signature: over the `MMTimeFrame` window (`15 .. 60` seconds) it collects trades sized from `MMOrderMin` to `MMOrderMax` dollars, groups them into cells `MMOrderStep` wide, and fires when one size clearly dominates. `MMOrderMin..Max` is where to look (`$100 .. $1000` by default), `MMOrderStep` is what spread to count as “one size”; both identical dollar amounts and identical coin quantities are checked. Whether the robot is buying or selling, the strategy does not distinguish — so `Activity` more often serves as a detect for manual trading or as a master strategy passing a key to strategies with a direction filter (`EMA`, `BV/SV`, `MoonHook`). Detection works on a machine with two or more cores and requires the Autotrading module.

### `WallsDetection` and `ChartWall`: buy-side liquidity below the price

A large order in the order book is a barrier: until it is eaten through, the price goes no further, and scalpers line up in front of it. **`WallsDetection`** is a slow detect: at the close of every five-minute candle it checks that the price sits on a shelf (the candle lows over `WallsMaxTime` lie within the `WallsPriceDelta` corridor) and that below the shelf — from the best price down to `WallBuyVolDeep` below the lower wick — the order book holds bids greater than `WallBuyVolume` and greater than `WallBuyVolToDailyVol` percent of the **daily** turnover; the asks above, up to `WallSellVolDeep`, are at the same time less than `WallSellVolToBuy` percent of the bids. Zeros in `WallsPriceDelta` and `WallSellVolToBuy` (the default values) do not disable the detect but block it. The entry is the usual `buyPrice`; there is no special “in front of the wall” price.

**`ChartWall`** is an experimental detect, hidden by default (enabled with the `Use_sk_ChartWall` key in the `[Special]` section of `MoonBot.ini`). It sums **all** the volume of one side of the order book within a band of `WallSpread` percent from the best price and fires when the sum is greater than `WallSize`; `RedWall` chooses the side (`YES` — asks, `NO` — bids). Then a normal order is placed: the strategy will not watch the wall or cancel the order when it is eaten.

---

## 6. `Liquidations`: a cascade of forced closes

The sharpest vertical spikes with an instant reversal on futures come from the chain liquidation of margin positions. A “long liquidation” is a forcibly closed long, that is, a market sell on a sell-off; a “short liquidation” is a forced buy on an upward squeeze. The strategy is available in PRO on futures with a supported liquidation feed, including Binance and Bybit.

The detect looks at a window of `LiqTime` seconds: no fewer than `LiqCount` liquidations, total volume within the `LiqVolumeMin .. LiqVolumeMax` dollar corridor (the comparison is strict — zero still requires a non-zero volume; any detect needs at least two liquidations in the coin's history). The window's direction is the side whose liquidations are larger by volume; `LiqDirection = OnlyLong` passes only windows dominated by long liquidations, `OnlyShort` — by short ones.

`LiqSameDirection` sets the entry side **relative to the liquidated positions**: `YES` (default) — the same way, that is, after a cascade of long liquidations on a sell-off the terminal buys: the classic bottom buyback, when the exchange has already sold the last margin longs at market and the sellers' pressure has run dry. `NO` — entry along the cascade. The `Combo` (two opposite liquidations in a row) and `Twice` (two identical ones) modes require two detects separated by at least `NextDetectPenalty`. `LiqWaitTime` — entry only after a lull: more than the set milliseconds have passed since the last liquidation; `LiqWithinTime` — the opposite, no later than the set time after the last one. `Liq_BV_SV_Filter` compares the counter volume in the feed with the volume along the cascade (after long liquidations — buys to sells, after short ones — the reverse) over `Liq_BV_SV_Time`: the ratio must be greater than the threshold. The default `0.5` does not yet mean the counter flow prevails — prevalence needs a threshold above `1`.

---

## 7. `Watcher`: trades of specific wallets on Hyperliquid

On Hyperliquid, every trade has a known participant wallet address. `Watcher` is subscribed to the trades of the addresses in the `WatchAddress` field; the coin is taken from the trade itself, so an open chart is not needed — it is enough for the coin to be in the terminal's Coins table. Whale trades are marked on the chart with arrows, and the `Watcher` table shows the address's current position with its sign. The address book is updated when the strategy is saved and on `Start`; in a kernel + client setup, the detect runs on the kernel and the client only displays the trades. The strategy is available in the PRO version and on Hyperliquid in MoonBonus mode.

- `WatchMinVolume` — the volume of the whale's batch of trades in dollars. `WatchMinPosition` — the address's position threshold: what is compared is the position **before** the trade plus the trade's own volume, not the remainder after it; on a partial close of a large position the threshold is passed. Within a batch, the check may go by individual fills.
- `WatchDirection` (`Both`, `OnlyOpen`, `OnlyClose`) chooses whether to react to position building or to its closing. `WatchSameDirection` is tied to the sign of the whale's **position**, not to the side of its last trade: with `YES` the terminal enters in the direction of its position — on a partial close of the whale's long with `OnlyClose` + `YES`, the strategy will open a long, not sell. On spot, `YES` gives a long on any trade by the address, and a short signal with `NO` will not become an order.
- `WatchPriceDeviation` keeps the limit order from falling behind a market that has left after the whale: in a long, the order is placed no lower than the whale's trade price raised by the set percent (in a short — no higher than lowered). This is a pull-up behind the price, not protection against overpaying.

---

## 8. External signals: Telegram, news, TradingView, your own code

### `Telegram`: a signal from a channel

Channels are connected on the **Settings → Telegram** tab. The words by which the terminal understands “this is a signal” are set **once for all channels** on the **Settings → AutoBuy** tab: “Keywords (comma separated) in Long signal”, “… in Short signal”, “Blackwords (comma separated) in message”. The parser finds the coin and the first word from these lists in the message; the strategy fires if its `ChannelName` matched the channel and its `ChannelKey` matched the word found. An empty `ChannelKey` — any message of the channel. A word that is not in the shared list is useless in `ChannelKey`: the strategy will always be silent. Several `Telegram` strategies on one channel are processed down the list, stopping at the first one without `IndependentSignals` (section 9).

`MultiTokens = YES` buys all the coins listed in the message (exchange announcements often name several at once) — enable it only understanding the consequences. Prices from the text are taken only with the shared checkboxes “Use specified price from the message” and “Use Stops, TakeProfit in message” enabled: for a long, the entry price is searched for below the current bid within 15%, choosing the nearest; a stop from the message attaches to the order (`UseSignalStops = YES`) only if `UseStopLoss = YES` is enabled in the strategy itself.

### `MoonNews`: listing and delisting news

Exchange announcements are delivered to the terminal over its own news channel (a News Service subscription is needed). To receive them you need a `Telegram` strategy with `ChannelName = MoonNews` and event tags in `ChannelKey` (`Listing`, `Delisting`, `hack` — several separated by commas or spaces); `MultiTokens` is always recommended for this channel — the coins are attached to the news by the server. News older than 10 seconds from the event time does not start strategies: a late delivery must not open a trade at a price that has left.

The news stream also lights the system keys: `201` on the coins from the news item, `202` on all markets of the terminal, on any news item regardless of tag. The keys work with the Autotrading module or in emulator mode, and their time is the event time, not the moment of receipt, so the `TriggerSeconds` window of the slave strategy counts from the event. For a targeted reaction specifically to a delisting (block buys, drop the position on the coin), use your own `Telegram` strategy with `ChannelKey = Delisting` and its own key.

### `TradingView WebHook`, `UDP`, `Combo`, `Alerts`, `TopMarket`, `NewListing`

- **TradingView WebHook.** An alert from an indicator or a Pine Script comes to the terminal as a message of the `WebHookTV` channel: you need a `Telegram` strategy with `ChannelName = WebHookTV`, and the same shared keywords apply. A request is accepted only with the key in the address; an active module and the enabled TradingView signal reception checkbox in the settings are needed. [Module on the site](https://moonbot.pro/moonbot-pro/modules/tradingview-webhook).
- **`UDP` and the MoonCMD protocol.** Your own screener, a cross-exchange link or a Python model sends a command to the terminal over local UDP, and the terminal takes over the exchange API, the order book, grids, stops and position protection. The protocol and client are in the [reference](../reference/mooncmd-udp-protocol.md) and the [integration example](../examples/integrations/mooncmd-python-client/).
- **`Combo`** links two detects: a `ComboStart` signal, then a `ComboEnd` signal on the same coin `ComboDelayMin .. ComboDelayMax` seconds later. The links can be strategies with an ordinary signal (and `Telegram` / `UDP` / `MoonNews`); `MoonShot` and `MoonStrike` cannot be links. A link with `AutoBuy = NO` does not show its own signal.
- **`Alerts`** fires on the crossing of a line you drew on the chart; `AlertByTrades` chooses whether to count the crossing by trades or by the smoothed average price.
- **`TopMarket`** gives a signal once per change of leader, on the coin with the largest fifteen-minute **range** among those that passed `PriceStepMax`, if the range is no less than `DeltaMin`; direction — by the deviation of the leader's price from the hourly average (`TMSameDirection`).
- **`NewListing`** trades pairs that have just appeared; its entry price can be set absolutely (`buyPriceAbsolute`). The type appears in the list after the agreement is accepted in the terminal. The pair's age and the global “Dont buy newly added coins” slider are in [chapter 01](01-market-selection-and-filters.md).

---

## 9. Several strategies on one coin

**`IndependentSignals`** is a parameter of each strategy on the `Main` tab, not a global setting. With `NO`, strategies of the same type are checked down the list from top to bottom, and after the first suitable one the rest are not checked on this signal. With `YES`, all strategies in a row down the list give a signal **up to the first one where the checkbox is cleared** — a chain, not full independence: for three `Drops` with different thresholds to work in parallel, each needs the checkbox. For `NewListing`, `EMA`, `Spread`, `MoonHook` and `Activity` it is always on; `MoonShot`, `PumpsDetection`, `UDP`, `Combo`, `Manual`, `TopMarket` and `Alerts` do not have the parameter. The order in the list matters within one type: different types are checked in their own cycles, and a slave strategy will see the key at its next check wherever it stands.

**`OneOrderPerMarket = YES`** is the one-order-per-coin mode: the strategy does not enter a busy market, does not place a grid, does not merge its orders with others' and cancels a triggered pending order if the market is busy. With `NO` (default) it adds on top of others' positions — needed for averaging and cascade entries.

**Pauses after a detect.** `NextDetectPenalty` — the same strategy does not fire on the same coin for the set number of seconds; the countdown runs from the detect, even if there was no order. `GlobalDetectPenalty` — the strategy waits after a detect by **any** strategy on the coin. `StrategyPenalty` — a pause of the whole strategy on all coins after any firing — exists only for the `EMA` type; for the others, the only shared pause across all markets is `GlobalFilterPenalty` after a violation of the Bitcoin or market deltas. `TradePenaltyTime`, `PenaltyTime` and the effect of `IgnoreFilters` on these pauses are in [chapter 01, section 6](01-market-selection-and-filters.md).

---

## 10. The Autotrading module, the paid and the free version

What of the above is available depends on the license, and some of the restrictions do not announce themselves with an error.

**The Free version** runs strategies of the `Delta`, `PumpsDetection`, `MoonShot`, `TopMarket`, `Manual`, `Alerts` types, and on Hyperliquid in MoonBonus mode — `Watcher`. The other types cannot be enabled. Orders are real, not emulation; the number of simultaneously active orders is limited by the license.

**The PRO version** opens the other types, with conditions: `MoonStrike`; `Liquidations` — futures with a supported liquidation feed, including Binance and Bybit; `MoonHook` — together with MoonBonus mode; `NewListing` — after accepting the agreement; `Watcher` — on Hyperliquid; `ChartWall` — by the key in `MoonBot.ini`.

**The Autotrading module** (or the terminal's global emulation mode — `EmulatorMode = YES` on an individual strategy does not count) enables what links strategies to each other and to formulas:

| With the module | Without the module |
| :--- | :--- |
| The `EMA`, `Spread`, `Activity` detects | do not fire (`MoonHook` does not require the module — it needs PRO and MoonBonus) |
| Triggers: lighting `TriggerKey`, checking `TriggerByKey`, `TriggerKeysBL`, `SellByTriggerBL`, the system keys `201` / `202` | the conditions are **silently skipped**: the slave enters without the master, the Bitcoin shield blocks nothing |
| Strategy sessions: `SessionPenaltyTime`, `SessionIncreaseOrder` / `SessionReduceOrder` | the limits are not applied |
| `CustomEMA` formulas on entry and `SellByCustomEMA` on exit | are not checked |
| Repeat entries `MShotRepeat*`, `SpreadRepeatIfProfit` | are not placed |

A strategy assembled “by the manual” without the module looks functional and even trades — but without the conditions it was configured for. Before looking for an error in the parameters, check that the module is active ([site](https://moonbot.pro/moonbot-pro/modules/autotrading)).
