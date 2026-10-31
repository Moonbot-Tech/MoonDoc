# Moonbot performance on trading terminal workloads

For a professional scalping tool, speed comes first. The terminal must keep up with streams of exchange data across many markets, perform calculations, and send orders — especially when market activity surges.

We develop our own compiler, [MoonCompiler](https://github.com/Moonbot-Tech/MoonCompiler), libraries, and data processing algorithms. The Linux version of the Moonbot kernel is built with MoonCompiler. Our goal is to do the required work using as little CPU time and memory as possible.

We evaluate efficiency through measurement. Below, we compare our implementations of several representative trading terminal tasks with typical Rust solutions: the same data, the same result, different resource use. Source code and prebuilt programs are available so you can verify the results yourself.

**How much more CPU time the Rust program needed:**

| Task | Intel | AMD |
| :--- | ---: | ---: |
| **Process almost a million trades** | **+120%** | **+114%** |
| **Parse a large exchange instrument list** | **+298%** | **+272%** |
| **Parse an order book and compute a purchase** | **+51%** | **+40%** |

**Peak memory while parsing the exchange instrument list:**

| Program | Intel | AMD |
| :--- | ---: | ---: |
| **Ours** | **43.5 MiB** | **41.9 MiB** |
| Rust | 123.7 MiB | 124.7 MiB |
| **More memory used by Rust** | **+184%** | **+198%** |

## Processing a stream of trades

The task: parse **957,952 exchange messages**, look up each market by its symbol, and update the last price and turnover for each of **3742 markets**.

The Rust implementation using `serde_json` and `HashMap` needed **more than twice the CPU time**.

[See the example and results →](benchmarks/README.md#trades)

## Parsing the exchange instrument list

When connecting to an exchange, the terminal loads its instruments and their trading parameters. The example uses a **17 MiB JSON document** with 3742 Binance instruments. Both programs parse the response completely and retain access to every field.

Our program uses about a quarter of the CPU time and a third of the peak memory compared with Rust.

[See the example and results →](benchmarks/README.md#exchange)

## Calculating a purchase from the order book

The task: use an order book snapshot to calculate a purchase for a given budget, including the quantity bought, average execution price, and slippage.

Both programs load the levels into numeric arrays and calculate purchases for three different budgets. The workload covers **288 snapshots and more than a million order book levels**. The Rust implementation using typed `serde_json` parsing needs **51% more CPU time on Intel** and **40% more on AMD**.

[Source code of both programs and results →](benchmarks/README.md#orderbook)

---

[How the examples work: source code, prebuilt Linux programs, and run commands](benchmarks/README.md).

[Server kernel and choosing a VPS](../concepts/07-kernel-vps-and-infrastructure.md) · [Open MoonProto SDK](https://github.com/Moonbot-Tech/MoonProto)
