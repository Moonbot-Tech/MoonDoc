# Template 01: CustomEMA diagnostic rulers and a market telemetry collector

> **Official Moonbot documentation:** [EMA Strategy and Its Parameters](https://moonbot.pro/documentation/advanced-strategy-parameters/ema-strategy-and-its-parameters) | ["Filters on charts" Button (funnel icon)](https://moonbot.pro/documentation/main-terminal-window-with-advanced-settings/funnel-button)  
> **Related chapters:** [05. CustomEMA formulas](../../concepts/05-ema-geometry-and-formulas.md) | [08. Testing and debugging strategies](../../concepts/08-testing-debugging-and-analytics.md)

> **Requires the Autotrading module** (PRO) or the terminal's global Emulation mode (Menu → Emulation mode). Without them `CustomEMA` formulas are not evaluated: the ruler shows nothing, the collector writes nothing, and the terminal gives no warning about it. The strategy's own `EmulatorMode=YES` checkbox does not replace the module.

---

## 1. Trading idea and purpose of the template

Before setting thresholds in `CustomEMA` formulas for real trading, two practical tasks need to be solved:

1. **See the exact formula values on the chart in real time.** The trader needs to know what numbers `EMA`, `Avg`, `MAX`, `MIN`, `Vol`, and `Arb` produce in a calm market and at the moment of an impulse. This is what diagnostic ruler strategies with a deliberately impossible threshold (`< -1000`) are for: no coin will ever pass it, and **Filters on charts (`Show Filters`, funnel icon)** shows the current formula value as the rejection reason.
2. **Collect labeled statistics on trades.** Collector thresholds (`> -888` / `< 888` for price functions and `> 0` for `Vol`) do not compare the value with the threshold; they only require that data exist. If the whole `CustomEMA` line consists of them, it does not restrict entry; at the moment the buy order is placed, the terminal writes the values of all listed functions to the log `logs/LOG_YYYY-MM-DD.log` (the `EMAFilter:` line) and, for all strategy types except `EMA`, to the `Comment` column of the Reports window. Filter boundaries are then chosen from the accumulated sample.

---

## 2. Template configuration (`FVersion=12`)

### 2.1. Diagnostic ruler for Filters on charts

The strategy places no orders (`AutoBuy=NO`, the `< -1000` thresholds are impossible). After import, **tick the strategy's checkbox and start it**: Filters on charts polls only running strategies.

```ini
##Begin_Strategy
Active=0
FVersion=12
StrategyName=01_Diag_Ruler_EMA_and_Vol
Comment=Diagnostic ruler for the Filters on charts mode (funnel icon). Tick and start the strategy, open the coin chart in Full Screen.
SignalType=EMA
EmulatorMode=YES
AutoBuy=NO
AutoSell=NO
OrderSize=10
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
IgnoreSession=YES
CustomEMA=EMA(5s,1s)<-1000 OR Avg(5s,1s)<-1000 OR MAX(15m,1s)<-1000 OR Vol(0s,1m)>999999999
Delta_3h_Max=1000
Delta_BTC_Min=-100
Delta_BTC_Max=100
PriceStepMax=100
MinVolume=1M
MaxVolume=100000M
MaxHourlyVolume=100000M
PenaltyTime=0
NextDetectPenalty=0
GlobalDetectPenalty=0
##End_Strategy
```

### 2.2. Embeddable telemetry collector line (`> -888`)

Put this `CustomEMA` line into a working strategy (`MoonShot`, `MoonHook`, `DropsDetection`, `Spread`) as a whole — then it only writes telemetry and does not restrict entry — or append it with `AND` to the working conditions. In the second case every collector requires data and cuts off coins with no trades within its window (item 4 below); it is safer to keep the collector in a separate emulator copy of the strategy.

```ini
CustomEMA=EMA(3s,1s)>-888 AND Avg(3s,1s)>-888 AND EMA(15s,1s)>-888 AND EMA(60s,1s)>-888 AND EMA(5m,1s)>-888 AND MAX(15m,1s)>-888 AND MIN(15m,1s)>-888 AND MAX(60m,1s)>-888 AND Vol(1h,5s)>0 AND Vol(0s,1m)>0 AND BTC(5m,1s)>-888 AND MAvg(5m,1s)>-888
```

---

## 3. Step-by-step breakdown of parameters and limitations

1. **What Filters on charts (funnel icon) shows:**
   * For each running strategy, **the first reason in check order** why the coin failed the checks. If the coin was cut off by `CoinsBlackList` or `BinanceTokenTags`, that reason is what you see on screen: the check never reaches `CustomEMA`.
   * The ruler's conditions are joined with `OR`: this way the terminal evaluates every branch and shows the values of all formulas in one line. In an `AND` chain only the first failed condition is visible.
   * Open the coin chart **in Full Screen**: on small charts the terminal saves CPU and writes only `EMA filter not passed. Open full screen chart to see more info`.
2. **`CustomEMA` syntax: no grouping parentheses and no `k/m` suffixes:**
   * All `AND` operators are evaluated first, then `OR`; each condition starts with a function name (`EMA`, `Avg`, `MIN`, `MAX`, `BTC`, `MAvg`, `Vol`, `Arb`). Parentheses around compound conditions (of the form `(EMA(...) AND ...)`) are not supported; round brackets go only around function arguments.
   * Thresholds are written as full numbers: `Vol(0s, 1m) > 100000`, not `> 100k`; letter suffixes are not expanded in the formula.
3. **The `Base` group must be enabled (`IgnoreFilters=NO`, `IgnoreBase=NO`):**
   * The `CustomEMA` formula belongs to the `Base` filter group. For the terminal to evaluate it and show it in Filters on charts, `IgnoreFilters` and `IgnoreBase` must be `NO`. The other groups (`IgnoreTime` … `IgnoreSession`) are disabled in the ruler (`YES`) so that their rejections do not hide the formula line.
4. **Exact boundaries of collector thresholds (`<= -887`, `>= 887`, and `Vol <= 0`):**
   * A condition counts as a collector in three cases: for price functions (`EMA`, `Avg`, `MAX`, `MIN`, `BTC`, `MAvg`, `Arb`), the `>` sign with a threshold of `-887` or lower (usually written `> -888`) or the `<` sign with a threshold of `887` or higher (`< 888`); for `Vol`, only the `>` sign with a threshold of `0` or lower (`Vol(...) > 0`).
   * If the whole formula consists of collectors only, it is not checked before the buy (in a `SignalType=EMA` strategy such a line is a signal on every coin that has data). Collectors appended with `AND` to working conditions require data and cut off coins with no trades within the window.
   * The `EMAFilter:` line is written to the daily log `logs/LOG_YYYY-MM-DD.log` when the strategy gets as far as placing the order. The same values reach the `Comment` column of the Reports window for all strategy types **except `EMA`**, which is why the collector is embedded into working `MoonShot`, `MoonHook`, `DropsDetection`, `Spread`, and other strategies.
5. **Do not put a collector in `SellByCustomEMA`:**
   * In `SellByCustomEMA` a collector is an always-true exit condition. With `SellEMACheckEnter=YES` (the default) the strategy will never buy: the exit condition is already met at the moment of entry. With `SellEMACheckEnter=NO` it sells immediately after the buy. The latter is a technique for emulator scouts ([chapter 05](../../concepts/05-ema-geometry-and-formulas.md), section 9); in a working strategy a collector does not belong in this field.

---

## Checking the result

* **Access:** the Autotrading module or the terminal's global Emulation mode; spot and futures.
* **Start:** paste `01_Diag_Ruler_EMA_and_Vol`, tick its checkbox and start it; turn on Filters on charts and open the coin chart in Full Screen.
* **Works if:** the Filters on charts line for the ruler shows the current values of `EMA`, `Avg`, `MAX`, and `Vol`. The collector from item 2.2 works if, after a buy by the working strategy, the log contains an `EMAFilter:` line with values, and for strategies of a type other than `EMA`, the same values appear in the `Comment` column of the report.
* **When the condition is not met:** the ruler places no orders at all; on a small chart, instead of values, you see `EMA filter not passed. Open full screen chart…`.
