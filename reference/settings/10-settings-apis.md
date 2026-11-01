# Choosing the settings API

[Settings reference](README.md)

Use the interface that owns the setting. A saved preference, a live runtime switch and a one-time order command are different operations.

| What you need to change | API |
| :--- | :--- |
| Portable trading and interface preferences | `client.settings().build_shared_config()` → `send_shared_config()` |
| Frequently updated controls exposed by compact settings | `client.settings().send(...)`; review the path differences below |
| Automatic leverage policy | `client.settings().manage_leverage(...)` |
| A market's leverage now | `client.account().set_leverage(...)` |
| Telegram reader, account and proxy | `client.telegram()` |
| Active control-bot observers | Moonbot Control bot settings; SDK management is not yet public |
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

Use `client.telegram()` and its `state()` snapshot to control the reader on the kernel's machine.

| Setting | API and meaning |
| :--- | :--- |
| Reader enabled | `set_enabled(bool)`. Disabling does not log out the Telegram account |
| Proxy | `set_proxy(TelegramProxy::None / Socks5 / MtProto)`. SOCKS5 takes host, port, user and password; MTProto takes host, port and secret. This replaces the proxy configuration; an empty password does not preserve the previous one |
| Login | Follow `service.auth_state` through phone/QR, code and 2FA steps. These are actions; do not replay them automatically after reconnect |

Remote login requires `state_supported`, a live service and the matching authentication step. The Telegram account and active service proxy are shared by Moonbot instances on the machine; logging out affects them together. Saved proxy preferences can differ from the service's active proxy.

The outgoing notification bot and channel binding are separate from the reader. **Their management API is not yet in the public MoonProto SDK**; configure them in Moonbot. See the [SDK Telegram workflow](https://github.com/Moonbot-Tech/MoonProto/blob/main/docs/telegram.md) for available methods and events.

## WatchDog: control bots and unaccounted positions

Configure active observers in Moonbot's **Control bot settings**. The [OrdersControl fields](03-trading-and-leverage.md#orderscontrol) include order ownership markers, reports and the response to unaccounted positions. Their first four legacy mirror fields do not configure the active observer list.

**Observer management is not yet exposed by the public MoonProto SDK.** A settings panel can edit the documented SharedConfig preferences, but must not present those legacy fields as a working observer editor. The observer-management API and its request/result handling will be documented here when published.

For the trading role and deployment, see [the kernel, VPS and control bot](../../concepts/07-kernel-vps-and-infrastructure.md).

## Settings belonging to the SDK itself

`ClientConfig`, `ConnectConfig`, `InitConfig`, `RefreshConfig`, `MarketHistorySizing` and Compact mode configure the **client's** connection, subscriptions, waits and storage. They are not kernel settings. For example, `subscribe_logs=false` stops log delivery to this client, while `trading.log_level` controls core diagnostics. The local blacklist exclusion for `markets().global_deltas()` likewise does not change the kernel's calculation rule.

Contracts: [SDK connection](https://github.com/Moonbot-Tech/MoonProto/blob/main/docs/client.md), [lifecycle](https://github.com/Moonbot-Tech/MoonProto/blob/main/docs/lifecycle.md), [UI settings](https://github.com/Moonbot-Tech/MoonProto/blob/main/docs/ui.md). Individual strategy parameters have a separate [strategy reference](../params/README.md).
