# Linux kernel commands: monitoring and service management

Use these commands over SSH on the VPS running Moonbot. `mb` talks to a selected kernel; `systemctl` starts and stops its Linux service. A running service and a successful exchange login are separate checks.

For a new VPS, start with [Download and install the Linux kernel](linux-installation.md). MoonTerminal can run the status, log and service actions in [Manage the core from MoonTerminal](#manage-the-core-from-moonterminal).

## Select the kernel

```sh
mb --help
```

This lists installed instances, their folders and ready-to-use commands. Copy the **full service name** for your instance into `unit`; the name below is an example:

```sh
unit='moonbot@root-Binance.service'
mb "$unit" --help
```

Use the same `unit` in the commands below. Set it again in a new SSH session. `moonbot` is an alias for `mb`.

`mb` asks for a sudo password when an instance command needs root and the shell is not already root. General `mb --help` does not. `systemctl` and `journalctl` still expect a root shell, so those examples keep `sudo`. The sudo prompt, when it appears, comes before the command's own prompts. For `--set-api-keys`, the system password is first and the hidden key prompts follow. JSON piped into `mb` is still delivered to the kernel command. An account that cannot use sudo is refused, and the instance command does not run.

With one installed instance, omit the name from any directory: `mb --status`, `mb --logs`. With several, run the command in that instance's folder, or pass the service name or an unambiguous prefix, such as `mb root-Binance --status`. If a prefix matches several instances, `mb` lists them and the ready commands instead of choosing one. A full name ending in `.service` selects that service. Quote a prefix that contains spaces.

## Everyday monitoring

| Task | Command | What it shows |
| :--- | :--- | :--- |
| Kernel and exchange status | `mb "$unit" --status` | JSON: login state, exchange, emulator mode and MoonProto listener status |
| Trading log | `mb "$unit" --logs` | The last 100 lines of today's trading log, then new lines; follows the next day's file at midnight |
| Service status | `sudo systemctl status "$unit" --no-pager` | Whether the process is running, its PID and recent service messages |
| Recent service messages | `sudo journalctl -u "$unit" -n 100 --no-pager` | Startup, shutdown and service errors |
| Follow service messages | `sudo journalctl -u "$unit" -f` | New journal entries as they arrive |
| Process and resource counters | `sudo systemctl show "$unit" -p MainPID -p MemoryCurrent -p CPUUsageNSec -p NRestarts` | PID, available memory/CPU counters and automatic restart count |
| Live CPU and memory by service | `sudo systemd-cgtop` | Find the Moonbot service in the list of control groups |
| Check the MoonProto UDP port | `sudo ss -lunp 'sport = :3000'` | Local processes listening on UDP 3000; substitute your configured port |

`Ctrl+C` ends a log viewer or `systemd-cgtop`; it does not stop the kernel. `CPUUsageNSec` is accumulated CPU time, not current CPU load. Resource counters depend on the host's systemd accounting settings.

The trading log is `logs/LOG_YYYY-MM-DD.log` in the instance folder. Timestamps use the local time of the machine running the core; account for its time zone when matching events. `journalctl` shows the service journal; it does not replace the trading log. To inspect a specific period:

```sh
sudo journalctl -u "$unit" --since '1 hour ago' --no-pager
```

### Reading `--status`

| `state` | Meaning / next step |
| :--- | :--- |
| `initializing` | Startup or exchange login is in progress; check again shortly |
| `ready` | Exchange initialization completed |
| `needs_keys` | Set credentials for the selected exchange |
| `login_error` | Read `login_error`; check the exchange credentials, permissions and IP restrictions |
| `registration_error` | Product registration failed; read `login_error` for the reason |
| `action_required` | An action is required, such as a Hyperliquid approval; read `login_error` |

`ok: true` means the status request succeeded; it does **not** mean `state` is `ready`. For automation, inspect `state` as well as the command's exit code. `ready` is a startup result, not a guarantee that every market stream or strategy is healthy.

`moonproto_enabled` reports the saved server setting; `moonproto_listening` reports the listener state. Read `moonproto_error` if it cannot start. A local listener does not prove that the VPS firewall or provider allows clients through. `emulator` tells you whether the kernel is in emulator mode.

## Start, stop, restart and boot settings

| Task | Command |
| :--- | :--- |
| Start | `sudo systemctl start "$unit"` |
| Stop | `sudo systemctl stop "$unit"` |
| Restart | `sudo systemctl restart "$unit"` |
| Start automatically after a VPS reboot | `sudo systemctl enable "$unit"` |
| Disable automatic startup at boot | `sudo systemctl disable "$unit"` |
| Check boot setting | `systemctl is-enabled "$unit"` |
| Check whether the service is active | `systemctl is-active "$unit"` |

`enable` and `disable` change the boot setting; they do not start or stop the current process. Add `--now` when you want both actions, for example `sudo systemctl enable --now "$unit"`.

Stopping or restarting interrupts trading on that kernel. While it is stopped, its strategies and stops cannot manage positions. A service stop is not a command to close every exchange position. Closing the SSH window leaves a running service running.

There are no `mb --start`, `mb --stop` or `mb --restart` commands. Running `./MoonBot` without an option launches a kernel process; use `systemctl` to manage an installed service.

## Connection, exchange and API keys

| Task | Command | Effect |
| :--- | :--- | :--- |
| Show the saved client connection package | `mb "$unit" --moonProtoKey` | Copy the output into **Paste Key** in the client; does not generate a new key |
| Configure MoonProto | `mb "$unit" --setup-moonproto --host 203.0.113.10 --port 3000` | Replace the example IP with the VPS address. Enables the server and returns JSON with a connection package in `key` |
| List exchange names and key requirements | `mb "$unit" --exchanges` | Exact exchange IDs, required passphrases and RSA support |
| Select an exchange | `mb "$unit" --exchange bybit-futures` | Uses that exchange's saved credentials, if present; use an ID from `--exchanges` |
| Enter API credentials | `mb "$unit" --set-api-keys` | Hidden prompts for the key and secret. A sudo password, if `mb` asks for one, comes before those prompts |
| Retry login with saved credentials | `mb "$unit" --retry-login` | Disconnects and starts exchange login again |

`--setup-moonproto` keeps an existing key. Add `--rotate-key` only to replace it, then update the connection package in every client. The IP may be IPv4 or IPv6; the port is UDP. Allow that port in the VPS and provider firewalls. Both `--moonProtoKey` and the setup response contain a secret connection package: keep their output private.

`--exchanges`, `--status` and the setup/login commands need the kernel to be running. Help, trading-log viewing and reading the saved connection package also work with a stopped service.

Exchange selection, credential changes and `--retry-login` use the normal exchange disconnect/login sequence: strategies stop, orders go through the usual disconnect handling and clients reconnect. The kernel process stays running. Selecting a previously configured exchange also restores its saved MoonProto settings; you may need to copy its connection package again. These are maintenance operations, not passive monitoring. Check `--status` after the request; an accepted change does not mean login has completed.

While that status is `initializing`, another `--exchange`, `--set-api-keys` or `--retry-login` is refused. The command reports `Exchange initialization is busy. Try again after it finishes.` and leaves the saved keys as they are.

For Bitget and OKX, use the passphrase reported by `--exchanges` when creating the exchange API key. For Hyperliquid, the prompts take the wallet address and signer's private key. Binance RSA uses the exported Moonbot RSA package through JSON on standard input.

For automation, `--set-api-keys` also accepts a JSON object on standard input: `api_key` and `api_secret`, with optional `user_name`; or `rsa_bundle` for Binance RSA. Supply it through a protected input source, not command-line arguments or shell history. `mb` passes that input through when it calls sudo.

## Update this kernel

```sh
mb "$unit" --update release
```

This requests the published Linux release. For a named test build, use its announced name, for example `mb "$unit" --update MoonBot-L7`; that name is an example, not an alias for the latest test build.

The kernel must be running with its MoonProto server enabled and its key saved. The command waits for the archive download and update request. Success at this point does not confirm that installation and restart have finished. If the requested package is unavailable, it reports the download error. Only the selected kernel is updated; other instances and connected terminals are not updated by this command.

Check the service journal, service status and `--status` after the restart:

```sh
sudo journalctl -u "$unit" -n 100 --no-pager
sudo systemctl status "$unit" --no-pager
mb "$unit" --status
```

If the command times out, inspect the journal and trading log before repeating it: the update may already be in progress.

## Manage the core from MoonTerminal

These instructions describe MoonTerminal **v0.69.2**.

In **Settings → Connections**, right-click a core with a literal, non-loopback IPv4 address. Hostnames and IPv6 addresses have no menu. If SSH access is not saved for that address, choose **Add server login…** first.

After MoonTerminal identifies the installation, **Core status**, **Show log**, **Retry exchange login** and service controls are available even for a core installed outside MoonTerminal. **Outgoing IP** is with those service controls. Changing the exchange, API keys or MoonProto address, showing the connection key and **Update core** require an installation managed by MoonTerminal.

- **Core status** checks exchange login, the service and the MoonProto listener separately. `Ready` means exchange login completed.
- **Show log** displays the tail of the trading log without changing its timestamps. If that file cannot be read, it falls back to the service journal in UTC.
- **Retry exchange login** uses the saved keys without restarting the process. Closing the window does not cancel the login. Wait for the result; a login error is not retried automatically.
- **Start** is available for a stopped service. **Stop** and **Restart** require a running service and ask for confirmation. Positions remain on the exchange, but the stopped core cannot manage them. Start/restart success requires the MoonProto UDP listener to open; check exchange login separately in **Core status**.

**From server** downloads one whole day of the core's trading log. The Log tab's own file holds only the hours this MoonTerminal was connected, and **Show log** is a tail. MoonTerminal shows it on the Log tab of a single core, for the same literal non-loopback IPv4 address and the same saved server login as the menu above. It is absent from a combined log, and from a panel an Auto workspace keeps on Live. Without a login, the menu offers to add one. The list is the days the core still keeps, with their size. Choosing a day downloads that day's file, stores it beside the live copy and opens it at the end. A day the core does not have is reported, and nothing is stored. The service journal is not put in its place. A file larger than 512 MB is refused before transfer. **Earlier** and **Later** walk a file longer than the view, one screen at a time. A time typed as `hh:mm` or `hh:mm:ss`, then Enter, jumps to that moment as the rows display it. The Report's trade log reads a downloaded day as well, and a line both copies hold is shown once. The download uses that core's server session, so the other server commands for the core wait until it finishes.

Changing the exchange stops strategies and then asks for the new exchange's API keys. Showing the connection key does not replace it.

**MoonProto address** saves the entered IPv4 address and UDP port in the core's settings and exported connection package, keeping the existing key. The listener uses that port on all IPv4 interfaces. This terminal keeps its existing host and updates only the port. If the page reports `MoonProto was configured, but its marker and firewall rule could not be updated`, the core has already saved the change: check the firewall before reconnecting or retrying.

**Update core** opens the Core updates window. Opening it does not install a build.

## Outgoing IP

Open it from the same right-click as the controls above, **Outgoing IP…**, including on a core that was not installed through MoonTerminal.

The page chooses which of the server's IPv4 addresses the core uses for new connections to the exchange. The MoonProto address the terminal connects to stays as it is. Add the chosen address to the exchange API key's allowed IPs. SSH and the MoonProto host may be the server's other address.

**Primary** is the terminal's own unbound state. With no other binding, exchange traffic leaves from the server's primary address. Any other listed address binds the core to it. A bound core reaches the exchange over that IPv4; its IPv6 connections are refused. The list is the global IPv4 addresses on the interface of the default IPv4 route. An address on another interface is left out.

The server must run systemd 255 or newer (Debian 13, Ubuntu 24.04 and newer). An older server shows the version it has and offers no choice. A bought address appears after the server has configured it: restart the server from the provider's panel and open the page again.

**Now** is the recorded address. The row marked **current** is the one in force. **Connections through this address** counts new connections since those rules were last loaded, summed across every core bound to that address.

Picking a different address asks **Move the core to …?** A running core restarts: its exchange connections close and reopen from the new address. Positions remain on the exchange, and the core cannot manage them until it is listening again. Confirm with **Move and restart**. Success is that address marked **current**, without **The core is not under its address's rules**. Check exchange login separately in **Core status**. If the restart fails, the previous binding is put back and the page shows the server's reason.

A stopped core is not started. The page says the address applies at the next start; confirm with **Apply**. Choosing the address a running core already uses, while it is under that address's rules, does not restart it. If the page says the core is not under its address's rules, its connections are leaving from the primary address: pick that same address again. That rewrites the rules and restarts a running core.

If the server no longer has the recorded address, the core's connections are blocked rather than sent out from another address. Pick another address, or **Primary**.

A hand-written `NFTSet=` in the core's systemd unit is another binding. **Now** shows **Set outside the terminal** and names its `table/set`. Choosing an address, including **Primary**, replaces that binding for this core. The confirmation names what will be disabled. A running core restarts; a stopped core takes the choice on its next start. If the new binding does not take effect, the terminal restores the previous one and reports the server's reason.

## When a command does not work

| Message / symptom | What to do |
| :--- | :--- |
| `No matching MoonBot service` | Run `mb --help`; supply the exact service name or enter its folder. With a single installed instance the name can be omitted from any directory |
| `sudo:` and the command does not run | This account cannot use sudo. Instance commands run as root; general `mb --help` does not need it |
| `More than one MoonBot service matches` | Use the full name, including `.service`, from the list |
| `The core command channel is unavailable` | Check `systemctl status`; start the intended instance if appropriate. The installed build must support local commands |
| `Unknown command or wrong arguments` | Read `mb "$unit" --help` for the selected build; check spelling and argument count |
| `Core is busy` / `Exchange initialization is busy` | Let initialization finish and check `--status` before changing settings again |
| Service exited with code `78` | The service does not restart itself. Read the journal and today's `logs/LOG_YYYY-MM-DD.log`. `Cannot start MoonBot: data directory is locked or inaccessible` means another copy is using this folder, or `data/lock.dat` cannot be opened. Stop the other copy, or correct access to the data folder if no other copy is running. Do not delete `lock.dat` to clear it: the running process keeps its lock, and a new start can open a different file. `password-protected or invalid configuration` in the trading log means the configuration cannot be loaded: correct it and transfer it again. Starting the service again does not remove either cause |
| Service runs but the client cannot connect | Check MoonProto listener/error fields, the client IP/port/key and both firewalls |
| `needs systemd 255 or newer` on **Outgoing IP** | That server cannot bind a core to its own address. Leave it on **Primary**. Debian 13, Ubuntu 24.04 and newer have a new enough systemd |
| `not on this server's main network interface` | Only an address on the interface of the default IPv4 route is accepted. If you just bought the address, restart the server from the provider's panel and open **Outgoing IP** again |

For support, collect the kernel's trading log for the relevant time and the service journal. Do not post API keys, SSH keys, MoonProto connection packages or the full configuration in a public chat.

Related: [kernel and VPS concepts](../concepts/07-kernel-vps-and-infrastructure.md), [kernel settings](settings/README.md), [trading-log messages](exchange-errors-and-logs.md), [systemctl reference](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html).
