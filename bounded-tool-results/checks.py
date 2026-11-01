"""Adversarial checks for the reference implementation. Run after benchmark.py."""
import json
from pathlib import Path
from benchmark import CoverageStore, fixture

checks = []

def check(name, fn):
    fn(); checks.append(name)

def empty():
    p = json.loads(CoverageStore(fixture(0, 0, "a")).page(512))
    assert p["complete"] and p["remaining"] == 0 and p["items"] == []

def short_budget():
    try:
        CoverageStore(fixture(1, 1000, "a")).page(64)
    except ValueError:
        return
    raise AssertionError("oversized envelope should be rejected")

def invalid_cursor():
    try:
        CoverageStore(fixture(1, 32, "a")).page(512, "fabricated")
    except ValueError:
        return
    raise AssertionError("unknown cursor accepted")

def corruption():
    store = CoverageStore(fixture(1, 2048, "中"))
    ref = json.loads(store.page(512))["items"][0]["resource"]
    store.resources[ref] = b'{}'
    try:
        store.resource(ref)
    except ValueError:
        return
    raise AssertionError("corruption accepted")

def cross_snapshot():
    a = CoverageStore(fixture(8, 128, "a"))
    cursor = json.loads(a.page(512))["next"]
    b = CoverageStore(fixture(8, 128, "中"))
    try:
        b.page(512, cursor)
    except ValueError:
        return
    raise AssertionError("foreign cursor accepted")

for name, fn in [("empty_snapshot", empty), ("envelope_underflow", short_budget),
                 ("unknown_cursor", invalid_cursor), ("resource_corruption", corruption),
                 ("cross_snapshot_cursor", cross_snapshot)]:
    check(name, fn)
result = {"passed": len(checks), "checks": checks}
Path(__file__).with_name("checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
