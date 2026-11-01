# Trading, leverage and position control

[Settings reference](README.md)

These settings define global order sizing, entry and exit defaults, and futures leverage policy. A strategy or an individual order can supply its own values where the field description allows it. Choosing a Manual strategy is separate from enabling automated strategies.

**Order amount and leverage are separate decisions.** `use_manual_balance` selects a fixed amount; otherwise `play_with` selects a share of the trading balance. Automatic leverage uses `auto_lev_control` for the required position limit and `auto_manage_lev` for the policy. Increasing leverage requires its own permission.

Related: [manual trading](../../concepts/03-spike-hunting-mechanics.md), [order management and stops](../../concepts/06-orders-exits-and-stops-cascade.md), [settings APIs](10-settings-apis.md). Field paths are relative to `SharedConfig`.

<a id="tradingsection"></a>

## `trading` — `TradingSection`

### Entry sizing and price

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="tradingsection-x-ask"></a>`x_ask` | `i32` | Global buy-price offset in half-percent units: 6 means +3%, -4 means -2%. Applied to the reference ask selected by `use_current_ask`; a strategy or explicit order price can override it. Not exchange tick steps. |
| <a id="tradingsection-use-current-ask"></a>`use_current_ask` | `bool` | Use the current ask as the reference for ordinary buy pricing; otherwise use the ask from about 30 seconds earlier. Strategies can select their own price source. The alternative is not the last trade price. |
| <a id="tradingsection-play-with"></a>`play_with` | `i32` | Order amount as thousandths of total trading balance: balance * `play_with` / 1000, then multiplied by leverage on futures. GUI 1..=1000. Ignored when `use_manual_balance` selects `fixed_trade_balance`. |
| <a id="tradingsection-use-manual-balance"></a>`use_manual_balance` | `bool` | Use `fixed_trade_balance` as the default order amount instead of the `play_with` share of balance. A strategy's explicit order size remains separate. |
| <a id="tradingsection-fixed-trade-balance"></a>`fixed_trade_balance` | `f64` | Fixed default order amount in the trading currency, selected by `use_manual_balance`. The amount is not automatically multiplied by leverage on this path; initialization defaults depend on the trading currency. |
| <a id="tradingsection-max-orders"></a>`max_orders` | `i32` | Global concurrent active-order limit used by entry checks. Includes active trade workers, not only unfilled buys. GUI 1..=1000, additionally restricted by edition and `unlimited_orders`; strategies can impose lower limits. |
| <a id="tradingsection-unlimited-orders"></a>`unlimited_orders` | `bool` | Allow the PRO settings editor to set `max_orders` above its ordinary 30-order ceiling. Does not remove `max_orders` or exchange/edition/strategy limits. |
| <a id="tradingsection-free-position-check"></a>`free_position_check` | `bool` | Use full balance/position amounts in relevant futures sizing checks rather than only currently free funds; in one-way mode, position-limit checks use the order's direction. Does not detect or close orphaned positions. Exchange rejection remains possible. |
| <a id="tradingsection-auto-reduce-order"></a>`auto_reduce_order` | `bool` | Reduce requested buy quantity to the market's exchange maximum order/position quantity where those limits are known. Not the free-balance sizing switch; inverse-base-currency mode is excluded, and some explicit split-order paths have their own sizing. |
| <a id="tradingsection-correct-order-price"></a>`correct_order_price` | `bool` | Allow the exchange engine to correct prices against exchange percentage-price limits once sufficient price data is available. This is separate from mandatory tick-size rounding and may change the requested price. |
| <a id="tradingsection-buy-iceberg"></a>`buy_iceberg` | `bool` | Allow iceberg buy orders where the exchange engine and market support them. Quantity/minimum-notional checks still apply; this flag does not emulate iceberg orders on unsupported exchanges. Mirrors the compact `buy_iceberg` setting. |
| <a id="tradingsection-sell-iceberg"></a>`sell_iceberg` | `bool` | Allow iceberg sell orders where supported by the exchange engine and market. Does not guarantee an iceberg for every sell; order quantity/type and market constraints still apply. Mirrors compact `sell_iceberg`. |
| <a id="tradingsection-iceberg-step"></a>`iceberg_step` | `f64` | In the standard iceberg check, require the market's tick size as a percentage of current ask to be strictly below this threshold. This is a price-step percentage, not a slice-size fraction. The engine calculates the slice quantity from exchange limits. |
| <a id="tradingsection-iceberg-click-count"></a>`iceberg_click_count` | `i32` | Remembered count used to stop showing the iceberg button hint after repeated use. Preserve as GUI state; not a trade quantity or retry limit. |
| <a id="tradingsection-fixed-balance-warning"></a>`fixed_balance_warning` | `bool` | Remembered acknowledgement of the fixed-amount warning dialog. Preserve it; not a risk-control switch or editable trading parameter. |

