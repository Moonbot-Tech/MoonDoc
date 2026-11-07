# Reference: exact tables for the trader and the AI assistant

Exact parameter names, units, conditions and interactions for configuring Moonbot and building integrations. Trading mechanics are explained in the [conceptual chapters](../concepts/README.md); ready-made configurations are in the [strategy templates](../examples/strategies/README.md).

| File | What is inside | When to open |
| :--- | :--- | :--- |
| [**Station MCP and ActiveLib**](station-mcp-guide.md) | AI tools, live schemas, commands, permissions, observation and reports | an AI connects to a Station to inspect or control cores |
| [**Log-analysis workflow**](station-log-analysis.md) | Bounded observations, order correlation, timestamps and causal evidence | an AI investigates what the bots are doing or why an action failed |
| [**Linux kernel commands**](linux-kernel-commands.md) | `mb`, service control, logs, status, MoonProto setup and updates over SSH | you need to monitor or manage a Linux kernel on a VPS |
| [**`settings/`**](settings/README.md) | Kernel settings for order sizing, leverage, risk controls, charts, Telegram and control bots; [539-field SDK index](settings/index.tsv) and [editing APIs](settings/10-settings-apis.md) | you are configuring global behavior or building a settings panel with MoonProto |
| [**`params/`**](params/README.md) | All 484 strategy parameters in eight thematic tables (filters and coins, detectors, buying, grids, selling, stops, triggers and sessions, system) and the alphabetical index [`params/index.tsv`](params/index.tsv) for machine reading | you need the exact meaning, type, default and relations of a parameter |
| [**`AI_GUIDE.md`**](AI_GUIDE.md) | Rules for importing strategy text (`Active`, `FVersion`, name case, suffixes), conditions of the Autotrading module, verified configuration-node templates, formula syntax | you are building a strategy with an AI assistant or by hand in text form |
| [**`strategy-selection-guide.md`**](strategy-selection-guide.md) | The navigator "trading task → strategy type → key parameters → template" and cards of all strategy types with access conditions | you do not know which `SignalType` fits the idea |
| [**`parameters-by-lifecycle.md`**](parameters-by-lifecycle.md) | Parameter matrix by trade phase: selection, detect, entry, tracking, exit — with enabling conditions and pitfalls | you want to see which parameters act at each stage |
| [**`filter-execution-order.md`**](filter-execution-order.md) | The order in which the terminal checks entry conditions; what `IgnoreFilters` removes, what is checked on the signal path and after the order is placed | "Filters on charts" shows a reason other than the one you expected |
| [**`silent-killers-and-traps.md`**](silent-killers-and-traps.md) | Configuration traps: parameter combinations that silently break a strategy or lead to a wrong trade | the strategy behaves differently from how it is configured |
| [**`exchange-errors-and-logs.md`**](exchange-errors-and-logs.md) | Exchange response codes and lines of the `logs/LOG_YYYY-MM-DD.log` log: what it means, what the terminal does, what the trader should do | there is an error or an unclear line in the log |
| [**`mooncmd-udp-protocol.md`**](mooncmd-udp-protocol.md) | The `MoonCMD` protocol: terminal control commands over UDP, `HMAC-SHA256` signature, response and telemetry format | you are writing your own automation on top of the terminal ([Python example](../examples/integrations/mooncmd-python-client/)) |

The strategy parameter tables use `v7.71`, `FVersion=12`. Kernel settings have a separate SDK model: use the connected kernel's state and the field-specific conditions in the settings reference.
