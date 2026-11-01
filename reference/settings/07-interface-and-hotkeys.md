# Interface state and hotkeys

[Settings reference](README.md)

These preferences organize Moonbot's windows, market table and manual-trading shortcuts. A shortcut can select a preset or execute an order action; those are different operations. Amount and sell-percentage preset arrays use zero-based indices, while their selected button numbers are **1..6**.

A remote terminal must register its own shortcuts and send the corresponding trading command. Saving these bindings on the kernel does not install a keyboard handler in MoonTerminal or another SDK application.

See [shortcut encoding](#shortcut-encoding-and-scope) and [market-table columns](#market-table-column-order). Field paths are relative to `SharedConfig`.

<a id="uisection"></a>

## `ui` — `UiSection`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="uisection-hide-demo-button"></a>`hide_demo_button` | `bool` | Hide the demo-mode GUI button; does not switch emulation on/off. |
| <a id="uisection-confirm-close"></a>`confirm_close` | `bool` | Ask for confirmation when closing the GUI normally. Update and OS-session shutdown paths can bypass this prompt. |
| <a id="uisection-new-markets-on-top"></a>`new_markets_on_top` | `bool` | Place newly opened/reopened market charts at the top of the chart list. Does not sort exchange listings by listing date. |
| <a id="uisection-coins-sort-order"></a>`coins_sort_order` | `i32` | Market-table sort direction multiplier: +1 or -1. Selected column is `markets_table_config`.`sort_col`. Not a column selector. |
| <a id="uisection-hotkeys-config"></a>`hotkeys_config` | [`HotkeysConfig`](07-interface-and-hotkeys.md#hotkeysconfig) | Saved Moonbot GUI keyboard shortcuts and manual-trading presets. Saving them does not register shortcuts in a remote terminal. |
| <a id="uisection-strat-editor-chapters"></a>`strat_editor_chapters` | `String` | Comma-separated displayed chapter names that were expanded in the strategy editor, not numeric indices. Preserve as GUI state. |
| <a id="uisection-markets-table-config"></a>`markets_table_config` | [`MarketsTableConfig`](07-interface-and-hotkeys.md#marketstableconfig) | Saved column visibility and sort-column selection of the kernel GUI market table. |
| <a id="uisection-main-button-index-1"></a>`main_button_index_1` | `u8` | First configurable toolbar button: 1=Help, 2=Reports, 3=Alerts, 4=Assets/Transfer, 6=BackTest. Other values normalize to Help. |
| <a id="uisection-strat-expanded-state"></a>`strat_expanded_state` | `[bool; 11]` | 11 saved expansion flags for strategy-editor subchapters in construction order. Not one flag per strategy. |
| <a id="uisection-unknown-tail"></a>`unknown_tail` | `Vec<u8>` | Preserve opaque bytes from newer kernels unchanged. |

<a id="hotkeysconfig"></a>

## `ui.hotkeys_config` — `HotkeysConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="hotkeysconfig-filled"></a>`filled` | `bool` | Legacy initialized marker without an active consumer; preserve. |
| <a id="hotkeysconfig-ver"></a>`ver` | `u8` | Stored shortcut-record version; preserve the received value. |
| <a id="hotkeysconfig-o-size"></a>`o_size` | `[f64; 6]` | Six manual order-amount presets in the trading currency. Used by `use_manual_balance`; amounts are not percentages. Array index 0 corresponds to button 1. |
| <a id="hotkeysconfig-b-num"></a>`b_num` | `i32` | Selected amount button, 1..=6 (one-based). Selecting it copies `o_size`[`b_num`-1] to `fixed_trade_balance`. |
| <a id="hotkeysconfig-o-keys"></a>`o_keys` | `[u16; 6]` | Six shortcuts selecting amount presets; require `use_manual_balance`. Each is an encoded shortcut, 0=unassigned. |
| <a id="hotkeysconfig-split-parts"></a>`split_parts` | `u8` | Number of parts for `split_order_x`; GUI accepts 1..=199. Not an iceberg setting. Actual splitting still obeys exchange lot-size rules. |
| <a id="hotkeysconfig-sb-num"></a>`sb_num` | `u8` | Selected sell-price button, 1..=6. The GUI clamps the selection and copies `s_price`[`sb_num`-1] to `fixed_sell_price`. |
| <a id="hotkeysconfig-s-keys"></a>`s_keys` | `[u16; 6]` | Six shortcuts selecting sell-percentage presets; require `fixed_sell_mode`. 0=unassigned. |
| <a id="hotkeysconfig-s-price"></a>`s_price` | `[f32; 6]` | Six sell-offset presets in percent, not absolute prices. The xT mode can multiply the effective value by 10; selecting a button updates `fixed_sell_price`. |
| <a id="hotkeysconfig-cancel-buy"></a>`cancel_buy` | `u16` | Shortcut: Cancel buys on the active full-screen market. 0=unassigned. |
| <a id="hotkeysconfig-panic-sell"></a>`panic_sell` | `u16` | Shortcut: Panic Sell on the active full-screen market. 0=unassigned. |
| <a id="hotkeysconfig-join-sells"></a>`join_sells` | `u16` | Shortcut: Join closing orders on the active full-screen market; the kernel selects the applicable position direction. 0=unassigned. |
| <a id="hotkeysconfig-switch-charts"></a>`switch_charts` | `u16` | Shortcut: Cycle to the next full-screen chart. 0=unassigned. |
| <a id="hotkeysconfig-reload-book"></a>`reload_book` | `u16` | Shortcut: Request order-book reload and refresh active chart TF candles. 0=unassigned. |
| <a id="hotkeysconfig-new-long"></a>`new_long` | `u16` | Shortcut: Trigger a manual long entry for the selected market through the normal signal/order flow. 0=unassigned. |
| <a id="hotkeysconfig-new-short"></a>`new_short` | `u16` | Shortcut: Trigger a manual short entry for the selected market through the normal signal/order flow. 0=unassigned. |
| <a id="hotkeysconfig-split-order"></a>`split_order` | `u16` | Shortcut: Split the largest eligible active closing order on the selected market into three parts. Not the hovered order; unavailable in emulator mode. 0=unassigned. |
| <a id="hotkeysconfig-shift-buy-up"></a>`shift_buy_up` | `u16` | Shortcut: Move buys up on the selected market using the normal group-move step. 0=unassigned. |
| <a id="hotkeysconfig-shift-buy-down"></a>`shift_buy_down` | `u16` | Shortcut: Move buys down on the selected market using the normal group-move step. 0=unassigned. |
| <a id="hotkeysconfig-shift-sell-up"></a>`shift_sell_up` | `u16` | Shortcut: Move closing orders up on the selected market. 0=unassigned. |
| <a id="hotkeysconfig-shift-sell-down"></a>`shift_sell_down` | `u16` | Shortcut: Move closing orders down on the selected market. 0=unassigned. |
| <a id="hotkeysconfig-make-shot"></a>`make_shot` | `u16` | Shortcut: Capture the active report/history chart, otherwise the last full-screen market chart. 0=unassigned. |
| <a id="hotkeysconfig-make-shot-bot"></a>`make_shot_bot` | `u16` | Shortcut: Capture the bot window. 0=unassigned. |
| <a id="hotkeysconfig-reload-chart"></a>`reload_chart` | `u16` | Shortcut: Reload trade history for the selected market. 0=unassigned. |
| <a id="hotkeysconfig-scale-plus"></a>`scale_plus` | `u16` | Shortcut: Increase the displayed price range (zoom out vertically). 0=unassigned. |
| <a id="hotkeysconfig-scale-minus"></a>`scale_minus` | `u16` | Shortcut: Decrease the displayed price range (zoom in vertically). 0=unassigned. |
| <a id="hotkeysconfig-sell-plus"></a>`sell_plus` | `u16` | Shortcut: Increase the sell-offset setting; may update the selected Manual strategy unless `ignore_strat_sell_price` is set. 0=unassigned. |
| <a id="hotkeysconfig-sell-minus"></a>`sell_minus` | `u16` | Shortcut: Decrease the sell-offset setting; same Manual-strategy dependency as `sell_plus`. 0=unassigned. |
| <a id="hotkeysconfig-spy-mode"></a>`spy_mode` | `u16` | Shortcut: Toggle the GUI privacy display mode. 0=unassigned. |
| <a id="hotkeysconfig-show-charts"></a>`show_charts` | `u16` | Shortcut: Toggle chart visibility. 0=unassigned. |
| <a id="hotkeysconfig-split-order-x"></a>`split_order_x` | `u16` | Shortcut: Same largest-order selection as `split_order`, using `split_parts` instead of three. 0=unassigned. |
| <a id="hotkeysconfig-switch-figure"></a>`switch_figure` | `u16` | Shortcut: Cycle drawing tools, skipping tools with `prevent_switch`. 0=unassigned. |
| <a id="hotkeysconfig-fit-sells"></a>`fit_sells` | `u16` | Shortcut: Toggle rectangle-drawing mode for redistributing closing orders within the drawn price zone; not an order-book fit. 0=unassigned. |
| <a id="hotkeysconfig-panic-sell-one"></a>`panic_sell_one` | `u16` | Shortcut: Panic-close one order selected by the kernel on the active market. 0=unassigned. |
| <a id="hotkeysconfig-cancel-all-buys"></a>`cancel_all_buys` | `u16` | Shortcut: Cancel all buys and pending orders in this bot. Distinct from broadcasting cancellation to other bots. 0=unassigned. |
| <a id="hotkeysconfig-broadcast"></a>`broadcast` | `u16` | Shortcut: Broadcast the selected ticker through the local bot-window mechanism. Not a MoonProto thin-client broadcast. 0=unassigned. |

<a id="marketstableconfig"></a>

## `ui.markets_table_config` — `MarketsTableConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="marketstableconfig-sort-col"></a>`sort_col` | `i32` | Zero-based displayed column index; -1 restores market-index order. The current GUI has 28 displayed columns, listed below; not the internal metric ID. |
| <a id="marketstableconfig-col-vis"></a>`col_vis` | `[bool; 41]` | 41 stored visibility flags, indexed by displayed column; only the current 28 columns are consumed. Preserve the remaining slots. |
| <a id="marketstableconfig-col-pos"></a>`col_pos` | `[u8; 41]` | Legacy stored positions without a current layout consumer. Preserve them; editing does not reorder current columns. |

## Shortcut encoding and scope

A `u16` contains a shortcut, not a Unicode character: combine the virtual-key code with Shift=`0x2000`, Ctrl=`0x4000`, Alt=`0x8000` using bitwise OR. Zero means unassigned. For example, Ctrl+F1 is `0x4070`. Arrays are zero-based, but selected button numbers `b_num`/`sb_num` are one-based.

These are Moonbot GUI bindings. The SDK does not listen to the terminal's keyboard. Its editor must translate bindings to its own GUI framework and implement the action separately; saving a binding does not execute a trading command.

## Market-table column order

Current order used by `sort_col` and `col_vis`:

| Index | Column | Index | Column |
| :--- | :--- | :--- | :--- |
| 0 | Market | 14 | 3h.Delta |
| 1 | Vol. | 15 | h.Delta |
| 2 | H.vol | 16 | 15m Delta |
| 3 | 1m vol | 17 | 1m Delta |
| 4 | 3m vol | 18 | Funding |
| 5 | 5m vol | 19 | MarkPrice |
| 6 | ASK | 20 | PumpsCount |
| 7 | H. High | 21 | 72h Delta |
| 8 | Max.Order | 22 | Pump Q |
| 9 | Buy x4 | 23 | Leverage |
| 10 | Buy x2 | 24 | PriceStep |
| 11 | sell x2 | 25 | Orders |
| 12 | sell x4 | 26 | Session |
| 13 | 24h Delta | 27 | MaxPos |

This is saved GUI layout, not the field list of the manual volume/delta refresh response. Do not use these positions as SDK metric IDs.
