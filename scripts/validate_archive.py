"""Validate archive integrity, derived fields and search-index consistency."""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ARCHIVE = PROJECT / "archive"
MANIFEST = json.loads((ARCHIVE / "manifest.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((PROJECT / "data" / "schema.json").read_text(encoding="utf-8"))
UTC8 = timezone(timedelta(hours=8))
REPLACEMENT_OR_CONTROL = re.compile(r"\ufffd|\x00")
RECORD_FIELDS = set(SCHEMA["required"])
DATE_FIELDS = set(SCHEMA["properties"]["date"]["properties"])
DATE_REQUIRED = set(SCHEMA["properties"]["date"]["required"])
DATE_PRECISIONS = set(SCHEMA["properties"]["date"]["properties"]["precision"]["enum"])
VEHICLE_FIELDS = set(SCHEMA["properties"]["vehicleDetails"]["required"])


def read_shard(entry: dict):
    path = ARCHIVE / entry["file"]
    payload = path.read_bytes()
    assert entry.get("bytes") == len(payload), f"byte-size mismatch: {entry['file']}"
    assert entry.get("sha256") == hashlib.sha256(payload).hexdigest(), (
        f"SHA-256 mismatch: {entry['file']}"
    )
    return json.loads(gzip.decompress(payload))


def expected_cn(date: dict) -> str | None:
    if not date.get("iso") or date.get("precision") not in {"分钟", "秒"}:
        return None
    instant = datetime.fromisoformat(date["iso"].replace("Z", "+00:00")).astimezone(UTC8)
    pattern = "%Y/%m/%d %H:%M:%S" if date["precision"] == "秒" else "%Y/%m/%d %H:%M"
    return instant.strftime(pattern)


ids: set[str] = set()
records: dict[str, dict] = {}
counts = {str(row["year"]): row["count"] for row in MANIFEST["years"]}
cutoff = datetime.fromisoformat(MANIFEST["cutoff"])

for shard in MANIFEST["yearShards"]:
    grouped = read_shard(shard)
    assert sorted(map(int, grouped)) == shard["years"], shard["file"]
    for year, rows in grouped.items():
        assert len(rows) == counts[year], year
        for row in rows:
            assert set(row) == RECORD_FIELDS, row.get("id", year)
            assert DATE_REQUIRED <= set(row["date"]) <= DATE_FIELDS, row["id"]
            assert row["date"]["precision"] in DATE_PRECISIONS, row["id"]
            assert set(row["vehicleDetails"]) == VEHICLE_FIELDS, row["id"]
            assert row["id"] not in ids, row["id"]
            ids.add(row["id"])
            records[row["id"]] = row
            assert row["date"]["year"] == int(year), row["id"]
            expected = expected_cn(row["date"])
            if expected is not None:
                assert row["date"]["cn"] == expected, row["id"]
            if row["date"].get("iso"):
                instant = datetime.fromisoformat(row["date"]["iso"].replace("Z", "+00:00"))
                assert instant.astimezone(UTC8) <= cutoff, row["id"]
            if row["longitude"] is not None:
                assert -180 <= row["longitude"] <= 180, row["id"]
            if row["latitude"] is not None:
                assert -90 <= row["latitude"] <= 90, row["id"]
            assert not REPLACEMENT_OR_CONTROL.search(
                json.dumps(row, ensure_ascii=False)
            ), row["id"]

assert len(ids) == MANIFEST["total"]

indexed: set[str] = set()
for shard in MANIFEST["searchShards"]:
    rows = read_shard(shard)
    assert len(rows) == shard["count"], shard["file"]
    for item in rows:
        assert item["id"] not in indexed, item["id"]
        indexed.add(item["id"])
        source = records[item["id"]]
        expected = {
            "y": source["date"]["year"],
            "d": source["date"]["cn"],
            "iso": source["date"].get("iso", ""),
            "v": source["vehicle"],
            "f": source["flight"] or source["mission"] or source["flightCode"] or source["flightId"],
            "s": source["siteName"],
            "a": source["agencyName"],
            "t": source["actionType"],
            "result": source["result"],
            "q": source["search"],
        }
        for key, value in expected.items():
            assert item.get(key) == value, f"{item['id']}:{key}"

assert indexed == ids
assert len(MANIFEST["years"]) == 85
assert len(MANIFEST["yearShards"]) == 24
assert len(MANIFEST["searchShards"]) == 8

print(
    f"PASS: {len(ids):,} unique records; 32 shard hashes, fixed UTC+8 times, "
    "year counts and search summaries all agree."
)
