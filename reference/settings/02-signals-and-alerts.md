# Signal parsing, alerts and saved filters

[Settings reference](README.md)

Telegram and clipboard input can use either the simple parser or the advanced parser. Both advanced paths share `signal_config`. Recognizing a ticker is the first step: automatic entry also depends on the source's auto-buy switch, strategy rules and the kernel's trading state.

For a Telegram integration, configure the [reader and account](10-settings-apis.md#telegram-on-the-kernel), select the channel, then choose parsing and entry rules. Clipboard settings apply to the machine running Moonbot; a remote terminal handles its own clipboard.

This section also contains saved chart, sound and search preferences. They are grouped separately below. Ordinary sound presets are 1..=11: Alarm, ringout, Ringin, TurnOn, Cork, Bark, BabyToy, Error, Hallo, PFIFF, YES_MAST; 0 is silent.

Related: [external signals and the detect pipeline](../../concepts/02-detect-pipeline-and-signals.md). Field paths are relative to `SharedConfig`.

<a id="signalssection"></a>

## `signals` — `SignalsSection`

### Telegram and clipboard input

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="signalssection-pump-channel"></a>`pump_channel` | `String` | Selected Telegram signal-channel name, or comma-separated selected names in multi-channel mode. Channel selection does not authenticate Telegram or start trading by itself. |
| <a id="signalssection-pump-channels"></a>`pump_channels` | `Vec<String>` | Saved list of channel choices shown by the channel selector. The active selection is `pump_channel`; listing a channel here alone does not subscribe a strategy to it. |
| <a id="signalssection-multi-channels"></a>`multi_channels` | `bool` | Enable multiple selections in the channel picker. Together with `more_then_1_channel`, enables repeated-signal confirmation. |
| <a id="signalssection-look-full-link-tlg"></a>`look_full_link_tlg` | `bool` | In the simple Telegram parser, require an exchange-market link. When false, ticker-text recognition is also attempted. Not used by the advanced parser. |
| <a id="signalssection-telegram-auto-buy"></a>`telegram_auto_buy` | `bool` | Allow automatic buys from ordinary Telegram signals. A matching Telegram strategy can supply its own auto-buy decision; this is not a master switch for all strategies. |
| <a id="signalssection-only-secret-signal"></a>`only_secret_signal` | `bool` | Legacy simple-parser option requiring the historical "X secret signal" marker in recognized links. No normal settings-page control; preserve the received value. |
| <a id="signalssection-more-then-1-channel"></a>`more_then_1_channel` | `bool` | With `multi_channels`, wait for a second accepted signal for the same coin within 3 seconds. The implementation counts messages, not distinct channel identities; do not promise confirmation by two independent channels. |
| <a id="signalssection-lower-case-token-tlg"></a>`lower_case_token_tlg` | `bool` | Allow lowercase ticker text in the simple Telegram parser by normalizing text to uppercase. Has no effect when `advanced_filter` selects the advanced parser. |
| <a id="signalssection-monitor-clipboard"></a>`monitor_clipboard` | `bool` | Process text from the kernel machine's clipboard for chart/signal selection. `clipboard_auto_buy` separately permits buying; `clipboard_auto_buy` also activates processing when this flag is false. |
| <a id="signalssection-clipboard-auto-buy"></a>`clipboard_auto_buy` | `bool` | Allow automatic buys from text copied to the kernel machine's clipboard, unless `manual_mode` is active. Independent of the terminal application's clipboard; not a remote clipboard subscription. |
| <a id="signalssection-lower-case-token-cbd"></a>`lower_case_token_cbd` | `bool` | Allow lowercase ticker text in the simple clipboard parser. Not used when `advanced_filter_clipboard` is enabled. |
| <a id="signalssection-look-full-link-cbd"></a>`look_full_link_cbd` | `bool` | Require an exchange-market link in the simple clipboard parser. When false, also recognize ticker text. Advanced clipboard parsing uses `signal_config` instead. |
| <a id="signalssection-dont-buy-reply"></a>`dont_buy_reply` | `bool` | Reject Telegram trading signals that reply to another message. Does not prevent parsing ordinary clipboard text. |
| <a id="signalssection-listen-moon-channel"></a>`listen_moon_channel` | `bool` | Accept the built-in Moonbot signal channel in addition to the ordinary selected-channel checks. Telegram service/account and channel availability are still required. |

### Parsing and automatic entry

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="signalssection-advanced-filter"></a>`advanced_filter` | `bool` | Select the advanced Telegram message parser with keyword, ticker, price and stop rules from `signal_config`. Does not itself enable auto-buy. |
| <a id="signalssection-advanced-filter-clipboard"></a>`advanced_filter_clipboard` | `bool` | Use `signal_config` for clipboard text; otherwise use the simple link/ticker parser with `look_full_link_cbd` and `lower_case_token_cbd`. |
| <a id="signalssection-signal-config"></a>`signal_config` | [`SignalConfig`](02-signals-and-alerts.md#signalconfig) | Shared advanced-parser rules used when `advanced_filter` or `advanced_filter_clipboard` is enabled. Both sources use the same rule record. |
| <a id="signalssection-msg-keywords-long"></a>`msg_keywords_long` | `String` | Comma-separated long/buy keywords for `signal_config`.`use_keywords`. Matching is case-insensitive; a keyword also identifies the signal type for strategy selection. |
| <a id="signalssection-msg-keywords-short"></a>`msg_keywords_short` | `String` | Comma-separated short keywords for `signal_config`.`use_keywords`. Considered on futures; does not enable short trading on spot. |
| <a id="signalssection-msg-token-tags"></a>`msg_token_tags` | `String` | Comma-separated ticker markers, for example #,$. Used by the configurable advanced token parser; markers may surround, precede or follow a ticker. |
| <a id="signalssection-msg-black-words"></a>`msg_black_words` | `String` | Comma-separated forbidden words or phrases for `signal_config`.`use_black_words`. A match rejects the parsed signal. |
| <a id="signalssection-max-too-long-msg-len"></a>`max_too_long_msg_len` | `i32` | Legacy character-limit field with no active consumer. Preserve it; the active advanced-parser limit is `signal_config`.`words_count` with `use_words_count`. |
| <a id="signalssection-lower-price-words"></a>`lower_price_words` | `String` | Comma-separated dip-buy phrases, such as wait dip. With `signal_config`.`use_lower_price_words`, switch the non-strategy signal to `x_lower_price` and `auto_cancel_lower_buy`; do not interpret this as a blacklist. |
| <a id="signalssection-autodetect-auto-buy"></a>`autodetect_auto_buy` | `bool` | Legacy flag: current detection and order-execution paths do not read it, and the GUI control is hidden. Configure auto-buy on the relevant strategies instead. |

### Charts and volume tools

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="signalssection-load-deep-history"></a>`load_deep_history` | `bool` | Load and analyze market history on kernel startup. The normal auto-start path enables this if necessary; changing it is not a one-shot history-refresh command. |
| <a id="signalssection-show-cross"></a>`show_cross` | `bool` | Show the chart crosshair in the Moonbot GUI. Does not change signal detection or order execution. |
| <a id="signalssection-auto-show-on-signal"></a>`auto_show_on_signal` | `bool` | Bring the Moonbot GUI/chart forward for a signal or order alert. Display preference; does not grant permission to trade. |
| <a id="signalssection-full-screen-prevent-signals"></a>`full_screen_prevent_signals` | `bool` | Keep signal-created charts from interrupting work on an existing full-screen chart. The GUI also protects orderbook interaction independently. Does not disable trading signals. |
| <a id="signalssection-base-vol-ind-type"></a>`base_vol_ind_type` | `i32` | Chart Bv/Sv display interval: -2 = last N minutes, -1 = last N trades, 0 = pre-pump view, or 1, 3, 5, 15, 30 minutes. N comes from `base_vol_n`. This is not a minimum-volume trading filter. |
| <a id="signalssection-base-vol-n"></a>`base_vol_n` | `i32` | N for the chart's N-trades or N-minutes Bv/Sv display, selected by `base_vol_ind_type`. Market initialization enforces at least 2; the minutes view uses at most 1440. Not a 24-hour-volume threshold. |
| <a id="signalssection-use-last-detect-caption"></a>`use_last_detect_caption` | `bool` | Replace the chart's stored signal caption with the latest detection caption. When false, retain an existing caption instead of replacing it on each detection. |
| <a id="signalssection-last-used-order-type"></a>`last_used_order_type` | `i32` | Remembered pending-order dialog choice: 0 = BUY, 1 = BUY STOP. Zero-based GUI state, not a protocol order-side enum. |

### Sounds and trade alerts

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="signalssection-signal-sound"></a>`signal_sound` | `i32` | Connectivity-alert sound selected by `play_signal_sound`. 1-based sound number (GUI 1..=11); 0 means no sound. Not the strategy signal-sound selector. |
| <a id="signalssection-play-signal-sound"></a>`play_signal_sound` | `bool` | Play `signal_sound` for connection problems or high API-load indication, at most once per 5 seconds. Does not enable sounds for every incoming trading signal. |
| <a id="signalssection-signal-sound-2"></a>`signal_sound_2` | `i32` | Sell-alert sound for `play_sell_alert`. 1-based sound number (GUI 1..=11); 0 means no sound. |
| <a id="signalssection-sell-alert-level"></a>`sell_alert_level` | `i32` | Sell-price proximity in percent, GUI 0..=20. With `play_sell_alert`, 0 alerts on completion; positive values alert as price approaches a sell order after it has been open for 30 seconds, with a 5-second repeat interval. |
| <a id="signalssection-play-sell-alert"></a>`play_sell_alert` | `bool` | Enable sell alerts using `signal_sound_2` and `sell_alert_level`. This only controls notification, not execution. |
| <a id="signalssection-buy-signal-sound"></a>`buy_signal_sound` | `i32` | Buy-alert sound for `play_buy_alert`. 1-based sound number (GUI 1..=11); 0 means no sound. |
| <a id="signalssection-play-buy-alert"></a>`play_buy_alert` | `bool` | Enable buy-completion alerts. A positive `buy_alert_level` also enables price-proximity alerts while waiting for the buy. |
| <a id="signalssection-buy-alert-level"></a>`buy_alert_level` | `i32` | Buy-price proximity in percent, GUI 0..=20. A positive value enables proximity alerts with a 5-second repeat interval; 0 leaves only the completion alert. Requires `play_buy_alert`. |

### Saved filters and compatibility

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="signalssection-strats-filter"></a>`strats_filter` | `String` | Saved search text in the strategy list: matches a strategy's full name, or recognized strategy-type shortcuts. Filters displayed rows; does not enable/disable strategy execution. |
| <a id="signalssection-news-tags-filter"></a>`news_tags_filter` | `String` | Selected MoonNews tags separated by newline (LF). Empty means all tags; feed mode bypasses the tag filter. Not comma-separated. |
| <a id="signalssection-news-tokens-filter"></a>`news_tokens_filter` | `String` | MoonNews coin filter, separated by commas or spaces and matched case-insensitively. Empty means all coins; any matching coin passes. Display filter, not a trading blacklist. |
| <a id="signalssection-do-monitoring"></a>`do_monitoring` | `bool` | Legacy stored flag without an active signal-processing consumer in the current kernel. Preserve it; do not expose it as a working master enable switch. |
| <a id="signalssection-unknown-tail"></a>`unknown_tail` | `Vec<u8>` | Opaque extension bytes from a newer kernel. Preserve exactly when editing or sharing a snapshot; never expose as an editable setting. |

<a id="signalconfig"></a>

## `signals.signal_config` — `SignalConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="signalconfig-ver"></a>`ver` | `i32` | Record version. Preserve the received value; not a user setting. |
| <a id="signalconfig-use-keywords"></a>`use_keywords` | `bool` | Require a configured long/short keyword in the advanced parser. A recognized exchange-market link can also satisfy this check. Short keywords are considered on futures. |
| <a id="signalconfig-use-token-tags"></a>`use_token_tags` | `bool` | Enable configurable token tags from `msg_token_tags` in the advanced parser. Tags may precede or follow a ticker; `tokens_no_tags` separately permits untagged uppercase tickers. |
| <a id="signalconfig-buy-key-dist"></a>`buy_key_dist` | `i32` | Maximum number of intervening words between a keyword and a ticker. Used with `use_keywords`; 0 means adjacent, values >=10 disable the distance limit. GUI range 0..=16. |
| <a id="signalconfig-only-1-token"></a>`only_1_token` | `bool` | Reject advanced-parser messages containing more than one candidate coin. BTC and ETH are treated as quote/context symbols when another candidate exists; repeated mentions of the same coin do not count as different coins. |
| <a id="signalconfig-buy-if-price-found"></a>`buy_if_price_found` | `bool` | Require a recognizable entry price in the message. This only filters messages; `use_price` separately selects that price for the order. The parser searches numeric values near the current market price, not arbitrary numbers. |
| <a id="signalconfig-x-found-price"></a>`x_found_price` | `i32` | Entry-price adjustment in percent, applied to the price parsed from the message when `use_price` is enabled. Uses the normal direction-aware price adjustment; unlike `x_lower_price`, one unit here is one percent. |
| <a id="signalconfig-use-black-words"></a>`use_black_words` | `bool` | Reject a parsed signal when a configured `msg_black_words` entry is found. Uses the advanced Telegram/clipboard parser. |
| <a id="signalconfig-words-count"></a>`words_count` | `i32` | Maximum counted words in a message, used with `use_words_count`. GUI range 2..=50. Numeric values and one-character items are excluded from this counter. |
| <a id="signalconfig-use-words-count"></a>`use_words_count` | `bool` | Reject messages whose parsed word count exceeds `words_count`. Does not limit raw character length. |
| <a id="signalconfig-use-price"></a>`use_price` | `bool` | Use an entry price found in the message, adjusted by `x_found_price`. Without a recognized price, normal pricing is used unless `buy_if_price_found` rejects the signal. |
| <a id="signalconfig-use-stops"></a>`use_stops` | `bool` | Parse stop-loss and take-profit candidates from message numbers for the signal. This is heuristic parsing near the current price, not a promise to interpret every channel's format. |
| <a id="signalconfig-tokens-no-tags"></a>`tokens_no_tags` | `bool` | Also recognize untagged uppercase tickers in the advanced parser. Ambiguous ordinary words are excluded; this does not make arbitrary lowercase words into tickers. |
| <a id="signalconfig-token-links"></a>`token_links` | `bool` | Recognize exchange-market URL patterns in the advanced token parser; links are parsed as text, not fetched over HTTP. Enable the configurable-token path with `use_token_tags` or `tokens_no_tags`. |
| <a id="signalconfig-use-lower-price-words"></a>`use_lower_price_words` | `bool` | Recognize `lower_price_words` phrases and place the non-strategy signal buy with `x_lower_price`, using `auto_cancel_lower_buy` as its timeout. Does not simply discard the signal; strategies have their own dip settings. |
| <a id="signalconfig-x-lower-price"></a>`x_lower_price` | `i32` | Dip-buy offset in half-percent units: -10 means -5%. GUI range -40..=40. Used when `use_lower_price_words` matches a phrase and no strategy supplies its own dip price. |
| <a id="signalconfig-special-formats"></a>`special_formats` | `bool` | Also recognize tickers spelled as separated letters, such as (B)(T)(C), B-T-C, B=T=C or B T C, before normal token matching. |
