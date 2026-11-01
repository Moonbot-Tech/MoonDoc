# Startup, loss stops and automatic recovery

[Settings reference](README.md)

Loss limits, exchange errors, slow responses and working hours can stop new trading. A stop cancels buys; closing existing positions is a separate choice. Global BTC/market-delta panic also closes positions.

Automatic recovery resumes monitoring and the configured detection/strategies. It does not restart the kernel process. Recovery delays are in **minutes**; `ping_level` is the kernel's exchange-response timing in **milliseconds**. Working hours use the kernel machine's local clock.

For example, `auto_stop_on_ping=true`, `ping_level=500`, `restart_after_ping=true` and `restart_ping_time=2` stop trading above 500 ms and allow recovery after two minutes within the threshold, subject to working hours. With `sell_all_on_ping=false`, existing positions continue through their normal exit management. This illustrates the units and dependencies, not a recommended trading preset.

The trade-count and hourly loss limits are independent. The trade-count check compares recent completed-trade results with the latest report records after the profit-counter reset and uses the worse result. The hourly check selects records by **opening time**, also respecting the reset boundary; neither is simply the account's current floating PnL.

Related: [position management and stops](../../concepts/06-orders-exits-and-stops-cascade.md), [editing settings through MoonProto](10-settings-apis.md). Field paths are relative to `SharedConfig`.

<a id="autostartconfig"></a>

## `trading.auto_start` — `AutoStartConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="autostartconfig-auto-start"></a>`auto_start` | `bool` | Start market monitoring automatically after startup analysis completes. Startup preference; changing it does not start the running kernel immediately. |
| <a id="autostartconfig-auto-detect-on"></a>`auto_detect_on` | `bool` | Enable detection when auto-start or an automatic recovery starts monitoring. With `remember_state`, this value is saved from the last running state. |
| <a id="autostartconfig-strategies-on"></a>`strategies_on` | `bool` | Start checked strategies on auto-start or automatic recovery. With `remember_state`, the kernel remembers whether any strategy was active. |
| <a id="autostartconfig-work-time"></a>`work_time` | `bool` | Restrict monitoring and strategies to `work_time_from`..`work_time_to` in the kernel machine's local time. Outside the window, stop strategies and cancel buys; existing sell positions remain managed. A window crossing midnight is supported. |
| <a id="autostartconfig-auto-stop-if-loss"></a>`auto_stop_if_loss` | `bool` | Stop monitoring, detection and strategies and cancel buys when the trade-count loss check exceeds `auto_stop_loss`. Uses the worse of recent completed-trade results and report-record results, with at least `stop_trades` records in either count. See the loss-window explanation above; `sell_if_loss` also closes positions. |
| <a id="autostartconfig-remember-state"></a>`remember_state` | `bool` | Remember monitoring, detection and strategy running state for the next startup. Overrides manual choices of `auto_start`, `auto_detect_on` and `strategies_on` as the running state changes. |
| <a id="autostartconfig-sell-if-loss"></a>`sell_if_loss` | `bool` | Also close all positions when either loss stop is triggered. Has no effect by itself without `auto_stop_if_loss` or `auto_stop_if_loss_hours`. |
| <a id="autostartconfig-dont-wait-sells"></a>`dont_wait_sells` | `bool` | Allow automatic update without waiting for all sell positions to finish. Applies to `auto_update`; this is not a general rule for stopping trading. |
| <a id="autostartconfig-auto-stop-loss"></a>`auto_stop_loss` | `f64` | Positive loss amount in the trading currency for the last `stop_trades` trades. GUI stores the absolute value. Used only by `auto_stop_if_loss`. |
| <a id="autostartconfig-panic-btc"></a>`panic_btc` | `bool` | Stop monitoring, cancel buys and close positions when the one-hour BTC delta is below `panic_btc_delta` or above `panic_btc_delta_up`. Recovery is configured in `auto_start_2`. |
| <a id="autostartconfig-panic-market"></a>`panic_market` | `bool` | Stop monitoring, cancel buys and close positions when the one-hour average market delta is below `panic_market_delta`. Recovery is configured in `auto_start_2`. |
| <a id="autostartconfig-auto-stop-if-loss-hours"></a>`auto_stop_if_loss_hours` | `bool` | Enable the separate loss stop for trades opened within `stop_hours`, after the profit counter's reset point. Requires at least `stop_hours_trades` records; compares loss with `auto_stop_hours_val`. |
| <a id="autostartconfig-auto-update"></a>`auto_update` | `bool` | Automatically install an available kernel update. Normally waits for sell positions to finish; `dont_wait_sells` removes that wait. |
| <a id="autostartconfig-restart-after-err"></a>`restart_after_err` | `bool` | Resume trading after an error stop once the error level has stayed below `errors_level` for `restart_err_time` minutes. This resumes monitoring and configured detection/strategies; it does not restart the process. |
| <a id="autostartconfig-restart-after-ping"></a>`restart_after_ping` | `bool` | Resume trading after a latency stop once latency has stayed at or below `ping_level` for `restart_ping_time` minutes, within working hours. Does not restart the process. |
| <a id="autostartconfig-ignore-emulator"></a>`ignore_emulator` | `bool` | Exclude emulator trades from both loss-stop calculations. Does not switch the kernel out of emulator mode. |
| <a id="autostartconfig-stop-trades"></a>`stop_trades` | `i32` | Length of the trade-count loss window. GUI minimum 1. The kernel compares the recent completed-trade buffer with the latest report records after the profit-counter reset; either count can satisfy the minimum. |
| <a id="autostartconfig-restart-err-time"></a>`restart_err_time` | `i32` | Error-free waiting period before automatic recovery, in minutes. GUI minimum 3; only used with `restart_after_err`. |
| <a id="autostartconfig-panic-btc-delta"></a>`panic_btc_delta` | `f64` | Lower one-hour BTC delta threshold in percent. GUI stores a non-positive value; `panic_btc` triggers strictly below it. |
| <a id="autostartconfig-panic-market-delta"></a>`panic_market_delta` | `f64` | Lower one-hour average market delta threshold in percent. GUI stores a non-positive value; `panic_market` triggers strictly below it. |
| <a id="autostartconfig-auto-stop-on-errors"></a>`auto_stop_on_errors` | `bool` | Stop monitoring and strategies and cancel buys when the kernel's smoothed API-error score reaches `errors_level`. `sell_all_on_errors` additionally closes positions. |
| <a id="autostartconfig-auto-stop-on-ping"></a>`auto_stop_on_ping` | `bool` | Stop monitoring and strategies and cancel buys when the kernel's smoothed exchange-response timing exceeds `ping_level`. This does not measure MoonProto client-to-kernel RTT. |
| <a id="autostartconfig-sell-all-on-errors"></a>`sell_all_on_errors` | `bool` | Close positions as well as canceling buys when `auto_stop_on_errors` triggers. Depends on that stop being enabled. |
| <a id="autostartconfig-sell-all-on-ping"></a>`sell_all_on_ping` | `bool` | Close positions as well as canceling buys when `auto_stop_on_ping` triggers. Depends on that stop being enabled. |
| <a id="autostartconfig-errors-level"></a>`errors_level` | `i32` | Threshold for the smoothed API-error score, not an error count. GUI range 1..=5; the stop triggers at score >= threshold. |
| <a id="autostartconfig-ping-level"></a>`ping_level` | `i32` | Exchange-response timing threshold in milliseconds. GUI range 100..=2000; the stop triggers strictly above it. Not a 1..=5 level and not MoonProto RTT. |
| <a id="autostartconfig-restart-ping-time"></a>`restart_ping_time` | `i32` | Normal-latency waiting period before automatic recovery, in minutes. GUI minimum 1; only used with `restart_after_ping`. |
| <a id="autostartconfig-auto-stop-hours-val"></a>`auto_stop_hours_val` | `f64` | Positive loss amount in the trading currency for the hourly loss window. Used with `auto_stop_if_loss_hours`, `stop_hours` and `stop_hours_trades`. |
| <a id="autostartconfig-stop-hours"></a>`stop_hours` | `i32` | Length of the loss lookback window in hours. GUI minimum 1. Trades are selected by opening time and the last counter-reset boundary. |
| <a id="autostartconfig-stop-hours-trades"></a>`stop_hours_trades` | `i32` | Minimum number of trades before the hourly loss stop can trigger. GUI minimum 0; 0 adds no trade-count requirement. |
| <a id="autostartconfig-panic-btc-delta-up"></a>`panic_btc_delta_up` | `f64` | Upper one-hour BTC delta threshold in percent. GUI stores a non-negative value; `panic_btc` triggers strictly above it. |
| <a id="autostartconfig-work-time-from"></a>`work_time_from` | `f64` | Work-window start as a fraction of a day in the kernel's local time: 0 = midnight, 0.5 = noon. GUI precision is one minute. Used with `work_time`. |
| <a id="autostartconfig-work-time-to"></a>`work_time_to` | `f64` | Work-window end as a fraction of a day in the kernel's local time, in [0, 1). A start later than the end means an overnight window. Boundaries are strict; equal endpoints do not mean an empty window. |

