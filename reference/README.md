# Reference: exact tables for the trader and the AI assistant

The reference layer of the knowledge base: no explanations here, only verifiable facts — parameters, check order, error codes, protocol. Meaning and context are in the [chapters](../concepts/README.md); ready-made configurations are in the [templates](../examples/strategies/README.md).

| File | What is inside | When to open |
| :--- | :--- | :--- |
| [**`params/`**](params/README.md) | All 484 strategy parameters in eight thematic tables (filters and coins, detectors, buying, grids, selling, stops, triggers and sessions, system) and the alphabetical index [`params/index.tsv`](params/index.tsv) for machine reading | you need the exact meaning, type, default and relations of a parameter |
| [**`AI_GUIDE.md`**](AI_GUIDE.md) | Rules for importing strategy text (`Active`, `FVersion`, name case, suffixes), conditions of the Autotrading module, verified configuration-node templates, formula syntax | you are building a strategy with an AI assistant or by hand in text form |
| [**`strategy-selection-guide.md`**](strategy-selection-guide.md) | The navigator "trading task → strategy type → key parameters → template" and cards of all strategy types with access conditions | you do not know which `SignalType` fits the idea |
| [**`parameters-by-lifecycle.md`**](parameters-by-lifecycle.md) | Parameter matrix by trade phase: selection, detect, entry, tracking, exit — with enabling conditions and pitfalls | you want to see which parameters act at each stage |
| [**`filter-execution-order.md`**](filter-execution-order.md) | The order in which the terminal checks entry conditions; what `IgnoreFilters` removes, what is checked on the signal path and after the order is placed | "Filters on charts" shows a reason other than the one you expected |
| [**`silent-killers-and-traps.md`**](silent-killers-and-traps.md) | Configuration traps: parameter combinations that silently break a strategy or lead to a wrong trade | the strategy behaves differently from how it is configured |
| [**`exchange-errors-and-logs.md`**](exchange-errors-and-logs.md) | Exchange response codes and lines of the `logs/LOG_YYYY-MM-DD.log` log: what it means, what the terminal does, what the trader should do | there is an error or an unclear line in the log |
| [**`mooncmd-udp-protocol.md`**](mooncmd-udp-protocol.md) | The `MoonCMD` protocol: terminal control commands over UDP, `HMAC-SHA256` signature, response and telemetry format | you are writing your own automation on top of the terminal ([Python example](../examples/integrations/mooncmd-python-client/)) |

All tables are verified against the terminal source code (`v7.71`, `FVersion=12`) and the parameter tooltips; where the tooltips or the site diverge from the code, this is noted in the text.
