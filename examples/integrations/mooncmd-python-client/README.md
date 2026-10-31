# Python client and telemetry collector for the `MoonCMD` protocol (UDP)

A self-contained script [`mooncmd_client.py`](mooncmd_client.py) (Python 3.9+, standard library only) for sending signed commands to a Moonbot terminal or kernel over UDP and receiving the telemetry stream (`GZip-JSON`).

Full specification of the protocol and all commands: [**`../../../reference/mooncmd-udp-protocol.md`**](../../../reference/mooncmd-udp-protocol.md).

## Architectural features of `MoonCMD`

1. **Mandatory password (`hmac_secret`):** the `MoonCMD` server in Moonbot starts only when a port and a non-empty password are set in the settings, and it verifies the `HMAC-SHA256` signature of every incoming packet.
2. **A single UDP socket for sending and receiving:** on receiving a valid command, Moonbot remembers the sender's address and port and sends the `replay` responses, the `strats` strategy export and the telemetry (`order`, `acc`, `errors`) back to exactly that address. That is why the client binds one socket to `--listen-port` and uses it both for sending and for receiving. The first packet to arrive after a command may be telemetry rather than the response — check the `cmd` field.
3. **Balance packet format (`acc`):** the available and total balance values are sent as strings inside the nested `"data"` object:
   ```json
   {"cmd": "acc", "bot": "MainFutures", "data": {"A": "1450.25", "T": "3200.00"}}
   ```
4. **Strategy export (`GetStrategiesFull` / `GetStrategiesActive`):** the response is `strats` packets with the text of several strategies in a row; a long list arrives in several packets (the packet number is in the `"N"` field). The lines of each block come in the order `##Begin_Strategy`, `Active` (`0` — disabled, `-1` — enabled), `FVersion`, `FIntID`, then the parameters:
   ```json
   {"cmd": "strats", "bot": "MainFutures", "N": 1, "data": "##Begin_Strategy\nActive=-1\nFVersion=12\nFIntID=…\nStrategyName=Shot_1\n…\n##End_Strategy\n"}
   ```
   `FIntID` is needed to address commands. When a block is pasted as plain text into the strategies window it is not preserved — the strategy gets a new number. To paste the dumped list in one go, add `##MultiSelection` as the first line, otherwise the terminal pastes only the first strategy. Double quotes are stripped from the strategy text in this packet.
5. **Targeted strategy pause (`sgStop` / `sgStart`):** to stop a strategy temporarily, use `sgStop {strategy_name} {minutes}` (and `sgStart {strategy_name}`): the `SetParam ... AutoBuy NO` command does not stop `MoonShot`-type strategies, which have no user-facing `AutoBuy` field.
6. **Boolean values in `SetParam` are `YES` / `NO` only:** writing `1` turns the parameter off, and the server response still reports success.
7. **Binary chart fragments:** with the `SubscribeCharts` subscription enabled, the chart packets for closed trades contain an 8-byte service header (`Flag=0, Kind=1, id, blockNum, blocksCount`) before a chunk of the `gzip` stream. The chart is compressed as a whole and cut into fragments, so you need to decompress the concatenation of all fragments with the same `id`, in order. The client prints only the fragment headers.

## Quick start

```bash
# 1. Send an activation/request command and keep listening for responses and the telemetry stream on the same socket (port 2101)
python3 mooncmd_client.py --host 127.0.0.1 --port 2100 --password "YOUR_PASSWORD" --listen-port 2101 --cmd "GetStrategiesFull" --listen

# 2. Temporarily stop a strategy (including MoonShot) for 30 minutes and get the replay response
python3 mooncmd_client.py --host 127.0.0.1 --port 2100 --password "YOUR_PASSWORD" --listen-port 2101 --cmd "sgStop Shot_1 30"

# 3. Change a strategy parameter on the fly
python3 mooncmd_client.py --host 127.0.0.1 --port 2100 --password "YOUR_PASSWORD" --listen-port 2101 --cmd 'SetParam "Shot_1" MShotPrice 2.5'

# 4. Add a coin to the strategy's White List without overwriting the current list
python3 mooncmd_client.py --host 127.0.0.1 --port 2100 --password "YOUR_PASSWORD" --listen-port 2101 --cmd 'SetWL+ "Shot_1" BTC'
```
