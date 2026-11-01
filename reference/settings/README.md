# Moonbot settings: trading, risk and terminal configuration

Global settings determine how Moonbot sizes orders, manages leverage, stops trading when conditions deteriorate, and presents market data. This reference explains their effects, units and dependencies for traders, terminal developers and AI assistants.

For a setting that belongs to one strategy, use the [strategy parameter reference](../params/README.md). For a terminal or integration that edits the kernel, start with [choosing the settings API](10-settings-apis.md).

## Find the setting for your task

| Task | Reference |
| :--- | :--- |
| Stop trading on losses, exchange errors or slow responses; resume automatically | [Startup and protection](01-startup-and-protection.md) |
| Read Telegram or clipboard signals and configure alerts | [Signals and alerts](02-signals-and-alerts.md) |
| Set order amounts, entry/exit defaults, leverage and margin policy | [Trading and leverage](03-trading-and-leverage.md) |
| Configure order controls, reports and screenshot sharing | [Orders, reports and notifications](04-orders-reports-and-notifications.md) |
| Read ticks, order books, volume profiles and comparison feeds | [Charts and display](05-charts-and-display.md) |
| Configure drawing tools, Pencil simulation and news cards | [Drawing and news](06-drawing-and-news.md) |
| Set manual-trading shortcuts and saved interface preferences | [Interface and hotkeys](07-interface-and-hotkeys.md) |
| Change chart colors, themes and supported INI options | [Themes and INI](08-theme-and-ini.md) |
| Locate a field in the SDK model | [SharedConfig structure](09-config-structure.md) · [field index (TSV)](index.tsv) |
| Read and save settings; check Telegram and control-bot API availability | [Settings APIs](10-settings-apis.md) |

## Reading the tables

Field names are the exact MoonProto names; paths are relative to `SharedConfig`. Each row gives the type, meaning, units, useful bounds and enabling conditions. **GUI** identifies limits used by Moonbot's editor; a Rust scalar type alone does not enforce those limits.

Amounts described as **trading currency** use the currency selected for that market/account. For BTC/USDT spot or USDT-margined futures, this is USDT, not the BTC base asset. Inverse-contract balance and settlement amounts follow the account's contract mode; do not assume every monetary field is USD. A row that explicitly says USD equivalent has its own conversion.

The catalog covers **539 public fields in 34 SharedConfig structures**, plus supported INI keys and separate service APIs. That includes nested records, saved interface state and compatibility fields, not 539 independent controls. Preserve inactive fields, learned values and unknown tails when editing a received snapshot.

## Settings that look alike but do different jobs

| Names | Difference |
| :--- | :--- |
| `errors_level`, `ping_level`, `log_level` | API-error score (1..5), exchange-response time in milliseconds (GUI 100..2000), and diagnostic verbosity (0..5) |
| `auto_lev_control`, `auto_manage_lev` | Target position-limit amounts and the policy that selects leverage for those amounts |
| `fixed_trade_balance`, `max_order`, `max_orders` | Default order amount, observed historical maximum, and concurrent active-order limit |
| `restart_after_err`, `restart_after_ping` | Resume trading after recovery; neither restarts the process |
| GUI preferences and terminal behavior | Saving a chart color or hotkey on the kernel does not implement it in a remote terminal |

## Editing through MoonProto

Start from the received kernel snapshot, apply the user's changes, send it and check the returned state. `SharedConfig::default()` is not a substitute for that snapshot. Full configuration updates can overwrite concurrent edits; INI updates replace each supplied section. The [API chapter](10-settings-apis.md) explains these contracts and the separate paths for Telegram, WatchDog, leverage and compact live controls.

The [MoonProto SDK documentation](https://github.com/Moonbot-Tech/MoonProto/blob/main/docs/shared_config.md) covers methods, events and serialization. MoonDoc explains what the settings mean and how they interact. Newly added kernel settings may not yet have a named SDK field; preserve their unknown bytes rather than mapping them to a similar-looking setting.
