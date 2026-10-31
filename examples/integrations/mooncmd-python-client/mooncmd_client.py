#!/usr/bin/env python3
"""
MoonCMD UDP Python Client & GZip-JSON Telemetry Collector (for Moonbot v7.56+ / v7.71+)
Requires Python 3.9+, standard library only.

Implements the MoonCMD remote control and telemetry protocol:
1. Mandatory command signing:
   `hash command` (space-separated), where `hash = HMAC-SHA256(command, hmac_secret)`.
   The MoonCMD server in Moonbot starts only with a port set and a non-empty password.
2. A single UDP socket (`self._sock`) bound to `listen_port` is used both for `sendto`
   and for `recvfrom`: Moonbot remembers the address and port of the last valid command packet
   and sends the `replay` responses and the telemetry stream back to that same address/port.
3. Receiving and decoding GZip-JSON and binary packets from Moonbot:
   - {"cmd": "replay", "bot": "...", "data": "..."}
   - {"cmd": "strats", "bot": "...", "N": 1,
      "data": "##Begin_Strategy\\nActive=-1\\nFVersion=12\\nFIntID=...\\nStrategyName=...\\n...##End_Strategy\\n..."}
     Response to GetStrategiesFull / GetStrategiesActive: several strategies in a row, a long list
     arrives in several packets (the packet number is in "N"). Line order in a block: ##Begin_Strategy, Active
     (0 — disabled, -1 — enabled), FVersion, FIntID, then the parameters. Double quotes are stripped
     from the strategy text in this packet. FIntID is needed to address commands: when a block is
     pasted as plain text into the strategies window it is not preserved, and the strategy gets a new
     number. To paste the whole list in one go, add `##MultiSelection` as the first line — otherwise
     the terminal pastes only the first strategy.
   - {"cmd": "order", "bot": "...", "oid": 123, "sql": "..."}
   - {"cmd": "acc", "bot": "MainFutures", "data": {"A": "1450.25", "T": "3200.00"}}
   - Binary chart fragments for closed trades (with the `SubscribeCharts` subscription): an 8-byte
     service header (`Flag=0, Kind=1, id, blockNum, blocksCount`) before a chunk of the `gzip` stream.
     The client prints only the fragment header; do the concatenation and decompression yourself
     (see `decode_mooncmd_datagram`).
"""

import argparse
import gzip
import hashlib
import hmac
import json
import socket
import struct
from typing import Any


def quote_arg(value: str) -> str:
    """Wraps a command argument in quotes according to the server's parsing rules.

    The server splits the command string on spaces and understands double quotes, so a strategy
    name with a space (`My Shot`) must be passed as `"My Shot"`; a quote inside the name is
    doubled (`Scalp"BTC` → `"Scalp""BTC"`). Without this, the command is addressed to a different
    strategy, and the server response still reports success.
    """
    return '"' + value.replace('"', '""') + '"'


class MoonCmdClient:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 2100,
        hmac_secret: str = "",
        listen_ip: str = "0.0.0.0",
        listen_port: int = 2101,
        timeout: float = 3.0,
    ) -> None:
        if not hmac_secret:
            raise ValueError(
                "A non-empty hmac_secret (UDP commands password) is required: "
                "the MoonCMD server in Moonbot is active only with a password set and requires HMAC-SHA256."
            )
        self.host = host
        self.port = port
        self.hmac_secret = hmac_secret.encode("utf-8")
        self.listen_ip = listen_ip
        self.listen_port = listen_port

        # One shared UDP socket for sending commands and receiving responses (PeerIP:PeerPort)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if listen_port > 0:
            self._sock.bind((listen_ip, listen_port))
        self._sock.settimeout(timeout)

    def _build_packet(self, command: str) -> bytes:
        cmd_clean = command.strip()
        cmd_bytes = cmd_clean.encode("utf-8")
        sig = hmac.new(self.hmac_secret, cmd_bytes, hashlib.sha256).hexdigest()
        return f"{sig} {cmd_clean}".encode("utf-8")

    def send_command(self, command: str, wait_reply: bool = True) -> Any:
        """Signs and sends the command; with `wait_reply`, returns the first packet that arrives.

        The first packet to arrive may be a telemetry packet (`acc`, `order`) that the server sends
        to the same address, rather than the `replay` response to this command. If you need the
        response itself, check the `cmd` field or listen to the stream via `listen_forever`.
        """
        packet = self._build_packet(command)
        self._sock.sendto(packet, (self.host, self.port))
        local_addr = self._sock.getsockname()
        print(f"[MoonCMD {local_addr[0]}:{local_addr[1]} -> {self.host}:{self.port}] Sent: {command}")
        if not wait_reply:
            return None
        try:
            data, addr = self._sock.recvfrom(65535)
            payload = decode_mooncmd_datagram(data)
            print_mooncmd_payload(payload, addr)
            return payload
        except socket.timeout:
            return None

    def get_strategies(self, active_only: bool = False) -> Any:
        """Requests the list of all (GetStrategiesFull) or only active (GetStrategiesActive) strategies with FIntID.

        The response is one or more `strats` packets; only the first packet that arrives is returned here.
        """
        return self.send_command("GetStrategiesActive" if active_only else "GetStrategiesFull")

    def set_param(self, strategy_or_folder: str, param: str, value: str) -> Any:
        """Changes a strategy or folder parameter on the fly."""
        return self.send_command(f"SetParam {quote_arg(strategy_or_folder)} {param} {value}")

    def add_whitelist_token(self, strategy_name: str, token: str) -> Any:
        """Adds a coin to the strategy's White List without overwriting the current list (SetWL+)."""
        return self.send_command(f"SetWL+ {quote_arg(strategy_name)} {token}")

    def add_blacklist_token(self, strategy_name: str, token: str) -> Any:
        """Adds a coin to the strategy's Black List without overwriting the current list (SetBL+)."""
        return self.send_command(f"SetBL+ {quote_arg(strategy_name)} {token}")

    def temp_blacklist(self, hours: int, *coins: str) -> Any:
        """Temporarily blacklists coins for N hours (TempBL +N Coin1 Coin2)."""
        coins_str = " ".join(coins)
        return self.send_command(f"TempBL +{hours} {coins_str}")

    def pause_strategy(self, strategy_name: str, minutes: int = 60) -> Any:
        """
        Temporarily stops a strategy for the given number of minutes via `sgStop {strategy_name} {minutes}`.
        Important: the `SetParam ... AutoBuy NO` command does NOT stop `MoonShot`-type strategies
        (`MoonShot` has no user-facing `AutoBuy` field: the running strategy places the shots itself).
        Use `sgStop` for a targeted strategy pause and `sgStart` to resume.
        """
        return self.send_command(f'sgStop {quote_arg(strategy_name)} {minutes}')

    def resume_strategy(self, strategy_name: str) -> Any:
        """Resumes a strategy via `sgStart "<name>"`."""
        return self.send_command(f'sgStart {quote_arg(strategy_name)}')

    def safe_pause_strategy(self, strategy_name: str, minutes: int = 60) -> Any:
        """Alias for `pause_strategy`: uses `sgStop {strategy_name} {minutes}`."""
        return self.pause_strategy(strategy_name, minutes=minutes)

    def listen_forever(self) -> None:
        """Listens for incoming packets on the same bound socket `self._sock`."""
        local_addr = self._sock.getsockname()
        print(f"[MoonCMD Collector] Listening on UDP {local_addr[0]}:{local_addr[1]} ...")
        self._sock.settimeout(None)
        while True:
            data, addr = self._sock.recvfrom(65535)
            try:
                payload = decode_mooncmd_datagram(data)
                print_mooncmd_payload(payload, addr)
            except Exception as exc:
                print(f"[Error decoding packet from {addr}] {exc}")


