# Install the Moonbot kernel on a Linux VPS

The native Linux kernel runs Moonbot on a server without a desktop. Connect to it from Moonbot for Windows or [MoonTerminal](https://moonterminal.pro/); trading continues when you close the client or disconnect SSH.

This guide covers **Moonbot 7.73**. For monitoring, logs, exchange changes and updates after installation, see [Linux kernel commands](linux-kernel-commands.md).

## Download and choose an installation method

**Full release distribution:** [MoonBot.zip for Linux x86-64](https://api.moonbot.pro/files/linux/MoonBot.zip).

The release download becomes available when 7.73 is published. If it returns `404`, wait for publication. Use the full distribution for a new installation: `botupdate.zip` is an update package for an existing installation and does not contain the service template or installation instructions.

| Method | What it installs | Best fit |
| :--- | :--- | :--- |
| [Moonbot for Windows wizard](#install-from-moonbot-for-windows) | Full Linux release | Transfer the settings of a working bot or connected kernel |
| [MoonTerminal wizard](#use-moonterminal) | Full Linux release; optional demo settings on a new core | Set up a new kernel from the terminal |
| [Manual SSH installation](#install-manually-over-ssh) | Full Linux release | Set up a fresh kernel with CLI commands |

The older [Moonbot for Linux package based on Wine](https://moonbot.pro/moonbot-pro/download/linux) runs the Windows desktop application. It is a separate installation route, not this native kernel.

## Prepare the VPS

- **Ubuntu 24.04 x86-64** is the verified system. The native package requires x86-64, systemd and glibc 2.38 or newer. Wine, a graphical desktop, a compiler and Python are not required; the archive includes the libraries and fonts.
- Have SSH access as `root`. The Windows wizard also accepts another administrator account with passwordless `sudo`.
- Choose a separate folder and a free **UDP port** for each kernel. The default MoonProto port is **3000**. Allow it in the provider firewall and, if enabled, the VPS firewall.
- Add the address the core uses to reach the exchange to that API key's allowed IPs. On a server with one address, that is the server's primary address. MoonTerminal can send one core's exchange connections from another IPv4 address on the same interface ([Outgoing IP](linux-kernel-commands.md#outgoing-ip)); the key must allow that address. Use the permissions required for trading, without withdrawal permission.
- If transferring settings, remove any password required to open the configuration in Windows first. A password-protected configuration cannot start on the Linux kernel.

## Install from Moonbot for Windows

Use Moonbot **7.73 or newer**:

1. Open **Menu → VPS setup** and choose **Install a new core**.
2. Select **Current bot** or **Connected core**, then **Get settings**. Alternatively, use **Select ZIP...** for a previously exported settings archive.
3. Enter the VPS address, SSH user and authentication details. Select your SSH private key or use **Create...** to generate one, then **Check SSH**. The wizard can use the server password to install the selected public key and verify key-based access.
4. Choose the instance folder and MoonProto UDP port, then **Install and check**. The wizard downloads the full release distribution, transfers the selected settings, installs the systemd service and enables startup after a VPS reboot.
5. Wait for the successful MoonProto connection check, then **Copy connection**. This package contains the server address, port and secret key; keep it private.
6. [Connect your client](#connect-and-check-the-result) and check exchange login and trading mode before handing trading over to the VPS.

The selected exchange, API keys, strategies and emulator mode transfer with the settings. **The original bot keeps running**: choose when to stop trading there to avoid unintended simultaneous trading. The report database, history, recorded charts and Windows Telegram session are not transferred by this wizard. The wizard's connection check does not switch your current client to the new kernel.

## Use MoonTerminal

In **MoonTerminal v0.69.2**, open **Settings → Cores → Connect a core…**. The same wizard opens when there are no connected cores.

- **Connect to a Moonbot core** connects to an existing installation without downloading a package. Follow [Connect by key](#connect-by-key).
- **New core on a Linux server** and **Move a core to a Linux server** use the full [MoonBot.zip](https://api.moonbot.pro/files/linux/MoonBot.zip) release. The package includes the `mb` command, installed on the server PATH as `mb` and `moonbot`. A failed download stops installation.

The old v0.65.12 wizard installs a test build. Update MoonTerminal or use the manual release installation below if you still run that version.

### Connect by key

Choose **Windows server** or **This computer**, and enter the UDP port Moonbot should use. The field starts at **3000**. On a Windows server, open that port in the server firewall and in the provider firewall; the screen shows a command for the port you entered. On this computer, no external port is required. The port still has to be free of the terminal's other UDP listeners ([chapter 07](../concepts/07-kernel-vps-and-infrastructure.md)).

In Moonbot, open the green **Info** circle at the bottom left, then **Moon Kernel → Settings → Moon Proto**. If the **Key** row shows a dash, press **New Key** and confirm before you change anything else. **New Key** reloads that window from the last applied settings, so a **Kernel (VPS)** tick or a port you have not applied is dropped. Then tick **Kernel (VPS)**, set the same port, press **Apply**, and use **Test Port** until the port is reported open. Press **Copy Key** only after **Apply**. The key carries the address, port and protocol that were applied, so a copy made before **Apply** still has the previous port. The checklist on this screen says to set version **V0**. If the provider chokes UDP, set **V1** or **V2** instead, press **Apply**, and copy the key again: MoonTerminal reads the protocol from the key, and both sides have to match ([chapter 07](../concepts/07-kernel-vps-and-infrastructure.md)).

Paste the key on the next screen. A name is optional; an empty one is stored as `Moonbot`. When the port inside the key differs from the one you opened, paste a key for the opened port, or press **Connect on port …** to use the port inside the key.

The terminal then waits up to a minute.

- **The core is not responding.** When no packets and no bytes came back, the screen says that no bytes arrived and lists **Test Port**, the server firewall and the provider firewall. If any traffic came back, the screen keeps the connection's own wording.
- **The core rejected the key.** The core answered and refused this key. In that same Moonbot, press **Copy Key** again after **Apply** and paste it. Pasting the same text still starts another attempt.
- **The key has no server address.** You marked Moonbot as a Windows server, but the key has no public host: it falls back to this computer, or the host is localhost. Enter the server's public IP address or host name, without a port. The port already in the key stays. Entering the same address again still retries.
- **Could not connect.** Any other failure shows the connection's own message.

**Remove the core** deletes a connection this attempt added. A key that was already in Settings stays there.

### A new core, and a core moved to Linux

On **New core** without **Demo mode**, the installer does not enable MoonProto before the exchange is chosen. It installs the core, waits until initialization has finished, and lists exchanges. After you pick an exchange it enables MoonProto for that exchange and stores the connection package that exchange returns. Choosing another exchange later replaces the stored package. MoonBot keeps MoonProto settings per exchange, so an exchange that was configured before keeps its own key; the wizard does not copy the previous exchange's key across. While the core is still initializing it refuses the exchange switch, the API keys and MoonProto setup (`Core is busy`). An accepted switch is not a finished one: the wizard waits until the core reports that exchange and is no longer initializing, then sends the API keys and waits for login.

If this terminal cannot save the core's row, login on the server can still finish, but there is no row to connect to. The stuck screen shows that error. **Check again** retries the login and, once initialization has finished, reads the exchange list and that exchange's connection package again. **Fix the keys** is available once the core has listed its exchanges, including before the row exists. Wait until exchange login and the terminal connection both complete.

**Demo mode** is a tick on the **New core on a Linux server** card in v0.69.2. The core installs from that same release and starts on Moonbot's demo settings: Moonbot's demo account on Binance, trading in the emulator, so no trade goes to the exchange. The wizard skips the exchange and API key step and turns MoonProto on for the exchange those settings already use. The done screen shows **Demo mode** and leaves the core in the emulator. Ticking **Demo mode** also selects that card. After the install has started, the tick stays as it was. Only a new core offers it.

To trade on your own account after the wizard finishes, open **Exchange API keys** from the core menu in [Manage the core from MoonTerminal](linux-kernel-commands.md#manage-the-core-from-moonterminal). If the demo login stops before that, **Connect my own keys** opens the exchange and key form in the wizard. **Check again** retries the demo login. The demo account's keys cannot be corrected on that screen.

**Turn off password login** is selected by default for **New core** and **Move a core**. After installation, the wizard disables password and keyboard-interactive SSH login only after verifying key access. Clear the checkbox if you still need password login.

If you entered the provider's password, MoonTerminal first installs its own key for that login and verifies that a new key-authenticated session can reach root without a password. Subsequent steps and later server operations from this terminal use that key for the same login and confirmed host. If key access fails, password login stays as it was and the progress line explains why. If hardening fails after a change, the wizard attempts to restore the previous SSH settings and reports the result; installation continues.

Keep the key file or MoonTerminal data folder that holds this access. Other authorized keys remain usable. Removing the core does not restore password login. If all keys are lost, use the provider's console. The wizard does not otherwise change the server's root-login policy.

If `/etc/ssh/sshd_config.d/00-moon-password.conf` is present, this close and the station's SSH hardening move it aside, because that file would keep password and root login open. A failed close puts it back. A file an earlier successful close already set aside is not restored when a later install rolls back.

MoonTerminal v0.69.2 prepares swap on **New core** and **Move a core** when the server needs it. After the package checksum passes, and before the core's first start, a server with 1 GB of memory or less and with no swap turned on gets a 1 GB file, `/swapfile`. The wizard turns it on and adds it to `/etc/fstab` as swap with `nofail`, so a later boot still tries it and continues if it cannot. The disk must keep at least 2 GB free beside that file. With less free space, no file is made and the progress line says how much is free. A server with more memory, or with swap already on, is left as it is, and the log says nothing about swap. An existing `/swapfile` that is present but not in use is left untouched. If the file cannot be created, the progress line gives the reason and the install continues. The file belongs to the server: removing the core does not remove it, and a later step that fails still leaves it. The manual steps below do not create this file.

Moonbot's own **Menu → VPS setup**, in the build labeled 7.73 N2, uses a different file on the same small server. Before the kernel's first start, a server with 1 GiB of RAM or less and with no swap turned on gets `/swapfile.moonbot`, turned on by the systemd unit `swapfile.moonbot.swap`, when `/` has at least 2 GiB free. The file stays across reboot and after the instance is removed. If that file or unit is already there, or the disk is short, the wizard reports the reason and the install continues. This is not MoonTerminal's `/swapfile`.

### Choose the core's outgoing address

On a server with more than one IPv4 address, MoonTerminal can send the new core's exchange connections from one of them. The address the terminal uses to reach the core stays the server address in the connection package.

On the **New core** check screen, **Outgoing IP** lists **Primary** and the other addresses on the interface of the server's default IPv4 route. **Primary** leaves the core unbound, so exchange traffic leaves from the primary address. Any other choice is applied before the core's first start. When systemd is new enough and the server has one address, the check screen says the outgoing IP is that primary address. A bought address is missing until the server has configured it: restart the server from the provider's panel, press **Back**, and check the server again.

On **Move a core**, **Outgoing IP** on the server step is optional. Leave it empty for the primary address. Another value must be an IPv4 address the server already has on that same interface, such as `203.0.113.12`. Typing the primary address is the same as leaving the field empty.

The server needs systemd 255 or newer (Debian 13, Ubuntu 24.04 and newer). When the server has several addresses and an older systemd, the check screen names that version and the install stays on the primary address. On a move to such a server, leave the field empty. An address on another interface is refused. Changing the address of a core that is already installed, and how to check that it took, is in [Outgoing IP](linux-kernel-commands.md#outgoing-ip).

After the core is connected, status, logs and service actions from the terminal are in [Manage the core from MoonTerminal](linux-kernel-commands.md#manage-the-core-from-moonterminal).

## Install manually over SSH

These steps create a **new instance with fresh settings**. To transfer an existing bot's configuration, use the Windows wizard above.

Log in over SSH and use a root shell (`sudo -i` if you logged in as another administrator). The example installs into `/root/MoonBot-Bybit`; use a new folder for each instance. Run the following block only after the release archive is available. It stops on an error, including a failed download or checksum check:

```sh
(
    set -eu
    apt-get update
    apt-get install -y curl unzip ca-certificates
    mkdir -m 700 /root/MoonBot-Bybit
    cd /root/MoonBot-Bybit
    curl --fail --show-error --location \
        https://api.moonbot.pro/files/linux/MoonBot.zip -o MoonBot.zip
    unzip MoonBot.zip
    sha256sum -c SHA256SUMS
    chmod 700 MoonBot moonbot-update

    unit=$(systemd-escape --path --template=moonbot@.service "$PWD")
    install -m 0644 moonbot@.service /etc/systemd/system/moonbot@.service
    if test ! -e /usr/local/bin/mb || test mb -nt /usr/local/bin/mb; then
        install -p -m 0755 mb /usr/local/bin/mb
    fi
    ln -sfn mb /usr/local/bin/moonbot
    systemctl daemon-reload
    systemctl enable --now "$unit"
    systemctl status "$unit" --no-pager
)
```

The supplied service runs as root; this also allows the kernel to manage its shared Telegram service. A failed installation block may leave the new folder behind: inspect the error before repeating the steps or starting anything from that folder.

Enter the instance folder and inspect startup:

```sh
cd /root/MoonBot-Bybit
mb --status
mb --exchanges
```

If the command channel is not available immediately, check the service status and retry after startup. Wait until `state` is no longer `initializing` before changing the exchange. Use an exact exchange ID from `--exchanges`, for example:

```sh
mb --exchange bybit-futures
mb --status
```

Once the exchange change has finished, enter the API key and secret at the hidden prompts:

```sh
mb --set-api-keys
mb --status
```

For Bitget and OKX, create the exchange key with the passphrase shown by `--exchanges`. Hyperliquid uses a wallet address and the signer's private key; Binance RSA uses an exported RSA package instead of these prompts. See [credentials and exchange commands](linux-kernel-commands.md#connection-exchange-and-api-keys).

After initialization finishes, configure MoonProto. Replace `203.0.113.10` with your VPS IP and use the UDP port you opened in both firewalls:

```sh
mb --setup-moonproto --host 203.0.113.10 --port 3000
mb --status
```

Copy the `key` value from the setup response into the client. To display the saved connection package again, run `mb --moonProtoKey`. Both outputs contain a secret.

Choose the exchange **before** configuring MoonProto: switching to a previously configured exchange also restores its saved connection settings. CLI exchange/key changes follow the same disconnect/login behavior as Windows; the kernel process stays running, but trading and client connections can be interrupted.

## Connect and check the result

In **Moonbot for Windows**, open **Menu → Moon Kernel → Settings**, use **Paste Key**, enable **Terminal**, leave **Kernel (VPS)** off, then **Apply**. In **MoonTerminal**, use the connection-by-key route above.

Check these separately:

1. The service is running and enabled for startup: `systemctl status` and `systemctl is-enabled` for your instance. Run `mb --help` to find its full service name.
2. `mb --status` reports **`state: ready`** after exchange login. If not, read `login_error` and follow the [status reference](linux-kernel-commands.md#reading---status). `ok: true` alone only confirms that the command succeeded.
3. **`moonproto_listening: true`** and an actual client connection confirm different things: a local listener alone does not check the provider firewall or the route from your computer.
4. Check the selected exchange, balance, strategies and **emulator mode** in the client before enabling real trading or stopping the old instance. A successful service start does not perform this handover for you.

For logs, stopping or restarting the kernel, changing keys, and installing later releases, continue with [Linux kernel commands](linux-kernel-commands.md).
