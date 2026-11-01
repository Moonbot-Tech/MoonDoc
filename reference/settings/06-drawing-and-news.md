# Drawing tools and news cards

[Settings reference](README.md)

Drawing tools annotate the chart and, in the Pencil's emulator mode, can supply a synthetic price path. Tool appearance and individual object alerts are separate settings. Hiding an object does not delete it.

News settings control card text, tags, sound and appearance. `feed_mode` bypasses selected-tag filtering; it does not change token filters. These preferences do not configure a news trading strategy.

Related: [Pencil and emulator testing](../../concepts/08-testing-debugging-and-analytics.md), [news and external signals](../../concepts/02-detect-pipeline-and-signals.md). Field paths are relative to `SharedConfig`.

<a id="customdrawconfig"></a>

## `visual.custom_draw_config` — `CustomDrawConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="customdrawconfig-ver"></a>`ver` | `i32` | Stored drawing-config version. Preserve the value received from the kernel. |
| <a id="customdrawconfig-f-opacity"></a>`f_opacity` | `f32` | Global drawing-stroke opacity, 0..=1. Order-line opacity has its own tool field. |
| <a id="customdrawconfig-f-show"></a>`f_show` | `bool` | Show/enable interaction with chart drawing objects. Hiding them does not delete saved objects. |
| <a id="customdrawconfig-tools"></a>`tools` | [`[CustomDrawTool; 16]`](06-drawing-and-news.md#customdrawtool) | 16 tool slots: 0=none, 1=price line, 2=channel, 3=Fibonacci, 4=triangle, 5=rectangle, 6=pencil, 7=order line, 8=system rectangle, 9=news marker; 10..15 reserved. Preserve reserved slots. |

<a id="customdrawtool"></a>

## `visual.custom_draw_config.tools[]` — `CustomDrawTool`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="customdrawtool-color-w"></a>`color_w` | `u32` | Light-theme stroke color, ARGB (0xAARRGGBB). |
| <a id="customdrawtool-color-b"></a>`color_b` | `u32` | Dark-theme stroke color, ARGB (0xAARRGGBB). |
| <a id="customdrawtool-fill-color-w"></a>`fill_color_w` | `u32` | Stored legacy/reserved field without a current tool-config consumer; preserve it. |
| <a id="customdrawtool-fill-color-b"></a>`fill_color_b` | `u32` | Stored legacy/reserved field without a current tool-config consumer; preserve it. |
| <a id="customdrawtool-sound-alert"></a>`sound_alert` | `bool` | Stored legacy/reserved field without a current tool-config consumer; preserve it. Individual drawing-object alerts are separate state. |
| <a id="customdrawtool-sound-kind"></a>`sound_kind` | `i32` | Stored legacy/reserved field without a current tool-config consumer; preserve it. Individual drawing-object alerts are separate state. |
| <a id="customdrawtool-thickness"></a>`thickness` | `f32` | Stroke width in pixels; GUI 0.5..=6. For news markers, values below 0.6 hide the marker and its hit target. |
| <a id="customdrawtool-stroke"></a>`stroke` | `i32` | Line dash style: 0=solid, 1=dash, 2=dot, 3=dash-dot, 4=dash-dot-dot. |
| <a id="customdrawtool-thickness-2"></a>`thickness_2` | `f32` | For tool 7 (order line): opacity 0..=1, not width; below 0.1 hides its drawing. Preserve for other tools. |
| <a id="customdrawtool-stroke-2"></a>`stroke_2` | `i32` | Stored legacy/reserved field without a current tool-config consumer; preserve it. |
| <a id="customdrawtool-color-2w"></a>`color_2w` | `[u32; 6]` | Stored legacy/reserved field without a current tool-config consumer; preserve it. |
| <a id="customdrawtool-color-2b"></a>`color_2b` | `[u32; 6]` | Stored legacy/reserved field without a current tool-config consumer; preserve it. |
| <a id="customdrawtool-fill-color-2w"></a>`fill_color_2w` | `[u32; 6]` | Six ARGB Fibonacci-zone fills; rectangle uses element 0. These are used in both themes despite the w suffix. |
| <a id="customdrawtool-fill-color-2b"></a>`fill_color_2b` | `[u32; 6]` | Stored legacy/reserved field without a current tool-config consumer; preserve it. |
| <a id="customdrawtool-emulate-trades"></a>`emulate_trades` | `bool` | Pencil-only simulation: use drawn future points as synthetic market ticks in the supported emulator mode. This is not an order-on-line-crossing switch. GUI forces it off for other tools. |
| <a id="customdrawtool-prevent-switch"></a>`prevent_switch` | `bool` | Exclude this tool from cycling through drawing tools with a hotkey. News-marker tool is excluded by default. Does not prevent chart switching. |

<a id="newsformconfig"></a>

## `visual.news_form_config` — `NewsFormConfig`

| Field | Type | Meaning, values and dependencies |
| :--- | :--- | :--- |
| <a id="newsformconfig-stay-on-top"></a>`stay_on_top` | `bool` | Keep the news window above other windows. |
| <a id="newsformconfig-exact-time"></a>`exact_time` | `bool` | Show exact news time instead of relative age. |
| <a id="newsformconfig-font-size"></a>`font_size` | `u8` | News-card font size; GUI 12..=16. |
| <a id="newsformconfig-strength"></a>`strength` | `u8` | Inactive saved filter: opening the current news form resets it to 0 and hides its control. Do not expose as a working strength filter. |
| <a id="newsformconfig-update-orig"></a>`update_orig` | `bool` | Use text in the current GUI language when available; false uses the original text. Not a server-side news-edit permission. |
| <a id="newsformconfig-sound"></a>`sound` | `u8` | News sound-list index: 0=off; positive indices select the kernel's named-sound list. This is not a boolean or the ordinary 1..11 alert-preset list. |
| <a id="newsformconfig-theme"></a>`theme` | `i32` | News theme: 0=Light Paper, 1=Light Default, 2=Light Classic, 3=Light Quartz, 4=Light Mist, 5=Light Sand, 6=Dark Carbon, 7=Dark Navy, 8=Dark Slate. Separate from the main GUI style. |
| <a id="newsformconfig-coin-card-font-size"></a>`coin_card_font_size` | `i32` | Coin-card font size: non-positive means default 13; positive values are clamped to 8..=30. |
| <a id="newsformconfig-full-tags"></a>`full_tags` | `bool` | Show all tags on a news card. When false and tag selections exist, show only selected matching tags; does not alter the news itself. |
| <a id="newsformconfig-feed-mode"></a>`feed_mode` | `bool` | Show the news feed without the selected-tag visibility filter. Token filters still apply. Not a scrolling/layout mode. |
