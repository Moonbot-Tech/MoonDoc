# Template 06: Entering on a reversal after a deep fall (CustomEMA) and tracking large players on Hyperliquid (Watcher)

> **Official Moonbot documentation:** [EMA Strategy and Its Parameters](https://moonbot.pro/documentation/advanced-strategy-parameters/ema-strategy-and-its-parameters) | [Watcher Strategy and Its Parameters](https://moonbot.pro/documentation/advanced-strategy-parameters/watcher-strategy-and-its-parameters)  
> **Related chapters:** [05. CustomEMA formulas](../../concepts/05-ema-geometry-and-formulas.md) | [02. Finding trading situations: detects and Watcher](../../concepts/02-detect-pipeline-and-signals.md)

---

## 1. Strategy A: entering on a reversal after a deep fall (`CustomEMA`)

> **The Autotrading module** (PRO) or the terminal's global Emulation mode is required: without them the `EMA` strategy does not detect, and `SellByCustomEMA` is not checked. The `EmulatorMode=YES` checkbox on the strategy does not replace the module.

### Trading idea and purpose of the template
When a coin loses `12–20%` of its value in 15–60 minutes, placing limit orders against the fall without signs of a bounce is risky. The task of the **`06A_Deep_Bounce_EMA`** strategy is to pick situations after a steep price decline where the price has already pulled away from the low of the last quarter-hour on elevated volume, and to exit if the bounce failed and the price went back below the bottom.

The `CustomEMA` formula combines six conditions:
1. **`MAX(60m, 1s) < -12`** — the current price is more than `12%` below the high of the last hour. The minute window does not include the last minute; `MAX(1h, 1s)` would describe the hour before last.
2. **`MIN(15m, 5s) > 0.4`** — the smoothed price of the last five seconds is at least `0.4%` **above** the low of the last 15 minutes. The second argument `5s` is the smoothed five-second price, not a trade from five seconds ago. The first argument of `MIN` / `MAX` is read in minutes or hours: seconds in it silently turn into minutes (`MIN(90s, 1s)` is `MIN(90m, 1s)`), so the window is written as `15m`.
3. **`Avg(4s, 1s) > 0.15`** — the price now is more than `0.15%` above the point of the average price line from four seconds ago: the bounce is happening right now.
4. **`Vol(1h, 5m) > 3.5`** — the average per-minute turnover of the last 5 minutes is at least `3.5` times the average per-minute turnover of the hour.
5. **`Vol(0s, 15s) > 120000`** — the turnover of the last 15 seconds, converted to a per-minute rate, is at least `120,000` in the quote currency (that is, `30,000` over 15 seconds; the threshold is written as a full number without the `k` suffix).
6. **`BTC(5m, 1s) > -1.2`** — bitcoin has not dropped more than `1.2%` relative to the average price of the minute that was five minutes ago.

```ini
##Begin_Strategy
Active=0
FVersion=12
StrategyName=06A_Deep_Bounce_EMA
Comment=Entry on a bounce after a deep decline (price more than 12% below the hourly high, 5s price bounce from the 15-minute low above 0.4%, Avg impulse and Vol surge). Exit if the price returned below the 15-minute low.
SignalType=EMA
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
CustomEMA=MAX(60m,1s)<-12 AND MIN(15m,5s)>0.4 AND Avg(4s,1s)>0.15 AND Vol(1h,5m)>3.5 AND Vol(0s,15s)>120000 AND BTC(5m,1s)>-1.2
WorkingPriceMin=0.001
WorkingPriceMax=10000
PriceStepMax=0.3
MarkPriceMin=-3.5
MarkPriceMax=1.5
MinLeverage=20
MaxMarkets=5
MaxPing=180
MaxLatency=600
BinancePriceBug=0.6
MinVolume=10M
MaxVolume=100000M
MinHourlyVolume=500K
MaxHourlyVolume=100000M
Delta_3h_Min=0
Delta_3h_Max=80.0
Delta_24h_Min=0
Delta_24h_Max=150.0
Delta2_Type=1h
Delta2_Min=0
Delta2_Max=80.0
Delta_BTC_Min=-5.0
Delta_BTC_Max=5.0
PenaltyTime=300
TradePenaltyTime=120
NextDetectPenalty=60
GlobalDetectPenalty=0
BuyType=Buy
buyPrice=0.2
UseScalpingMode=YES
AutoCancelBuy=5
SellPrice=3.5
SellEMADelay=4
SellEMACheckEnter=YES
SellByCustomEMA=MIN(15m,1s)<-0.3
UseStopLoss=YES
FastStopLoss=YES
UseMarketOrder=YES
StopLossEMA=0
StopLossDelay=1.5
StopLoss=-2.8
StopLossSpread=1.2
StopSpreadAdd1mDelta=0.1
AllowedDrop=-10.0
UseSecondStop=YES
TimeToSwitch2Stop=20
PriceToSwitch2Stop=-0.3
SecondStopLoss=-1.0
AllowedDrop3=-10.0
UseTrailing=YES
TakeProfit=1.5
TrailingPercent=-0.4
TrailingSpread=0.4
UseTakeProfit=YES
##End_Strategy
```

### Key entry and exit parameters in `06A_Deep_Bounce_EMA`:
* **`buyPrice = 0.2` (lowercase `b`):** buy price offset `+0.2%`; a `BuyPrice` line with a capital letter is silently ignored on text import.
* **`SellByCustomEMA = MIN(15m, 1s) < -0.3` — exit if the bounce broke:** the price went more than `0.3%` below the low of the last 15 minutes, that is, the coin broke the bottom it was bought from. The formula exit does not look at the trade's profit and closes the position the same way as an exit by filters. Profit taking is handled by the `SellPrice` take-profit and the trailing stop (`TakeProfit`, `TrailingPercent`).
* **`SellEMACheckEnter = YES` and `SellEMADelay = 4`:** the exit condition is also checked before the buy: if it is already true, the strategy does not enter. At entry the price is `0.4%` above the low (condition 2), so the exit is false at that moment and does not block the entry — it only prevents a buy if the bottom has already been broken. After the buy, the exit formula starts being checked `SellEMADelay = 4` seconds after the take-profit is placed.
* **Why not a pullback from the high.** The tempting exit `MAX(5m, 1s) < -0.5` (“the price went half a percent below the high of the last minutes”) is true on a fresh bounce even before the entry: the coin has just been falling, and the high from five minutes ago is well above the price. With `SellEMACheckEnter = YES` such a formula forbids almost every reversal entry; with `NO` it sells right after `SellEMADelay`. Build the exit condition for a bounce from the bottom rather than from the high of the fall.
* **`Delta2_Type = 1h`, `Delta2_Max = 80`:** without an explicit line the default applies — an hourly price range of no more than `20%`, and a coin that fell deeper than about `17%` in an hour (`1 / 0.83 − 1 ≈ 0.2`) would be cut off by the delta filter, although the template is designed for a `12–20%` fall.
* **`MinLeverage = 20`:** on futures the template takes only coins where your leverage is set to ×20 or higher; adjust to your own.

---

## 2. Strategy B: tracking large wallets on Hyperliquid (`SignalType = Watcher`)

### Trading idea and purpose of the template
On the decentralized exchange **Hyperliquid (`HL`)** the wallet address of the participant is known for every trade. The **`Watcher`** strategy subscribes to the fills of the addresses in the `WatchAddress` field and, on a suitable position opening (`WatchDirection = OnlyOpen`, batch volume strictly above `WatchMinVolume = 50000`, the address's position before the trade plus the trade volume strictly above `WatchMinPosition = 200000`):
1. Forms a signal in the direction of the tracked participant's position (`WatchSameDirection = YES`);
2. With the Autotrading module (or in the terminal's global Emulation mode) activates the key **`TriggerKey = 77`**, which can start slave strategies.

The coin is taken from the trade itself, so an open chart is not needed — it is enough for the coin to be in the terminal's Coins table. The strategy is available in the PRO version and on Hyperliquid in MoonBonus mode.

> **Required before launch:** replace the placeholder address `0x0000000000000000000000000000000000000000` in the `WatchAddress` field with the real 42-character hex address of the tracked Hyperliquid wallet. Several addresses are listed in the same field separated by spaces or commas — this is the strategy's address book. The terminal maintains the file `data\HLAddrBook.txt` itself as a reference of “address → name” labels; addresses written only there are not tracked. After adding or changing an address, click **“Start Checked”**: the address subscription is refreshed when the strategy is saved and on start.

> **Exchange limit on addresses.** Hyperliquid limits how many unique addresses can be followed for events from one IP: ten, according to the exchange documentation. This limit includes your trading bot, the control bot and every address from `WatchAddress` of all `Watcher` strategies on this server. The terminal does not keep itself within the limit — the field accepts more than ten addresses. When the limit is exhausted, the exchange may reject a new subscription — the Problems window shows which address and channel were rejected; if the subscription to the events of your **own** account is rejected, the bot loses those events ([chapter 07](../../concepts/07-kernel-vps-and-infrastructure.md), section 4). Keep only as many addresses in `WatchAddress` as stay within the limit together with the bot and the control bot.

```ini
##Begin_Strategy
Active=0
FVersion=12
StrategyName=06B_HL_Whale_Watcher
Comment=Tracking the opening of large positions on Hyperliquid (WatchDirection=OnlyOpen) with generation of trigger 77. Replace WatchAddress with a real address!
SignalType=Watcher
EmulatorMode=YES
AutoBuy=YES
AutoSell=YES
OrderSize=100
WatchAddress=0x0000000000000000000000000000000000000000
WatchDirection=OnlyOpen
WatchSameDirection=YES
WatchMinVolume=50000
WatchMinPosition=200000
CoinsWhiteList=
CoinsBlackList=
BinanceTokenTags=!Monitoring !Alpha
IgnoreFilters=NO
IgnoreBase=NO
IgnoreTime=YES
IgnorePrice=NO
IgnorePing=NO
IgnoreVolume=NO
IgnoreDelta=YES
IgnoreSession=NO
PriceStepMax=0.3
MaxLatency=600
MinVolume=5M
MaxVolume=100000M
MaxHourlyVolume=100000M
Delta_3h_Max=1000
Delta_BTC_Min=-100
Delta_BTC_Max=100
PenaltyTime=300
NextDetectPenalty=30
GlobalDetectPenalty=0
TriggerKey=77
TriggerAllMarkets=NO
BuyType=Buy
buyPrice=0.3
AutoCancelBuy=10
SellPrice=2.0
UseStopLoss=YES
FastStopLoss=YES
StopLossDelay=2.0
StopLoss=-2.5
StopLossSpread=1.0
AllowedDrop=-8.0
UseTrailing=YES
TakeProfit=1.2
TrailingPercent=-0.35
TrailingSpread=0.3
UseTakeProfit=YES
##End_Strategy
```

### Key parameters and limitations of `Watcher`:
1. **Openings only (`WatchDirection = OnlyOpen`) and direction (`WatchSameDirection = YES`):**
   * In a new strategy the default is `WatchDirection = Both` — it also reacts to position closings. `WatchSameDirection` is tied to the sign of the whale's **position**, not to the side of its last trade: with `Both` and `YES`, a partial close of the whale's long would give a long signal. Setting **`WatchDirection = OnlyOpen`** explicitly cuts off closings and leaves only opening and building up a position.
2. **Address subscription:**
   * The list of tracked addresses is assembled from `WatchAddress` of the running `Watcher` strategies and refreshed when a strategy is saved and on `Start Checked`. The address book `data\HLAddrBook.txt` stores only labels for addresses.
3. **Kernel + client setup (`Full Proxy`):**
   * In this setup, the `Watcher` detect runs on the kernel: the kernel computes the filters and detects of all checked strategies regardless of `AutoBuy`, and the client only displays the whales' trades. There is no separate “run on the kernel” option, and there is no need to set `AutoBuy = YES` to move the detect to the kernel.

---

## Checking the result

**06A**
* **Access:** the Autotrading module or the terminal's global Emulation mode; spot and futures (on futures — leverage of ×20 or higher on the coin).
* **Start:** check and start `06A_Deep_Bounce_EMA`; open the chart of a fallen coin full-screen and turn on “Filters on charts”.
* **Works if:** the “Filters on charts” line shows the first unmet condition of the formula with its current value, and when all six are met, a virtual buy `(E)` appears.
* **When the condition is not met:** on a coin without a fall deeper than `12%` from the hourly high, the line shows the unmet `MAX(60m,1s)<-12`, and there are no orders.

**06B**
* **Access:** a connection to Hyperliquid; the PRO version or MoonBonus mode; key `77` — only with the Autotrading module or in the terminal's global Emulation mode.
* **Replace:** the placeholder address in `WatchAddress` with a real one, then click “Start Checked”.
* **Works if:** the address's trades are marked with arrows on the coin's chart, and the `Watcher` table shows the address's position with its sign; on an opening above the thresholds, the strategy places a virtual order `(E)`.
* **When the condition is not met:** the whale's position closings and batches smaller than `WatchMinVolume` give no signal.
