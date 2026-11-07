# Using MoonStation MCP with an AI assistant

MoonStation collects reports and maintains connections to MoonBot trading cores. Its MCP interface lets an authorized AI read those connections and request specific changes through ActiveLib MoonProto. Telegram is a separate feature and is not required.

This guide describes the Station MCP tools. Read the tool catalog exposed by the connected Station: an older installation may not provide all of them. Documentation describes meaning; live core snapshots and schemas describe the connected account.

## Overview

Start with `station_overview`. It lists only the cores authorized for this AI client, their connection state, trading state and report synchronization. A core ID identifies a configured core on this Station; a strategy ID and an order UID are local to that core.

Core, strategy and order identities are decimal strings in MCP. Copy them exactly; do not convert them to JavaScript numbers, which can round a 64-bit identifier. Strategy-kind ordinals, counters and timestamps remain numeric.

Keep these states separate:

| Fact | What it establishes |
| :--- | :--- |
| Connection is ready | The Station has a working MoonProto session; individual snapshots may still be loading |
| Runtime started | The kernel's runtime is started |
| Autodetect enabled | The detect subsystem is enabled; this alone does not prove a strategy can enter |
| Strategies running | The strategy engine is running; individual checkboxes, filters and trading conditions still apply |
| Strategy checked | The strategy is selected; this is not an execution report |
| Submitted operation | A command entered a queue; this is not an exchange fill |

Use `core_state` for account data, orders and runtime facts, `strategy_read` for an exact strategy, and `reports_query` for replicated historical trades. Report synchronization, missing clock offsets, missing currency conversion and stale state must remain visible in the answer.

Use `core_state` with `section=positions` for exact per-market position quantities, entries and both hedge legs. A zero one-way size does not rule out simultaneous long and short positions. Balance rows and their USDT valuations are a separate view.

