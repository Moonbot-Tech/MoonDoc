# General Strategy Settings, Telegram, Interface and Version Migrations (Main, UI & FVersion)

> **Concept overview:** [Kernel + Client architecture, VPS and emulation](../../concepts/07-kernel-vps-and-infrastructure.md) · [Testing, debugging and analytics](../../concepts/08-testing-debugging-and-analytics.md) · [The UDP protocol and external signals](../mooncmd-udp-protocol.md)  
> **Reference navigation:** [Overview by trade phase](../parameters-by-lifecycle.md) · [Alphabetical index (TSV)](index.tsv) · [Detect algorithm parameters](02-detectors-and-signals.md)

This section covers 25 general strategy parameters (the `Main`, `User Interface` and `Remote Control` tabs), the table of renamed and historical parameters in the profile format migrations `FVersion 1..12`, and the service keys of the `MoonBot.ini` configuration file.

---

## 1. Strategy identification, Telegram/UDP signals and Trust Management

This group sets the strategy's name and working algorithm (`SignalType`), the reception of external signals from Telegram/MoonNews and over the UDP protocol, and the sending of detect and trade reports to your own Telegram channel.

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`StrategyName`** | `string · ''` | Name of the strategy. `Combo` and `UseHookStrategy` look it up without regard to case. The kernel can store two strategies under one name; what that does to those links, and the refusal on Station MCP in published MoonTerminal v0.66.0, is in the [Station guide](../station-mcp-guide.md#strategies). |
| **`Comment`** | `string · ''` | Free-form text note for the strategy (does not affect trading). |
| **`SignalType`** | `string · 'DropsDetection'` | The strategy's working detect algorithm (one of 23 types). When the type is changed in the editor, the fields of the other algorithms are kept in the profile in an inactive state. |
| **`LastEditDate`** | `string · ''` | Date and time the strategy was last saved, `yyyy-mm-dd hh:nn`, filled in by the terminal. In MoonTerminal through published **v0.65.13**, a copy saved from [Strategy Tuning](../../concepts/08-testing-debugging-and-analytics.md#the-strategy-tuner-in-moonterminal) keeps the source strategy's date. Published **v0.66.0** writes the current minute on the target core's wall clock, or in this computer's time zone when that core's offset has never been measured. The version list's time is a separate observation ([chapter 08](../../concepts/08-testing-debugging-and-analytics.md#strategy-version-history)). |
| **`ChannelName`** | `string · ''` | Only for `Telegram`: the name of the monitored Telegram channel. The special value `MoonNews` connects the Moon News system news feed (requires an active subscription on the kernel). |
| **`ChannelKey`** | `string · ''` | Only for `Telegram`: the signal keyword (`buy`, `moon_1..moon_20`). For the `MoonNews` channel — a list of categories without `#`, separated by commas or spaces (`Listing`, `Delisting`, etc.; an empty field accepts any news; enabling `MultiTokens=YES` is recommended). |
| **`AcceptCommands`** | `bool · NO` | For `Telegram` and `UDP`: allow receiving Trust Management text commands (`buy`, `sell`, `stop`, `short:`, etc.). For `Telegram` the commands are accepted only from the `ChannelName` channel (and with the `ChannelKey` key, if set), for `UDP` — from signal packets. |
| **`OnlyEncryptedCommands`** | `bool · NO` | Only for `UDP`: accept buy signals only from packets that passed the sender signature check; an unsigned packet is discarded. This is a source check, not secrecy — the packet contents are not hidden. Exception: the `sell` and `sellAll` commands for a coin are executed from unsigned packets as well. Does not apply to the `MoonCMD` terminal control protocol. **Enable only in a `UDP` strategy:** a message from Telegram is never a signed UDP packet, so in a `Telegram` strategy `YES` rejects all Trust Management commands. |
| **`SilentNoCharts`** | `bool · NO` | With `YES`, suppresses the automatic opening of the coin's chart when the strategy's signal fires. |
| **`ReportToTelegram`** | `bool · NO` | Send a notification about the very fact of the strategy's detect to your Telegram channel (in a `Kernel + Client` setup the kernel does the sending). |
| **`ReportTradesToTelegram`** | `bool · YES` | Send reports on filled buys and sells of this strategy to your Telegram channel. |

---

## 2. Opening charts, sound alerts, emulator and debugging

These parameters control the visualization of signals and orders on the client's charts, the local emulation mode of the strategy (`EmulatorMode`), verbose logging (`DebugLog`) and the order of group polling of strategies of the same type (`IndependentSignals`).

| Parameter | Type · Default | Meaning, formula and key interactions |
| :--- | :--- | :--- |
| **`SoundAlert`** | `bool · NO` | When the signal fires, play a sound alert and show a button for quick opening of the coin's chart. |
| **`SoundKind`** | `string · 'TurnOn'` | Name of the predefined sound with `SoundAlert=YES`. |
| **`KeepAlert`** | `int · 60` | How long the button with the signal coin's ticker is shown above the chart, in seconds. |
| **`AddToChart`** | `int · 0` | Index of a separate chart window (`>= 0`, `0` — off) to which the coin is added automatically after the strategy fires. |
| **`KeepInChart`** | `int · 0` | How long the coin's chart is kept in the `AddToChart` window, in seconds (`0` — do not remove by timer). |
| **`EmulatorMode`** | `bool · NO` | Switches only this strategy to emulation while the terminal is in live mode: orders are filled inside the terminal, trades are marked `(Emulator)` / `(E)`. Does not replace the Autotrading module (only the terminal's global emulation mode substitutes for it). Virtual trades affect the coin's market session and the coin pauses of other strategies; virtual `MoonShot` orders take up the common order limit. In a kernel + client setup, checked strategies run their detects on the kernel regardless of `AutoBuy` — there is no need to enable `AutoBuy` "for the kernel". |
| **`DebugLog`** | `bool · NO` | Write extended diagnostics of filter and detector rejection reasons to the `logs/LOG_YYYY-MM-DD.log` log (with anti-spam throttling of 10 s per coin). In the strategy editor a forgotten flag is highlighted with a warning, since it increases disk load. |
| **`IndependentSignals`** | `bool · NO` | A `Main` tab parameter, not a global setting. With `NO`, strategies of the same type are checked down the list from top to bottom, and after the first matching one the rest are not checked on this signal. With `YES`, all strategies in a row give the signal **down to the first one where the checkbox is cleared** — a chain, not full independence: for several `Drops` with different thresholds to work in parallel, each needs the checkbox. For `NewListing`, `EMA`, `Spread`, `MoonHook` and `Activity` it is always on; `MoonShot`, `PumpsDetection`, `UDP`, `Combo`, `Manual`, `TopMarket` and `Alerts` do not have the parameter. |
| **`DontWriteLog`** | `bool · NO` | Only with `EmulatorMode=YES`: do not write operations on the strategy's virtual orders to the `logs/LOG_YYYY-MM-DD.log` log (for real strategies it is automatically reset to `NO`). |
| **`DontKeepOrdersOnChart`** | `bool · NO` | Only with `EmulatorMode=YES`: do not keep the history of the strategy's cancelled virtual `Buy` orders on the chart. |
| **`UseCustomColors`** | `bool · NO` | Use this strategy's individual line style (`OrderLineKind`) and order colors (`SellOrderColor`, `BuyOrderColor`) on the chart. |
| **`OrderLineKind`** | `string · 'Solid'` | Drawing style of the strategy's `Buy`, `Sell` and `Trailing` order lines on the chart with `UseCustomColors=YES`. |
| **`SellOrderColor`** | `string · HexColor` | Color of the strategy's `Sell` order (take-profit) line in hexadecimal format with `UseCustomColors=YES`. |
| **`BuyOrderColor`** | `string · HexColor` | Color of the strategy's `Buy` order line in hexadecimal format with `UseCustomColors=YES`. |

---

## 3. What changes when an old strategy is loaded (`FVersion`)

The main rule: the `FVersion=12` line must come **immediately after** `Active=…`, as the second line of the block. If it is missing or stands elsewhere, the terminal treats the text as a version-zero strategy and applies to it all the transformations below — including those that break links.

**Transformations when pasting text (`Ctrl+V` into the strategies window) — by the version number in the block:**

| Condition | What the terminal does | Risk for old or version-less text |
| :--- | :--- | :--- |
| `FVersion < 7` | In `MoonShot`, the value of `TriggerKey` is written into `TriggerKeyBuy`; the value of the old `ClearTriggers` — into `ClearTriggersBelow` and `ClearTriggersAbove` | `MoonShot` has no `TriggerKey` field, its value is `0` — the buy key is zeroed and the Master → Slave chain breaks; key clearing is reset to `NO` |
| `FVersion < 8` | `SellByTriggerBL=YES` is expanded into the list of all keys from `TriggerKeysBL`, `SellByTriggerBL=NO` — into an empty string | The modern key-list notation is not affected |
| `FVersion < 9` | `HookAntiPump` is forced to `YES` | A deliberately disabled anti-pump in `MoonHook` turns back on |
| `FVersion = 10` (exactly) | `MShotReplaceDelay` and `HookReplaceDelay` are divided by `1000` (milliseconds → seconds) | Text without a version line does not fall under this rule: its delays stay as written |
| `FVersion < 12` | `TokenTags` is read as `BinanceTokenTags` | — |

The core runs the same `FVersion < 7`, `< 8` and `< 9` conversions when a strategy arrives over MoonProto with a format number below the threshold, and then stores the strategy at format 12. The delay rescaling and the `TokenTags` rename happen while reading text, not on that check.

Published MoonTerminal **v0.65.13** sends format 1 for every strategy created through Station MCP. It sends format 0 for the first strategy placed from the terminal onto a core that holds none. Either way the core applies those conversions before it stores format 12. On a MoonShot the buy key comes back as 0, so a Master → Slave link that depended on `TriggerKeyBuy` is missing until you set the key on the stored strategy and read it back. On a MoonHook, `HookAntiPump` is forced on. A later strategy placed from the terminal onto a core that already holds some uses the highest format those strategies carry. Published **v0.66.0** sends format 12 when the core holds none, including for the MCP create, so this conversion does not run.

**Only when loading a strategy profile file (not when pasting text):** `TrailingPersent` is read as `TrailingPercent`; `TriggerOnProfit` / `TriggerOnLoss` — as `TriggerKeyProfit` / `TriggerKeyLoss`; the old integer `FastShotAlgo=0` is read as `YES`. Text pasted from a chat with such lines **loses** these values.

Any other unknown parameter name (including working names from beta builds and chats — `DShot*`, `BeforeFunding`, `IntervalDelay` and the like) is **silently skipped** by the terminal when pasting: there is no conversion, the parameter keeps the constructor default. Check the pasted strategy in the window after import.

---

## 4. Service keys of the MoonBot.ini configuration file

Several service settings are set only in the `MoonBot.ini` file in the terminal folder. Edit it with the terminal **shut down**, adding the line to the end of the needed section: a key written into the wrong section is not read. Terminal version `7.71` reads these keys:

| Section and key | Default | What it does |
| :--- | :---: | :--- |
| `[Special]` **`KeepOrdersAfterCrash`** | `0` | With `1`, the terminal does not cancel open `Buy` orders at startup after a crash or an OS reboot, or on an automatic stop due to an API ban. |
| `[Special]` **`CopyFullStrategyText`** | `0` | With `1`, copying a strategy to the clipboard exports all fields **of the current strategy type**, not only those differing from the defaults. |
| `[Special]` **`Use_sk_ChartWall`** | `0` | With `1`, the experimental `ChartWall` detect appears in the strategy type list. |
| `[Special]` **`SpecialBinanceEndPoint`** | `0` | Switch to an alternative Binance API address; enable only when instructed by support. |
| `[Charts]` **`MaxOpenedCharts`** | `20` | Limit on simultaneously open chart windows, `1..50`. |

The keys `FastMoonShotRestart`, `FastMoonShotOrders`, `UseBUSDFutures`, `UseShortBinanceWS`, which appear in old FAQ answers, do not exist in the terminal; `NoTradesCompression` is read but has no effect (the terminal chooses stream compression itself: off on VDS, on on a desktop). **`IgnoreReplacingBug` is no longer an `ini` key but the "Ignore Replacing Bug" checkbox on the `Advanced` settings tab** (forced on for Bybit): if a `Sell` order gets stuck in the re-placement state on exchange errors, enable it there; the cost is an occasional duplicate `Sell` order.
