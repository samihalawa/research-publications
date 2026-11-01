# Bounded Tool Results with Explicit Coverage

Technical report by Sami Halawa Ribas, version 1.0, 1 November 2026.

Read [paper.md](paper.md), [paper.pdf](paper.pdf) and [case-study.md](case-study.md).

Reproduce with Python 3.10 or later, standard library only:

```sh
python3 benchmark.py
python3 checks.py
```

The factorial experiment produces 512 configurations, four policies and 2,048 observations. `results.csv.gz` contains every observation (decompress to CSV); rerunning creates `results.csv`; `summary.json` contains aggregate counts. `checks.json` lists five additional adversarial checks. No model calls or network access are required. These are synthetic transport checks, not LLM-accuracy or production-performance results. Resource retrieval is outside the bounded page channel and is counted separately.

`CoverageStore` is an in-memory application-result adapter, not a deployed MCP server. MCP discovery pagination and application-result pagination are different contracts. The code does not implement authorization, tenant isolation, expiry, persistence or streaming. Do not expose it directly as a production storage service.

Documents: CC BY 4.0. `benchmark.py` and `checks.py`: MIT (see LICENSE-code). Synthetic output data: CC BY 4.0. AI assistance was used for code, execution and manuscript preparation under the author's direction.
