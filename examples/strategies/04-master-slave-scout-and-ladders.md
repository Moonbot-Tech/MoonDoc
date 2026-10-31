# Template 04: Master and slave strategy links: spike scouting, a static add-on and a take-profit cascade

> **Official Moonbot documentation:** [“Triggers Master/Slave” Tab](https://moonbot.pro/documentation/general-parameters-for-all-strategies/triggers-masterslave-tab) | [Manage Triggers Window](https://moonbot.pro/documentation/menu-button/manage-triggers) | [MoonShot Strategy and Its Parameters](https://moonbot.pro/documentation/advanced-strategy-parameters/moonshot-strategy-and-its-parameters)  
> **Related chapters:** [04. Strategy links: Master → Slave triggers](../../concepts/04-triggers-and-master-slave.md) | [06. Orders, take-profit, and stops](../../concepts/06-orders-exits-and-stops-cascade.md)

---

## 1. Link A: a virtual scout and a live sniper (`MoonShot`, `TriggerKeyBuy = 10`)

### Trading idea and purpose of the template
Keeping real `MoonShot` limit orders on 200 trading pairs at once is costly because of exchange restrictions (`Quantitative Rules` `-4400` on Binance Futures and the per-minute request limit). The `Master → Slave` link separates monitoring from placing real orders:
* **The master scout strategy (`04A_Master_Scout_Emulator`)** runs in emulator mode (`EmulatorMode=YES`) on 200 coins at once at a close distance — the order sits `1.3%` below the price, corridor `0.9…1.7%` — and places no real orders on the exchange.
* When the first impulse spike happens on a specific coin and the scout's virtual order fills, the strategy activates the trigger key **`TriggerKeyBuy = 10`** on that pair.
* **The slave strategy (`04A_Slave_Sniper_Real`)** starts on key `10` (`TriggerByKey = 10=180`) **only on that coin** for 180 seconds and keeps a `MoonShot` order at the working depth — `2.5%` below the price, corridor `1.8…3.2%`. The sniper sets up from the price that has already moved and catches the continuation or the next spike, not the one that hit the scout.

> **Important about emulation mode (`EmulatorMode=YES`):** for a safe first import, `EmulatorMode=YES` is enabled in every block of this file. To switch the slave sniper `04A_Slave_Sniper_Real` to real trading after checking the settings, clear its Emulator checkbox (`EmulatorMode=NO`).
>
> **Three conditions without which the link does not work:**
> 1. **The Autotrading module** (PRO) or the terminal's global Emulation mode (Menu → Emulation mode). Trigger keys are passed and checked only under one of them; `EmulatorMode=YES` on the strategy itself does not replace it. Without the module the sniper **does not wait for the scout** and enters on any coin that passes its filters.
> 2. **The terminal's order limit.** The scout's virtual orders take up slots in the shared limit of simultaneous `MoonShot` orders on a par with real ones. Without the “Unlimited orders” checkbox (Settings → Advanced → System) the Max Orders field cannot go above 30 — a scout on 200 coins takes every slot, and neither the sniper nor the protective strategies have anywhere to place an order. Tick the checkbox and set Max Orders with headroom: the scout's coins + the sniper's orders + the protective strategies.
> 3. **Spot.** The “buy and do not sell” recipe (`AutoSell = NO`) exists only on spot. On futures `AutoSell` is hidden and forced to `YES`: after firing, the scout holds the virtual position until it closes and does not re-arm on that coin all that time. For futures, give the scout a short exit (`SellPrice`, `StopLoss`) or build the master on a signal detect without a buy.

The block contains **two strategies** and starts with the `##MultiSelection` line — on `Ctrl+V` the terminal pastes both. To paste one, copy it from `##Begin_Strategy` to `##End_Strategy`.

```ini
##MultiSelection
##Begin_Strategy
Active=0
FVersion=12
StrategyName=04A_Master_Scout_Emulator
Comment=Scout in the emulator on 200 coins. AutoSell=NO and ActiveTrigger=NO are mandatory.
SignalType=MoonShot
EmulatorMode=YES
AutoBuy=YES
AutoSell=NO
OrderSize=20
CoinsWhiteList=
CoinsBlackList=BTC,ETH,*3L,*3S,*5L,*5S,*UP,*DOWN,USDC,FDUSD,USDE,TUSD,DAI,EUR
BinanceTokenTags=!Monitoring !Alpha
IgnoreFilters=NO
IgnoreSession=YES
CheckAfterBuy=YES
MaxMarkets=200
MShotSortBy=HourlyVol
AutoCancelBuy=120
MinVolume=10M
MaxVolume=100000M
MinHourlyVolume=500K
MaxHourlyVolume=100000M
Delta_3h_Max=50.0
Delta_BTC_Min=-4.0
Delta_BTC_Max=4.0
PriceStepMax=0.35
PenaltyTime=0
NextDetectPenalty=10
GlobalDetectPenalty=0
MShotPriceMin=0.9
MShotPrice=1.3
MShotReplaceDelay=0.1
MShotRaiseWait=0.3
MShotUsePrice=Trade
FastShotAlgo=YES
TriggerKeyBuy=10
TriggerKeyProfit=0
TriggerKeyLoss=0
ActiveTrigger=NO
TriggerAllMarkets=NO
##End_Strategy

##Begin_Strategy
Active=0
FVersion=12
StrategyName=04A_Slave_Sniper_Real
Comment=Slave MoonShot: order 2.5% below the price (corridor 1.8..3.2%) only on the coin where the scout caught a spike (key 10 for 180 s). For real trading switch EmulatorMode=NO.
SignalType=MoonShot
EmulatorMode=YES
AutoBuy=YES
AutoSell=YES
OrderSize=100
CoinsWhiteList=
CoinsBlackList=BTC,ETH,*3L,*3S,*5L,*5S,*UP,*DOWN,USDC,FDUSD,USDE,TUSD,DAI,EUR
BinanceTokenTags=!Monitoring !Alpha
IgnoreFilters=NO
IgnoreSession=NO
CheckAfterBuy=YES
TriggerByKey=10=180
TriggerKeysBL=101=45 102=120
CancelByTriggerBL=YES
SellByTriggerBL=102
MaxMarkets=10
MShotSortBy=HourlyVol
AutoCancelBuy=60
MaxLatency=500
MinVolume=10M
MaxVolume=100000M
MaxHourlyVolume=100000M
Delta_3h_Max=50.0
Delta_BTC_Min=-4.0
Delta_BTC_Max=4.0
PriceStepMax=0.35
PenaltyTime=300
TradePenaltyTime=60
NextDetectPenalty=15
GlobalDetectPenalty=0
MShotPriceMin=1.8
MShotPrice=2.5
MShotAddHourlyDelta=0.15
MShotAdd15minDelta=0.25
MShotAddBTC5mDelta=0.5
MShotAddDistance=45
MaxModifier=8.0
MShotReplaceDelay=0.2
MShotRaiseWait=0.4
MShotUsePrice=Trade
FastShotAlgo=YES
HFT=250
MShotSellAtLastPrice=YES
SellPrice=1.2
UseStopLoss=YES
FastStopLoss=YES
UseMarketOrder=YES
StopLossDelay=1.0
StopLoss=-2.5
StopLossSpread=1.2
AllowedDrop=-10.0
##End_Strategy
```

### Key parameters and limitations of Link A:
1. **`AutoSell = NO` on the scout strategy (spot only):** the scout's virtual trade is not as harmless as it looks. If it closes at a loss, the coin gets the `TradePenaltyTime` pause (after one) and `PenaltyTime` (after three in a row) in every strategy where they are set, and the close activates `TriggerKeyProfit` / `TriggerKeyLoss`. `AutoSell = NO` ends the scout's job right after the virtual buy — no take-profit, no close, no side effects. On futures this parameter is unavailable (see the conditions above).
2. **`ActiveTrigger = NO` on the master `MoonShot`:** on `MoonShot`, an enabled `ActiveTrigger` keeps refreshing `TriggerKeyBuy` the whole time the order simply sits in the order book, before it fills. For key `10` to be passed strictly at the moment of the spike (the fill of the virtual buy), `ActiveTrigger` is off. `MoonShot` has no `TriggerKey` field — it passes a key only by a buy.
3. **The sniper's take-profit (`MShotSellAtLastPrice = YES`, `SellPrice = 1.2`):** the shot's take-profit is placed at the higher of two prices — `SellPrice` from the entry and the sell price before the spike (the ask a few seconds before the hit). `SellPrice` here is the lower bound; for a fixed take-profit use `MShotSellAtLastPrice = NO`.
4. **Shield keys in the sniper (`TriggerKeysBL = 101=45 102=120`, `SellByTriggerBL = 102`):** the sniper is connected to the protection in [template 05](05-btc-dump-shield-and-delist-guard.md) with the same key times.

---

## 2. Link B: a one-time static add-on to the position (`EMA` + `BuyLimit`)

### Trading idea and purpose of the template
If the price keeps falling after the main order fills, the trader often needs to add to the position at a fixed distance (for example, at `-2.0%` from the price at the moment the slave strategy fires). A slave `MoonShot` is not suitable for this: in a fall it keeps moving the order lower and lower.

The task is solved by a slave strategy of the `EMA` type (`04B_Slave_Static_Add_Minus2pct`), which on the master's buy key (`TriggerByKey = 20=3`) places a conditional `BuyLimit` order with `buyPrice = -2.0` (and `PendingOrderSpread = 0.3`), immediately clears the incoming key `20` via `ClearTriggerKeys = 20`, and on a fill on a real account joins their remaining quantities under a shared take-profit using `JoinSellKey = 20`.

A conditional order is a level in the terminal's memory, not an order in the order book. With `AutoCancelBuy = 0` it waits for the `-2%` touch indefinitely, and after the touch it places a limit order that lives about three seconds: this is an attempt to buy at the moment of the touch, not an order resting in the order book. If you need a limit order that sits in the order book in advance, use `BuyType = Buy` with a negative `buyPrice = -2`.

> **What the master strategy must contain** (its block is not in this file — add these to your working strategy): `TriggerKeyBuy = 20` (the key is activated by a buy), `JoinSellKey = 20` (without it there is no merging), `OneOrderPerMarket = NO` (otherwise merging is disabled) and **`CancelBuyAfterSell = YES`**. The last one is critical: the add-on order sits with `AutoCancelBuy = 0` and is not re-checked (`DontCheckBeforeBuy = YES`, `CheckAfterBuy = NO`). If the main position closed by take-profit before the price reached `-2%`, an add-on without `CancelBuyAfterSell` outlives it and later opens a **standalone** trade on a falling coin — there is nothing left for it to merge with.

```ini
##Begin_Strategy
Active=0
FVersion=12
StrategyName=04B_Slave_Static_Add_Minus2pct
Comment=One-time static add-on (buyPrice=-2.0) on key 20 with key reset (TriggerKey=20 + ClearTriggerKeys=20) and joining take-profit orders by JoinSellKey=20 in live trading.
SignalType=EMA
EmulatorMode=YES
AutoBuy=YES
AutoSell=YES
OrderSize=150
CoinsWhiteList=
CoinsBlackList=*3L,*3S,*5L,*5S,*UP,*DOWN,USDC,FDUSD,USDE
BinanceTokenTags=!Monitoring !Alpha
IgnoreFilters=NO
IgnoreBase=NO
IgnoreTime=YES
IgnorePrice=YES
IgnorePing=YES
IgnoreVolume=YES
IgnoreDelta=YES
IgnoreSession=NO
OneOrderPerMarket=NO
DontCheckBeforeBuy=YES
CustomEMA=EMA(30m,1s)>-888
TriggerByKey=20=3
TriggerKey=20
ClearTriggerKeys=20
BuyType=BuyLimit
PendingOrderSpread=0.3
buyPrice=-2.0
UseScalpingMode=YES
AutoCancelBuy=0
JoinSellKey=20
JoinPriceFixed=NO
SellPrice=1.0
UseStopLoss=YES
FastStopLoss=YES
UseMarketOrder=YES
StopLossDelay=1.0
StopLoss=-3.0
StopLossSpread=1.5
AllowedDrop=-12.0
Delta_3h_Max=1000
Delta_BTC_Min=-100
Delta_BTC_Max=100
PriceStepMax=100
MinVolume=100
MaxVolume=100000M
MaxHourlyVolume=100000M
PenaltyTime=0
NextDetectPenalty=1
GlobalDetectPenalty=0
##End_Strategy
```

### Key parameters and limitations of Link B:
1. **Exact case of `buyPrice=-2.0` and the reference price:** on text import, field names are compared case-sensitively — the parameter is written strictly in lowercase: **`buyPrice`**; a `BuyPrice` line is silently ignored and the field stays at its default value. `buyPrice=-2.0` is measured from the price at the moment the **slave** fires, not from the master's buy price: the key arrives right after the buy, so the two are usually close, but not guaranteed. When the conditional level is touched, the limit order is sent with a `PendingOrderSpread=0.3` tolerance.
2. **One-time firing and key reset (`TriggerKey = 20`, `ClearTriggerKeys = 20`):** key clearing (`ClearTriggerKeys`, `ClearTriggersBelow`, `ClearTriggersAbove`) runs **only together with the strategy's own non-zero key**: with `TriggerKey = 0` it does not run at all. In local mode (`TriggerAllMarkets = NO`) key `20` is first written and then immediately erased from the coin by the clear list — so the add-on starts exactly once.
3. **Joining take-profit orders with `JoinSellKey = 20` works only in live trading:** orders are not merged either in the terminal's global Emulation mode or with `EmulatorMode = YES` on the strategy. `EmulatorMode = YES` is set here for a safe first import; to check the merging of two orders into a shared take-profit, both the master and the slave must run on real orders (`EmulatorMode = NO`).

---

## 3. Link C: scaling out of the position with a take-profit cascade

### Trading idea and purpose of the template
When a trade is opened with a single order (or with a grid merged by `JoinSellKey`), the whole position volume is closed by one shared take-profit. To split the entry on one signal into several independent orders with stepwise profit taking (for example, close the first part at `+0.8%`, the second at `+1.6%` and the third at `+2.8%`), the master strategy buys the first part and activates the key `TriggerKeyBuy = 30`, and the slave `EMA` strategies on key `30` place their own orders with individual `SellPrice` levels without `JoinSellKey` merging.

```ini
##Begin_Strategy
Active=0
FVersion=12
StrategyName=04C_Slave_Ladder_Take2_1.6pct
Comment=Second profit-taking step (+1.6%), entering on the master strategy's buy key (Key 30) without JoinSellKey merging.
SignalType=EMA
EmulatorMode=YES
AutoBuy=YES
AutoSell=YES
OrderSize=50
CoinsWhiteList=
CoinsBlackList=*3L,*3S,*5L,*5S,*UP,*DOWN,USDC,FDUSD,USDE
BinanceTokenTags=!Monitoring !Alpha
IgnoreFilters=NO
IgnoreBase=NO
IgnoreTime=YES
IgnorePrice=YES
IgnorePing=YES
IgnoreVolume=YES
IgnoreDelta=YES
IgnoreSession=NO
OneOrderPerMarket=NO
DontCheckBeforeBuy=YES
CustomEMA=EMA(30m,1s)>-888
TriggerByKey=30=2
TriggerKey=0
ClearTriggerKeys=
BuyType=Buy
buyPrice=0.2
UseScalpingMode=YES
AutoCancelBuy=3
SellPrice=1.6
UseStopLoss=YES
FastStopLoss=YES
UseMarketOrder=YES
StopLossDelay=1.0
StopLoss=-2.5
StopLossSpread=1.2
AllowedDrop=-10.0
Delta_3h_Max=1000
Delta_BTC_Min=-100
Delta_BTC_Max=100
PriceStepMax=100
MinVolume=100
MaxVolume=100000M
MaxHourlyVolume=100000M
PenaltyTime=0
NextDetectPenalty=30
GlobalDetectPenalty=0
##End_Strategy
```

### Key parameters and limitations of Link C:
1. **`OneOrderPerMarket = NO` and `DontCheckBeforeBuy = YES`:** allow the slave strategy to open an additional independent order on a pair where the master strategy has already opened, without re-checking the general filters before the buy.
2. **Independent take-profit tracking:** the absence of `JoinSellKey` leaves the order a standalone task with its own target level `SellPrice = 1.6%` and its own stop / trailing.
3. **The shared ladder key is not cleared in the steps.** Slave `EMA` strategies are checked one after another in a single pass: if the first step erased key `30` (`ClearTriggerKeys = 30`), the second would no longer see it, and the ladder would not fill up. That is why the steps have `TriggerKey = 0` and an empty `ClearTriggerKeys`, and a single entry per step is ensured by the short key window (`TriggerByKey = 30=2`) and the repeat-detect pause `NextDetectPenalty = 30`, which is longer than the window. The third step (`+2.8%`) is a copy of this block with a different `StrategyName` and `SellPrice`; the master must activate `TriggerKeyBuy = 30` with its buy. Before a live launch, run the ladder in the emulator.

---

## Checking the result

* **Access:** the Autotrading module or the terminal's global Emulation mode — without them the sniper and the slaves enter without a key. The scout recipe with `AutoSell = NO` is for spot; with a scout on 200 coins — the “Unlimited orders” checkbox and `Max Orders` with headroom.
* **Start:** the whole `04A` block (scout and sniper), both strategies checked and started; for `04B` / `04C` — your master with `TriggerKeyBuy = 20` / `30` (and for `04B` — with `JoinSellKey = 20`, `OneOrderPerMarket = NO`, `CancelBuyAfterSell = YES`).
* **Works if:** on the coin where the scout's virtual order filled, the sniper's line `This market is not triggered (By key 10 …)` disappears in “Filters on charts” and its order appears. Without a spike, the link is checked with a manual key: `Menu → Manage Triggers`, key `10` (for the slaves `04B` / `04C` — `20` / `30`), the coin, `Set`. The window itself shows which keys are used by strategies (`Used Keys`), not which are currently active on coins.
* **When the condition is not met:** on the other coins the sniper shows `This market is not triggered (By key 10 …)` and places no orders; 180 seconds after the key it leaves this coin too. `JoinSellKey` merging is not checked in the emulator — only on real orders.
