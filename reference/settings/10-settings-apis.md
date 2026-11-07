# Choosing the settings API

[Settings reference](README.md)

Use the interface that owns the setting. A saved preference, a live runtime switch and a one-time order command are different operations.

| What you need to change | API |
| :--- | :--- |
| Portable trading and interface preferences | `client.settings().build_shared_config()` → `send_shared_config()` |
| Frequently updated controls exposed by compact settings | `client.settings().send(...)`; review the path differences below |
| Automatic leverage policy | `client.settings().manage_leverage(...)` |
| A market's leverage now | `client.account().set_leverage(...)` |
| Telegram reader, account, proxy and outgoing bot | `client.telegram()` |
| Active control-bot observers | `client.watchdogs()` |
| Client connection, subscriptions and storage | SDK configuration; not SharedConfig |

Field meanings: [trading and leverage](03-trading-and-leverage.md), [startup and protection](01-startup-and-protection.md).

## Shared configuration: read, edit, send, verify

`client.settings().build_shared_config()` builds an editable copy of received configuration. It returns `StateUnavailable` until the first full snapshot; `Ready` alone does not guarantee that snapshot. The SDK requests it in the background and retries every five seconds until received.

```rust
let mut config = client.settings().build_shared_config()?;
config.trading.auto_start.auto_stop_on_ping = true;
config.trading.auto_start.ping_level = 500;
client.settings().send_shared_config(&config)?;
```

Here, 500 means milliseconds of exchange-response timing at the kernel. After sending, wait for `SettingsEvent::SharedConfigUpdated` and check the returned value. Successful enqueue is not application confirmation. An update event can also reflect another terminal's edit; it is not a request-ID acknowledgement.

The API sends a **complete snapshot**. Editing an old copy can overwrite concurrent changes: obtain a fresh base before applying and transfer only the user's edits into it. Shared configuration has no compare-and-save revision check. `build_shared_config()` overlays newer compact/leverage settings onto the retained full snapshot, but does not eliminate races between editors.

Preserve unknown section tails and all unedited values. Kernel import is not a rollback transaction: sections are applied sequentially, and a later failure does not undo earlier changes. Use SDK serialization. If the expected state does not arrive, request it with `refresh_shared_config()` and compare the fields you changed; a rejected import is not a rollback guarantee. Successful import refreshes related lists/GUI state, broadcasts snapshots and saves configuration; it does not promise an immediate reconnect of every external service.

For a partial JSON edit, use `SharedConfig::patch_json` with only the fields to change; arrays are replaced whole. Omitted fields retain their stored values, including nonfinite floats. Do not build a replacement snapshot from `json_values()`: it represents nonfinite floats as `null` and omits opaque future data. A numeric field cannot be cleared by sending `null`. Nonfinite replacements and values that overflow the destination type (for example, `1e100` for a 32-bit float) are rejected without changing the original snapshot. The returned patch is still local: send it and verify the kernel's returned values as above.

## Compact settings and leverage

`snapshot().settings().client_settings` contains `ClientSettingsCommand`. Clone a received snapshot, edit the required field/typed view, then call `client.settings().send(settings)`. This is also a snapshot, not a single-field patch.

Most fields map to `SharedConfig.trading` with the same units. Exceptions and additional views:

