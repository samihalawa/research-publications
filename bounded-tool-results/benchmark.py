"""Deterministic transport study; Python standard library only. MIT licensed."""
import csv
import hashlib
import itertools
import json
import platform
import statistics
from pathlib import Path


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def fixture(n, width, alphabet, reverse=False):
    records = [{"id": i, "text": alphabet * width} for i in range(n)]
    proof = {"state": "verified", "receipt": "R-2026-001"}
    d = {"proof": proof, "records": records}
    return dict(reversed(list(d.items()))) if reverse else d


def blind_prefix(source, budget):
    return encode(source)[:budget]


def character_prefix(source, budget):
    return encode(source).decode("utf-8")[:budget].encode("utf-8")


def record_prefix(source, budget):
    """Valid JSON prefix; no completeness declaration or retrieval path."""
    out = {"proof": source["proof"], "records": []}
    for row in source["records"]:
        candidate = {"proof": source["proof"], "records": out["records"] + [row]}
        if len(encode(candidate)) > budget:
            break
        out = candidate
    return encode(out)


class CoverageStore:
    """In-memory immutable snapshot demo, not an authenticated MCP server.

    Budget applies to serialized application JSON, excluding MCP envelope,
    model tokenization and network framing. Production integration must reserve
    those costs separately. Opaque cursors are server-side lookup keys.
    """
    def __init__(self, source):
        self.source = source
        self.snapshot = hashlib.sha256(encode(source)).hexdigest()[:16]
        self.cursors = {"start": 0}
        self.resources = {}

    def _cursor(self, offset):
        token = hashlib.sha256(f"{self.snapshot}:{offset}".encode()).hexdigest()[:24]
        self.cursors[token] = offset
        return token

    def page(self, budget, cursor="start"):
        if cursor not in self.cursors:
            raise ValueError("unknown cursor")
        start = self.cursors[cursor]
        rows = self.source["records"]

        def envelope(items, end):
            return {"snapshot": self.snapshot, "proof": self.source["proof"],
                    "total": len(rows), "start": start, "returned": len(items),
                    "remaining": len(rows) - end, "complete": end == len(rows),
                    "next": None if end == len(rows) else self._cursor(end),
                    "items": items}

        items = []
        end = start
        while end < len(rows):
            row = rows[end]
            if len(encode(envelope(items + [row], end + 1))) <= budget:
                items.append(row)
                end += 1
                continue
            if items:
                break
            # One record cannot fit: return a content-addressed resource handle.
            raw = encode(row)
            digest = hashlib.sha256(raw).hexdigest()
            uri = "sha256:" + digest
            self.resources[uri] = raw
            ref = {"id": row["id"], "resource": uri, "bytes": len(raw)}
            if len(encode(envelope([ref], end + 1))) > budget:
                raise ValueError("budget cannot hold coverage envelope and reference")
            items.append(ref)
            end += 1
            break
        out = encode(envelope(items, end))
        if len(out) > budget:
            raise ValueError("budget cannot hold envelope")
        return out

    def resource(self, uri):
        raw = self.resources[uri]
        if hashlib.sha256(raw).hexdigest() != uri.removeprefix("sha256:"):
            raise ValueError("resource hash mismatch")
        return raw


def run():
    here = Path(__file__).parent
    rows = []
    for n, width, alphabet, budget, reverse in itertools.product(
        [1, 8, 32, 128], [32, 128, 512, 2048],
        ["a", "é", "中", "😀"], [512, 1024, 2048, 4096], [False, True]
    ):
        source = fixture(n, width, alphabet, reverse)
        for policy in ["blind_prefix", "character_prefix", "record_prefix", "coverage"]:
            store = CoverageStore(source)
            first = (blind_prefix(source, budget) if policy == "blind_prefix" else
                     character_prefix(source, budget) if policy == "character_prefix" else
                     record_prefix(source, budget) if policy == "record_prefix" else
                     store.page(budget))
            try:
                parsed = json.loads(first)
                valid = True
            except (ValueError, UnicodeDecodeError):
                parsed = {}
                valid = False
            returned = parsed.get("records", parsed.get("items", []))
            proof = parsed.get("proof") == source["proof"]
            recovered = list(returned)
            pages, resource_reads, resource_bytes = 1, 0, 0
            if policy == "coverage":
                recovered = []
                cur, seen = "start", set()
                pages = 0
                while cur is not None:
                    if cur in seen:
                        raise AssertionError("cursor cycle")
                    seen.add(cur)
                    page_bytes = store.page(budget, cur)
                    assert len(page_bytes) <= budget
                    page = json.loads(page_bytes)
                    assert page["proof"] == source["proof"]
                    assert page["snapshot"] == store.snapshot
                    assert page["start"] == len(recovered)
                    assert page["remaining"] == n - page["start"] - page["returned"]
                    assert page["complete"] == (page["next"] is None)
                    for row in page["items"]:
                        if "resource" in row:
                            raw = store.resource(row["resource"])
                            resource_reads += 1
                            resource_bytes += len(raw)
                            recovered.append(json.loads(raw))
                        else:
                            recovered.append(row)
                    cur = page["next"]
                    pages += 1
                assert len(recovered) == n
            complete_recovery = recovered == source["records"] and proof
            rows.append(dict(n=n, width=width, alphabet=alphabet, budget=budget,
                reverse=reverse, source_bytes=len(encode(source)), policy=policy,
                valid_json=int(valid), within_budget=int(len(first) <= budget),
                proof_present=int(proof), first_records=len(returned),
                coverage_declared=int(all(k in parsed for k in ["total", "remaining", "complete"])),
                complete_recovery=int(complete_recovery), pages=pages,
                resource_reads=resource_reads, resource_bytes=resource_bytes))
    with (here / "results.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    summary = {}
    for policy in ["blind_prefix", "character_prefix", "record_prefix", "coverage"]:
        sub = [r for r in rows if r["policy"] == policy]
        summary[policy] = {"configurations": len(sub)}
        for key in ["valid_json", "within_budget", "proof_present", "coverage_declared", "complete_recovery"]:
            summary[policy][key] = sum(r[key] for r in sub)
        for key in ["pages", "resource_reads", "resource_bytes", "first_records"]:
            summary[policy][key + "_mean"] = statistics.mean(r[key] for r in sub)
        summary[policy]["pages_max"] = max(r["pages"] for r in sub)
    result = {"python": platform.python_version(), "configurations": len(rows)//4,
              "observations": len(rows), "summary": summary}
    (here / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run()
