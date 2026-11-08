# Install the Moonbot kernel on a Linux VPS

The native Linux kernel runs Moonbot on a server without a desktop. Connect to it from Moonbot for Windows or [MoonTerminal](https://github.com/Moonbot-Tech/MoonTerminal); trading continues when you close the client or disconnect SSH.

This guide covers **Moonbot 7.73**. For monitoring, logs, exchange changes and updates after installation, see [Linux kernel commands](linux-kernel-commands.md).

## Download and choose an installation method

**Full release distribution:** [MoonBot.zip for Linux x86-64](https://api.moonbot.pro/files/linux/MoonBot.zip).

The release download becomes available when 7.73 is published. If it returns `404`, wait for publication. Use the full distribution for a new installation: `botupdate.zip` is an update package for an existing installation and does not contain the service template or installation instructions.

| Method | What it installs | Best fit |
| :--- | :--- | :--- |
| [Moonbot for Windows wizard](#install-from-moonbot-for-windows) | Full Linux release | Transfer the settings of a working bot or connected kernel |
| [MoonTerminal wizard](#use-moonterminal) | Full Linux release (MoonTerminal v0.65.13 or newer) | Set up a fresh kernel from the terminal without opening an SSH shell |
| [Manual SSH installation](#install-manually-over-ssh) | Full Linux release | Set up a fresh kernel with CLI commands |

The older [Moonbot for Linux package based on Wine](https://moonbot.pro/moonbot-pro/download/linux) runs the Windows desktop application. It is a separate installation route, not this native kernel.

## Prepare the VPS

- **Ubuntu 24.04 x86-64** is the verified system. The native package requires x86-64, systemd and glibc 2.38 or newer. Wine, a graphical desktop, a compiler and Python are not required; the archive includes the libraries and fonts.
- Have SSH access as `root`. The Windows wizard also accepts another administrator account with passwordless `sudo`.
- Choose a separate folder and a free **UDP port** for each kernel. The default MoonProto port is **3000**. Allow it in the provider firewall and, if enabled, the VPS firewall.
- Add the **VPS IP** to the exchange API key's allowed IPs. Use the permissions required for trading, without withdrawal permission.
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

Open **Settings → Cores → Connect a core…**. The same wizard opens when there are no connected kernels.

- **To install through MoonTerminal:** choose **New core on a Linux server**, enter the SSH details, check the server, then follow the installation and exchange-key steps. MoonTerminal v0.65.13 and newer downloads the full release distribution, selects the exchange, enables MoonProto for it, enters the API keys and waits until the exchange login and the terminal connection complete. Earlier MoonTerminal versions install the latest test build instead: update MoonTerminal first.
- **To connect a kernel installed another way** (the Windows wizard or the manual steps below): choose **Connect to a Moonbot core**, enter a name, paste the connection package into **Key**, and press **Connect**.

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