### Exits, stops and cancellation

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="tradingsection-x-sell"></a>`x_sell` | `i32` | Main sell target in percent before leverage adjustment. Positive values use `x_t_mode`'s optional x10 scale, capped at 900%; 0 selects scalp mode using `x_sell_scalp` / 50. `fixed_sell_mode` selects its own target. Prefer the typed ClientSettingsCommand helpers for UI controls. |
| <a id="tradingsection-x-sell-scalp"></a>`x_sell_scalp` | `i32` | Minimum scalp sell target in 1/50-percent units: 10 means 0.2%. Used when `x_sell` = 0 and `fixed_sell_mode` is off; `sell_auto_move` can place the sell above this minimum based on the order book. |
| <a id="tradingsection-x-t-mode"></a>`x_t_mode` | `bool` | Multiply the main/fixed sell percentage by 10. Does not multiply every numeric setting, and does not scale `x_sell_scalp` / 50. Shared with the compact settings x_tmode field. |
| <a id="tradingsection-fixed-sell-mode"></a>`fixed_sell_mode` | `bool` | Use `fixed_sell_price` as the global sell percentage instead of the `x_sell` slider/scalp mode. This is a fixed percentage target, not an absolute exchange price; strategy/per-order overrides remain separate. |
| <a id="tradingsection-fixed-sell-price"></a>`fixed_sell_price` | `f64` | Sell-target percentage used in `fixed_sell_mode`, multiplied by 10 when `x_t_mode` is on. It is not an absolute quote price. Leverage-aware take-profit mode can further scale the resulting price distance. |
| <a id="tradingsection-sell-auto-move"></a>`sell_auto_move` | `bool` | Adjust the initial sell placement using order-book liquidity. In scalp mode, search above the minimum scalp target; this is not a periodic timer that continually moves every sell. |
| <a id="tradingsection-random-price"></a>`random_price` | `bool` | Randomize the initial global sell-target percentage by up to about 5% of that target, before leverage adjustment. Does not randomize every order or guarantee concealment from other traders. |
| <a id="tradingsection-use-lev-for-take"></a>`use_lev_for_take` | `bool` | Interpret relevant futures profit/target percentages with leverage: the global sell price distance is divided by leverage, while displayed/calculated profit percentages include it. Strategy-specific leverage options still apply; this does not change exchange leverage itself. |
| <a id="tradingsection-auto-sell-partial"></a>`auto_sell_partial` | `i32` | For ordinary buys, cancel the unfilled remainder and proceed to selling the filled portion once the fill percentage is strictly greater than this threshold and the filled amount is tradable. GUI 1..=100; 100 disables this early transition. |
| <a id="tradingsection-cancel-buy-on-sell-fill"></a>`cancel_buy_on_sell_fill` | `bool` | When a sell completes, cancel remaining buys on the same market through the kernel's normal cancellation path. Strategy-specific cancellation rules also exist independently. |
| <a id="tradingsection-auto-cancel-buy-order"></a>`auto_cancel_buy_order` | `i32` | Timeout for ordinary automatically started buys without a strategy: values <30 are seconds; 30..59 mean (value - 29) minutes; 60 disables this timeout. Dip-word signals use `auto_cancel_lower_buy`. A manually moved order and strategy timers follow their own rules. |
| <a id="tradingsection-auto-cancel-lower-buy"></a>`auto_cancel_lower_buy` | `i32` | Timeout in minutes for a non-strategy signal using dip-word pricing. 600 disables the timeout. Different from the strategy parameter AutoCancelLowerBuy, whose unit is seconds. |
| <a id="tradingsection-vol-drop-level"></a>`vol_drop_level` | `i32` | V-Stop price offset in half-percent units: 7 means +3.5% from entry. GUI -20..=20. Defines the price at which available order-book volume is checked for an enabled per-order V-Stop; it is not the percentage by which volume must fall. |
| <a id="tradingsection-price-drop-level"></a>`price_drop_level` | `f32` | Global stop-loss price adjustment in percent, normally negative. Used when an order follows the global stop; per-order/strategy settings can override it. Long price = entry * (1 + value/100); short price = entry / (1 + value/100), so the same numeric value is not a symmetric market move. |
| <a id="tradingsection-panic-if-price-drop"></a>`panic_if_price_drop` | `bool` | Default stop-loss enablement for orders using global settings. Does not override every strategy's or already edited order's individual stop state. |
| <a id="tradingsection-trailing-stop"></a>`trailing_stop` | `bool` | Default trailing-stop enablement for orders using global settings. Strategy and individual-order trailing settings remain separate. |
| <a id="tradingsection-trailing-drop"></a>`trailing_drop` | `f32` | Base trailing distance in percent, normally negative, for orders following the global trailing level. `trailing_float` adjusts the distance as favorable price movement grows. |
| <a id="tradingsection-trailing-float"></a>`trailing_float` | `f64` | Coefficient widening the trailing distance as favorable price movement grows: subtract coefficient * favorable gain percent from the negative trailing level. 0 keeps a fixed distance. GUI coefficient range -0.5..=2, stored directly (not percent units). |
| <a id="tradingsection-g-take-profit"></a>`g_take_profit` | `f64` | Profit threshold in percent for `use_g_take_profit`. Gates global trailing activation and constrains its closing price; it is separate from the initial sell target `x_sell`. GUI range 0.5..=10. |
| <a id="tradingsection-use-g-take-profit"></a>`use_g_take_profit` | `bool` | Require the global `g_take_profit` threshold before global trailing closes a non-strategy order. Does not place a separate take-profit order by itself. |
| <a id="tradingsection-use-stop-market"></a>`use_stop_market` | `bool` | Allow supported server-side market-stop handling. The kernel's platform gate admits Binance spot and main Binance Futures; compatible order/strategy stop conditions are also required. This is not a universal conversion of all stops on every exchange. |

