# Themes and INI keys

[Settings reference](README.md)

Main-window themes, chart colors and chart rendering options are stored in named INI sections. SharedConfig exposes only `ColorsLight`, `ColorsDark`, `Charts` and `ArbColors`.

**Sending an INI section replaces that entire section.** To change one color, copy the received section, update that entry and retain its other keys. An empty entry list clears the section. Candle colors also appear in `visual.candle_colors`; keep the two representations consistent.

Related: [charts and display](05-charts-and-display.md), [saving settings](10-settings-apis.md). Field paths are relative to `SharedConfig`.

<a id="themesection"></a>

## `theme` — `ThemeSection`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="themesection-current-style"></a>`current_style` | `i32` | Main GUI style: 0=Native, 1=Light, 2=Diamond, 3=Dark, 4=Dark OldSchool. Styles 3/4 use the dark color set; 0/1/2 use the light one. |
| <a id="themesection-ini-sections"></a>`ini_sections` | [`Vec<IniSectionData>`](08-theme-and-ini.md#inisectiondata) | ColorsLight and ColorsDark sections. Import replaces every supplied section completely: retain untouched keys. See the INI section notes below. |
| <a id="themesection-unknown-tail"></a>`unknown_tail` | `Vec<u8>` | Preserve opaque bytes from newer kernels unchanged. |

<a id="inisection"></a>

## `ini` — `IniSection`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="inisection-ini-sections"></a>`ini_sections` | [`Vec<IniSectionData>`](08-theme-and-ini.md#inisectiondata) | Charts and ArbColors sections. Import replaces every supplied section completely; unknown section names are rejected. See the INI key reference below. |
| <a id="inisection-unknown-tail"></a>`unknown_tail` | `Vec<u8>` | Preserve opaque bytes from newer kernels unchanged. |

<a id="inisectiondata"></a>

## `theme.ini_sections[] / ini.ini_sections[]` — `IniSectionData`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="inisectiondata-name"></a>`name` | `String` | Section name from the corresponding allowlist: ColorsLight/ColorsDark in theme, Charts/ArbColors in ini. |
| <a id="inisectiondata-entries"></a>`entries` | `Vec<(String, String)>` | Ordered text key/value pairs. Preserve keys you do not edit. Import erases the supplied section before writing its entries; an empty list clears it. |

## `Charts` keys

INI values are strings. Use `0`/`1` for booleans and decimal notation for numbers. Missing-key behavior below describes loading, not an instruction to reset a running configuration.

| Key | Value and meaning |
| :--- | :--- |
| `RepaintOnMouseOver` | Boolean, false when absent. Repaint the chart directly on mouse movement instead of marking the cursor for refresh. |
| `HighMouseDPI` | Boolean, false when absent. The Windows GUI suppresses repeated mouse-move messages with the same timestamp. Not UI scaling. |
| `SmoothCharts` | Boolean, true when absent. Smooth updating of fast live charts; does not smooth market prices used for trading. |
| `DrawTradesOverPrice` | Boolean, true when absent. Draw trades above the price layer rather than below it. |
| `ReportChartLength` | Minutes of history **before** the trade in its saved report chart; loader clamps to 15..60. An absent key reads as 5, then becomes 15. Post-trade recording is the separate `visual.chart_history_len`. |
| `PixelAlign` | Legacy key still written but no longer read from INI. Preserve; do not expose as an effective switch. |
| `HugePixels` | Boolean, false when absent. Legacy tick-size selection used only when `ChartPixelSize=0`, selecting 3 instead of 2. |
| `ChartPixelSize` | Tick drawing size, 1..4. Zero selects 2/3 through HugePixels; the loader then clamps to 1..4. |
| `OrderBookFastUpdate` | Boolean, true when absent. Selects the 100 ms book stream in supported Binance fast-chart paths and participates in redraw decisions. Not a universal update interval for all exchanges. Saving the value and reconnecting the stream are separate stages. |
| `MaxOpenedCharts` | Limit on automatic chart additions during signals/startup; loader clamps to 1..50, absent=20. Does not limit trading to this many markets and is separate from monitoring-window `charts_settings.max_charts`. |

## `ColorsLight` and `ColorsDark` keys

A value is eight hexadecimal digits `AARRGGBB` **without** `#`, `0x` or `$`, for example `FF00FF00`. Light and dark themes have separate sets. Preserve unedited keys. Missing `CandleGreen`/`CandleRed` inherit `GraphGreen`/`GraphRed`.

| Key | Element |
| :--- | :--- |
| `graphFont` | Chart text |
| `graphBK` | Chart background |
| `graphNet` | Chart grid |
| `graphCursor` | Chart cursor |
| `BuyOrder` | Buy-order line |
| `BuyPendingOrder` | Pending buy |
| `SellOrder` | Sell-order line |
| `BuyOrderDone` | Filled buy |
| `BuyShort` | Short entry |
| `SellShort` | Short close |
| `Trailing` | Trailing |
| `LastPrice` | Last price |
| `GraphRed`, `GraphGreen` | Red/green parts of the price chart |
| `CandleNeutral` | Neutral tick-region color in candle mode |
| `CandleGreen`, `CandleRed` | Rising/falling candles |
| `VolRed`, `VolGreen` | Sell/buy volume |
| `OrderBookRed`, `OrderBookGreen` | Ask/bid sides of the order book |
| `BookLevelRed`, `BookLevelGreen` | Ask/bid order-book levels |
| `SpotRed`, `SpotGreen` | Red/green parts of the additional spot chart |
| `SpotBookRed`, `SpotBookGreen` | Sides of the additional spot order book |
| `MarkPrice` | Mark Price |
| `LiqPrice` | Position liquidation price |
| `LiqOrdersLong`, `LiqOrdersShort` | Market long/short liquidation events |

Candle colors also appear in `visual.candle_colors`. These are the same settings, not independent palettes. Do not send conflicting values through both representations.

## `ArbColors` keys

A key is an arbitrage-platform code `0..255`, optionally followed by an underscore and a descriptive name (`code_name`). The numeric prefix identifies the platform; it is not a UI row index. Values are `AARRGGBB`, as above. Missing entries use `FF8B4513`. Use `ArbPlatformCode` in the SDK and preserve unknown codes. Choosing a color does not enable a subscription or arbitrage trading.