<a id="autostartconfig2"></a>

## `trading.auto_start_2` — `AutoStartConfig2`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="autostartconfig2-restart-on-market"></a>`restart_on_market` | `bool` | Resume after the global delta panic when the one-hour BTC delta is between `btc_higher_then` and `btc_lower_then` and the one-hour market delta exceeds `market_higher_then`. Working-hour restrictions still apply. |
| <a id="autostartconfig2-btc-higher-then"></a>`btc_higher_then` | `f64` | Lower one-hour BTC delta bound for recovery, in percent. Requires `restart_on_market`; the comparison is strict. GUI stores a non-positive value. |
| <a id="autostartconfig2-btc-lower-then"></a>`btc_lower_then` | `f64` | Upper one-hour BTC delta bound for recovery, in percent. Requires `restart_on_market`; the comparison is strict. GUI stores a non-negative value. |
| <a id="autostartconfig2-market-higher-then"></a>`market_higher_then` | `f64` | Lower one-hour average market delta bound for recovery, in percent. Requires `restart_on_market`; the comparison is strict. GUI stores a non-positive value. |
| <a id="autostartconfig2-show-old-listing"></a>`show_old_listing` | `bool` | Gate market-list option: allow markets that have price and volume data even if present in the unavailable/delisted-market list. Does not enable trading on a closed exchange market; this is not a generic notification toggle. |
| <a id="autostartconfig2-reset-session"></a>`reset_session` | `bool` | Reset each market's session profit after `rs_hours` without a completed trade on that market. This is an inactivity timeout, not a global periodic reset. |
| <a id="autostartconfig2-max-session-cap"></a>`max_session_cap` | `i32` | Upper cap on accumulated per-market session profit in USD equivalent. 0 disables the cap. Does not limit orders, account balance or loss; applied when a trade completes. |
| <a id="autostartconfig2-rs-hours"></a>`rs_hours` | `i32` | Inactivity timeout in hours for `reset_session`. GUI minimum 1; read the connected kernel's value rather than using the offline default as a UI preset. |
