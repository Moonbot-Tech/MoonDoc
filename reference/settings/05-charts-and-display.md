# Charts and display

[Settings reference](README.md)

Tick charts, order books, volume profiles and comparison feeds answer different trading questions. These settings control how Moonbot displays those data: what is visible, how much history fits on screen, and how volumes and prices are scaled.

Three settings often confused with one another are `chart_time_scale` (visible history in seconds), `chart_history_len` (post-trade wait before saving a chart, in minutes), and `charts_settings.refresh` (a preset index for recentering monitoring charts). None sets a universal exchange-data refresh rate.

These are saved Moonbot GUI preferences. A MoonProto terminal implements its own rendering and decides which preferences to support. Hiding a stop line, order caption or balance does not disable the trading function or remove the data from the API.

Related: [market selection and chart data](../../concepts/01-market-selection-and-filters.md), [themes and colors](08-theme-and-ini.md). Field paths are relative to `SharedConfig`.

<a id="visualsection"></a>

## `visual` — `VisualSection`

### Opening charts and following the market

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="visualsection-scrolling-charts"></a>`scrolling_charts` | `bool` | Place multiple charts in a scrollable container instead of fitting them into the fixed chart panel. Does not control following the latest time within a chart. |
| <a id="visualsection-startup-load-charts"></a>`startup_load_charts` | `bool` | Restore saved chart selections on Moonbot startup. Does not itself enable automatic trading on those markets. |
| <a id="visualsection-auto-close-charts"></a>`auto_close_charts` | `bool` | Enable automatic cleanup of eligible inactive charts using `trading.chart_clean_up_time` and the kernel's activity/load checks. Does not close a chart immediately just because another coin was selected. |
| <a id="visualsection-chart-time-scale"></a>`chart_time_scale` | `i32` | Saved chart time span in seconds, not minutes. Tick charts clamp to 60..=21600 seconds; candle mode has its own available-history limit and remembered tick scale. |
| <a id="visualsection-new-markets-max-scale"></a>`new_markets_max_scale` | `bool` | Open a new chart at its maximum available time span: normally six hours for ticks, candle-history capacity in candle mode. Not maximum price zoom and not limited to newly listed coins. |
| <a id="visualsection-charts-auto-shift"></a>`charts_auto_shift` | `bool` | Keep eligible charts following the latest time automatically. Panned/history views and chart modes still influence recentering. |
| <a id="visualsection-auto-request-charts"></a>`auto_request_charts` | `bool` | Request missing market history when opening a Moonbot chart. Separate from restoring the saved chart set on startup and from the SDK's own candle refresh settings. |
| <a id="visualsection-manual-charts-full-screen"></a>`manual_charts_full_screen` | `bool` | Open manually added charts full-screen in the applicable GUI path; automatic signal/startup additions have separate rules. Does not enable manual trading mode. |
| <a id="visualsection-scale-plus-index"></a>`scale_plus_index` | `i32` | Extra price-span preset: 0 normal scale; 1..=9 select 100%, 200%, 500%, 1000%, 2000%, 5000%, 10000%, 20000%, 50000%. Used in the expanded price-scale mode, not as a generic zoom-step size. |

