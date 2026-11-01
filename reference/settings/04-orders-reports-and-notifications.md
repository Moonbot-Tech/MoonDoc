# Order controls, reports and notifications

[Settings reference](README.md)

Order controls define what clicks, hotkeys and group actions do. Reports and notifications describe the resulting trades. Saving a mouse binding, report filter or transfer-panel preference does not execute the corresponding action.

Report filters and column layouts here belong to the Moonbot GUI. A terminal using MoonProto chooses its own report queries and layout. Automatic screenshots have separate Telegram and public-service destinations; disabling one does not disable the other.

Related: [testing and trade analytics](../../concepts/08-testing-debugging-and-analytics.md), [Telegram and control-bot APIs](10-settings-apis.md). Field paths are relative to `SharedConfig`.

<a id="multiordersconfig"></a>

## `trading.multi_orders` — `MultiOrdersConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="multiordersconfig-ver"></a>`ver` | `u8` | Serialized sub-record version; preserve the received value. Not a user-selectable feature level. |
| <a id="multiordersconfig-use-multi-orders"></a>`use_multi_orders` | `bool` | Obsolete enable byte retained for compatibility: current kernel export writes true and import ignores it. Multi-orders remain available; this is not the current grid-pause control. |
| <a id="multiordersconfig-buy-set-click"></a>`buy_set_click` | `u8` | Mouse action for placing a long entry at the clicked chart price. Use the mouse-action codes below; 0 disables this binding. |
| <a id="multiordersconfig-buy-move-click"></a>`buy_move_click` | `u8` | Primary mouse action for moving long entry orders, using `replace_buy_kind`. If equal to `short_buy_move_click`, the handler selects both directions. |
| <a id="multiordersconfig-sell-move-click"></a>`sell_move_click` | `u8` | Primary mouse action for moving long exit orders, using `replace_sell_kind`. If equal to `short_sell_move_click`, the handler selects both directions. |
| <a id="multiordersconfig-replace-buy-kind"></a>`replace_buy_kind` | `u8` | Primary entry-order selection/movement mode, codes 0..=7 below. Mode 4 uses the largest quantity for entries because no completed-position profit is available. |
| <a id="multiordersconfig-replace-sell-kind"></a>`replace_sell_kind` | `u8` | Primary exit-order selection/movement mode, codes 0..=7 below. Only eligible active orders on the chosen side are affected; click-immune orders are excluded. |
| <a id="multiordersconfig-split-sells"></a>`split_sells` | `i32` | Legacy unused field; does not split current orders. Preserve it. Explicit split actions and strategy split settings are separate. |
| <a id="multiordersconfig-show-orders-num"></a>`show_orders_num` | `bool` | Show the worker/order number alongside order labels on charts. Does not change order count or grouping. |
| <a id="multiordersconfig-kir-style"></a>`kir_style` | `bool` | Unused reserved byte in the current kernel, despite the historical SDK name. Preserve; no current visualization switch is connected to it. |
| <a id="multiordersconfig-fix-pos"></a>`fix_pos` | `u8` | Legacy direction selector replaced by separate long/short mouse bindings. Preserve; current movement direction is selected by matching those bindings. |
| <a id="multiordersconfig-join-sell-kind"></a>`join_sell_kind` | `u8` | Global exit-joining policy: 0 disabled, 1 retain a fixed target price, 2 retain a profit-percentage target. Applies to eligible same-market/same-direction orders; strategy join keys can independently request joining. |
| <a id="multiordersconfig-short-set-click"></a>`short_set_click` | `u8` | Mouse action for placing a short entry at the clicked price. Uses the same codes as `buy_set_click` and still requires a supported short-trading path. |
| <a id="multiordersconfig-pending-short-set-click"></a>`pending_short_set_click` | `u8` | Mouse action for a pending short in the Moonbot GUI; requires futures. GUI pending orders are not available in kernel mode. |
| <a id="multiordersconfig-done-opacity"></a>`done_opacity` | `f32` | Base opacity of completed order lines, 0..=1. Some closed/unfilled lines are faded further by the renderer; not a retention period. |
| <a id="multiordersconfig-buy-move-click-2"></a>`buy_move_click_2` | `u8` | Secondary long-entry movement binding, paired with `replace_buy_kind_2`; same mouse-action codes as the primary binding. |
| <a id="multiordersconfig-sell-move-click-2"></a>`sell_move_click_2` | `u8` | Secondary long-exit movement binding, paired with `replace_sell_kind_2`; same mouse-action codes as the primary binding. |
| <a id="multiordersconfig-replace-buy-kind-2"></a>`replace_buy_kind_2` | `u8` | Selection/movement mode 0..=7 for the secondary entry binding. Same semantics as `replace_buy_kind`. |
| <a id="multiordersconfig-replace-sell-kind-2"></a>`replace_sell_kind_2` | `u8` | Selection/movement mode 0..=7 for the secondary exit binding. Same semantics as `replace_sell_kind`. |
| <a id="multiordersconfig-same-hotkeys-for-move"></a>`same_hotkeys_for_move` | `bool` | GUI preference to copy each long movement binding into its corresponding short binding, for both primary and secondary actions. Does not make primary and secondary actions equal. The runtime compares the actual binding values, so an editor must update them consistently. |
| <a id="multiordersconfig-short-buy-move-click"></a>`short_buy_move_click` | `u8` | Primary short-entry movement binding. Shares `replace_buy_kind`; matching the long binding selects both directions. |
| <a id="multiordersconfig-short-sell-move-click"></a>`short_sell_move_click` | `u8` | Primary short-exit movement binding. Shares `replace_sell_kind`; matching the long binding selects both directions. |
| <a id="multiordersconfig-short-buy-move-click-2"></a>`short_buy_move_click_2` | `u8` | Secondary short-entry movement binding; shares `replace_buy_kind_2`. Matching `buy_move_click_2` selects both directions. |
| <a id="multiordersconfig-short-sell-move-click-2"></a>`short_sell_move_click_2` | `u8` | Secondary short-exit movement binding; shares `replace_sell_kind_2`. Matching `sell_move_click_2` selects both directions. |

