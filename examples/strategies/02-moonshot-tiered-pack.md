# Template 02: Tiered MoonShot strategy pack with volatility adaptation

> **Official Moonbot documentation:** [MoonShot Strategy and Its Parameters](https://moonbot.pro/documentation/advanced-strategy-parameters/moonshot-strategy-and-its-parameters)  
> **Related chapters:** [03. Spike hunting](../../concepts/03-spike-hunting-mechanics.md) | [01. Coin selection for scalping](../../concepts/01-market-selection-and-filters.md)

> **What works without the module.** `MoonShot` also runs in the Free version (real orders, up to 30 active). The `CustomEMA` line (statistics collector) and the session thresholds (`SessionStratMin` / `SessionStratMax`, `SessionPenaltyTime`) work only with the Autotrading module or in the terminal's global Emulation mode: without them the template trades, but the collector stays silent and the session limits are not applied.

---

## 1. Trading idea and purpose of the template

A single `MoonShot` strategy with a fixed depth does not suit every phase of an impulsive market:
* a near order catches brief downward price spikes, but on a strong move with no pullback it fills at the very start of the candle;
* a far order survives small waves but fills rarely: only strong spikes reach its depth.

So the pack is built from several independent strategies separated by order depth and by their response to volatility. The `MoonShot` order sits `MShotPrice` below the price, with a corridor around it: the near boundary is `MShotPriceMin`, the far one is `MShotPrice + min(MShotPriceMin, MShotPrice − MShotPriceMin)` ([chapter 03](../../concepts/03-spike-hunting-mechanics.md), section 2). When the price comes closer to the order than the near boundary, the order moves deeper; when the price moves up so far that the order ends up beyond the far boundary, the order is pulled up.

1. **Tier one (`02_MShot_Tier1_Fast_1.7pct`):** the order is `1.7%` below the price, corridor `1.2…2.2%`. It stays only while the coin trades more actively than usual: minute volume at least `1.2` times the reference average minute volume (`MinuteVolDeltaMin`). The shot checks the filters the whole time the order is in place, so when volume quiets down, the limit order is cancelled. The `MShotReplaceDelay = 0.1` s delay before moving the order deeper lets a fast spike fill the limit order.
2. **Tier two (`02_MShot_Tier2_Deep_3.8pct`):** the order is `3.8%` below the price, corridor `2.8…4.8%`, a larger order size, and a longer hold before moving the order, `MShotReplaceDelay = 0.3` s, so that a deep cascading spike has time to fill the limit order instead of chasing it down.

---

## 2. Strategy configuration (`FVersion=12`)

The block contains **two strategies** and starts with the `##MultiSelection` line: on `Ctrl+V` the terminal pastes both. To paste one, copy it from `##Begin_Strategy` to `##End_Strategy`.

```ini
##MultiSelection
##Begin_Strategy
Active=0
FVersion=12
StrategyName=02_MShot_Tier1_Fast_1.7pct
Comment=Near MoonShot: order 1.7% below the price, corridor 1.2..2.2%, on a volatile market the order moves deeper (MShotAdd*, MShotAddDistance).
SignalType=MoonShot
EmulatorMode=YES
AutoBuy=YES
AutoSell=YES
OrderSize=50
CoinsWhiteList=
CoinsBlackList=BTC,ETH,*3L,*3S,*5L,*5S,*UP,*DOWN,USDC,FDUSD,USDE,TUSD,DAI,EUR
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
DeltaSwitch=0.2
WorkingPriceMin=0.001
WorkingPriceMax=10000
PriceStepMax=0.25
MarkPriceMin=-2.0
MarkPriceMax=1.0
MinLeverage=20
MaxMarkets=8
AutoCancelBuy=60
MaxPing=150
MaxLatency=450
BinancePriceBug=0.5
MinVolume=15M
MaxVolume=100000M
MinHourlyVolume=1M
MaxHourlyVolume=100000M
MinHourlyVolFast=1500K
MaxHourlyVolFast=100000M
MinuteVolDeltaMin=1.2
MinuteVolDeltaMax=50
Delta_3h_Min=0
Delta_3h_Max=25.0
Delta_24h_Min=0
Delta_24h_Max=45.0
Delta2_Type=1h
Delta2_Min=0.5
Delta2_Max=12.0
Delta3_Type=15m
Delta3_Min=0
Delta3_Max=6.0
Delta_BTC_5m_Min=0
Delta_BTC_5m_Max=1.2
Delta_BTC_Min=-3.0
Delta_BTC_Max=3.0
PenaltyTime=300
TradePenaltyTime=60
NextDetectPenalty=15
GlobalDetectPenalty=0
MShotPriceMin=1.2
MShotPrice=1.7
MShotAddHourlyDelta=0.15
MShotAdd15minDelta=0.25
MShotAddMarketDelta=0.2
MShotAddBTC5mDelta=0.5
MShotAddPriceBug=0.3
MShotAddMarkDelta=0.5
MShotAddDistance=40
MShotMinusSatoshi=NO
MaxModifier=6.0
MShotReplaceDelay=0.1
MShotRaiseWait=0.4
MShotSortBy=HourlyVol
MShotUsePrice=Trade
FastShotAlgo=YES
MShotRepeatAfterBuy=NO
HFT=250
MShotSellAtLastPrice=YES
SellPrice=0.9
PriceDownDelay=8
PriceDownTimer=2
PriceDownPercent=0.15
PriceDownRelative=NO
PriceDownAllowedDrop=0.1
SellByFilters=12
SellByFiltersDelay=1.5
UseStopLoss=YES
FastStopLoss=YES
UseMarketOrder=YES
StopLossEMA=0
StopLossDelay=1.0
StopLoss=-2.2
StopLossSpread=1.2
StopSpreadAdd1mDelta=0.1
AllowedDrop=-8.0
UseSecondStop=YES
TimeToSwitch2Stop=12
PriceToSwitch2Stop=-0.2
SecondStopLoss=-0.8
AllowedDrop3=-8.0
UseTrailing=YES
TakeProfit=0.7
TrailingPercent=-0.25
TrailingSpread=0.3
UseTakeProfit=YES
SessionStratMin=-6.0
SessionStratMax=30.0
SessionLevelsUSDT=NO
SessionPenaltyTime=600
CustomEMA=EMA(5s,1s)>-888 AND EMA(60s,1s)>-888 AND MAX(15m,1s)>-888 AND Vol(1h,5s)>0 AND BTC(5m,1s)>-888
##End_Strategy

##Begin_Strategy
Active=0
FVersion=12
StrategyName=02_MShot_Tier2_Deep_3.8pct
Comment=Deep MoonShot: order 3.8% below the price, corridor 2.8..4.8%, MShotReplaceDelay=0.3 s hold for deep cascading spikes.
SignalType=MoonShot
EmulatorMode=YES
AutoBuy=YES
AutoSell=YES
OrderSize=100
CoinsWhiteList=
CoinsBlackList=BTC,ETH,*3L,*3S,*5L,*5S,*UP,*DOWN,USDC,FDUSD,USDE,TUSD,DAI,EUR
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
PriceStepMax=0.35
MarkPriceMin=-3.5
MarkPriceMax=1.5
MinLeverage=20
MaxMarkets=12
AutoCancelBuy=90
MaxPing=200
MaxLatency=700
BinancePriceBug=0.8
MinVolume=10M
MaxVolume=100000M
MinHourlyVolume=500K
MaxHourlyVolume=100000M
MinHourlyVolFast=1M
MaxHourlyVolFast=100000M
Delta_3h_Min=0
Delta_3h_Max=40.0
Delta_24h_Min=0
Delta_24h_Max=80.0
Delta2_Type=1h
Delta2_Min=1.0
Delta2_Max=25.0
Delta_BTC_5m_Min=0
Delta_BTC_5m_Max=2.2
Delta_BTC_Min=-5.0
Delta_BTC_Max=5.0
PenaltyTime=300
TradePenaltyTime=90
NextDetectPenalty=20
GlobalDetectPenalty=0
MShotPriceMin=2.8
MShotPrice=3.8
MShotAddHourlyDelta=0.2
MShotAdd15minDelta=0.35
MShotAddMarketDelta=0.3
MShotAddBTC5mDelta=0.8
MShotAddPriceBug=0.4
MShotAddMarkDelta=0.5
MShotAddDistance=50
MShotMinusSatoshi=NO
MaxModifier=12.0
MShotReplaceDelay=0.3
MShotRaiseWait=0.6
MShotSortBy=HourlyVol
MShotUsePrice=Trade
FastShotAlgo=YES
MShotRepeatAfterBuy=NO
HFT=350
MShotSellAtLastPrice=YES
SellPrice=1.8
PriceDownDelay=10
PriceDownTimer=3
PriceDownPercent=0.2
PriceDownRelative=NO
PriceDownAllowedDrop=0.2
UseStopLoss=YES
FastStopLoss=YES
UseMarketOrder=YES
StopLossEMA=0
StopLossDelay=1.5
StopLoss=-3.5
StopLossSpread=1.5
StopSpreadAdd1mDelta=0.15
AllowedDrop=-12.0
UseSecondStop=YES
TimeToSwitch2Stop=18
PriceToSwitch2Stop=-0.5
SecondStopLoss=-1.2
AllowedDrop3=-12.0
UseTrailing=YES
TakeProfit=1.2
TrailingPercent=-0.35
TrailingSpread=0.4
UseTakeProfit=YES
SessionStratMin=-10.0
SessionStratMax=50.0
SessionLevelsUSDT=NO
SessionPenaltyTime=900
CustomEMA=EMA(5s,1s)>-888 AND EMA(60s,1s)>-888 AND MAX(15m,1s)>-888 AND Vol(1h,5s)>0 AND BTC(5m,1s)>-888
##End_Strategy
```

---

## 3. Step-by-step breakdown of key parameters and limitations

1. **Integer volume fields (`MinHourlyVolFast = 1500K`):**
   * `MinVolume`, `MinHourlyVolume`, `MinHourlyVolFast` are integer fields. The `K` and `M` suffixes work in them only with an integer: one and a half million is written `1500K` or `1500000`. Such a field will not read `1.5M`, and the filter stays at its default value, with no error or warning.
2. **Delays and the fast algorithm (`MShotReplaceDelay`, `MShotRaiseWait`, `FastShotAlgo = YES`):**
   * `MShotReplaceDelay` is the pause before moving the order deeper when the price has come closer than the near boundary. With zero, the order can escape from a fast but not instantaneous spike; with a pause, the spike fills the limit order, but a slow slide also fills it more often. Tier1 keeps `0.1` s, Tier2 `0.3` s.
   * `MShotRaiseWait` is the pause before pulling the order up after the price has moved up and, at the same time, the window in which the price minimum is sought, from which the order distance is measured.
   * `FastShotAlgo = YES` (the default) with a non-zero `MShotRaiseWait` takes the deepest trade of the last instant rather than the last one in the batch, and places the take-profit as soon as the fill happens ([chapter 03](../../concepts/03-spike-hunting-mechanics.md), section 2).
3. **Volatility adjustments and corridor widening (`MShotAdd*Delta`, `MShotAddDistance = 40..50`):**
   * The `MShotAdd*Delta` parameters produce a combined distance adjustment `D` (capped by `MaxModifier`). The near boundary becomes `MShotPriceMin + D`, the order itself `MShotPrice + D · (1 + MShotAddDistance / 100)`, and the far boundary moves together with the order by the same corridor formula.
   * Example for Tier1: the adjustments gave `D = 1`: near boundary `2.2%`, order `1.7 + 1 · 1.4 = 3.1%`, far boundary `3.1 + min(2.2, 0.9) = 4.0%`. In a calm market the order waits in a narrow corridor; on a burst it moves deeper and the corridor widens, so there are fewer re-placements.
4. **The shot's take-profit (`MShotSellAtLastPrice = YES`, `SellPrice = 0.9 / 1.8`):**
   * `MShotSellAtLastPrice = YES` is the default; the block sets it explicitly. The take-profit is placed at the higher of two prices: `SellPrice` from the entry price, and the pre-spike sell price (the ask a few seconds before the hit) minus `MShotSellPriceAdjust`. A Tier1 order filled at the full `1.7%` depth gets a take-profit near the pre-spike price, roughly `+1.7%` from entry rather than `+0.9%`: `SellPrice` acts here as a lower bound. For a fixed take-profit in percent, set `MShotSellAtLastPrice = NO`.
5. **Repeat shot disabled (`MShotRepeatAfterBuy = NO`):**
   * If enabled, the repeat works in both directions. In the window from `MShotRepeatDelay` to `MShotRepeatWait` seconds after the take-profit is placed: price above entry by `MShotRepeatIfProfit` — the next shot follows the move; price below entry by `MShotRepeatIfDrop` — a second shot on the same coin, that is, **averaging down** (with `0`, at any price below entry). The drop branch is enabled together with the repeat, and the repeat shot takes the coin out of turn and is not counted in `MaxActiveOrders`.
   * Next to the `−2.2%` stop this doubles the position on a falling coin: if you enable the repeat, choose a stop sized for the doubled position. The repeat works only with the Autotrading module or in the terminal's global Emulation mode.
6. **Two-phase exit by filters (`SellByFilters = 12`, `SellByFiltersDelay = 1.5`):**
   * If 12 seconds after the buy a tier-one coin no longer passes the filters, the terminal first moves the take-profit to the current price (not below `PriceDownAllowedDrop`), and after 1.5 seconds, if the position is not closed, triggers `Panic Sell`.
7. **Switching to the second stop (`PriceToSwitch2Stop = -0.2` / `-0.5`):**
   * `SecondStopLoss` moves the main stop. It kicks in when, **at the same time**, `TimeToSwitch2Stop` seconds have passed since the take-profit was placed and the price holds above `PriceToSwitch2Stop` from the average entry price ([chapter 06](../../concepts/06-orders-exits-and-stops-cascade.md)).
   * If by the 12th second the price is already deeper than `−0.2%`, there is no switch to `SecondStopLoss = −0.8%` until the price returns above the threshold: the first stop, `StopLoss = −2.2%`, keeps protecting the position.
8. **Leverage on futures (`MinLeverage = 20`):**
   * The filter works only on futures: the template takes coins where **you have set** leverage of ×20 or more. On an account with ×10 leverage the strategy will not take a single coin, and only Filters on charts will show the reason (`Leverage on this market (10) is less than min Leverage (20)`). Adjust the value to your leverage.
9. **Statistics collector (`CustomEMA`):**
   * All conditions in the line are collector thresholds: they do not restrict entry, and the function values at the moment of entry go to the log and to the `Comment` column of the report ([template 01](01-ema-rulers-and-data-collector.md)). Works only with the Autotrading module or in the terminal's global Emulation mode.

---

## Checking the result

* **Access:** Free or PRO; the statistics collector and sessions need the Autotrading module or the terminal's global Emulation mode. Spot and futures; on futures, leverage of ×20 or more on the coin, or your own `MinLeverage` value.
* **Replace:** `OrderSize` to match your balance; for real trading, `EmulatorMode=NO`.
* **Start:** paste the whole block (both strategies), tick both and start them.
* **Works if:** the chart of a selected coin shows virtual orders marked `(E)` at `1.7%` and `3.8%` below the price; the corridor boundaries are shown by right-clicking Filters on charts → `Show MoonShot price corridor`.
* **When the condition is not met:** when the coin's minute volume drops below `1.2` times the average (after the order is placed, the terminal gives the filter a small tolerance), the Tier1 order on that coin is cancelled (Tier2 does not have this filter).