def decode_mooncmd_datagram(data: bytes) -> Any:
    """
    Decodes a datagram from Moonbot:
    - Standard GZip-JSON starts with the `1F 8B` signature.
    - Binary chart packets for closed trades (after the `SubscribeCharts` command) carry an 8-byte
      service header (`Flag=0, Kind=1, id, blockNum, blocksCount`) before a chunk of the `gzip` stream.
      The server compresses the chart as a whole and cuts the result into fragments of up to 50,000 bytes,
      so `gzip.decompress` applies only to the concatenated payload of all fragments
      `0..blocksCount-1` with the same `id`, in order. This function does not do the concatenation: it
      returns the fragment metadata (`chart_chunk`).
    - Authorization/format errors (`ERR bad_hmac`, `ERR format`) arrive as plain UTF-8 text.
    """
    if len(data) >= 2 and data[0] == 0x1F and data[1] == 0x8B:
        raw_text = gzip.decompress(data).decode("utf-8", errors="replace")
    elif len(data) >= 8 and data[0] == 0 and data[1] == 1:
        # 8-byte chart fragment header: Flag=0, Kind=1, id:int32, blockNum:u8, blocksCount:u8
        _flag, _kind, order_id, block_num, blocks_count = struct.unpack("<BBiBB", data[:8])
        return {
            "cmd": "chart_chunk",
            "oid": order_id,
            "block": block_num,
            "blocks_count": blocks_count,
            "chunk_bytes": len(data) - 8,
        }
    else:
        raw_text = data.decode("utf-8", errors="replace")
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return raw_text


def print_mooncmd_payload(payload: Any, addr: tuple[str, int]) -> None:
    if isinstance(payload, dict):
        cmd_type = payload.get("cmd", "unknown")
        bot_name = payload.get("bot", "?")
        if cmd_type == "order":
            print(f"[{bot_name} ORDER oid={payload.get('oid')}] {payload.get('sql')}")
        elif cmd_type == "acc":
            acc_data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
            print(f"[{bot_name} BALANCE] Available={acc_data.get('A')} Total={acc_data.get('T')}")
        elif cmd_type == "strats":
            print(f"[{bot_name} STRATS packet #{payload.get('N')}] len={len(str(payload.get('data', '')))}")
        elif cmd_type == "replay":
            print(f"[{bot_name} REPLAY] {payload.get('data')}")
        else:
            print(f"[{bot_name} {cmd_type}] {json.dumps(payload, ensure_ascii=False)}")
    else:
        print(f"[Raw from {addr[0]}:{addr[1]}] {payload}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MoonCMD UDP Client & Collector")
    parser.add_argument("--host", default="127.0.0.1", help="Moonbot IP address")
    parser.add_argument("--port", type=int, default=2100, help="Moonbot UDP Commands Port")
    parser.add_argument("--password", "--hmac-secret", dest="hmac_secret", required=True, help="UDP Commands Password for HMAC-SHA256 (required)")
    parser.add_argument("--cmd", default="", help='Command to send, e.g. \'GetStrategiesFull\' or \'sgStop Shot_1 30\'')
    parser.add_argument("--listen-port", type=int, default=2101, help="Local UDP port bound to the client socket")
    parser.add_argument("--listen", action="store_true", help="Keep listening for incoming telemetry packets after sending command")
    args = parser.parse_args()

    client = MoonCmdClient(
        host=args.host,
        port=args.port,
        hmac_secret=args.hmac_secret,
        listen_port=args.listen_port,
    )
    if args.cmd:
        client.send_command(args.cmd, wait_reply=not args.listen)
    if args.listen:
        client.listen_forever()