<a id="manualstratsconfig"></a>

## `trading.manual_strats_config` — `ManualStratsConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="manualstratsconfig-use-buttons"></a>`use_buttons` | `bool` | Show enabled Manual-strategy quick buttons while `trading.use_manual_strategy` is active. Does not execute a strategy merely by showing it. |
| <a id="manualstratsconfig-hot-keys"></a>`hot_keys` | `[u16; 10]` | Ten GUI shortcuts selecting the corresponding `manual_strats_names` slots. Each is a 16-bit shortcut encoding described in the keyboard chapter; 0 means unassigned. A hidden/disabled slot also disables its action in Moonbot. |
| <a id="manualstratsconfig-show-button"></a>`show_button` | `[bool; 10]` | Ten per-slot enable/visibility flags. In Moonbot these also enable the slot's shortcut action; `use_buttons` controls the overall button strip. |

<a id="reportconfig"></a>

## `trading.report_config` — `ReportConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="reportconfig-fields-vis"></a>`fields_vis` | `[bool; 51]` | 51 saved report-column visibility slots. Current GUI consumes 43 columns, listed below; preserve unused slots. Not a projection for report API requests. Column 11 is synchronized with `trading.use_lev_for_take`. |
| <a id="reportconfig-fields-width"></a>`fields_width` | `[u16; 51]` | Saved widths of the same 51 report-column slots in GUI pixels. Moonbot enforces a minimum of 10 when using them; stretch can redistribute displayed widths. |
| <a id="reportconfig-only-active"></a>`only_active` | `bool` | Legacy field without a current report-filter consumer. Use `active_type` for the Moonbot report UI; API request filters are separate. |
| <a id="reportconfig-range"></a>`range` | `i32` | Legacy saved value without a current consumer. The active report date controls use other core state; this is not the SDK report-query range. |
| <a id="reportconfig-filter1"></a>`filter1` | `[u8; 26]` | First saved report filter, combined with filter2 by AND. Length-prefixed UTF-8: byte 0 is a byte count up to 25, bytes 1..=25 hold text; do not split a UTF-8 character. Accepts a coin, strategy/type text, `manual`, `+` for profit, `-` for loss and recognized type aliases; otherwise searches channel/signal text and, for longer nonnumeric text, sell reason. Empty means no first filter. |
| <a id="reportconfig-filter2"></a>`filter2` | `[u8; 26]` | Second saved report filter; same encoding and matching rules as filter1. Both non-empty filters must match; this is not an alternative OR filter. |
| <a id="reportconfig-filter3"></a>`filter3` | `[u8; 26]` | Unused third legacy filter slot. Preserve its 26 bytes unchanged; current report filtering consumes filter1 and filter2 only. |
| <a id="reportconfig-active-type"></a>`active_type` | `u8` | Report UI selection: 0 all non-deleted records, 1 active non-deleted, 2 closed non-deleted, 3 also include deleted records. Does not select a custom query or delete records. |
| <a id="reportconfig-rep-emulator-orders"></a>`rep_emulator_orders` | `bool` | Choose emulator-only records when true, real-only records when false. It does not merge emulator trades with real ones. |
| <a id="reportconfig-stretch"></a>`stretch` | `bool` | Fit visible report columns to the available GUI width; false uses saved column widths. |
| <a id="reportconfig-only-2-orders"></a>`only_2_orders` | `bool` | In a static saved-trade chart, show the selected trade's buy/sell pair rather than unrelated order lines. Does not aggregate multi-orders into one report row. |
| <a id="reportconfig-use-leverage"></a>`use_leverage` | `bool` | Select the leverage-aware spent-amount basis for report summary percentages. Its effect depends on `trading.use_lev_for_take`; it does not change exchange leverage or stored execution prices. |
| <a id="reportconfig-max-lines"></a>`max_lines` | `u16` | Maximum rows loaded into the Moonbot report grid; the normal setter clamps to 50..=1000. Report totals use a separate query without this row limit. This is not an SDK request page size. |
| <a id="reportconfig-pos-direction"></a>`pos_direction` | `u8` | Report UI direction filter: 0 both, 1 long, 2 short. Does not change order direction. |
| <a id="reportconfig-store-liq"></a>`store_liq` | `bool` | Write detected liquidation events as report records. Not a switch for recording a liquidation-price column in ordinary trades. |
| <a id="reportconfig-store-fund"></a>`store_fund` | `bool` | Write received funding payments as separate report records. The current path excludes inverse-base-currency mode and global emulator mode. Does not merely store a funding-rate indicator. |
| <a id="reportconfig-by-close-date"></a>`by_close_date` | `bool` | Apply the report's date-range filter to closing time instead of buying/opening time. Sorting has separate state; this is not the sort-order switch. |

