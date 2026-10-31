# `MoonCMD` protocol specification: UDP control, `HMAC-SHA256` signature, `GZip-JSON` and trade chart export

> **Purpose of this document:** The technical specification of the `MoonCMD` protocol for external automation, the `Moonbot Commander` system, Python/PowerShell scripts and Moonbot analytics collectors (`v7.71`).  
> **Official Moonbot documentation:** [Documentation](https://moonbot.pro/documentation) | [Education](https://moonbot.pro/education)  
> **Ready-made client example:** [`examples/integrations/mooncmd-python-client/`](../examples/integrations/mooncmd-python-client/)

---

## 1. Purpose and the three independent UDP/signal loops in Moonbot

In the Moonbot architecture it is important to clearly distinguish three different mechanisms for receiving packets and commands:
1. **`MoonProto` (the internal `Moon Kernel ↔ MoonTerminal` protocol):** encrypted transport of trades, order books and orders between the server kernel and the graphical client. The `V1 / V2` masking modes hide the stream from ISP blocking of UDP. The kernel port must not match any other UDP port of the terminal, including the MoonCMD command port ([chapter 07](../concepts/07-kernel-vps-and-infrastructure.md)).
2. **`MoonCMD` (configured in `Settings → Advanced → Remote → "UDP Commands Port / Pass"`):**
   * A service UDP protocol for remote control of the terminal itself and for telemetry export (`GZip-JSON` and binary trade snapshots `.bin`).
   * Accepts the commands of the remote-control Telegram chat (the list is sent by `hi`), except the trading `buy …`/`short …`, plus its own: strategy export and chart subscription. Telegram is not needed for this; only `report` and `ConvertBNB` send their result to Telegram.
   * The response to a command arrives over UDP at the address of the last signed command (section 2.1).
3. **The Telegram/UDP strategy signal receiver (`SignalType = Telegram` and `SignalType = UDP` with `AcceptCommands = YES`):**
   * A separate input loop for trading signals and Trust Management commands (`cmd_Buy`, `cmd_Short`, `cmd_Sell`, `cmd_SetStop`, `cmd_StopPanicSell`, `cmd_CancelBuy <Coin>`, `cmd_Update*`, `cmd_SplitOrder`, `cmd_JoinOrders`), which is configured inside the strategy itself and **must not be mixed with the `MoonCMD` service port**.

---

## 2. Format of incoming `MoonCMD` control commands (`Client → Moonbot`, UDP)

### 2.1. Mandatory password and the `HMAC-SHA256` packet signature
The command port opens **only if both the port and a non-empty password are set in `"UDP Commands Port / Pass"`**. A command is one UDP datagram in UTF-8:

```text
hash command
```

* The separator between `hash` and the command text is **one space** (` `), without a `timestamp` and without `|` characters.
* `hash = HMAC-SHA256(command, password)` in hexadecimal (hex) representation; case does not matter. The signature is computed over the command text without leading and trailing spaces.
* **Signature and format errors:** no space after `hash` — the response is `ERR format`; the signature does not match — `ERR bad_hmac`. Both arrive as plain text (without GZip) at the sender's address and do not change the response address.
* **Response address:** every command with a valid signature remembers the sender's `IP:Port`. Responses, exports and regular packets (`acc`, `errors`, `order`, charts) go to the address of the **last** signed command, so send and receive from one socket. Regular packets start after the first signed command and continue until the terminal restarts or the port changes.

### 2.2. Reference of the `MoonCMD` service port commands

| Category | `MoonCMD` command | Example | What it does |
| :--- | :--- | :--- | :--- |
| **Strategy export and chart subscription** | `GetStrategiesFull`<br>`GetStrategiesActive`<br>`SubscribeCharts`<br>`UnsubscribeCharts` | `GetStrategiesFull`<br>`SubscribeCharts` | `GetStrategiesFull` exports all strategies, `GetStrategiesActive` — only those running now. On a kernel client terminal the second list is empty: strategies run on the kernel. If there are no matching strategies, there will be no response. The response is `cmd: "strats"` packets (section 3.2). The export works like copying a strategy to the clipboard: only fields that differ from the defaults; all fields of its type — the `[Special] CopyFullStrategyText=1` key in `MoonBot.ini`. `SubscribeCharts` / `UnsubscribeCharts` turn on and off the sending of `.bin` charts of closed trades (section 4); there is no response to them. These four commands are written exactly and without the `BotName:` prefix — otherwise the terminal treats them as an unknown command and sends the help text. |
| **Starting, stopping and pausing strategies** | `start`<br>`stop`<br>`sgStop "<Name>" [Minutes]`<br>`sgStart "<Name>"`<br>`BotName:<Name> <Command>` | `start`<br>`stop`<br>`sgStop "My Shot" 30`<br>`sgStart "My Shot"`<br>`BotName:Bot1 sgStop Shot 60` | **`start`** presses Start, turns on autodetect (the `Autodetect: ON` button) and launches **all strategies ticked with the checkbox**. **`stop`** releases Start, turns off autodetect, stops all strategies and cancels the scheduled auto-restart after an autostop. A name after `start`/`stop` is ignored — the command acts on the whole terminal.<br>**`sgStop` / `sgStart`** — only a pause for an already running strategy or for all strategies of a folder; they do not touch the checkboxes. `sgStop "<Name>" N` pauses for `N` minutes; without a number or with a non-numeric value — for **120 minutes**; `0` changes nothing; a negative number lifts the pause, like `sgStart`. `sgStart` will answer "Started" even for a strategy that is not running, but it will not start trading: launching ticked strategies is `start`. Put a name with a space in quotes: without them the name is cut at the first space, and the response will be "no strategy with name … found" (or the pause will be set on the strategy named by the first word).<br>**`BotName:<Name> <Command>`** executes the command only on the terminal with this name; another terminal responds with an empty `data`. The prefix does not work with `GetStrategies*` and `SubscribeCharts`/`UnsubscribeCharts`. |
| **Emergency sell and cancelling buys** | `Sell <Coin>`<br>`SellALL`<br>`SellPiece <Coin \| ALL>`<br>`CancelBuy` | `Sell BTC`<br>`SellALL`<br>`SellPiece SOL`<br>`CancelBuy` | `Sell <Coin>` turns on `Panic Sell` for the specified coin — **only if the terminal is running a trade on it with a sell order placed** (otherwise the response says there is no trading on the coin or the sell order is not open yet); the response confirms that `Panic Sell` is turned on, not the fill on the exchange. There is **no** `PanicSell <Coin>` variant: the handler cuts the word `Sell` out of the text and looks for the coin in the remainder — `PanicSell BTC` becomes `Panic BTC`, the coin is not found, the position stays open. **`SellALL`** (written as one word) is the emergency button: it releases Start, turns off autodetect and all strategies, cancels all buys and turns on `Panic Sell` for all positions. The terminal stays stopped — then `start`. `SellPiece` sells a `SplitPiece` share; **`CancelBuy`** cancels open `Buy` orders **on all coins of the terminal**. |
| **Dynamic parameter changes** | `SetParam "<Strategy>" <Param> <Value>` | `SetParam "Shot_1" MShotPrice 2.5`<br>`SetParam "Shot_1" CoinsBlackList empty` | Changes a parameter in a strategy or a strategy folder on the fly (`empty` clears a string list). **Boolean parameters are turned on only by the word `YES`; `NO` and any other value — `1`, `true`, `ON` — are written as "off", while the response reports a successful change** (`SetParam "Shot" UseMarketOrder 1` will turn off the market exit). For numeric fields the `k`/`m` suffixes multiply the value (`2k` → `2000`). The command does not change the `Active` checkbox (the response is "Wrong param"): it cannot be set or cleared remotely. Pause — `sgStop`/`sgStart`, launching ticked strategies — `start`. |
| **Coin list management** | `SetWL+ "<Strategy>" <Coins>`<br>`SetWL- "<Strategy>" <Coins>`<br>`SetBL+ "<Strategy>" <Coins>`<br>`SetBL- "<Strategy>" <Coins>`<br>`TempBL +<Hours> <Coin1> <Coin2>`<br>`BL`<br>`BL + <Coin>` / `BL - <Coin>` | `SetWL+ "Shot_1" BTC,ETH`<br>`SetBL- "Shot_1" XRP`<br>`TempBL +4 DOGE PEPE`<br>`BL + SOL` | Adds (`+`) or removes (`-`) tickers in the `CoinsWhiteList` / `CoinsBlackList` of a strategy or of all strategies of a folder (`SetWL`/`SetBL` variants without the `+`/`-` sign are not supported); `TempBL +N` adds coins to the temporary blacklist for `N` hours; `BL` shows the global blacklist, `BL +` / `BL -` edit it (`BL +` also turns on the global blacklist). |
| **Sessions, profit counters, leverage and margin** | `ResetSession <Coin \| ALL>`<br>`ResetLoss`<br>`Leverage <X> <Coin1> <Coin2>`<br>`Margin <Coin1> <Coin2> ISO\|Cross`<br>`SetAutoLeverage ON\|OFF` | `ResetSession ALL`<br>`ResetLoss`<br>`Leverage 20 BTC ETH SOL`<br>`Margin ALL ISO`<br>`SetAutoLeverage ON` | `ResetSession` resets sessions for a coin or on all markets. `ResetLoss` zeroes the profit counters used for the loss autostop; it does not start the terminal — after an autostop you need `start`. `Leverage` sets leverage `X` on explicitly listed tickers (**the `ALL` keyword is not supported**). `Margin` switches isolated (`ISO`) or cross margin (`Cross`) on the listed coins or on all (`ALL`); the margin type is the last word; without coins and without `ALL` nothing changes (on OKX the command always acts on all coins). `SetAutoLeverage` sets or clears the "Auto Leverage" checkbox (futures): when the position limit is exceeded, the terminal changes the leverage itself, down to `5`. |
| **Reports, dust conversion and maintenance** | `hi`<br>`lst` (or `list`)<br>`report [N days\|weeks\|months] [coin] [hide]`<br>`ConvertBNB`<br>`Silent` / `talk`<br>`SetGroupDelay <ms>`<br>`SetMultiLine ON\|OFF`<br>`SetQRules ON\|OFF`<br>`SetDeltasByTrades ON\|OFF`<br>`DoUpdate`<br>`InstallTestVersion <Ver>`<br>`GenerateBugReport` | `hi`<br>`lst`<br>`report 7 days hide`<br>`ConvertBNB`<br>`Silent`<br>`talk`<br>`SetQRules ON` | `hi` — a greeting and the list of commands; the same text arrives for any unrecognized command. `list` — open sell orders and the balance, `lst` — the same in short. `report` — a report image for `N` days, weeks or months (or for dates `01.01.2024-17.03.2024`), for one coin, with `hide` — with blurred lines. The image goes **only to your own Telegram bot** (`Settings → Advanced → Remote`); a confirmation arrives over UDP; without your own bot the response says that one is needed. There are no hours: `report 5 hours` gives a report for 5 days. `ConvertBNB` — conversion of small non-tradable leftovers ("dust") into `BNB`, Binance only; the result arrives in Telegram. `Silent` / `talk` turn off and on notifications about closed trades in Telegram. `SetGroupDelay` — the interval for sending messages to Telegram, `1000–5000` ms. `SetMultiLine ON` — every non-empty line of the message is executed as a separate command. `SetQRules` — the "Quantitative Rules" checkbox (Binance Futures only). `SetDeltasByTrades` — the "Deltas include raw trades" checkbox (`Settings → Main`). `DoUpdate` — update if a new version is out. |

> [!CAUTION]
> **Do not send signal receiver commands (`cmd_*`) to the `MoonCMD` service port.** The handler looks for keywords anywhere in the text:
> 1. Any line containing the substring **`stop`** (for example, `cmd_StopPanicSell BTC`, `cmd_SetStop BNB 0.002`, `cmd_UpdateStopLoss -2.0`) is executed as `stop`: it releases Start and **stops all strategies of the terminal**.
> 2. A line with the substring **`SellAll`** (for example, `cmd_PanicSellAll`) is executed as `SellALL`: it **cancels buys, sells all positions via `Panic Sell` and stops the terminal**.
> 3. The command **`cmd_CancelBuy BTC`** is executed as `CancelBuy` and **cancels `Buy` orders on all coins of the terminal**, not only on `BTC`.
> 4. Text with `buy` (except `CancelBuy`), and on futures also with `short`, `MoonCMD` does not execute and responds with an empty `data`. Send trading signals and Trust Management commands (`buy`, `short:`, `cmd_Buy`, `cmd_Short`, `cmd_Sell`, `cmd_SetStop`, `cmd_StopPanicSell`, `cmd_CancelBuy <Coin>`, `cmd_SplitOrder`, `cmd_JoinOrders`, `cmd_Update*`) to a `SignalType = Telegram` or `SignalType = UDP` strategy with `AcceptCommands = YES`.

---

## 3. Response and push telemetry protocol (`Moonbot → Collector`, `GZip-JSON`)

The terminal sends responses, exports and regular packets over UDP as `JSON` compressed with **`GZip`** (the first two bytes of the datagram are `0x1F 0x8B`). Exceptions:
* `ERR format` and `ERR bad_hmac` arrive as plain text (section 2.1);
* trade chart chunks start with an 8-byte binary header before the `GZip` block (section 4);
* there is no response to `SubscribeCharts` and `UnsubscribeCharts`.

### 3.1. The base JSON envelope of command responses (`cmd: "replay"`)
```json
{
  "cmd": "replay",
  "bot": "BotName",
  "data": "string"
}
```
* `cmd` — the packet type: `"replay"` — a response to a command, `"strats"` — a strategy export with the `"N"` field, `"order"` — an order record, `"acc"` — the balance and the Start button state, `"errors"` — API errors;
* `bot` — the Moonbot terminal name;
* `data` in `replay` — the response text as one line: line breaks are replaced with spaces, double quotes and `\` are stripped.

### 3.2. Response format for `GetStrategiesFull` and `GetStrategiesActive`
```json
{
  "cmd": "strats",
  "bot": "BotName",
  "N": 1,
  "data": "##Begin_Strategy\nActive=-1\nFVersion=12\nFIntID=14630066297276943871\nStrategyName=MyShot\n...\n##End_Strategy\n"
}
```
* `N` — the packet number, from `1`. Strategies are cut into packets; one packet may contain several. The total number of packets is not transmitted.
* Each block starts with the lines `Active` (the checkbox: `-1` — ticked, `0` — not), `FVersion`, `FIntID`, followed by the strategy fields. Double quotes and `\` are stripped from the text.
* **`FIntID`** — the permanent 64-bit strategy identifier; it does not change on renaming. Orders are matched to the strategy by it (the `StrategyID` column in the `sql` field, section 3.3). Commands are addressed by name, not by `FIntID`. On a regular text paste of the block `FIntID` is not preserved — the strategy gets a new one.

### 3.3. Regular push updates from the terminal

1. **Order records (`cmd: "order"`):**
   ```json
   {
     "cmd": "order",
     "bot": "BotName",
     "oid": 12345,
     "sql": "update Orders set CloseDate=..., SellPrice=... where ID=12345"
   }
   ```
   * `oid` — the order number in the terminal's database. It is the same for the `insert into Orders …` and for all subsequent `update Orders set … where ID=…` of one trade, and matches the `id` in the chart header (section 4). `0` — other records: funding, manual report edits, row deletions.
   * `sql` — an SQL command against the `Orders` table of the terminal's report with substituted values. Double quotes, `\` and line breaks are stripped from it, so executing it as is is unreliable — parse the fields.
2. **Balances, version and Start button status (`cmd: "acc"`, every 5 seconds):**
   ```json
   {
     "cmd": "acc",
     "bot": "BotName",
     "data": {
       "A": "1250.45$",
       "T": "1500.00$",
       "S": true,
       "V": 771
     }
   }
   ```
   * All fields are packed inside the `"data"` object. `A` — the available balance, `T` — the total balance; both are strings with the currency: `"1250.45$"` for dollar bases, for others — the number and the ticker separated by a space (`"0.0512 BTC"`).
   * `S` — JSON `true`/`false`: `true` — the Start button is pressed, `false` — the terminal is stopped. A parser expecting a number will break on this field.
   * `V` — the terminal version number without the dot (`771` for 7.71).
3. **The exchange API error stream (`cmd: "errors"`):**
   * Arrives together with `acc` if errors have accumulated since the last packet: an array of strings in the object `"data": {"E": ["..."]}`. Line breaks inside the text are preserved (`\n`), double quotes and `\` are stripped.

---

## 4. Compact `.bin` trade charts via the `SubscribeCharts` subscription

For external monitoring services and `Moonbot Commander`, the terminal exports a binary chart snapshot after a trade closes. Turned on with the `SubscribeCharts` command, off with `UnsubscribeCharts`.
1. **The binary datagram header before `GZip` (8 bytes):**
   * The `.bin` chart stream is first compressed with `GZip`, then cut into datagrams of `50 000` bytes. Each datagram starts with an **8-byte header** (`<BBiBB`, little-endian): `Flag` — a byte, always `0` (distinguishes a chart from a regular `GZip` packet `0x1F 0x8B`); `Kind` — a byte, `1` — chart; `id` — a 4-byte integer, the order number in the terminal's database (the same as `oid` in `order` packets); `blockNum` — a byte, the chunk number `0 .. blocksCount - 1`; `blocksCount` — a byte, the total number of chunks. For a multi-block chart, `gzip.decompress` is called after concatenating all chunks `0 .. blocksCount - 1` of one `id`.
2. **How long the terminal keeps writing the chart after the exit:**
   * Without a subscription, the terminal keeps writing the chart to the report for 3 seconds after the close, and if `Settings → Advanced → System → "Charts in reports N mins after close"` is set to `N > 0` — for `N` minutes.
   * With a subscription, continued chart recording is limited to 15–90 seconds: at `N = 0` — 15 s, at `N = 1` — 60 s, at `N ≥ 2` — 90 s. This also shortens the chart in the local report.
   * Charts are not written at all if "Delete old logs since N days" on the same tab is set to `0`.
3. **The lightweight snapshot contents:**
   * The window is the last 3 minutes before saving, so the longer the recording continues after the close, the less is visible before the exit (at 90 s — a minute and a half before the close). Inside: the price line, the trade feed, **the 2 orders of the trade itself** (buy and sell), the coin's deltas and volumes. There are no `MarkPrice` or `EMA` lines and no liquidation levels in the snapshot.

---

## 5. Practical rules for working with commands and UDP traffic

1. **Excluding UDP traffic from a TCP proxy (`ProxyCap`):**
   * Do not route the `MoonCMD` and `MoonProto` UDP streams through TCP tunnels (`ProxyCap`). Add your VPS IP address to the direct connection list (`Direct`) or proxy only the exchange TCP ports (`443`).
2. **A separate port for commands:**
   * The UDP command port must not match any other UDP port of the terminal: the `Listen UDP port` for receiving signals (`Settings → Advanced → System`), the kernel port in the `Moon Proto` window, the Moon Streamer server port and the control bot port ([chapter 07](../concepts/07-kernel-vps-and-infrastructure.md)). If they match, one of the services will not come up.
3. **Specifics of the `SetParam` and `sgStop` commands and the `MultiLine` batch mode:**
   * **Batch mode `SetMultiLine ON` / `SetMultiLine OFF`:** with `ON`, every non-empty line of the message is executed as a separate command (`SetParam`, `SetBL+`, `Sell <Coin>`, `sgStop`, etc.), and the responses arrive as one `replay`. With `OFF`, a multi-line message is parsed as one command.
   * **Clearing string parameters with `empty`:** passing the keyword `empty` fully clears the list (for example, `SetParam StrategyName CoinsBlackList empty`). The `SetParam` target can be either the name of an individual strategy or the name of a strategy folder.
   * **Escaping spaces in `SetParam`:** if the strategy or folder name contains spaces, it must be enclosed in double quotes (`SetParam "My Strategy" ReportToTelegram NO`). Spaces inside the parameter value itself (for example, `SetParam MyShot TriggerKeysBL 400 50=10 44=20000`) are passed without quotes.
   * **A pause instead of the checkbox:** `SetParam "StrategyName" Active 0` does not clear the checkbox. `sgStop` and `sgStart` set and lift the pause of a strategy or of all strategies of a folder without touching their checkboxes. When calling `SetParam FolderName StrategyName NewName`, a protection applies: the name is not changed through a folder, so that all strategies of the folder do not get the same name.
   * **Managing the `Quantitative Rules` protection:** the command `SetQRules ON` / `SetQRules OFF` turns the built-in protection against exceeding Binance Futures quantitative limits on or off; on other exchanges the command does not work.