| Compact field/API | Mapping and meaning |
| :--- | :--- |
| `x_tmode` | `trading.x_t_mode` |
| `auto_start_config()` / `auto_start_config2()` | [Auto-start settings](01-startup-and-protection.md); use update methods and retain other values |
| `btc_higher_than`, `btc_lower_than`, `market_higher_than` | Correspond to the `*_then` spelling in shared configuration |
| `fixed_sell_presets()` / `selected_fixed_sell_slot()` | `ui.hotkeys_config.s_price` / `sb_num`; slot 1..6 |
| `effective_take_profit_percent()` | Computes the effective percentage including fixed presets, xT and scalp mode; `set_main_take_profit_percent()` / `set_scalp_take_profit_percent()` accept percentages rather than storage units |
| `join_sell_mode()` | `trading.multi_orders.join_sell_kind`: none / fixed price / fixed profit |
| `sign_orders` | Mirror of `trading.orders_control.sign_orders`, the order-owner marking flag. The current kernel compact handler does not assign it; edit through SharedConfig |
| `manual_strategy_id` | Strategy-instance ID; SharedConfig stores the name. `build_shared_config()` does not resolve IDs into names automatically |
| `emu_mode` | Kernel emulator; absent from portable SharedConfig |
| `temp_blacklist_entries()` | Temporary blacklist; `remaining_duration()` returns its duration, `set_temp_blacklist_entries()` accepts `Duration`. Runtime state, not the persistent blacklist |
| `arb_config` | Selected arbitrage platforms and five display flags |

The current kernel has a compact-path rule: after applying it, the server forces `auto_start`, `auto_detect_on`, `strategies_on` to true and `remember_state` to false. Use full SharedConfig to edit those persisted settings. A typed view does not guarantee identical behavior of the two sending paths.

`client.settings().manage_leverage(&LevManage)` sends `auto_max_order`, `auto_lev_up`, `auto_isolated`, `auto_cross`, `auto_fix_lev`, `fix_lev`, `tlg_report` and `lev_control`. Meanings match the [leverage settings](03-trading-and-leverage.md); `lev_control` maps to `trading.auto_lev_control`. A one-time leverage change for a market is the separate `client.account().set_leverage(...)` action, not a change to automatic policy.

## Arbitrage platforms

`ArbConfigCompact::set_wanted(ArbPlatformCode, bool)` selects platform reception/display; `is_wanted()` and `wanted_platforms()` read the selection. Use SDK platform codes rather than UI row positions. Selection does not start an arbitrage trading strategy or purchase a subscription.

