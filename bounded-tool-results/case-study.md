---
title: "Preserving Evidence in Bounded Agent Tool Results"
date: "2026-11-01"
author: "Sami Halawa"
summary: "An executable transport study across 512 synthetic configurations separates valid JSON, byte budgets, explicit coverage and complete retrieval."
slug: "bounded-agent-tool-results"
tags: ["AI Agents", "MCP", "Python", "Evaluation", "Case Study"]
---

A tool can return valid JSON and still leave an agent unable to tell whether the list is complete. That distinction matters whenever an agent has to inspect every record, preserve a workflow status or prove that it has exhausted a search.

This engineering study implements a small Python adapter that keeps those states explicit. It is a reproducible prototype with measured transport behavior. It has not been deployed as a FastAPI or LangGraph production service.

## The problem

A response budget often becomes a string slice. Byte slicing can break JSON or UTF-8. Character slicing can exceed a byte limit when the response contains accented text, Chinese characters or emoji. Selecting whole records fixes parsing, but a bare shortened list does not explain how much was omitted.

Recent research on information attrition in agent harnesses motivated the experiment. The new implementation and synthetic inputs are separate from that research's kernel-trace environment.

## What was built

The adapter packs whole records into a complete serialized envelope. Every page includes a snapshot identifier, the source status field, total and returned counts, remaining coverage, a completeness flag and a continuation cursor. Records that cannot fit are represented by content-addressed references, with explicit lengths and verified retrieval.

The implementation measures UTF-8 bytes after serialization. Its page budget excludes MCP wrappers and model tokens; those must be budgeted separately in an integration. Full resource reads are outside the page budget and are counted as additional traffic.

## The experiment

The deterministic suite combines four record counts, four text widths, four alphabets, four budgets and two top-level field orders: 512 configurations and 2,048 observations across four policies. It uses synthetic records only and makes no model calls.

| Delivery policy | Valid JSON | Byte budget respected | Exact source reconstruction |
| --- | ---: | ---: | ---: |
| Byte prefix | 120 / 512 | 512 / 512 | 120 / 512 |
| Character prefix | 160 / 512 | 208 / 512 | 160 / 512 |
| Whole-record prefix | 512 / 512 | 512 / 512 | 120 / 512 |
| Explicit coverage and exhaustive retrieval | 512 / 512 | 512 / 512 | 512 / 512 |

The last row includes every required continuation and resource read. It does not show that an LLM will follow those steps. The whole-record baseline retains the same status field as the coverage adapter, so its lower reconstruction result comes from incomplete record delivery rather than a deliberately removed status.

## The tradeoff

The coverage adapter needs an average of 25.60 pages and 16.50 resource reads across this deliberately broad grid, with up to 128 pages. Referenced contents add an average of approximately 61.4 kB per configuration. Complete retrieval can be expensive. A production client should retrieve the subset needed for a decision or use a bulk artifact when the task requires the whole collection.

Five adversarial checks also passed: empty results, insufficient envelope budget, unknown cursors, corrupt resources and cross-snapshot cursors. The in-memory adapter still needs authorization, persistent storage, expiration and bounded resource streaming before production deployment.

## Applying the result

For a FastAPI endpoint or LangGraph node, the useful integration is a completion gate that distinguishes records returned, records inspected and records still available. Measure the final wrapped output, keep retrieval costs visible and verify the provider's actual state separately. A digest checks bytes; it does not establish that a receipt is authentic or a business action succeeded.

The result of this case study is an executable contract and a reproducible dataset. Improved task accuracy, latency and operating cost would require a separate evaluation with real workloads and model-driven clients.

**Paper, code and raw results:** [Research package](https://github.com/samihalawa/research-publications/tree/main/bounded-tool-results).

**Research reference:** Sehgal, Panahandeh and Ezzati-Jivan (2026), [Context Is a Pipeline, Not a Window](https://arxiv.org/abs/2610.36114).

Prepared with AI assistance under Sami Halawa Ribas's direction. The assistant generated and ran the reference implementation and prepared the manuscript. This is an engineering research prototype, not a claim of a deployed customer outcome or peer review.