<a id="moonbotconfig"></a>

## `trading.moonbot_config` — `MoonBotConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="moonbotconfig-silent"></a>`silent` | `bool` | Suppress ordinary trade/signal Telegram messages and image sending while allowing service-message paths. Does not mute Moonbot's local sounds or stop trading. |
| <a id="moonbotconfig-auto-margin-borrow"></a>`auto_margin_borrow` | `bool` | Allow automatic asset borrowing for eligible short orders on a margin-capable engine. The implemented Binance margin path requires the relevant account mode, API permissions and borrowing capacity. Does not borrow funds for ordinary futures leverage. |
| <a id="moonbotconfig-auto-margin-transfer"></a>`auto_margin_transfer` | `bool` | Within automatic margin borrowing, allow transfer of collateral from spot to margin; the borrowing flow can return the transfer on failure. Requires the borrowing path and API permissions. Not an independent wallet-balancing service. |
| <a id="moonbotconfig-group-delay"></a>`group_delay` | `i32` | Batch outgoing Telegram messages over this many milliseconds. Normal command setter clamps to 1000..=5000; the shared-bot path uses at least 3500. The worker polls separately, so this is not a precise delivery deadline. Service messages may bypass batching. |

<a id="alertconfig"></a>

## `trading.alert_config` — `AlertConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="alertconfig-enabled"></a>`enabled` | `bool` | Legacy byte without a current global price-alert consumer. Alert enablement belongs to the individual chart object/strategy; do not expose this as a working master switch. |
| <a id="alertconfig-keep-time"></a>`keep_time` | `i32` | How long a figure/price-alert button remains active, in seconds; GUI 10..=3600. A strategy alert can supply its own KeepAlert instead. |
| <a id="alertconfig-sound-kind"></a>`sound_kind` | `i32` | Sound preset 1..=11 as listed in the signals chapter; 0 plays nothing. Strategy figure alerts can use their own named sound. |
| <a id="alertconfig-repeat-count"></a>`repeat_count` | `i32` | Repeat counter for a figure alert, GUI 1..=10. Repeats are checked at five-second intervals while the alert remains active, in addition to the initial notification; `keep_time` can end them earlier. |