For "what is happening now?", first give the observable state. If the question requires a cause, collect a bounded log observation and follow [Diagnosis](#diagnosis). No trades in a short interval does not establish a failure.

Knowledge tools read the public MoonDoc snapshot stored on the Station. Answers carry its commit, last check time and any refresh failure. A failed refresh keeps the previous complete snapshot. Current facts come from the user's Station, not from MoonDoc.

## Commands

Every mutation uses `action_preview` followed by `action_apply`. The preview contains the core, concrete change, relevant current state and a short-lived preview ID. Explain the resulting behavior and use the user's actual authorization; reading a strategy is not permission to enable trading.

`action_apply` accepts that preview ID. Applying the same ID again returns the existing operation rather than submitting the command twice. A changed or reconnected core can invalidate the preview. Read the state again before preparing another one.

Use `operation_get` after applying. Distinguish:

| Result | Interpretation |
| :--- | :--- |
| Queued in Station or ActiveLib | Dispatch has not yet been established |
| Submitted | The command entered an ActiveLib queue; observe the core and exchange result |
| Confirmed strategy | The matching strategy revision was observed as requested |
| Adjusted strategy | The core saved different values; compare the returned sent and saved snapshots |
| Superseded strategy | Another revision displaced this submission |
| Confirmed settings | All requested values appeared in a subsequent full snapshot; this is observation, not a transaction acknowledgement |
| Rejected | Admission or a local precondition failed; read the stated reason |
| Unknown or timeout | The action may already have happened; do not automatically repeat a trading command |

The preview checks supported types and current preconditions. It is not a backtest, profitability assessment or atomic lock on the exchange. Other terminals and the market can change state after dispatch. Operations across cores are separate operations, not one all-or-nothing transaction.

## Strategies

Read `strategy_list`, then `strategy_read` and `strategy_schema` for the selected core and kind. Use the schema's exact field names, types, visibility and current dynamic choices. Preserve all fields not requested by the user.

`strategy_edit` changes fields on an existing strategy. `checked` and `path` are separate attributes. `apply_to_orders` explicitly requests propagation to existing orders; do not infer that the user wanted to alter an already open trade. `strategy_create` creates an unchecked strategy. Creation alone does not start it. Deleting a strategy does not close its existing positions. The strategy must already be unchecked, and that change observed, before deletion is accepted.

The native strategy API is different from text import. Do not send `##Begin_Strategy`, `Active`, `FVersion`, `K`/`M` number suffixes or `YES`/`NO` strings as native typed values. JSON booleans are booleans. The tools represent 64-bit integer field values as decimal strings to preserve precision in JavaScript clients. Other numeric fields retain their native values without UI rounding.

Use the [parameter index](params/index.tsv) to find units and meaning, [strategy selection guide](strategy-selection-guide.md) to choose a detector, and [lifecycle guide](parameters-by-lifecycle.md) to understand when a field acts. The [text-import guide](AI_GUIDE.md) applies when the user specifically wants an importable text block.

Before changing a strategy, check relevant filters, market selection, direction, detector conditions, entry sizing, exit behavior and linked strategies. A field being present or visible does not establish an active license, suitable market conditions or available balance.

After submission, compare the exact sent and saved revisions from `operation_get`. A later live strategy snapshot may already describe another edit; it must not be presented as the earlier command's acknowledgement. The core can normalize or reject combinations. Report any adjustment instead of claiming that every requested value was saved.

## Orders

Read the core's orders and `market_read` for the exact market name. Separate an entry/exit target price from exchange-reported price, remaining quantity and fill state. A strategy or order UID has meaning only together with its core ID.

For `order_place`, `balance_amount` is an amount in the account's balance or settlement currency. It is not the base-asset quantity. For linear futures it is not margin and is not multiplied by leverage. On inverse contracts, use the market's settlement currency and contract size. Read the preview's currency, effective amount and quantity estimate.

A selected non-Manual strategy with a positive `OrderSize` can override the supplied amount. The preview identifies this. The kernel applies exchange-specific rounding, minimum order size, available funds and position limits; an estimate is not a guaranteed executed quantity. Do not silently increase a user's risk to satisfy a minimum.

Leaving `strategy_id` absent requests no strategy on current kernels; older kernels may attach Manual. Check observed behavior when working with an older core. Setting leverage, enabling hedge mode, closing a position and switching Panic Sell are distinct actions with different effects.

Order preview records the global emulator flag and the selected strategy's emulator flag; a change requires a new preview. The size and quantity estimates describe the initial order. A strategy can create several orders and scale their amounts through `OrdersCount`, `OrderSizeStep` and related grid settings. Do not present the initial size as total exposure or assume one command means one exchange order. For older cores with an implicit Manual fallback, use an explicit strategy when exact behavior is required.

`order_cancel` and `order_move` recheck the order's identity, phase, relevant quantities and prices in the ActiveLib runtime before dispatch. An entry that filled while the request waited must not turn into an unintended cancellation of the exit. This local guard is not an exchange-side compare-and-swap.

`panic_sell` selects one order UID that is already in the sell phase and sets its Panic Sell flag to the requested value. The same value again is rejected and sends nothing. It is not the market UI's toggle and does not clear stop settings.

`position_close` requests cancellation of current orders on the market before starting closing orders, including both legs in hedge mode. A failed cancellation does not prevent the closing attempt. In ordinary mode, sells target about 2% above and buys about 2% below the core's last ask. With `aggressive_limit=true`, sells target about 4% below and buys about 4% above that ask. This flag selects requested prices; it does not guarantee a market order or a fill.

The core can attach its configured Manual strategy to this close flow. On Binance Futures, when `trading.use_manual_strategy`, `trading.use_stop_market` and that Manual strategy's `UseMarketStop` are enabled, an aggressive close can submit a conditional stop that waits for its trigger. Inspect these settings, the resulting order type and the remaining position. The preview records the global emulator mode but does not model this inherited stop behavior.

Order creation returns a client ticket, but the current order stream does not echo that ticket as an exact server-UID correlation. Do not manufacture a match from similar price and timing. If the result is uncertain, read live orders and logs before any new instruction; repeating the request with a new preview can create another order.

## Settings

Use `settings_read` for the live safe-share configuration and SDK schema, including exact dot paths, types, array sizes and read-only metadata. Use [the settings index](settings/index.tsv) for units, dependencies and headless limitations.

`settings_patch` names only the requested fields. The Station rebuilds the full outgoing configuration from its fresh retained base, preserving untouched values and opaque future data. It shares the existing settings writer, so a busy writer can reject the operation and ask for a new preview. Arrays are replaced as whole typed values, not patched through guessed numeric path components.

A nonfinite numeric value appears in `settings_read` as JSON `null`. Omit that field to preserve it; copying `null` into the patch is rejected, not treated as a request to clear it. Nonfinite replacements and values that overflow the field's type are also rejected before sending. If all requested values already match, the result is `already_applied` and nothing is sent.

The kernel imports a complete snapshot and does not provide a server-side revision lock or rollback transaction. Another terminal can still race after dispatch. A timeout does not prove that nothing changed. Read all requested fields and any affected behavior before deciding what to do next.

Persisted startup preferences, current autodetect state, strategy-engine state and one-time account actions are different controls. Use the named runtime action for a runtime change. A GUI setting can be stored successfully without producing a headless feature. A schema default is not proof of the connected core's current or supported value.

`runtime_restart` requires trading permission: it starts or restarts market processing, leaves passive mode and starts checked strategies. It can initiate trading; it is not a harmless process-maintenance command.

See [Choosing the settings API](settings/10-settings-apis.md) for full versus compact settings and the APIs that own Telegram, leverage and observers. MCP intentionally exposes a named subset of these controls; documentation of an SDK method does not make it an available MCP tool.

## Diagnosis

For a causal explanation, combine current state, configuration, reports and a short observation of new log messages:

1. Read `station_overview` and the relevant core state. Record the connection generation, stale markers and the time of the question.
2. Identify the market, strategy, order and interval. Read exact strategy values and relevant settings before attributing behavior to them.
3. Call `logs_start` for explicitly selected cores and a bounded interval. Wait for that interval or stop early with `logs_stop`, then page through `logs_get`.
4. Keep neighboring log lines and correlate identities. Read [the log-analysis workflow](station-log-analysis.md) and look up unfamiliar lines in [the log reference](exchange-errors-and-logs.md).
5. Explain the observed sequence, the supported cause and what remains uncertain. If a check can distinguish alternatives, name that check rather than choosing the most plausible story as fact.

The observation subscribes this Station connection to new server logs. It does not retrieve arbitrary files, replay all earlier logs or raise the kernel's global log level. The Station ends the subscription lease even if the chat closes, and overlapping observations do not turn each other's delivery off.

Keep core-local timestamps separate from UTC reception time. Missing messages, reconnects, retention limits and truncation make an observation incomplete. Empty logs do not prove that the bot is healthy or that no action occurred. Credentials are redacted where recognized; avoid publishing unnecessary account details.

## Reports

`reports_query` returns closed trades for an explicit set of authorized cores over a UTC interval. Open positions stay in `core_state` with `section=positions`. Compare report synchronization in `station_overview` before calling an empty or partial result the complete trading history.

Native profit is grouped by currency. Different native currencies cannot be added directly. USDT valuation includes coverage information; report missing conversions instead of treating them as zero. Emulator trades are excluded unless explicitly requested.

Rows preserve raw core-local seconds separately from corrected UTC milliseconds. If the Station has no clock offset for a row, its UTC time is unknown. Interval filtering may fall back to the core clock; report this limitation when it affects the requested period.

Specify the interval, cores, emulator inclusion, currencies and data coverage in a summary. Separate historical performance from a forecast. A profitable sample does not establish future returns, and a short losing interval alone does not identify a malfunction.

## Events

`events_read` is a bounded feed with a cursor. The Station records connection/runtime/strategy-engine state changes and outcomes of this client's operations. Permission checks apply on every read; operation events from another authorization are not exposed.

Save `next_cursor` and pass it as `after` on the next call. A reported gap requires refreshing the current state. The journal is not a permanent trading ledger and is cleared on restart.

MCP itself does not wake an absent AI chat. Continuous monitoring requires the AI application or another authorized runner to schedule calls, retain cursors, decide which changes matter and deliver notifications. A subscription or polling capability must be checked in that application rather than assumed from MCP support.

## Connection and permissions

On a prepared VPS, the Terminal's MCP setup button installs a dedicated HTTPS listener and certificate renewal, restarts the Station, verifies the public endpoint and enables authorization requests. A public IP can receive a trusted short-lived certificate without buying a domain. TCP 443 must be reachable; provider firewalls or NAT may require a separate network change. An occupied HTTPS port is reported instead of replacing another web server. If MCP is already configured for a different address, setup stops: changing that address revokes clients and is a separate reconfiguration.

Copy the Station's MCP URL into an AI application that supports remote MCP with OAuth. The authorization page displays a code. Enter it in the Terminal's Station AI-access page and choose the specific cores and permissions. Client names are labels supplied by the client, not proof of a provider's identity. Approve the code from the connection flow you initiated.

Read is required with every grant, and the grant cannot add a permission the client did not request. Strategy edits, trading and settings changes are otherwise separate permissions enforced by the Station. The public HTTPS interface cannot approve its own access. Owner administration uses the existing private Station connection. Revoking a client or disabling AI access invalidates its authorization; enabling access again does not restore revoked clients.

HTTPS encrypts the connection; OAuth restricts who can use it. Neither promises that software can never have a vulnerability. Keep the Station and certificate manager updated, grant only the intended cores/actions, and use the action history to inspect admitted operations. A successful command already dispatched to a core cannot be undone by revoking a token afterward.