`show_absolute`, `show_numbers`, `show_lines`, `show_percent` and `show_right` have the meanings of [ArbViewConfig](05-charts-and-display.md#arbviewconfig-show-absolute). Portable SharedConfig contains these display flags but not the platform-selection mask. Colors are in [ArbColors](08-theme-and-ini.md).

## Telegram on the kernel

The Telegram reader and outgoing bot are separate components. Use `client.telegram()` and its `state()` snapshot. This controls the service on the kernel's machine, not a local Telegram client in the terminal.

| Setting | API and meaning |
| :--- | :--- |
| Reader enabled | `set_enabled(bool)`. Disabling does not log out the Telegram account |
| Proxy | `set_proxy(TelegramProxy::None / Socks5 / MtProto)`. SOCKS5: host, port, user, password; MTProto: host, port, secret. Complete replacement: an empty password does not preserve the previous one. Password/secret is never returned |
| Own outgoing bot | `set_outgoing_bot(own_bot, token)`. `None` preserves the token, `Some("")` clears it. State exposes only `token_set` |
| Channel binding | `generate_channel_pin()`, then the user sends the PIN to the intended channel; `channel_id`/`channel_name` describe the binding. `reset_channel()` clears it |
| Login | Phone/QR, code, 2FA and other steps follow `service.auth_state`. These are actions, not SharedConfig fields; never replay automatically after reconnect |

Availability: outgoing settings require Moonbot 7.72 L6 with service-settings support and `settings_supported=true` in the received snapshot. Earlier builds do not expose these controls. Remote login requires `state_supported`, a live service and the current authentication step. Saved proxy fields (`proxy_type`: 0=none, 1=SOCKS5, 2=MTProto) can differ from the actual `service.proxy`. The Telegram account and active service proxy are shared by bots on the machine; logout affects them, not just the selected core.

Outgoing-bot and channel operations return a request ID: match `ServiceSettingsApplied.request_id`. `applied=true` with a nonempty `error` means the change is active in memory but saving failed. Login/proxy actions are observed through state, not this result ID. Full workflow: [SDK Telegram documentation](https://github.com/Moonbot-Tech/MoonProto/blob/main/docs/telegram.md).

## WatchDog: control bots and unaccounted positions

Use `client.watchdogs().state()`, `refresh()`, `state.edit()`, `apply(&settings)` and `remove(id)`. This requires Moonbot 7.72 L6 with service-settings support; on older cores the snapshot stays unavailable. Disable edits while disconnected and obtain a fresh snapshot after reconnect. The first four legacy `OrdersControl` fields do not replace this API.

| Field | Meaning |
| :--- | :--- |
| `server_ip` | Observer-server IPv4 to which this bot sends information; empty/0.0.0.0 disables the destination. Not an exchange API endpoint |
| `sign_orders` | Mark orders to identify their owning bot; also required for sending information to the observer server |
| `report` | Telegram notifications about confirmed unaccounted positions |
| `auto_sell` | Automatically close confirmed unaccounted positions; requires position control |
| `blacklist` | Position-control exclusions, as in `trading.h_pos_black_list_text` |
| `entries[].id` | Opaque identity in the current kernel session; empty adds an observer. Obtain fresh IDs after reconnect |
| `name` | Observed-account label |
| `api_key`, `api_secret` | `None` preserves the stored credential; a supplied string replaces it. Empty/too-short keys are rejected. Changing keys reconnects only that observer |
| `rsa` | Signature type of the observed account's keys |
| `orders` | Control buys by distance from market price and time without an update |
| `price` | Nonnegative percentage: a buy becomes a cancellation candidate when distance from current price is **at most** the threshold. Zero disables this check |
| `time` | Nonnegative seconds without an update to the tracked order; reaching the threshold makes it a cancellation candidate. Zero disables age checking |
| `positions` | Control unaccounted positions; requires core support and license |
| `ip` | Cancel related buys after losing the observed bots' heartbeat. Not exchange API-key IP verification |

`available` indicates a controller, `supported` core/platform support, and `can_edit` the observer-editing license. Sender address is independent. Row statuses are Added, Error, Ready, Checking and Removing; the snapshot also has error, online bot count, duplicate flag and addition date. These are read-only state, not editable settings.

Entries omitted from `apply` are **retained**; deletion is explicit. Full credentials are never returned. Observe `ServiceSettingsApplied` as for Telegram; after a save failure use the returned IDs so retrying does not add duplicates. `cancel_buys()` is a separate action, whose acknowledgement does not confirm exchange execution. More: [SDK WatchDog documentation](https://github.com/Moonbot-Tech/MoonProto/blob/main/docs/watchdogs.md).

`refresh()` returns the full state in the matching `ServiceSettingsApplied` result, action `get`. A separate `WatchDogsUpdated` event is not required. Both paths update the retained snapshot, and delayed replies cannot roll it back to an older revision.

For the trading role and deployment, see [the kernel, VPS and control bot](../../concepts/07-kernel-vps-and-infrastructure.md).

## Settings belonging to the SDK itself

`ClientConfig`, `ConnectConfig`, `InitConfig`, `RefreshConfig`, `MarketHistorySizing` and Compact mode configure the **client's** connection, subscriptions, waits and storage. They are not kernel settings. For example, `subscribe_logs=false` stops log delivery to this client, while `trading.log_level` controls core diagnostics. The local blacklist exclusion for `markets().global_deltas()` likewise does not change the kernel's calculation rule.

Contracts: [SDK connection](https://github.com/Moonbot-Tech/MoonProto/blob/main/docs/client.md), [lifecycle](https://github.com/Moonbot-Tech/MoonProto/blob/main/docs/lifecycle.md), [UI settings](https://github.com/Moonbot-Tech/MoonProto/blob/main/docs/ui.md). Individual strategy parameters have a separate [strategy reference](../params/README.md).
