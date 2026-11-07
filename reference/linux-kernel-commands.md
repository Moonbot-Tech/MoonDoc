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
sudo mb "$unit" --help
```

Use the same `unit` in the commands below. Set it again in a new SSH session. `moonbot` is an alias for `mb`.

Inside the instance's own folder, you can omit the name: `sudo mb --status`, `sudo mb --logs`. Outside that folder, supply a service name or an unambiguous prefix, such as `sudo mb root-Binance --status`. If a prefix matches several instances, `mb` lists them instead of choosing one. General `mb --help` works without sudo; instance commands require root.

## Everyday monitoring

| Task | Command | What it shows |
| :--- | :--- | :--- |
| Kernel and exchange status | `sudo mb "$unit" --status` | JSON: login state, exchange, emulator mode and MoonProto listener status |
| Trading log | `sudo mb "$unit" --logs` | The last 100 lines of today's trading log, then new lines; follows the next day's file at midnight |
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
| Show the saved client connection package | `sudo mb "$unit" --moonProtoKey` | Copy the output into **Paste Key** in the client; does not generate a new key |
| Configure MoonProto | `sudo mb "$unit" --setup-moonproto --host 203.0.113.10 --port 3000` | Replace the example IP with the VPS address. Enables the server and returns JSON with a connection package in `key` |
| List exchange names and key requirements | `sudo mb "$unit" --exchanges` | Exact exchange IDs, required passphrases and RSA support |
| Select an exchange | `sudo mb "$unit" --exchange bybit-futures` | Uses that exchange's saved credentials, if present; use an ID from `--exchanges` |
| Enter API credentials | `sudo mb "$unit" --set-api-keys` | Hidden prompts for the key and secret |
| Retry login with saved credentials | `sudo mb "$unit" --retry-login` | Disconnects and starts exchange login again |

`--setup-moonproto` keeps an existing key. Add `--rotate-key` only to replace it, then update the connection package in every client. The IP may be IPv4 or IPv6; the port is UDP. Allow that port in the VPS and provider firewalls. Both `--moonProtoKey` and the setup response contain a secret connection package: keep their output private.

`--exchanges`, `--status` and the setup/login commands need the kernel to be running. Help, trading-log viewing and reading the saved connection package also work with a stopped service.

Exchange selection, credential changes and `--retry-login` use the normal exchange disconnect/login sequence: strategies stop, orders go through the usual disconnect handling and clients reconnect. The kernel process stays running. Selecting a previously configured exchange also restores its saved MoonProto settings; you may need to copy its connection package again. These are maintenance operations, not passive monitoring. Check `--status` after the request; an accepted change does not mean login has completed.

While that status is `initializing`, another `--exchange`, `--set-api-keys` or `--retry-login` is refused. The command reports `Exchange initialization is busy. Try again after it finishes.` and leaves the saved keys as they are.

For Bitget and OKX, use the passphrase reported by `--exchanges` when creating the exchange API key. For Hyperliquid, the prompts take the wallet address and signer's private key. Binance RSA uses the exported Moonbot RSA package through JSON on standard input.

For automation, `--set-api-keys` also accepts a JSON object on standard input: `api_key` and `api_secret`, with optional `user_name`; or `rsa_bundle` for Binance RSA. Supply it through a protected input source, not command-line arguments or shell history.

## Update this kernel

```sh
sudo mb "$unit" --update release
```

This requests the published Linux release. For a named test build, use its announced name, for example `sudo mb "$unit" --update MoonBot-L7`; that name is an example, not an alias for the latest test build.

The kernel must be running with its MoonProto server enabled and its key saved. The command waits for the archive download and update request. Success at this point does not confirm that installation and restart have finished. If the requested package is unavailable, it reports the download error. Only the selected kernel is updated; other instances and connected terminals are not updated by this command.

Check the service journal, service status and `--status` after the restart:

```sh
sudo journalctl -u "$unit" -n 100 --no-pager
sudo systemctl status "$unit" --no-pager
sudo mb "$unit" --status
```

If the command times out, inspect the journal and trading log before repeating it: the update may already be in progress.

## Manage the core from MoonTerminal

These controls are available in development builds after v0.65.12; that published release does not include them.

In **Settings → Connections**, right-click a core with a literal, non-loopback IPv4 address. Hostnames and IPv6 addresses have no menu. If SSH access is not saved for that address, choose **Add server login…** first.

After MoonTerminal identifies the installation, **Core status**, **Show log**, **Retry exchange login** and service controls are available even for a core installed outside MoonTerminal. Changing the exchange, API keys or MoonProto address, showing the connection key and **Update core** require an installation managed by MoonTerminal.

- **Core status** checks exchange login, the service and the MoonProto listener separately. `Ready` means exchange login completed.
- **Show log** displays the tail of the trading log without changing its timestamps. If that file cannot be read, it falls back to the service journal in UTC.
- **Retry exchange login** uses the saved keys without restarting the process. Closing the window does not cancel the login. Wait for the result; a login error is not retried automatically.
- **Start** is available for a stopped service. **Stop** and **Restart** require a running service and ask for confirmation. Positions remain on the exchange, but the stopped core cannot manage them. Start/restart success requires the MoonProto UDP listener to open; check exchange login separately in **Core status**.

Changing the exchange stops strategies and then asks for the new exchange's API keys. Showing the connection key does not replace it.

**MoonProto address** saves the entered IPv4 address and UDP port in the core's settings and exported connection package, keeping the existing key. The listener uses that port on all IPv4 interfaces. This terminal keeps its existing host and updates only the port. If the page reports `MoonProto was configured, but its marker and firewall rule could not be updated`, the core has already saved the change: check the firewall before reconnecting or retrying.

**Update core** opens the Core updates window. Opening it does not install a build.

## When a command does not work

| Message / symptom | What to do |
| :--- | :--- |
| `No matching MoonBot service` | Run `mb --help`; supply the exact service name or enter its folder |
| `More than one MoonBot service matches` | Use the full name, including `.service`, from the list |
| `The core command channel is unavailable` | Check `systemctl status`; start the intended instance if appropriate. The installed build must support local commands |
| `Unknown command or wrong arguments` | Read `sudo mb "$unit" --help` for the selected build; check spelling and argument count |
| `Core is busy` / `Exchange initialization is busy` | Let initialization finish and check `--status` before changing settings again |
| Service exited with code `78` | The service does not restart itself. Read the journal and today's `logs/LOG_YYYY-MM-DD.log`. `Cannot start MoonBot: data directory is locked or inaccessible` means another copy is using this folder, or `data/lock.dat` cannot be opened. Stop the other copy, or correct access to the data folder if no other copy is running. Do not delete `lock.dat` to clear it: the running process keeps its lock, and a new start can open a different file. `password-protected or invalid configuration` in the trading log means the configuration cannot be loaded: correct it and transfer it again. Starting the service again does not remove either cause |
| Service runs but the client cannot connect | Check MoonProto listener/error fields, the client IP/port/key and both firewalls |

For support, collect the kernel's trading log for the relevant time and the service journal. Do not post API keys, SSH keys, MoonProto connection packages or the full configuration in a public chat.

Related: [kernel and VPS concepts](../concepts/07-kernel-vps-and-infrastructure.md), [kernel settings](settings/README.md), [trading-log messages](exchange-errors-and-logs.md), [systemctl reference](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html).
