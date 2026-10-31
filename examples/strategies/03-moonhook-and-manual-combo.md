# Template 03: Standalone MoonHook and a hybrid strategy link for manual trading

> **Official Moonbot documentation:** [MoonHook Strategy and Its Parameters](https://moonbot.pro/documentation/advanced-strategy-parameters/moonhook-strategy-and-its-parameters) | [Manual Strategy and Its Parameters](https://moonbot.pro/documentation/advanced-strategy-parameters/manual-strategy-and-its-parameters)  
> **Related chapters:** [03. Spike hunting](../../concepts/03-spike-hunting-mechanics.md) | [06. Orders, take-profit, and stops](../../concepts/06-orders-exits-and-stops-cascade.md)

> **Access.** `MoonHook` works in PRO together with the MoonBonus mode; the hook itself does not need the Autotrading module. The `CustomEMA` line in the standalone hook is a statistics collector: it writes values only with the Autotrading module or in the terminal's global Emulation mode.

---

## 1. Trading idea and purpose of the template

Unlike `MoonShot`, the **`MoonHook`** strategy keeps no orders in the order book in a calm market: the limit order is placed only after a spike and the first price pullback.

The template has three strategies for two modes of operation:
1. **Standalone entry on a repeat impulse (`03_MoonHook_Auto_v771`).** Within the `HookTimeFrame` window (`0.4…10` s) the price went deeper than `HookDetectDepth` and pulled back by more than `HookPriceRollBack` percent of the depth but no more than `HookPriceRollBackMax`: the strategy places a limit order within the wick left by the spike, anticipating another spike.
2. **Manual hook (`03_Manual_RukaHook_Driver` + the slave `03B_MoonHook_Manual_Slave`).** You click in the order book at the chosen depth, the `Manual` strategy hands the order over to the slave `MoonHook` via `UseHookStrategy=03B_MoonHook_Manual_Slave`, and the slave tracks it within the corridor, places the take-profit, and re-arms the hook when allowed.

> [!IMPORTANT]
> **Why the standalone and the slave `MoonHook` are two different strategies.**  
> When `Manual` is saved, the terminal switches the strategy named in `UseHookStrategy` to slave mode: it turns on its `AutoBuy`, zeroes its `OrderSize`, and clears its start checkbox. After the click, the order is managed by the slave's settings: the `HookPriceDistance` corridor, the `HookSellLevel` take-profit, the `HookRepeatAfterSell` / `HookRepeatIfProfit` re-arm. Do not name a standalone live strategy in `UseHookStrategy`: it will stop trading on its own.

**How to enable the manual hook.**
1. Paste the whole block: the slave comes before `Manual` in it, so the terminal finds it right away on paste. Do not tick the slave's checkbox; the terminal clears it itself.
2. Enable **Menu → Manual Trading → Use Manual Strategy** and select `03_Manual_RukaHook_Driver` by name above the chart.
3. Click in the order book at the desired depth: an order with a green corridor band appears.
4. The manual hook's lifetime is the slave's `AutoCancelBuy = 30`: an order not filled within 30 seconds is cancelled (`0` — until filled or cancelled manually).

---

## 2. Strategy configuration (`FVersion=12`)

The block contains **three strategies** and starts with the `##MultiSelection` line: on `Ctrl+V` the terminal pastes all three. To paste one, copy it from `##Begin_Strategy` to `##End_Strategy`.

```ini
##MultiSelection
##Begin_Strategy
Active=0
FVersion=12
StrategyName=03_MoonHook_Auto_v771
Comment=Standalone MoonHook (OrderSize=100): interpolation mode 2, spike volume threshold HookDetectMinVolume, BuyOrderReduce order size reduction for a large OrderSize.
SignalType=MoonHook
EmulatorMode=YES
AutoBuy=YES
AutoSell=YES
OrderSize=100
CoinsWhiteList=
CoinsBlackList=*3L,*3S,*5L,*5S,*UP,*DOWN,USDC,FDUSD,USDE,TUSD,DAI,EUR
BinanceTokenTags=!Monitoring !Alpha
IgnoreFilters=NO
IgnoreBase=NO
IgnoreTime=NO
IgnorePrice=NO
IgnorePing=NO
IgnoreVolume=NO
IgnoreDelta=NO
IgnoreSession=NO
CheckAfterBuy=YES
DeltaSwitch=0.3
WorkingPriceMin=0.001
WorkingPriceMax=10000
PriceStepMax=0.3
MarkPriceMin=-3.0
MarkPriceMax=1.5
MinLeverage=20
MaxMarkets=20
MaxPing=180
MaxLatency=600
BinancePriceBug=0.6
MinVolume=5M
MaxVolume=100000M
MinHourlyVolume=300K
MaxHourlyVolume=100000M
MinHourlyVolFast=500K
MaxHourlyVolFast=100000M
Delta_3h_Min=0
Delta_3h_Max=60.0
Delta_24h_Min=0
Delta_24h_Max=100.0
Delta_BTC_5m_Min=0
Delta_BTC_5m_Max=2.0
Delta_BTC_Min=-5.0
Delta_BTC_Max=5.0
PenaltyTime=300
TradePenaltyTime=60
NextDetectPenalty=10
GlobalDetectPenalty=0
HookTimeFrame=2.5
HookDetectDepth=2.2
HookDetectDepthMax=60.0
HookAntiPump=YES
HookPriceRollBack=28
HookPriceRollBackMax=85
HookRollBackWait=80
HookDropMin=0
HookDropMax=150
HookDetectMinVolume=50000
HookDirection=OnlyLong
HookOppositeOrder=NO
HookInterpolate=2
HookInitialPrice=45
HookPriceDistance=18
HookRaiseWait=0.3
HookPartFilledDelay=0
HookRepeatIfProfit=0.5
HookRepeatAfterSell=NO
FastShotAlgo=YES
BuyOrderReduce=400
MinReducedSize=0
AutoCancelBuy=12
Add15minDelta=0.2
AddHourlyDelta=0.1
AddMarketDelta=0.1
AddBTC5mDelta=0.4
AddPriceBug=0.3
DetectModifier=0.25
BuyModifier=-0.15
SellModifier=0.2
MaxModifier=8.0
HookSellLevel=55
HookSellFixed=YES
PriceDownDelay=8
PriceDownTimer=2
PriceDownPercent=0.15
PriceDownRelative=NO
PriceDownAllowedDrop=0.1
UseStopLoss=YES
FastStopLoss=YES
UseMarketOrder=YES
StopLossEMA=0
StopLossDelay=1.0
StopLoss=-2.5
StopLossSpread=1.2
StopSpreadAdd1mDelta=0.1
AllowedDrop=-10.0
UseSecondStop=YES
TimeToSwitch2Stop=12
PriceToSwitch2Stop=-0.2
SecondStopLoss=-0.9
AllowedDrop3=-10.0
UseTrailing=YES
TakeProfit=0.9
TrailingPercent=-0.25
TrailingSpread=0.3
UseTakeProfit=YES
SessionStratMin=-8.0
SessionStratMax=40.0
SessionLevelsUSDT=NO
SessionPenaltyTime=600
CustomEMA=EMA(5s,1s)>-888 AND MAX(15m,1s)>-888 AND Vol(1h,5s)>0 AND BTC(5m,1s)>-888
##End_Strategy

##Begin_Strategy
Active=0
FVersion=12
StrategyName=03B_MoonHook_Manual_Slave
Comment=Slave MoonHook for manual hooks (UseHookStrategy in Manual): corridor, HookSellLevel take-profit, stops, HookRepeatAfterSell re-arm. AutoCancelBuy=30 - lifetime of a manual hook.
SignalType=MoonHook
EmulatorMode=YES
AutoBuy=YES
AutoSell=YES
OrderSize=0
IgnoreFilters=YES
IgnoreSession=YES
HookTimeFrame=2.5
HookDetectDepth=2.0
HookDetectDepthMax=60.0
HookPriceRollBack=25
HookPriceRollBackMax=85
HookDirection=OnlyLong
HookInterpolate=2
HookInitialPrice=45
HookPriceDistance=18
HookRaiseWait=0.3
HookPartFilledDelay=0
HookRepeatIfProfit=0.5
HookRepeatAfterSell=YES
FastShotAlgo=YES
AutoCancelBuy=30
HookSellLevel=55
HookSellFixed=YES
UseStopLoss=YES
FastStopLoss=YES
UseMarketOrder=YES
StopLossDelay=1.0
StopLoss=-2.5
StopLossSpread=1.2
AllowedDrop=-10.0
UseTrailing=YES
TakeProfit=0.9
TrailingPercent=-0.25
TrailingSpread=0.3
UseTakeProfit=YES
##End_Strategy

##Begin_Strategy
Active=0
FVersion=12
StrategyName=03_Manual_RukaHook_Driver
Comment=Manual strategy: an order placed by clicking in the order book is handed over to the slave 03B_MoonHook_Manual_Slave.
SignalType=Manual
EmulatorMode=YES
AutoBuy=YES
AutoSell=YES
OrderSize=100
UseHookStrategy=03B_MoonHook_Manual_Slave
IgnoreFilters=YES
IgnoreSession=YES
Delta_3h_Max=1000
Delta_BTC_Min=-100
Delta_BTC_Max=100
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

---

## 3. Step-by-step breakdown of key parameters and limitations

1. **The `HookTimeFrame = 2.5` s window and the `HookAntiPump = YES` filter:**
   * The spike, the pullback, and the `HookRollBackWait` wait must all fit within the `HookTimeFrame` window (allowed `0.4…10` s). A repeat detect on the same coin in the same direction is possible no earlier than roughly `HookTimeFrame` plus one second.
   * `HookAntiPump = YES` counts a spike only if, before it, the price held above the low by at least the detect depth for several windows in a row: a return to the previous level after a short upward burst does not qualify.
2. **Where the order is placed (`HookInterpolate = 2`, `HookInitialPrice = 45`, `HookPriceDistance = 18`, `HookPriceRollBackMax = 85`):**
   * In mode `2` the order is placed at `45%` of the spike above the low, and the `HookPriceDistance` corridor is built around the order. Until the price has pulled back above this level there is no signal, so the minimum pullback in the template is set by `HookInitialPrice = 45`, and `HookPriceRollBack = 28` barely takes part.
   * `HookPriceRollBackMax = 85` is checked **at the detect**: if the price has already recovered more than `85%` of the spike, there is no signal. An order already in place is not cancelled because of it; it is managed by the corridor, the `AutoCancelBuy` timer, and the filters when `CheckAfterBuy = YES`.
3. **Volume threshold and order size reduction (`HookDetectMinVolume = 50000`, `BuyOrderReduce = 400`, `MinReducedSize = 0`):**
   * `HookDetectMinVolume` is how much money must trade within the `HookTimeFrame` window for the spike to count: here `50,000` in `2.5` s. This is the template's volume filter.
   * `BuyOrderReduce` estimates the average turnover over `400` ms within the same window: **estimate = window turnover × `BuyOrderReduce` / `HookTimeFrame`**, with both time values expressed in the same units. If the estimate is less than `OrderSize`, the order is reduced to it (not below the exchange minimum). Reduction is possible even after the volume threshold has been passed, when `OrderSize` exceeds the estimate. A spike that passed the `50,000` threshold in `2.5` s gives an estimate of at least `50,000 × 0.4 / 2.5 = 8000`: with `OrderSize = 100` there is no reduction, and with `OrderSize = 10,000` such a spike reduces the order to `8000`.
   * `MinReducedSize` cancels the detect if the estimate is below the threshold. Volume is already filtered here by `HookDetectMinVolume`, so the threshold is off (`0`). A manual hook is never reduced; in the log this is the line `Buy order reduce not applied (manual hook!)`.
4. **Adapting to rising volatility (`DetectModifier = 0.25`, `BuyModifier = -0.15`, `HookDetectDepthMax = 60.0`):**
   * `DetectModifier` raises the `HookDetectDepth` depth threshold in a volatile market. The `HookDetectDepthMax` ceiling is not shifted by the modifier, so it is set with a margin (`0` — no ceiling): otherwise the raised lower threshold would catch up with the upper one and detects would stop.
   * A negative `BuyModifier = -0.15` does not shift the hook's initial price; it widens the corridor if volatility rose **after** the detect: the lower boundary moves deeper by the increase in the sum of modifiers × `0.15`, the upper one by half as much; the order moves at the next re-placement. A positive `BuyModifier` has no effect on the hook.
5. **Take-profit from the spike depth (`HookSellLevel = 55`, `HookSellFixed = YES`):**
   * With `HookSellFixed = YES`, `55%` of the spike depth is added to the actual entry price, wherever inside the spike the order filled. Example: spike `110 → 100` (depth `10%`), entry `104.5`: take-profit around `110.2`.
   * `SellPrice` is not used by hooks: the take-profit is set by `HookSellLevel` (terminal tooltip: "Replaces SellPrice"), which is why the `MoonHook` blocks have no such field.
6. **Partially filled order (`HookPartFilledDelay = 0`):**
   * The parameter is set in **milliseconds**: `0` — the remainder of a partially filled order is cancelled immediately, as with shots. If the remainder needs time, write thousands: `2000` is two seconds.
7. **Filter checks after the order is placed (`CheckAfterBuy = YES`):**
   * Unlike `MoonShot`, `MoonHook` re-checks the filters while the buy order is in place only when `CheckAfterBuy = YES` is enabled.
8. **Leverage on futures (`MinLeverage = 20`):** the standalone hook takes only coins where you have set leverage of ×20 or more; adjust to your own.
9. **Manual hook and the `Manual` strategy:** `HookRepeatAfterSell` is read from the slave, so the `Manual` block does not have it. The stops in `Manual` and in the slave are identical. The slave's filters also apply: for a coin from its blacklist, the order is placed and immediately cancelled; that is why the slave has `IgnoreFilters = YES` and empty coin lists.

---

## Checking the result

* **Access:** PRO with the MoonBonus mode; the Autotrading module is needed only by the statistics collector in the standalone hook. Spot and futures (on futures, leverage of ×20 or more on the coin).
* **Start:** standalone hook — tick and start `03_MoonHook_Auto_v771`; manual — `Menu → Manual Trading → Use Manual Strategy`, select `03_Manual_RukaHook_Driver`, do not tick the slave.
* **Works if:** a click in the order book produces an order with a green corridor band, and the log shows the line `Manual strategy 03_Manual_RukaHook_Driver turned into Hook 03B_MoonHook_Manual_Slave`; the standalone hook places a virtual `(E)` order only after a spike deeper than `2.2%` followed by a pullback.
* **When the condition is not met:** in a calm market the standalone hook holds no orders; a manual hook not filled within 30 seconds is cancelled.