### Manual trading and pending orders

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="tradingsection-manual-mode"></a>`manual_mode` | `bool` | Disable automatic entry through the normal signal/detection paths while retaining manual order controls and management of existing positions. Not an emulator switch. |
| <a id="tradingsection-use-manual-strategy"></a>`use_manual_strategy` | `bool` | Use the selected Manual strategy for manual order parameters. The strategy must exist; selecting it does not start automatic strategy execution. |
| <a id="tradingsection-manual-strategy"></a>`manual_strategy` | `String` | Name of the selected Manual strategy, used with `use_manual_strategy`. The compact settings view identifies the selected strategy by manual_strategy_id instead. |
| <a id="tradingsection-ignore-strat-sell-price"></a>`ignore_strat_sell_price` | `bool` | For Manual strategies, use the global sell target instead of the strategy's SellPrice. Does not override SellPrice for every automatic strategy. |
| <a id="tradingsection-manual-strats-names"></a>`manual_strats_names` | `[String; 10]` | Ten saved Manual-strategy names for quick-selection slots. Each must refer to an existing Manual strategy; these names do not create strategies or start them automatically. |
| <a id="tradingsection-manual-strats-config"></a>`manual_strats_config` | [`ManualStratsConfig`](04-orders-reports-and-notifications.md#manualstratsconfig) | Visibility and shortcut bindings for Manual-strategy quick-selection buttons. The slot contents are in `manual_strats_names`. |
| <a id="tradingsection-buy-on-enter"></a>`buy_on_enter` | `bool` | Allow Enter in the coin-search workflow to buy on the last opened chart. Ctrl+Enter is excluded. This is a manual trading action, not automatic buying whenever search text changes. |
| <a id="tradingsection-multi-orders"></a>`multi_orders` | [`MultiOrdersConfig`](04-orders-reports-and-notifications.md#multiordersconfig) | Current chart mouse bindings, order-movement selection and multi-order display options. See MultiOrdersConfig; the obsolete enable byte is not an execution switch. |
| <a id="tradingsection-dbl-click-panic-sell"></a>`dbl_click_panic_sell` | `bool` | Require a second click within 300 ms to activate chart Panic Sell. The explicit hotkey path bypasses this mouse confirmation. |
| <a id="tradingsection-pending-order-set-click"></a>`pending_order_set_click` | `u8` | Mouse binding for a pending long order in the classic Moonbot chart; uses the [mouse-action codes](04-orders-reports-and-notifications.md#mouse-action-codes). A remote terminal sends a separate [`new_pending_order` action](https://github.com/Moonbot-Tech/MoonProto/blob/main/docs/trade_actions.md); saving this binding does not place an order. |
| <a id="tradingsection-pending-orders-spread"></a>`pending_orders_spread` | `f64` | Execution-price offset from the trigger, in percent, for manual pending orders placed locally or through MoonProto. Effective spread = this value + one-hour market delta × `pending_orders_spread_h_delta`; long and short directions use the normal price adjustment. Strategy pending orders use their own `PendingOrderSpread`. |
| <a id="tradingsection-pending-orders-spread-h-delta"></a>`pending_orders_spread_h_delta` | `f64` | Dimensionless coefficient multiplying the one-hour market delta in the pending-order spread formula. It is not a delta threshold; 0 removes the delta-dependent term. |
| <a id="tradingsection-show-order-comment"></a>`show_order_comment` | `bool` | Show the comment editor in the pending-order dialog. Does not control all strategy labels on charts. |
| <a id="tradingsection-clear-triggers-string"></a>`clear_triggers_string` | `String` | Saved text for the explicit clear-triggers dialog: comma-separated IDs or inclusive ranges, e.g. `1,5-12`. Updating this text alone does not clear triggers; the separate action must run. |

### Market selection and protection

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="tradingsection-auto-start"></a>`auto_start` | [`AutoStartConfig`](01-startup-and-protection.md#autostartconfig) | Kernel startup, working hours, loss stops and recovery settings. See the startup and protection reference. |
| <a id="tradingsection-auto-start-2"></a>`auto_start_2` | [`AutoStartConfig2`](01-startup-and-protection.md#autostartconfig2) | Recovery after delta panic and per-market session-profit options. These are separate from process restart and order-size limits. |
| <a id="tradingsection-coins-black-list-text"></a>`coins_black_list_text` | `String` | Comma-separated global coin blacklist, used with `use_coins_black_list`. Strategy-specific ignore/blacklist rules still apply. Use coin symbols, not one symbol per line. |
| <a id="tradingsection-use-coins-black-list"></a>`use_coins_black_list` | `bool` | Enable `coins_black_list_text` in ordinary entry checks. A strategy may explicitly bypass the global blacklist through its own settings. |
| <a id="tradingsection-dont-buy-delisted"></a>`dont_buy_delisted` | `bool` | Block ordinary signal auto-buy for markets marked as being delisted. The flag relies on the kernel's market status; it does not query the exchange on each click. |
| <a id="tradingsection-dont-buy-new-coins"></a>`dont_buy_new_coins` | `i32` | Block automatic entry for this many minutes after a market was added. 0 disables the restriction. NewListing strategies are exempt; the check adds a 10-second margin. |
| <a id="tradingsection-dont-buy-forward"></a>`dont_buy_forward` | `bool` | Reject trading signals from forwarded Telegram messages. Unrelated to forward contracts or pre-market listings. |
| <a id="tradingsection-use-moon-bl"></a>`use_moon_bl` | `bool` | Respect temporary Moonbot-system market penalties in strategy filtering. Separate from the user's own coin blacklist; does not erase or edit that list. |
| <a id="tradingsection-orders-control"></a>`orders_control` | [`OrdersControl`](03-trading-and-leverage.md#orderscontrol) | Control-bot coordination, unaccounted-position handling and recovery options. The first four fields are legacy mirrors; current WatchDog rows are managed separately. |
| <a id="tradingsection-h-pos-black-list-text"></a>`h_pos_black_list_text` | `String` | Comma-separated coins excluded from hanging-position control. Does not blacklist them from normal trading. The control-bot settings use the same list. |

### Futures leverage and margin

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="tradingsection-auto-manage-lev"></a>`auto_manage_lev` | [`AutoManageLevConfig`](03-trading-and-leverage.md#automanagelevconfig) | Automatic leverage and margin-mode policy. The target-amount expression is stored separately in `auto_lev_control`; see AutoManageLevConfig for dependencies and exchange restrictions. |
| <a id="tradingsection-auto-lev-control"></a>`auto_lev_control` | `String` | Target position-limit amounts for automatic leverage selection, not an enable flag. Example: `1k def 5k BTC*` sets a default target of 1000 and 5000 for matching tickers; K/M suffixes and wildcard ticker masks are supported. Empty text clears targets. Used by `auto_manage_lev`.`auto_max_order`; `auto_lev_up` only permits upward adjustments within that mode. |
| <a id="tradingsection-auto-lower-lev"></a>`auto_lower_lev` | `bool` | Automatically reduce futures leverage after an exchange position-limit condition asks for deleveraging. Independent of `auto_max_order`: chooses the next lower supported step from the kernel's ladder and respects temporary change restrictions. |
| <a id="tradingsection-futures-rules"></a>`futures_rules` | `bool` | Enable the kernel's Binance Futures quantitative-trading checks before strategy orders, including recent order counts and a temporary market block. Applies to Binance Futures variants, not all futures exchanges; does not configure hedge/one-way position mode. |
| <a id="tradingsection-auto-close-zero-pos"></a>`auto_close_zero_pos` | `bool` | For Binance Futures variants, allow correction of a zero-quantity position with negative isolated margin even when its absolute margin deficit is 5 or more. Smaller deficits already enter the correction path with this flag off. Does not close all zero-size records or control normal stop-losses. |

### Exchange connections and data

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="tradingsection-binance-connection"></a>`binance_connection` | `i32` | REST connection-method selector: 0 = Original, 1 = Method 2, 2 = Method 3, 3 = Method 4. Historical name; some exchange engines force a method and startup fallback may change it. Does not choose an exchange or MoonProto transport. |
| <a id="tradingsection-use-websocket-api"></a>`use_websocket_api` | `bool` | Prefer the authenticated WebSocket order API when the exchange engine supports it and its API connection is active. Does not control public market-data subscriptions, and does not remove all REST usage. |
| <a id="tradingsection-use-hl-fast-ioc"></a>`use_hl_fast_ioc` | `bool` | Enable Hyperliquid's paid-priority IOC path for eligible taker actions. An IOC remainder is cancelled rather than left resting in the orderbook; outcome/prediction assets are excluded. This does not make every order IOC and is not a free latency preference. |
| <a id="tradingsection-use-book-ticker"></a>`use_book_ticker` | `bool` | Enable the best-bid/ask WebSocket feed where the engine advertises support. Feed freshness and reconnect logic still apply; it is not a blanket replacement of all REST requests. Moonbot's GUI/startup clears it on single-processor systems. |
| <a id="tradingsection-no-trades-markets-text"></a>`no_trades_markets_text` | `String` | Comma-separated exact tickers excluded from trade-history collection/stream subscription where that path supports the exclusion. Comparison is case-insensitive. Separate from the blacklist for trading signals; this is not a newline-separated signal filter. |
| <a id="tradingsection-trades-gap-time"></a>`trades_gap_time` | `i32` | Adaptive trade-stream silence threshold in milliseconds, used by exchange reconnect checks. The kernel adjusts it as streams go silent/recover; not a minimum interval between the user's trades. Preserve as runtime state. |
| <a id="tradingsection-sell-x2-level"></a>`sell_x2_level` | `i32` | Percent spacing of the order-book analysis bands used for Buy/Sell x2..x4 volumes and PumpQ calculations. It does not double an order's quantity. |
| <a id="tradingsection-exclude-black-list-delta"></a>`exclude_black_list_delta` | `bool` | Exclude user-blacklisted markets from aggregate market/market-average calculations. Does not switch off an individual market's own delta calculation. |
| <a id="tradingsection-m-avg-use-vol-weight"></a>`m_avg_use_vol_weight` | `bool` | Weight markets by their volume in aggregate market-average calculations; false gives equal market weights. Does not select a moving-average indicator on an individual chart. |
| <a id="tradingsection-deltas-by-trades"></a>`deltas_by_trades` | `bool` | Include raw trade-history extrema in the legacy short-window delta calculation. The current average-price/ticker path still runs, including when trades stop; this is not a global switch between trades and the orderbook for every delta. |
| <a id="tradingsection-engine-check-buy"></a>`engine_check_buy` | `bool` | Recheck purchased quantity through the balance when cancellation/order-status checks failed, after market data initialization. Not a routine balance check before every buy; preserve unless this recovery option is intentionally needed. |

### Fees and reporting

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="tradingsection-auto-buy-bnb"></a>`auto_buy_bnb` | `bool` | Automatically replenish the exchange's supported fee token when its balance is low; the historical name is not a guarantee of BNB on every exchange. Disabled in emulator mode. Binance Futures uses a separate BNB purchase/transfer flow requiring the appropriate account mode and API permissions; unsupported engines do not gain this feature from the flag. |
| <a id="tradingsection-auto-buy-bnb-level"></a>`auto_buy_bnb_level` | `f64` | Low-balance threshold in units of the supported fee token, used with `auto_buy_bnb`. Some balance paths also reserve this quantity when the fee token itself is the asset being traded. Not a USD amount or percentage. |
| <a id="tradingsection-auto-buy-bnb-volume"></a>`auto_buy_bnb_volume` | `f64` | Quantity of the supported fee token to buy per replenishment, not the target total balance. Must satisfy that exchange/flow's minimum order value and available funds; Binance Futures additionally checks a minimum purchase value of 10. |
| <a id="tradingsection-moonbot-config"></a>`moonbot_config` | [`MoonBotConfig`](04-orders-reports-and-notifications.md#moonbotconfig) | Telegram reporting mode, batching and margin-management defaults. Telegram sender/account setup is exposed separately through service settings. |
| <a id="tradingsection-report-config"></a>`report_config` | [`ReportConfig`](04-orders-reports-and-notifications.md#reportconfig) | Saved report-window columns, filters and display preferences. Does not change the SDK's report record format. |
| <a id="tradingsection-alert-config"></a>`alert_config` | [`AlertConfig`](04-orders-reports-and-notifications.md#alertconfig) | Manual chart price-alert behavior and sounds. See AlertConfig; these alerts are separate from automatic trading strategies. |
| <a id="tradingsection-transfer-config"></a>`transfer_config` | [`AssetTransferConfig`](04-orders-reports-and-notifications.md#assettransferconfig) | Asset-transfer panel display preferences; changing this record does not execute a transfer. |
| <a id="tradingsection-cashback-settings"></a>`cashback_settings` | [`CashBackSettings`](04-orders-reports-and-notifications.md#cashbacksettings) | Cashback history/panel preferences. Does not enable the exchange's BNB fee discount. |
| <a id="tradingsection-send-shots-config"></a>`send_shots_config` | [`SendShotsConfig`](04-orders-reports-and-notifications.md#sendshotsconfig) | Automatic sharing of trade screenshots and their scale/recipient settings. See SendShotsConfig; Telegram destination configuration is separate. |
| <a id="tradingsection-auto-delete-logs"></a>`auto_delete_logs` | `i32` | Retention for ordinary logs, binary chart records and screenshots, in days. GUI 0..=15; 15 disables routine age cleanup, while low-disk-space cleanup remains independent. 0 does not mean keep forever. |
| <a id="tradingsection-log-level"></a>`log_level` | `i32` | Kernel diagnostic verbosity, 0..=5 in the GUI. Higher values enable more detailed logs; 0 does not suppress all essential messages. Independent of InitConfig.subscribe_logs, which controls delivery to one SDK client. |

### Trust Management

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="tradingsection-tm-panic-sell-closed"></a>`tm_panic_sell_closed` | `bool` | Trust Management master: when its sell completes, send a panic-close command for this market to linked slave bots. Requires the order to participate in MoonFriend forwarding. Unrelated to a MoonProto terminal disconnect. |
| <a id="tradingsection-tm-send-only-share"></a>`tm_send_only_share` | `bool` | For Telegram Trust Management forwarding, send only on explicit Share instead of automatically forwarding new orders. Requires auto-posting enabled. The separate UDP forwarding switch remains independent. |
| <a id="tradingsection-tm-cancel-closed"></a>`tm_cancel_closed` | `bool` | Trust Management master: send a cancel-buy command for the market to linked slave bots when the master's sell completes. Requires MoonFriend forwarding for the order. |
| <a id="tradingsection-tm-cancel-buy-on-fill"></a>`tm_cancel_buy_on_fill` | `bool` | Trust Management master: after its buy fills, send a cancel-buy command to linked slave bots with a five-second delay. |
| <a id="tradingsection-multi-commands"></a>`multi_commands` | `bool` | Permit multiple Telegram commands in one message on the authorized own-channel command path. Does not change MoonProto API batching. |
| <a id="tradingsection-tm-send-first-sell"></a>`tm_send_first_sell` | `bool` | Trust Management master: forward the initial sell price after a successful buy. Does not send every later sell-price change by itself. |
| <a id="tradingsection-tm-sell-if-master-not-filled"></a>`tm_sell_if_master_not_filled` | `bool` | Trust Management master: ask slaves to panic-close when the master's buy is cancelled unfilled or placement fails. On placement failure with this flag off, the master instead requests a commission-based sell target after cancel-buy commands. |
| <a id="tradingsection-tm-max-order"></a>`tm_max_order` | `f64` | Master reference order value for Trust Management sizing. The forwarded percentage is clamped to 1..=100 from actual buy value / this amount × 100; a non-positive amount yields 100%. Does not cap the master's actual order. |

### Chart preferences stored in the trading section

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="tradingsection-fav-markets"></a>`fav_markets` | `String` | Saved favorite coin symbols, comma-separated. Used by favorite-market buttons and lists; does not select the universe of tradable markets. |
| <a id="tradingsection-price-range"></a>`price_range` | `i32` | Chart price-scale preset, not an order-price filter. 1 = automatic; 2/3/4/5/6 select progressively different fixed spans. Normal spot spans are 20/50/100/10/5%; futures spans are 10/20/50/5/2%. `x9_mode` and `scale_plus_index` can replace these spans. |
| <a id="tradingsection-x9-mode"></a>`x9_mode` | `bool` | Wide chart-price scale mode: standard buttons use 100%, 200%, 500%, 1000% and 2000% spans. Does not create a nine-order grid or split orders. |
| <a id="tradingsection-draw-all-buy"></a>`draw_all_buy` | `bool` | Show completed/partially filled buy markers on charts, including historical ones. This controls drawing, not the set of active pending orders. |
| <a id="tradingsection-chart-clean-up-time"></a>`chart_clean_up_time` | `i32` | Inactivity timeout for closing chart windows when `visual.auto_close_charts` is enabled. Normally minutes; 0 means about 10 seconds in a normal build, 60 disables routine closure. API pressure or the chart-count limit can shorten the effective timeout. |
| <a id="tradingsection-chart-split-zones"></a>`chart_split_zones` | `bool` | Separate chart mouse-interaction zones: drawing/order actions are restricted to the appropriate chart or orderbook side. This is interaction behavior, not merely drawing divider lines. |
| <a id="tradingsection-draw-stop"></a>`draw_stop` | `bool` | Draw stop-loss lines and allow their direct mouse interaction on charts. Does not enable or disable the underlying stop itself. |
| <a id="tradingsection-pending-buy-price"></a>`pending_buy_price` | `bool` | Draw an additional dashed execution-price line for pending orders on the Moonbot chart. Does not choose the price used for sell calculations. |
| <a id="tradingsection-spot-config"></a>`spot_config` | [`SpotConfig`](05-charts-and-display.md#spotconfig) | Spot/reference-market overlays and comparisons on the chart. Does not change the account from futures to spot. |
| <a id="tradingsection-arb-view-config"></a>`arb_view_config` | [`ArbViewConfig`](05-charts-and-display.md#arbviewconfig) | Arbitrage chart/table presentation preferences. Actual arbitrage subscriptions and slot configuration are separate from this shared display record. |

### Learned state and inactive fields

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="tradingsection-max-order"></a>`max_order` | `f64` | Historical runtime statistic of maximum observed order size, not an editable maximum-order risk limit. Preserve the kernel value; do not build an order-size limit control from it. |
| <a id="tradingsection-min-balance"></a>`min_balance` | `f64` | Observed minimum account balance shown in the transfer panel. Negative initial value means not initialized; the balance updater replaces it and tracks subsequent lows. Not a minimum reserve that trading must keep. |
| <a id="tradingsection-f-binance-commission"></a>`f_binance_commission` | `f64` | Cached Binance Futures fee multiplier: 1 + fractional fee, e.g. 1.0005 means 0.05%. Updated from observed fills; engine initialization limits it to its default ceiling. Preserve as learned state, not a universal commission percentage input. |
| <a id="tradingsection-bybit-commission"></a>`bybit_commission` | `f64` | Cached Bybit fee multiplier, e.g. 1.001 = 0.1%. The engine accepts saved values strictly between 0.999 and 1.003 and updates them from exchange data/fills. Preserve as learned state. |
| <a id="tradingsection-gate-commission"></a>`gate_commission` | `f64` | Shared cached fee multiplier historically named for Gate; also used by Bitget, OKX and Hyperliquid engines. Values strictly between 0.999 and 1.003 are accepted at initialization; exchange data updates it. Not a plain percent or a Gate-only user setting. |
| <a id="tradingsection-h-pos-black-list-add"></a>`h_pos_black_list_add` | `String` | Derived remainder of `h_pos_black_list_text` for symbols absent from the current market list. Preserve it; edit the full blacklist rather than presenting this as an independent user list. |
| <a id="tradingsection-check-glass"></a>`check_glass` | `bool` | Legacy stored flag without an active order-book check consumer. Preserve it; do not expose it as a working pre-buy protection. |
| <a id="tradingsection-pump-q-level"></a>`pump_q_level` | `i32` | Legacy threshold referenced by the old predictor filter, which has no current callers. Preserve it; do not use it as a general auto-buy quality control. |
| <a id="tradingsection-panic-if-vol-drop"></a>`panic_if_vol_drop` | `bool` | Legacy stored toggle without an active V-Stop consumer. Actual V-Stop enablement belongs to the order; `vol_drop_level` still supplies its global price offset. |
| <a id="tradingsection-order-replace-click-buy"></a>`order_replace_click_buy` | `u8` | Legacy single-order click binding without a current consumer. Current chart movement uses `multi_orders` buy-move bindings; preserve this old field. |
| <a id="tradingsection-order-replace-click-sell"></a>`order_replace_click_sell` | `u8` | Legacy sell-movement mouse binding with no current consumer. Current bindings are in `multi_orders`; preserve this serialized field. |
| <a id="tradingsection-order-set-click"></a>`order_set_click` | `u8` | Legacy mouse binding without a current order-placement consumer. Preserve it; current long-order placement uses `multi_orders`.`buy_set_click`. |
| <a id="tradingsection-buy-pending-spread"></a>`buy_pending_spread` | `i32` | Legacy serialized value with no current consumer. Preserve; use `pending_orders_spread` and the strategy's own pending-order parameters where applicable. |
| <a id="tradingsection-buy-stop-pending-spread"></a>`buy_stop_pending_spread` | `i32` | Legacy serialized value with no current consumer. Preserve it instead of exposing an ineffective editor control. |
| <a id="tradingsection-order-book-levels-ws"></a>`order_book_levels_ws` | `i32` | Legacy GUI depth-selector index, not a number of levels. The current Bybit futures engine fixes its depth at 1000 and no longer consumes this choice. Preserve rather than offer an effective depth control. |
| <a id="tradingsection-unknown-tail"></a>`unknown_tail` | `Vec<u8>` | Opaque bytes added by newer kernels. Preserve unchanged when editing and round-tripping a received configuration; never expose as a setting. |

<a id="automanagelevconfig"></a>

## `trading.auto_manage_lev` — `AutoManageLevConfig`

### How automatic leverage uses a target

With `auto_lev_control="1k def 5k BTC*"`, the default target position limit is 1,000 and the target for matching BTC tickers is 5,000, in the market's trading currency. For USDT markets those amounts are USDT. The amounts describe the capacity required from the exchange risk bracket, not an instruction to place an order of that size.

| Policy | Result |
| :--- | :--- |
| `auto_max_order=true`, `auto_lev_up=false` | Select a bracket that accommodates the target; reduce leverage when needed, without raising it |
| `auto_max_order=true`, `auto_lev_up=true` | Allow both reductions and increases for that target |
| `auto_fix_lev=true`, `fix_lev=10` | Request 10x, within the market's exchange maximum, where target-based management is off or no positive target applies |
| `trading.auto_lower_lev=true` | Allow a separate reduction after an exchange position-limit condition requests it |

The target-based policy requires futures risk-bracket data and excludes inverse contracts. Cross/isolated margin selection has its own switches and remains subject to exchange/account restrictions.

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="automanagelevconfig-auto-max-order"></a>`auto_max_order` | `bool` | Choose leverage from exchange risk brackets so their maximum position size accommodates the amount configured in `trading.auto_lev_control`. Needs loaded leverage/bracket data and a positive effective target for the market; unsupported for inverse-base-currency mode. Lowering is allowed; raising additionally requires `auto_lev_up`. This is not sizing an order from free balance. |
| <a id="automanagelevconfig-auto-lev-up"></a>`auto_lev_up` | `bool` | Allow `auto_max_order` to increase leverage as well as decrease it. Has no independent effect when `auto_max_order` is off or the market has no positive target amount. |
| <a id="automanagelevconfig-fix-lev"></a>`fix_lev` | `i32` | Requested fixed leverage multiplier, GUI integer 1..=500; each market is limited by its exchange maximum. Used by `auto_fix_lev`, including new-listing initialization. It may coexist with `auto_max_order` for markets without an effective target amount. |
| <a id="automanagelevconfig-auto-isolated"></a>`auto_isolated` | `bool` | Automatically request isolated futures margin. Exchange support and account/position restrictions still apply. Mutually exclusive with `auto_cross` in the GUI; if both are received as true, isolated has priority. Uses account-wide mode on engines with a global margin-mode setting, otherwise per-market mode. |
| <a id="automanagelevconfig-tlg-report"></a>`tlg_report` | `bool` | Report successful automatic leverage changes to Telegram. Does not control leverage selection itself or exchange-request logging. |
| <a id="automanagelevconfig-auto-cross"></a>`auto_cross` | `bool` | Automatically request cross futures margin when `auto_isolated` is off. Subject to exchange support and account/position restrictions; mutually exclusive with `auto_isolated` in the GUI. |
| <a id="automanagelevconfig-auto-fix-lev"></a>`auto_fix_lev` | `bool` | Apply `fix_lev` automatically where `auto_max_order` is disabled or has no effective target amount for the market. Exchange maximums and temporary change restrictions remain in force. |

<a id="orderscontrol"></a>

## `trading.orders_control` — `OrdersControl`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="orderscontrol-active"></a>`active` | `bool` | Legacy mirror of a WatchDog row's order-control switch. Current control workers use the separate WatchDog list; editing this field alone does not enable that row. Preserve it and use [the WatchDog API](10-settings-apis.md#watchdog-control-bots-and-unaccounted-positions) or Moonbot Control bot settings. |
| <a id="orderscontrol-min-price"></a>`min_price` | `f64` | Legacy WatchDog row mirror: price distance in percent. The active row cancels a monitored order when its market-price distance is at or below this threshold; 0 skips the distance check. Edit the observer through [the WatchDog API](10-settings-apis.md#watchdog-control-bots-and-unaccounted-positions) or Moonbot Control bot settings. |
| <a id="orderscontrol-max-time"></a>`max_time` | `i32` | Legacy WatchDog row mirror: maximum time since an order update, in seconds; 0 disables this age check. Current workers read the separate WatchDog row. |
| <a id="orderscontrol-h-pos-control"></a>`h_pos_control` | `bool` | Legacy mirror of a WatchDog row's position-control switch. Current position checking uses that row's active_pos flag and requires a paid version. Use [the WatchDog API](10-settings-apis.md#watchdog-control-bots-and-unaccounted-positions) or Moonbot Control bot settings. |
| <a id="orderscontrol-h-pos-report"></a>`h_pos_report` | `bool` | Send Telegram reports when the position controller confirms an unaccounted position. Requires active position control; the repeat interval comes from the kernel system-report interval. |
| <a id="orderscontrol-h-pos-auto-sell"></a>`h_pos_auto_sell` | `bool` | Automatically close positions confirmed as unaccounted by the position controller. Requires active position control; repeated closure attempts for the same market are limited to once per minute. This is a trading action, not merely an alert. |
| <a id="orderscontrol-ignore-replacing-bug"></a>`ignore_replacing_bug` | `bool` | Skip some recovery checks after an uncertain placement/replacement result; a failed classic buy replacement can be marked closed locally. Affects recovery behavior and some exchange-native replacement paths. Do not present as a harmless performance toggle. |
| <a id="orderscontrol-ignore-protection"></a>`ignore_protection` | `i32` | Protection bypass marker: 0 is normal, exactly 1666 activates bypasses in order/strategy protection. Not a numeric severity level. Moonbot requires explicit acknowledgement before setting it; preserve that meaning in an editor. |
| <a id="orderscontrol-sign-orders"></a>`sign_orders` | `bool` | Mark buy orders as belonging to this Moonbot for control-bot coordination; also permits WatchDog keepalives when a destination is configured. Does not enable exchange API cryptographic signing: authentication remains independent. |
| <a id="orderscontrol-liq-control"></a>`liq_control` | `bool` | After a detected futures liquidation, cancel that market's orders and attempt to close remaining positions. It reacts to liquidation detection; it is not a configurable pre-liquidation price-distance stop. |