### Trades, order books and chart information

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="visualsection-show-red-green-lines"></a>`show_red_green_lines` | `bool` | Draw bid/ask price-history lines. The renderer uses the supported book-ticker path when enabled, otherwise its ordinary price-history path. |
| <a id="visualsection-show-red-green-dots"></a>`show_red_green_dots` | `bool` | Draw market trade dots. Candle/combo modes can force a tick layer independently; this does not stop collecting trades. |
| <a id="visualsection-glass-opacity"></a>`glass_opacity` | `i32` | Opacity of the orderbook background fill, percent 0..=100. Cumulative and individual-level strokes have separate opacity settings. |
| <a id="visualsection-book-cumulative-opacity"></a>`book_cumulative_opacity` | `i32` | Cumulative orderbook stroke opacity in percent 0..=100. The renderer skips the strokes at values 0 or 1. |
| <a id="visualsection-book-orders-opacity"></a>`book_orders_opacity` | `i32` | Individual orderbook-level stroke opacity in percent 0..=100. The renderer skips these strokes at 0 or 1. |
| <a id="visualsection-book-orders-width"></a>`book_orders_width` | `i32` | Stroke thickness of individual orderbook levels, GUI 1..=6 pixels. Not the horizontal length of the volume bar. |
| <a id="visualsection-draw-cur-price"></a>`draw_cur_price` | `i32` | Current-price label placement: 0 in the right panel, 1 in the orderbook spread, 2 hidden. Not a solid/dashed line selector. |
| <a id="visualsection-left-chart-info"></a>`left_chart_info` | `bool` | Prefer chart information on the left. Individual chart modes/layout constraints can override its placement. |
| <a id="visualsection-show-market-captions"></a>`show_market_captions` | `bool` | Show transient market/order-status messages on the chart. Not simply the ticker/title label; the VDS mode suppresses these messages. |
| <a id="visualsection-blink-config"></a>`blink_config` | [`BlinkConfig`](05-charts-and-display.md#blinkconfig) | BTC one-hour-delta visual/audible notification thresholds. Separate from automatic panic/stop settings. |

### Vertical volume and cursor measurements

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="visualsection-show-vert-volume"></a>`show_vert_volume` | `bool` | Show the vertical trade-volume histogram. Uses the fast renderer; candle mode can supply candle-volume bins. Separate from whether the trade dots themselves are shown. |
| <a id="visualsection-vert-vol-time-frame"></a>`vert_vol_time_frame` | `i32` | Volume bin index: 0 automatic by chart span, 1 five seconds, 2 fifteen seconds, 3 thirty seconds, 4 one minute, 5 three minutes, 6 five minutes. Candle-volume rendering can use the selected candle timeframe instead. |
| <a id="visualsection-vert-vol-opacity"></a>`vert_vol_opacity` | `f32` | Vertical-volume opacity as a fraction 0..=1. GUI percentages are divided by 100 before storing. |
| <a id="visualsection-vert-vol-height"></a>`vert_vol_height` | `f32` | Vertical-volume maximum height as a fraction of chart height, 0..=1. Not a number of pixels. |
| <a id="visualsection-vert-vol-kind"></a>`vert_vol_kind` | `i32` | Volume display: 0 overlay buy/sell bars from the same baseline, 1 stack buy and sell volumes. Not bars versus area rendering. |
| <a id="visualsection-vert-vol-ind-pos"></a>`vert_vol_ind_pos` | `i32` | Volume-scale placement: 0 left, 1 right. Changes label/scale layout, not the histogram time direction. |
| <a id="visualsection-v-tool-show"></a>`v_tool_show` | `bool` | Enable the cursor volume tool and, with horizontal volumes, its price-range measurements. Does not enable a strategy detector. |
| <a id="visualsection-v-tool-time"></a>`v_tool_time` | `f64` | Cursor-tool time-window length in seconds; 0 uses the current vertical-volume interval. Keep consistent with `v_tool_time_index` when editing the preset. |
| <a id="visualsection-v-tool-opacity"></a>`v_tool_opacity` | `f32` | Opacity fraction 0..=1 for the cursor-tool selection area; the time-selection rectangle uses half this value. |
| <a id="visualsection-v-tool-time-index"></a>`v_tool_time_index` | `i32` | GUI preset index 0..=10 mapping to `v_tool_time` seconds: 0, 2, 5, 15, 30, 60, 180, 300, 900, 1800, 3600. The GUI writes both fields; the renderer reads `v_tool_time`. |

### Horizontal volume profile

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="visualsection-hv-show"></a>`hv_show` | `bool` | Show the horizontal volume profile by price. Uses the fast renderer and applies to the main chart rather than every secondary frame. |
| <a id="visualsection-hv-width"></a>`hv_width` | `f32` | Horizontal-volume panel width as a fraction of available chart width, 0..=1. |
| <a id="visualsection-hv-time-frame-ind"></a>`hv_time_frame_ind` | `i32` | Horizontal-volume history selector: 0 automatic; 1..=9 correspond to 1, 5, 15, 30, 60, 120, 360, 720, 1440 minutes. Index 10 uses the available deep candle archive, not an exact guaranteed 48-hour window. |
| <a id="visualsection-hv-price-frame"></a>`hv_price_frame` | `f32` | Price smoothing half-width for horizontal-volume accumulation, in percent, GUI 0..=1. The renderer uses at least the market's percentage price tick. Not a fraction of the visible chart price range. |
| <a id="visualsection-hv-opacity"></a>`hv_opacity` | `f32` | Horizontal-volume stroke opacity, fraction 0..=1. |
| <a id="visualsection-hv-disp-vol"></a>`hv_disp_vol` | `i32` | Horizontal-volume label placement: 0 right with cleared background, 1 left with guide line, 2 right over the chart, 3 left over the chart with guide line. |
| <a id="visualsection-hv-kind"></a>`hv_kind` | `i32` | Horizontal-volume composition: 0 overlay buyer/seller volumes, 1 stack them. Deep-candle archive mode has combined volume rather than a true buy/sell split. |

### Candles

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="visualsection-chart-candles-style"></a>`chart_candles_style` | `u8` | Candle bodies: 0 filled, 1 outlines, 2 outlines where raw ticks are available and filled outside that region. Does not select a candle interval. |
| <a id="visualsection-chart-candles-tick-opacity"></a>`chart_candles_tick_opacity` | `u8` | Candle opacity in the region with raw ticks, integer percent 0..=100. Does not set opacity of the trade dots themselves. |
| <a id="visualsection-chart-candles-neutral-ticks"></a>`chart_candles_neutral_ticks` | `bool` | Use the neutral candle color in the region with raw ticks regardless of bullish/bearish direction. Not specifically a doji-color rule. |
| <a id="visualsection-chart-candles-outline-width"></a>`chart_candles_outline_width` | `u8` | Candle outline thickness setting 1..=3; renderer scales it for DPI and limits it to the actual candle width. |
| <a id="visualsection-chart-candles-tick-wicks"></a>`chart_candles_tick_wicks` | `bool` | Also draw candle wicks in the raw-tick region. Outside that region wicks are drawn independently of this flag. |
| <a id="visualsection-candle-colors"></a>`candle_colors` | [`[CandleColorSet; 2]`](05-charts-and-display.md#candlecolorset) | Two ARGB candle palettes in order [light, dark]. Each contains rising, falling and tick-region neutral colors. |

### Orders, profit and control panels

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="visualsection-panic-sell-opacity"></a>`panic_sell_opacity` | `i32` | Opacity of the panic-sell price-area overlay, percent 0..=100; 0 hides it. Does not alter panic selling. |
| <a id="visualsection-show-orders-captions"></a>`show_orders_captions` | `bool` | Show detailed order captions unless `spy_hide_mode` suppresses them. Does not hide the underlying order lines. |
| <a id="visualsection-orders-captions-lower"></a>`orders_captions_lower` | `bool` | Place eligible captions below their line; short-order captions use the lower placement even when this flag is false. |
| <a id="visualsection-show-usd-on-charts"></a>`show_usd_on_charts` | `bool` | Use USD valuation for chart profit/session/position amounts and related totals instead of the account's trading-currency amount. Does not convert the chart's price axis into USD. |
| <a id="visualsection-hide-right-chart-panel"></a>`hide_right_chart_panel` | `bool` | Collapse the right chart control panel by default. A chart can temporarily expand it; hiding controls does not disable their underlying trading functions. |
| <a id="visualsection-show-iceberg"></a>`show_iceberg` | `bool` | Use the iceberg-specific appearance for an order identified as iceberg. Does not enable iceberg order placement. |
| <a id="visualsection-hide-pnl"></a>`hide_pnl` | `bool` | Hide the futures PnL label on charts. Does not stop profit calculation or remove profit from API snapshots. |
| <a id="visualsection-vo-sort-kind"></a>`vo_sort_kind` | `u8` | Order-panel sort: 0 entries first, 1 exits first, 2 creation order. Applies to GUI order controls, not API delivery order. |
| <a id="visualsection-vo-older-first"></a>`vo_older_first` | `bool` | Show older order controls first; false reverses the normal order when not grouping by market. |
| <a id="visualsection-vo-sort-by-market"></a>`vo_sort_by_market` | `bool` | Group GUI order controls by market. The VDS layout suppresses this grouping; it can override the older/newer ordering preference. |
| <a id="visualsection-hide-buy-button"></a>`hide_buy_button` | `bool` | Hide the chart Buy button and related global buy-offset controls. Does not prohibit buy orders from shortcuts, strategies or API commands. |
| <a id="visualsection-remember-chart-buttons"></a>`remember_chart_buttons` | `bool` | Remember each market's selected fixed buy-amount and fixed sell-percentage buttons and restore them on selection in the corresponding modes. Not a blanket persistence switch for every chart button. |
| <a id="visualsection-spy-hide-mode"></a>`spy_hide_mode` | `bool` | Visually blur or suppress selected balance/profit/order information in Moonbot's GUI. Not a data-access or secrecy control: the underlying values remain available to the program/API. |

### Reports, drawing, detects and monitoring

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="visualsection-chart-watch-multi-frames"></a>`chart_watch_multi_frames` | `bool` | Keep multiple saved-trade charts in the chart-watch viewer. False clears previous viewer frames when another saved chart is opened; not a multi-timeframe switch. |
| <a id="visualsection-chart-history-len"></a>`chart_history_len` | `i32` | Extra wait in minutes after a trade before saving its chart history, GUI 0..=60. Normal saving waits at least about three seconds even at 0; chart-forwarding paths use their own 15..90-second bounds. Not a number of historical candles to request. |
| <a id="visualsection-custom-draw-config"></a>`custom_draw_config` | [`CustomDrawConfig`](06-drawing-and-news.md#customdrawconfig) | Drawing-tool appearance and behavior. Individual drawing-object alerts are separate state; see the drawing-tools chapter. |
| <a id="visualsection-global-current-draw-kind"></a>`global_current_draw_kind` | `u8` | Selected chart drawing tool, using the [tool codes](06-drawing-and-news.md#customdrawconfig-tools). Preserve reserved/internal kinds; ordinary drawing excludes the none, order-line and news-marker kinds. |
| <a id="visualsection-show-strat-numbers"></a>`show_strat_numbers` | `bool` | Prefix strategy names in the strategy tree with their numeric identifier. Does not change strategy IDs. |
| <a id="visualsection-show-filters"></a>`show_filters` | [`ShowFilters`](05-charts-and-display.md#showfilters) | Visibility and interaction preferences for filter/session/detection annotations on charts. Does not enable or disable actual strategy filters. |
| <a id="visualsection-charts-settings"></a>`charts_settings` | [`ChartsSettings`](05-charts-and-display.md#chartssettings) | Separate chart-monitor window layout and recentering preferences. Not the main chart's render rate. |
| <a id="visualsection-heatmap-config"></a>`heatmap_config` | [`HeatMapConfig`](05-charts-and-display.md#heatmapconfig) | Trade-size heatmap and optional system/timing overlays. See HeatMapConfig; this is a display preference, not the SDK CPU profiler. |
| <a id="visualsection-show-detects-tool"></a>`show_detects_tool` | `bool` | Place detection alert buttons in a separate detection-tool window instead of the main toolbar. |

### News, AI cards and appearance

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="visualsection-news-form-config"></a>`news_form_config` | [`NewsFormConfig`](06-drawing-and-news.md#newsformconfig) | News-window filtering and presentation settings; see NewsFormConfig. Visibility itself is not a field in this public record. |
| <a id="visualsection-ai-card-provider"></a>`ai_card_provider` | `u8` | Provider index in this core: 0 OpenAI, 1 Anthropic, 2 Google Gemini, 3 xAI Grok, 4 DeepSeek, 5 Perplexity, 6 OpenRouter. Out-of-range selects 0. API keys are separate private settings and are not included in SharedConfig. |
| <a id="visualsection-ai-card-model"></a>`ai_card_model` | `String` | Model ID for the selected provider. The core uses it only if present in that provider's current cached/fallback list; otherwise it chooses the first available model. Do not hardcode a universal model list in a settings editor. |
| <a id="visualsection-ai-card-prompt"></a>`ai_card_prompt` | `String` | AI-card prompt template; blank uses the built-in prompt for the GUI language. Supported placeholders: {symbol}, {exchange}, {price}, {deltas}, {volume}, {mcap}, {news}. Saving the template does not send an AI request. |
| <a id="visualsection-icon-selection"></a>`icon_selection` | `i32` | Moonbot icon-set choice: 1 Original, 2 Mark black-and-white. Stored as one-based value, unlike many other GUI selectors. |
| <a id="visualsection-hide-forum-label"></a>`hide_forum_label` | `bool` | Hide the community/forum label on Moonbot's main form. |
| <a id="visualsection-hide-ny-elka"></a>`hide_ny_elka` | `bool` | Hide the seasonal New Year decoration/greetings when that seasonal UI would otherwise be shown. |
| <a id="visualsection-font-sizes"></a>`font_sizes` | `[u8; 20]` | Twenty saved GUI font slots. Current explicit consumer uses slot 0 for the takers viewer: 0 leaves its default, positive values are clamped to 8..=20. Preserve unrecognized slots; not twenty interchangeable global font sizes. |
| <a id="visualsection-colors"></a>`colors` | [`IntColors`](05-charts-and-display.md#intcolors) | Legacy order-color record plus the active `price_line_width` setting. The seven color slots have no current rendering consumers; active theme colors are stored separately. |

### Inactive fields and compatibility

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="visualsection-v-tool-show-buyers"></a>`v_tool_show_buyers` | `bool` | Legacy saved checkbox without a current renderer consumer. Preserve; it does not currently hide/show buyer volume. |
| <a id="visualsection-hv-time-frame"></a>`hv_time_frame` | `i32` | Unused serialized value. The renderer calculates its own window from `hv_time_frame_ind`; preserve this field. |
| <a id="visualsection-hide-cashback-button"></a>`hide_cashback_button` | `bool` | Unused legacy flag in the current kernel. Preserve it; current cashback visibility uses other settings such as `cashback_settings`.`hide_info`. |
| <a id="visualsection-scale-minus-index"></a>`scale_minus_index` | `i32` | Unused serialized companion to `scale_plus_index`. Preserve; current zoom-out controls do not consume it. |
| <a id="visualsection-use-ai-coin-card"></a>`use_ai_coin_card` | `bool` | Legacy format flag; current AI-card runtime uses the configured own-provider path independently. Not an effective enable switch. |
| <a id="visualsection-unknown-tail"></a>`unknown_tail` | `Vec<u8>` | Preserve opaque bytes from newer kernels unchanged when round-tripping the visual section. |

<a id="spotconfig"></a>

## `trading.spot_config` — `SpotConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="spotconfig-show-trades"></a>`show_trades` | `bool` | Draw the corresponding spot/reference market's trade dots when that stream is available. Separate from the current market's trade-dot switch. |
| <a id="spotconfig-show-book"></a>`show_book` | `bool` | Draw the corresponding spot/second orderbook when supported and fresh. Does not hide the primary market's orderbook. |
| <a id="spotconfig-book-len"></a>`book_len` | `f32` | Visual width multiplier for the second/spot orderbook, in percent. Does not request this percentage of exchange depth levels. |
| <a id="spotconfig-show-market-avg"></a>`show_market_avg` | `bool` | Overlay the aggregate market-average history, normalized to the current chart. Weighting follows `trading.m_avg_use_vol_weight`; not necessarily volume-weighted. |
| <a id="spotconfig-show-min-max"></a>`show_min_max` | `bool` | Draw historical minimum/maximum price-envelope curves from the market's stored extrema. Not simply two 24-hour high/low markers. |
| <a id="spotconfig-show-avg-price"></a>`show_avg_price` | `bool` | Draw the market's smoothed price history from second/minute averages. Does not show the user's average position entry price. |
| <a id="spotconfig-spot-btc"></a>`spot_btc` | `bool` | Select a BTC-based corresponding/reference-market feed where supported, instead of the usual matching spot comparison. Changing it can require the kernel's subscription-refresh path; not just a BTC text label. |
| <a id="spotconfig-shift-spot"></a>`shift_spot` | `bool` | Shift spot/reference prices vertically by the current spot/futures price difference for comparison, except BTC-reference mode. Does not compensate for panel width or alter order prices. |
| <a id="spotconfig-show-mark-price"></a>`show_mark_price` | `bool` | Draw mark-price history when the market has enough mark-price samples. Requires a feed supporting mark price; does not configure liquidation protection. |
| <a id="spotconfig-show-liq"></a>`show_liq` | `bool` | Draw exchange liquidation-event dots on the chart. These are market events, not the liquidation-price line of the user's own position. |
| <a id="spotconfig-huge-liq"></a>`huge_liq` | `bool` | Increase the drawn size of liquidation-event dots when `show_liq` is on. Does not filter events by liquidation amount. |
| <a id="spotconfig-show-open-int"></a>`show_open_int` | `bool` | Draw futures open-interest history and cursor information when available. Does not enable a trading filter. |
| <a id="spotconfig-show-avg-price-line"></a>`show_avg_price_line` | `bool` | Draw the market's recent averaged-price history line. Separate from `show_avg_price`'s second/minute smoothed curves and from position entry prices. |

<a id="arbviewconfig"></a>

## `trading.arb_view_config` — `ArbViewConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="arbviewconfig-ver"></a>`ver` | `u8` | Serialized display-record version. Preserve received value. |
| <a id="arbviewconfig-show-absolute"></a>`show_absolute` | `bool` | Show absolute arbitrage price differences in the numeric block; requires `show_numbers`. May be combined with `show_percent`. |
| <a id="arbviewconfig-show-numbers"></a>`show_numbers` | `bool` | Show numeric arbitrage differences when arbitrage data is active. Does not create subscriptions or enable arbitrage trading. |
| <a id="arbviewconfig-show-lines"></a>`show_lines` | `bool` | Draw corresponding arbitrage price lines when arbitrage data is active. Independent of numeric-block visibility. |
| <a id="arbviewconfig-show-percent"></a>`show_percent` | `bool` | Show percentage differences in the numeric block. When both `show_percent` and `show_absolute` are false, the renderer still uses percent as its fallback. |
| <a id="arbviewconfig-show-right"></a>`show_right` | `bool` | Place the arbitrage numeric block on the right instead of the left of the chart. |

<a id="blinkconfig"></a>

## `visual.blink_config` — `BlinkConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="blinkconfig-blink-btc"></a>`blink_btc` | `bool` | Blink when the one-hour BTC delta leaves the lower/upper bounds. Blinking clears after the delta returns inside 99% of each threshold: for -5%/+5%, inside approximately -4.95%/+4.95%. This notification does not stop trading. |
| <a id="blinkconfig-blink-btc-delta"></a>`blink_btc_delta` | `f64` | Lower BTC one-hour delta bound, percent. The GUI stores a non-positive value (-abs(input)). |
| <a id="blinkconfig-blink-btc-delta-up"></a>`blink_btc_delta_up` | `f64` | Upper BTC one-hour delta bound, percent. The GUI stores abs(input). |
| <a id="blinkconfig-alarm-btc"></a>`alarm_btc` | `bool` | Repeat a sound every five seconds while BTC blinking is active; requires `blink_btc`. |
| <a id="blinkconfig-alarm-type"></a>`alarm_type` | `u8` | Normal sound preset 1..=11; 0 is silent. Used when `alarm_btc` is enabled. |

<a id="showfilters"></a>

## `visual.show_filters` — `ShowFilters`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="showfilters-need-show"></a>`need_show` | `bool` | Show the strategy-filter/session annotation area and eligible MoonShot bounds on charts. Does not enable the underlying strategy conditions. |
| <a id="showfilters-filters"></a>`filters` | `bool` | Show strategy-filter annotations when `need_show` is enabled. |
| <a id="showfilters-sessions"></a>`sessions` | `bool` | Show session annotations when `need_show` is enabled. |
| <a id="showfilters-hide-zero"></a>`hide_zero` | `bool` | Hide inactive or near-zero session annotations, using the session limits, counters and penalty state. This is not a report filter for exactly zero profit. |
| <a id="showfilters-m-shot-area"></a>`m_shot_area` | `bool` | Show eligible MoonShot price boundaries in the annotation area; requires `need_show`. |
| <a id="showfilters-scale-tool"></a>`scale_tool` | `bool` | Show the percentage-distance tool between the cursor price and spread. Independent of `need_show`; does not add zoom controls. |
| <a id="showfilters-scroll-filters"></a>`scroll_filters` | `bool` | Allow Alt+mouse-wheel scrolling inside the visible filter area. |
| <a id="showfilters-show-detects"></a>`show_detects` | `bool` | Show detection annotations on charts. Separate from the `need_show` filter-area switch and from detection execution. |

<a id="chartssettings"></a>

## `visual.charts_settings` — `ChartsSettings`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="chartssettings-auto-arrange"></a>`auto_arrange` | `bool` | Automatically arrange charts in monitoring windows. |
| <a id="chartssettings-visible"></a>`visible` | `bool` | Saved visibility of monitoring windows, not all main-window charts. |
| <a id="chartssettings-wide"></a>`wide` | `bool` | Use the wide layout of charts in monitoring windows. |
| <a id="chartssettings-stay-on-top"></a>`stay_on_top` | `bool` | Keep monitoring windows above other windows. |
| <a id="chartssettings-max-charts"></a>`max_charts` | `i32` | Maximum chart frames per monitoring window. GUI minimum: 10. Not the number of monitoring windows; use the received value rather than SDK Default (0). |
| <a id="chartssettings-refresh"></a>`refresh` | `i32` | Recentring interval selector: 0=5 s, 1=15 s, 2=30 s, 3=60 s, 4=300 s, 5=900 s. Recentres charts around the latest price; not FPS or a data-download interval. |
| <a id="chartssettings-x1"></a>`x1` | `f64` | Reserved legacy value without a current consumer; preserve it. |
| <a id="chartssettings-x2"></a>`x2` | `f64` | Reserved legacy value without a current consumer; preserve it. |

<a id="heatmapconfig"></a>

## `visual.heatmap_config` — `HeatMapConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="heatmapconfig-show"></a>`show` | `bool` | Show the heatmap area. Trade-size heatmap requires fast charts and market-maker detection; selecting any CPU/trade/app/draw diagnostic overlay replaces it with system data. Not a new market subscription. |
| <a id="heatmapconfig-use-q"></a>`use_q` | `bool` | Calculate relative heatmap intensity from trade quantity (normalized by a common average price), instead of each trade's notional at its own price. |
| <a id="heatmapconfig-height"></a>`height` | `f32` | Heatmap height as a fraction of the chart; GUI 0.05..=0.8. |
| <a id="heatmapconfig-cpu"></a>`cpu` | `bool` | Show the CPU history overlay. A display switch, not a detailed profiler. |
| <a id="heatmapconfig-trades"></a>`trades` | `bool` | Show trade-feed latency history, not trade count or throughput. |
| <a id="heatmapconfig-app-latency"></a>`app_latency` | `bool` | Show application-latency history. |
| <a id="heatmapconfig-draw-latency"></a>`draw_latency` | `bool` | Show chart-rendering latency history. |

<a id="candlecolorset"></a>

## `visual.candle_colors[]` — `CandleColorSet`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="candlecolorset-green"></a>`green` | `u32` | ARGB color (0xAARRGGBB) for rising candles, including equal open/close. |
| <a id="candlecolorset-red"></a>`red` | `u32` | ARGB color (0xAARRGGBB) for falling candles. |
| <a id="candlecolorset-neutral"></a>`neutral` | `u32` | ARGB color for the tick region when `chart_candles_neutral_ticks` is enabled; not specifically a doji color. |

<a id="intcolors"></a>

## `visual.colors` — `IntColors`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="intcolors-buy-order-color-bu"></a>`buy_order_color_bu` | `u32` | Legacy stored color without an active renderer consumer. Preserve it; do not offer it as an effective color control. |
| <a id="intcolors-sell-color-u"></a>`sell_color_u` | `u32` | Legacy stored color without an active renderer consumer. Preserve it; do not offer it as an effective color control. |
| <a id="intcolors-buy-order-color-wu"></a>`buy_order_color_wu` | `u32` | Legacy stored color without an active renderer consumer. Preserve it; do not offer it as an effective color control. |
| <a id="intcolors-sell-order-color-u"></a>`sell_order_color_u` | `u32` | Legacy stored color without an active renderer consumer. Preserve it; do not offer it as an effective color control. |
| <a id="intcolors-buy-order-done-color-u"></a>`buy_order_done_color_u` | `u32` | Legacy stored color without an active renderer consumer. Preserve it; do not offer it as an effective color control. |
| <a id="intcolors-sell-order-done-color-u"></a>`sell_order_done_color_u` | `u32` | Legacy stored color without an active renderer consumer. Preserve it; do not offer it as an effective color control. |
| <a id="intcolors-trailing-color-u"></a>`trailing_color_u` | `u32` | Legacy stored color without an active renderer consumer. Preserve it; do not offer it as an effective color control. |
| <a id="intcolors-price-line-width"></a>`price_line_width` | `i32` | Base price/order-line width in pixels; GUI 1..=5. Individual line renderers may add their own width adjustment. |
