# Template 05: Protecting long trades: a two-tier BTC crash shield and a delisting news filter

> **Official Moonbot documentation:** [“Triggers Master/Slave” Tab](https://moonbot.pro/documentation/general-parameters-for-all-strategies/triggers-masterslave-tab) | [Moon News](https://moonbot.pro/documentation/menu-button/moon-news) | [Manage Triggers Window](https://moonbot.pro/documentation/menu-button/manage-triggers)  
> **Related chapters:** [04. Strategy links: Master → Slave triggers](../../concepts/04-triggers-and-master-slave.md) | [02. Finding trading situations: detects and external signals](../../concepts/02-detect-pipeline-and-signals.md)

---

## 1. Trading idea and purpose of the template

Two market events can quickly cause large losses in long altcoin trades:
1. **A sudden `BTC` drop.** While bitcoin's 1-minute and 5-minute deltas slowly build up to the threshold value, the very first one-second drop of `BTC` drags the whole altcoin market with it and fills the limit orders sitting in the order books. The shield catches precisely the sudden drop — of medium strength (tier 1) and of large strength (tier 2) — and not a slide accumulated over minutes.
2. **A coin delisting announcement.** In the first seconds after such news the price falls through every placed buy level. On futures the exchange does not always set the spot `Monitoring` tag before removing a pair, so the `BinanceTokenTags = !Monitoring` filter does not protect fully there. The guard for the `Delisting` tag in the `MoonNews` feed provides additional protection alongside the filters: the tag arrives with a refined copy of the news, and news older than about ten seconds by event time gives no signal. The main protection against delisting is the selection filters and stops ([chapter 04](../../concepts/04-triggers-and-master-slave.md), section 2).

These three strategies block entries or trigger an exit when they detect a threat:
* **Tier 1 (`05A_BTC_Shield_Tier1_0.45pct`):** keeps a virtual `MoonShot` order on the `BTC` pair `0.45%` below the price (corridor `0.35…0.55%`) and, when it fills virtually, turns on the global key **`101`** on all coins of the terminal (`TriggerAllMarkets = YES`): the connected long strategies cancel their resting buys and do not enter for the key's lifetime.
* **Tier 2 (`05B_BTC_Shield_Tier2_0.90pct`):** keeps a deeper virtual `MoonShot` on `BTC` — `0.90%` below the price (corridor `0.75…1.05%`) — and, when it fills, turns on the global key **`102`**, which starts a forced exit in the connected long strategies.

> **What this shield catches and what it does not.** The shield is built on `MoonShot`, and `MoonShot` keeps the order at a set distance from the *current* price: in a gradual decline it moves the order down (`MShotReplaceDelay = 0` — immediately). So the shield fires only on a **sudden drop** — when bitcoin breaks through the order sitting `0.45%` (or `0.90%`) below the price in a single move, faster than the order manages to move deeper. A drawn-out sell-off in `−0.3%` steps with pauses will not activate the key. Against a slow slide, the protection is the `Delta_BTC_Min` filter in the working strategies themselves, or a master that measures the accumulated fall with the `BTC(5m, 1s)` formula.
* **The news guard (`05C_MoonNews_Delist_Guard`):** watches the `MoonNews` feed (`MultiTokens = YES`, `IndependentSignals = YES`) for the `Delisting` tag (`ChannelKey = Delisting`) and blocks the coins from the news with key **`109`**. To react to hack news as well, add the tag separated by a comma: `ChannelKey = Delisting,hack`.

---

## 2. Configuration of the protective set (`FVersion=12`)

The block contains **three strategies** and starts with the `##MultiSelection` line — on `Ctrl+V` the terminal pastes all three. To paste one, copy it from `##Begin_Strategy` to `##End_Strategy`.

```ini
##MultiSelection
##Begin_Strategy
Active=0
FVersion=12
StrategyName=05A_BTC_Shield_Tier1_0.45pct
Comment=Virtual MoonShot shield on the BTC pair (Tier 1: order 0.45% below the price, corridor 0.35..0.55%). On fill, activates key 101 on all coins.
SignalType=MoonShot
EmulatorMode=YES
AutoBuy=YES
AutoSell=NO
OrderSize=20
CoinsWhiteList=BTC
CoinsBlackList=
IgnoreFilters=YES
IgnoreSession=YES
CheckAfterBuy=YES
MaxMarkets=1
AutoCancelBuy=60
Delta_3h_Max=1000
Delta_BTC_Min=-100
Delta_BTC_Max=100
NextDetectPenalty=5
GlobalDetectPenalty=0
MShotPriceMin=0.35
MShotPrice=0.45
MShotReplaceDelay=0
MShotRaiseWait=0.2
MShotUsePrice=Trade
FastShotAlgo=YES
TriggerKeyBuy=101
ActiveTrigger=NO
TriggerAllMarkets=YES
##End_Strategy

##Begin_Strategy
Active=0
FVersion=12
StrategyName=05B_BTC_Shield_Tier2_0.90pct
Comment=Virtual MoonShot shield on the BTC pair (Tier 2: order 0.90% below the price, corridor 0.75..1.05%). On fill, activates key 102 on all coins.
SignalType=MoonShot
EmulatorMode=YES
AutoBuy=YES
AutoSell=NO
OrderSize=20
CoinsWhiteList=BTC
CoinsBlackList=
IgnoreFilters=YES
IgnoreSession=YES
CheckAfterBuy=YES
MaxMarkets=1
AutoCancelBuy=60
Delta_3h_Max=1000
Delta_BTC_Min=-100
Delta_BTC_Max=100
NextDetectPenalty=10
GlobalDetectPenalty=0
MShotPriceMin=0.75
MShotPrice=0.90
MShotReplaceDelay=0
MShotRaiseWait=0.3
MShotUsePrice=Trade
FastShotAlgo=YES
TriggerKeyBuy=102
ActiveTrigger=NO
TriggerAllMarkets=YES
##End_Strategy

##Begin_Strategy
Active=0
FVersion=12
StrategyName=05C_MoonNews_Delist_Guard
Comment=Guard for news with the Delisting tag in the MoonNews feed (ChannelKey=Delisting, IndependentSignals=YES, MultiTokens=YES). Sets key 109 on the coins from the news.
SignalType=Telegram
EmulatorMode=YES
AutoBuy=NO
AutoSell=NO
OrderSize=20
ChannelName=MoonNews
ChannelKey=Delisting
MultiTokens=YES
IndependentSignals=YES
AcceptCommands=NO
IgnoreFilters=YES
IgnoreSession=YES
Delta_3h_Max=1000
Delta_BTC_Min=-100
Delta_BTC_Max=100
TriggerKey=109
TriggerAllMarkets=NO
NextDetectPenalty=5
GlobalDetectPenalty=0
##End_Strategy
```

---

## 3. Step-by-step parameter breakdown and connecting to working strategies

To add this protection to your working long strategies (`MoonShot`, `MoonHook`, `DropsDetection`, `Spread`), add the following `Triggers` tab parameters to them:

```ini
TriggerKeysBL=101=45 102=120 109=86400
CancelByTriggerBL=YES
SellByTriggerBL=102 109
```

### Key setup rules and firing conditions:
1. **The Autotrading module (PRO) or the terminal's global Emulation mode is a mandatory condition:**
   * Even if the shield strategies `05A..05C` have their own `EmulatorMode = YES`, writing trigger keys, checking `TriggerKeysBL` and the emergency exit by `SellByTriggerBL` run **only with the Autotrading module active or the terminal's global Emulation mode enabled** (Menu → Emulation mode). Without them the shield's virtual order will not pass the keys and the working strategies will not check them — there will be no protection at all, and the terminal will not warn you about it.
   * **Order limit.** The virtual orders of shields `05A`/`05B` take up slots in the shared limit of simultaneous `MoonShot` orders; with a scout on hundreds of coins and without the “Unlimited orders” checkbox, the shields may run out of slots.
   * **Futures.** `AutoSell = NO` in blocks `05A`/`05B` works only on spot; on futures the parameter is hidden and forced to `YES`. There, after firing, the shield holds the virtual `BTC` position until it closes (with the default exit) and does not re-arm all that time — it will not see a second sell-off in a row. For futures, give the shields conditions for closing the virtual position (`SellPrice = 0.3`, `StopLoss = -0.3`); `MShotRepeatAfterBuy = YES` does not close the position: it is a repeat shot while the position is still open, within the `MShotRepeatWait` window, and it only lets the shield fire once more right after the first firing.
2. **Keys from `SellByTriggerBL` must also be present in `TriggerKeysBL`:**
   * The exit by key is checked **only for keys that are also in `TriggerKeysBL` with a non-zero time**.
   * If you enter `102 109` in `SellByTriggerBL` but forget to list them in `TriggerKeysBL = 101=45 102=120 109=86400`, the position will not be closed by the key. A key present in both fields both turns on the forced close (`Panic Sell`) and blocks new entries for its time (`120` s for key `102`, `86400` s for key `109`).
   * Keys are stored together with market data and survive a terminal restart if the downtime was under an hour; after a longer downtime all keys, including the 24-hour `109`, are reset.
3. **Exact tag match `ChannelKey = Delisting` and independence `IndependentSignals = YES`:**
   * The news tag is compared with each word of `ChannelKey` **as a whole** (case-insensitive, the `#` sign is dropped), not as a substring. So the abbreviation `delist` will not fire on the `#Delisting` tag — the exact tag name is needed (`ChannelKey = Delisting`); several tags are listed separated by commas or spaces.
   * The **`IndependentSignals = YES`** flag in block `05C` is mandatory: without it, any other active `Telegram` strategy on `MoonNews` that stands higher in the list and fired on the same news would prevent the guard `05C` from setting key `109`.
4. **Mechanics of the virtual shields `05A` / `05B` (`ActiveTrigger = NO`, `MShotReplaceDelay = 0`):**
   * `05A` and `05B` keep virtual `MoonShot` orders on the `BTC` pair `0.45%` and `0.90%` below the `Trade` price (corridors `0.35…0.55%` and `0.75…1.05%`), re-placing the order every `AutoCancelBuy = 60` s. A sharp `BTC` spike through the virtual order's price is a buy: it activates key `101` / `102` on all coins (`TriggerAllMarkets = YES`). `ActiveTrigger = NO` keeps the key from being activated in advance while the order simply sits. `MoonShot` has no `TriggerKey` field — the key is passed only by a buy.
5. **Coin lists in news (`MultiTokens = YES`):**
   * `MultiTokens = YES` (with multi-token support enabled in the terminal) sets key `109` at once on all coins from one announcement that are found in the terminal. News older than about ten seconds by event time gives no signal.

---

## Checking the result

* **Access:** the Autotrading module or the terminal's global Emulation mode — without them the shields pass no keys and the working strategies do not check them. The shield recipe with `AutoSell = NO` is for spot; on futures the shields need an exit (item 1). For `05C` — an active Moon News module.
* **Start:** paste the whole block (three strategies), check and start them; add the three lines from section 3 to every working long strategy. Keys can be activated manually without waiting for a sell-off: `Menu → Manage Triggers`, the key, a coin of the working strategy, `Set` — in the terminal's global Emulation mode.
* **Works if:** key `101` — **a new entry is forbidden**: in the working strategy's “Filters on charts” the line `This market is BlackListed at … by trigger 101. Wait … seconds`; **the resting buy is canceled** (`CancelByTriggerBL = YES`); an open position runs on with its own take-profit and stop. Key `102` or `109` — **the position is closed** via `Panic Sell` by the working strategy's stop rules.
* **When the condition is not met:** 45 seconds after key `101` the blocking line disappears and the strategy places orders again; a gradual `BTC` slide without a sudden drop activates no keys.