<a id="assettransferconfig"></a>

## `trading.transfer_config` — `AssetTransferConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="assettransferconfig-show-total"></a>`show_total` | `bool` | Show free quantity, total quantity and estimated USD value in each asset row. False shows free quantity only; does not transfer or reserve funds. |
| <a id="assettransferconfig-hide-zero"></a>`hide_zero` | `bool` | Hide an asset only when neither its free nor total quantity is positive. Does not delete the asset or its balance. |
| <a id="assettransferconfig-show-baks"></a>`show_baks` | `bool` | Unused serialized display flag in the current kernel. Preserve; it does not select backup balances or currently toggle USD valuation. |

<a id="cashbacksettings"></a>

## `trading.cashback_settings` — `CashBackSettings`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="cashbacksettings-sep"></a>`sep` | `bool` | Display spot and futures cashback estimates separately instead of their sum. |
| <a id="cashbacksettings-agg-accounts"></a>`agg_accounts` | `bool` | Legacy unused flag; current cashback display has no consumer for it. Preserve rather than promise subaccount aggregation. |
| <a id="cashbacksettings-max-days"></a>`max_days` | `i32` | Period selector, not a literal day count: 0 all stored history, 1 last 90 days, 2 last 30 days, 3 current half-month payout-period selection. Current-day data is included separately. GUI clamps the index to 0..=3. |
| <a id="cashbacksettings-instant-bnb"></a>`instant_bnb` | `bool` | Use the stored at-the-time BNB valuation for cashback estimates. When false, recent records with currency components revalue the BNB component at the current cached BNB price; old/incomplete records fall back to stored totals. Does not buy, sell or convert BNB. |
| <a id="cashbacksettings-hide-info"></a>`hide_info` | `bool` | Hide the cashback information UI. Its visibility is also limited to the supported Binance platforms; does not disable cashback accrual or payment. |

<a id="sendshotsconfig"></a>

