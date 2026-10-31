# Thematic Reference of Moonbot Strategy Parameters (`FVersion=12`)

The complete registry of **484 parameters** of Moonbot strategies (`v7.71`), split into 8 compact sections by editor tab and by stage of the trade lifecycle.

* **Choosing the algorithm for a trading task:** [`../strategy-selection-guide.md`](../strategy-selection-guide.md)
* **Matrix of parameter interactions by trade phase:** [`../parameters-by-lifecycle.md`](../parameters-by-lifecycle.md)
* **Quick tabular index of all 484 parameters:** [`index.tsv`](index.tsv)

| Section file | Terminal tabs | Parameters | Size |
| :--- | :--- | :---: | :---: |
| [**`01-filters-and-coins.md`**](01-filters-and-coins.md) | `Coins`, `Filters` (`Base`, `Time`, `Price`, `Ping`, `Volume`, `Delta`) | 96 | ~21 KB |
| [**`02-detectors-and-signals.md`**](02-detectors-and-signals.md) | `Strategy Settings` (all 23 strategy types, by subsection) | 196 | ~53 KB |
| [**`03-buy-and-modifiers.md`**](03-buy-and-modifiers.md) | `Buy`, `Delta Modifiers` | 45 | ~15 KB |
| [**`04-multiorders-and-scales.md`**](04-multiorders-and-scales.md) | `MultiOrders` (`OrdersCount`, `JoinSellKey`) | 10 | ~10 KB |
| [**`05-sell-and-take-profit.md`**](05-sell-and-take-profit.md) | `Sell` (`PriceDown`, `SellLevel`, `SellShot`, `SellSpread`) | 46 | ~18 KB |
| [**`06-stops-and-trailing.md`**](06-stops-and-trailing.md) | `Stops` (`StopLoss 1/2/3`, `Trailing`, `BV/SV Stop`) | 35 | ~15 KB |
| [**`07-triggers-and-sessions.md`**](07-triggers-and-sessions.md) | `Triggers` (`Master / Slave`), `Session` | 31 | ~16 KB |
| [**`08-ui-system-and-migrations.md`**](08-ui-system-and-migrations.md) | `Main`, `Telegram / UDP`, `UI`, `FVersion` and `MoonBot.ini` migrations | 25 + migrations | ~17 KB |
