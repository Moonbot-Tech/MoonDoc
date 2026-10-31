# Performance examples: download and verify

[← Comparison results](../README.md)

The examples compare trade processing, exchange instrument parsing, and purchase calculations from an order book. Our programs are built with MoonCompiler for Linux; the Rust implementations use `serde_json`. Each task uses identical input data and checks the computed results.

## Run the prebuilt programs

The [example set](https://github.com/Moonbot-Tech/MoonCompiler/tree/main/qualification/performance/showcase) contains the source code, the input data, and **[prebuilt Linux x86-64 programs for both sides](https://github.com/Moonbot-Tech/MoonCompiler/tree/main/qualification/performance/showcase/bin/linux-x86_64)**. No compilers are needed to run them.

You need Linux with glibc 2.34+, `libgcc_s.so.1`, Python 3.11+, Git, and the usual utilities `bash`, `tar`, `sha256sum`, `taskset`.

```sh
git clone --depth 1 https://github.com/Moonbot-Tech/MoonCompiler.git
cd MoonCompiler/qualification/performance/showcase
./reproduce.sh run
```

The run checks the answers and prints CPU time and memory use. Detailed results are saved as JSON.

## Build it yourself

From the same folder:

```sh
./reproduce.sh build
./reproduce.sh run
```

[Requirements and build commands](https://github.com/Moonbot-Tech/MoonCompiler/blob/main/qualification/performance/showcase/README.md). The required Common units are included in the set; the MoonCompiler SDK and the open-source MoonORMot are available through the links in the instructions.

## What the examples do

<a id="trades"></a>

### Trades: parsing messages and tracking turnover

**Input:** 239,488 synthetic Binance `aggTrade` messages across 3742 markets, four passes — **957,952 messages processed**.

From every message the programs extract the ticker, price, and quantity, find the market in a dictionary, and add `price × quantity` to its turnover. The trade count, last price, and turnover of every market are checked.

[Our program — `RunTrades`](https://github.com/Moonbot-Tech/MoonCompiler/blob/main/qualification/performance/showcase/showcase_moon.dpr) · [Rust — `run_trades`](https://github.com/Moonbot-Tech/MoonCompiler/blob/main/qualification/performance/showcase/showcase.rs)

<a id="exchange"></a>

### Exchange instruments: parsing the full JSON document

**Input:** a saved Binance `exchangeInfo` response, **17 MiB and 3742 instruments**.

Both programs parse the document and keep access to every field. The check compares the entire content. Here both the parsing time and the memory held by the process with the parsed document are measured.

[Our program — `RunExchange`](https://github.com/Moonbot-Tech/MoonCompiler/blob/main/qualification/performance/showcase/showcase_moon.dpr) · [Rust — `run_exchange`](https://github.com/Moonbot-Tech/MoonCompiler/blob/main/qualification/performance/showcase/showcase.rs)

<a id="orderbook"></a>

### Order book: calculating a purchase and its slippage

**Input:** order book snapshots with 100, 1000, and 5000 levels per side. Per run — **288 snapshots and more than a million levels**.

The programs turn prices and volumes into numeric arrays and compute purchases for three amounts: a small one, one that reaches into the depth of the book, and one that exceeds the available liquidity. All levels, the quantity bought, the amount spent, the average and last price, the slippage, and the unspent balance are checked.

[Our program](https://github.com/Moonbot-Tech/MoonCompiler/blob/main/qualification/performance/showcase/orderbook/orderbook_moon.dpr) · [Rust](https://github.com/Moonbot-Tech/MoonCompiler/blob/main/qualification/performance/showcase/orderbook/orderbook.rs)

## How the results are compared

Both programs run in turn on one CPU core; the result is the median of five runs of each. Preparing the files is not part of the processing time. The computations are verified by an independent Python calculation.

CPU is the processor time used by the program. Memory is the peak resident memory of the whole process (RSS), in MiB. The percentages on the main page show how much more of a resource Rust needed: `(Rust / our program − 1) × 100%`.

[How the set is organized, dependencies, and run results](https://github.com/Moonbot-Tech/MoonCompiler/blob/main/qualification/performance/showcase/README.md)