## `trading.send_shots_config` — `SendShotsConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="sendshotsconfig-may-send"></a>`may_send` | `bool` | Send qualifying automatic screenshots to the configured personal Telegram destination. Requires an own Telegram bot and non-silent image sending. Public screenshot sending has a separate switch; false does not disable that path. |
| <a id="sendshotsconfig-profit-abs"></a>`profit_abs` | `i32` | Strict profit threshold in USDT for a single-trade screenshot. The absolute-amount and percentage tests are alternatives (OR), not both required. GUI minimum 1; enabled exchange promotion policy can adjust thresholds. |
| <a id="sendshotsconfig-profit-pers"></a>`profit_pers` | `i32` | Strict profit-percentage threshold alternative to `profit_abs`. GUI minimum 1. With `send_negative`, the loss magnitude is tested against the same threshold. |
| <a id="sendshotsconfig-profit-session"></a>`profit_session` | `i32` | Threshold for a market's accumulated hourly-session profit screenshot when the single-trade tests did not qualify. GUI uses at least 50 and at least twice `profit_abs`; server/promotion policy can also affect the session threshold. Not a global account loss limit. |
| <a id="sendshotsconfig-send-negative"></a>`send_negative` | `bool` | Allow single-trade loss screenshots when loss magnitude exceeds `profit_abs` or `profit_pers`. Does not itself enable either delivery destination. |
| <a id="sendshotsconfig-send-to-open-chat"></a>`send_to_open_chat` | `bool` | Legacy unused flag. Current automatic delivery uses the configured Telegram destination, not whichever chat is open in Telegram. |
| <a id="sendshotsconfig-send-public"></a>`send_public` | `bool` | Allow real-trade screenshots to be sent to the Moonbot public screenshot service. Independent of `may_send`; emulator screenshots are excluded from this automatic public path. Some enabled exchange promotion modes force public sending. |
| <a id="sendshotsconfig-time-scale"></a>`time_scale` | `i32` | Screenshot history expansion percentage, GUI 100..=400. Values above 120 activate the volatility-aware expansion logic; not a fixed number of seconds. |
| <a id="sendshotsconfig-price-scale"></a>`price_scale` | `i32` | Optional price-span percentage for automatic screenshots, GUI 0..=100; 0 leaves automatic scale. Positive values only widen the already selected range when the new bounds contain it. |

## Mouse-action codes

Click-binding fields use: 0=none; 1=double left; 2=Ctrl+left; 3=Shift+left; 4=Alt+left; 5=middle; 6=Ctrl+middle; 7=Shift+middle; 8=Alt+middle; 9=double right; 10=Ctrl+right; 11=Shift+right; 12=Alt+right; 13=Ctrl+double left; 14=Shift+double left; 15=Alt+double left.

Group-move modes: 0=none; 1=shift the group; 2=largest order; 3=smallest order; 4=highest current profit (largest size for buys); 5=all to one price; 6=last created; 7=last moved.

These configure Moonbot GUI handlers. An SDK terminal binds its own input to action APIs.

## Reports and notifications

`ReportConfig` stores the report presentation. SDK report-request filters and columns have their own contract; GUI settings are not automatically applied to requests. Column visibility/width refers to the Moonbot table, not an arbitrary terminal table.

Trade screenshots, system notifications and observers have separate switches. Outgoing Telegram-bot settings and active WatchDog rows have [dedicated SDK APIs](10-settings-apis.md); enable remote controls only when the connected core advertises support.

## Report-column slots

Current GUI columns for fields_vis/fields_width. Slots 43..50 are reserved; preserve them. These are display labels, not SDK report-field IDs.

| Index | Column |
| :--- | :--- |
| 0 | `Coin` |
| 1 | `BuyDate` |
| 2 | `CloseDate` |
| 3 | `Quantity` |
| 4 | `BuyPrice` |
| 5 | `SellPrice` |
| 6 | `SpentBTC` |
| 7 | `GainedBTC` |
| 8 | `ProfitBTC` |
| 9 | `ProfitUSDT` |
| 10 | `Profit` |
| 11 | `ProfitAbs` |
| 12 | `Lev` |
| 13 | `Source` |
| 14 | `ChannelName` |
| 15 | `Comment` |
| 16 | `SignalType` |
| 17 | `SellReason` |
| 18 | `Status` |
| 19 | `dBTC` |
| 20 | `dBTC24` |
| 21 | `dMarket` |
| 22 | `dM24` |
| 23 | `bvsv` |
| 24 | `dBTC5m` |
| 25 | `Pump1H` |
| 26 | `Dump1H` |
| 27 | `d24h` |
| 28 | `d3h` |
| 29 | `d1h` |
| 30 | `d15m` |
| 31 | `d5m` |
| 32 | `d1m` |
| 33 | `dBTC1m` |
| 34 | `PriceBug` |
| 35 | `Vd1m` |
| 36 | `H. Vol` |
| 37 | `HVolFast` |
| 38 | `D. Vol` |
| 39 | `LagTP` |
| 40 | `da1m` |
| 41 | `d5s` |
| 42 | `dmark` |
