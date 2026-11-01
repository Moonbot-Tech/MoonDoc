# Shared configuration structure

[Settings reference](README.md)

`SharedConfig` is the portable settings model exchanged with the Moonbot kernel. Its six sections contain trading policy, presentation preferences and saved state. The section names reflect storage: some chart preferences live under `trading` or `signals`.

Use a received snapshot as the base for edits, preserve values outside the edit, and keep unknown tails unchanged. A field marked reserved or inactive is still part of that round trip. `SharedConfig::default()` is an offline constructor, not the connected kernel's configuration.

Secrets and live service settings use separate interfaces. See [API selection and the editing cycle](10-settings-apis.md); find individual fields in the [index](index.tsv).

<a id="sharedconfig"></a>

## `SharedConfig` — `SharedConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="sharedconfig-signals"></a>`signals` | [`SignalsSection`](02-signals-and-alerts.md#signalssection) | Signal parsing, sounds, filters and several saved preferences; see the signals chapter. |
| <a id="sharedconfig-trading"></a>`trading` | [`TradingSection`](03-trading-and-leverage.md#tradingsection) | Shared trading policy, risk controls, manual execution and nested settings. |
| <a id="sharedconfig-visual"></a>`visual` | [`VisualSection`](05-charts-and-display.md#visualsection) | Saved chart and GUI presentation settings on the kernel. A remote terminal must implement its own renderer. |
| <a id="sharedconfig-theme"></a>`theme` | [`ThemeSection`](08-theme-and-ini.md#themesection) | Main GUI style and allowlisted color overrides. |
| <a id="sharedconfig-ini"></a>`ini` | [`IniSection`](08-theme-and-ini.md#inisection) | Allowlisted Charts and ArbColors INI sections. Not access to arbitrary core configuration files. |
| <a id="sharedconfig-ui"></a>`ui` | [`UiSection`](07-interface-and-hotkeys.md#uisection) | Hotkeys, chart ordering, table layout and strategy-editor expansion state. |
