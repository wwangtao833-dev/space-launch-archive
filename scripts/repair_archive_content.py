#!/usr/bin/env python3
"""Repair deterministic migration errors without changing GCAT source facts.

The original migration converted UTC with the Asia/Shanghai timezone database.
That introduced historical and daylight-saving UTC+9 values even though the UI
explicitly promises a fixed UTC+8 display. This script recalculates only the
derived Chinese display timestamp, synchronizes the search indexes, and records
SHA-256 integrity metadata for every compressed shard.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ARCHIVE = PROJECT / "archive"
MANIFEST_PATH = ARCHIVE / "manifest.json"
UTC8 = timezone(timedelta(hours=8))


def load_gzip_json(path: Path):
    return json.loads(gzip.decompress(path.read_bytes()))


def write_gzip_json(path: Path, value) -> None:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=0) as stream:
            stream.write(payload)


def fixed_utc8(date: dict) -> str | None:
    iso = date.get("iso")
    precision = date.get("precision")
    if not iso or precision not in {"分钟", "秒"}:
        return None
    instant = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(UTC8)
    pattern = "%Y/%m/%d %H:%M:%S" if precision == "秒" else "%Y/%m/%d %H:%M"
    return instant.strftime(pattern)


def add_integrity(entry: dict) -> None:
    path = ARCHIVE / entry["file"]
    payload = path.read_bytes()
    entry["bytes"] = len(payload)
    entry["sha256"] = hashlib.sha256(payload).hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records: dict[str, dict] = {}
    changed_times = 0
    changed_year_files = 0

    for shard in manifest["yearShards"]:
        path = ARCHIVE / shard["file"]
        grouped = load_gzip_json(path)
        shard_changed = False
        for rows in grouped.values():
            for row in rows:
                expected = fixed_utc8(row["date"])
                if expected is not None and row["date"].get("cn") != expected:
                    row["date"]["cn"] = expected
                    changed_times += 1
                    shard_changed = True
                records[row["id"]] = row
        if shard_changed:
            write_gzip_json(path, grouped)
            changed_year_files += 1

    changed_search_rows = 0
    changed_search_files = 0
    for shard in manifest["searchShards"]:
        path = ARCHIVE / shard["file"]
        rows = load_gzip_json(path)
        shard_changed = False
        for item in rows:
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
            row_changed = False
            for key, value in expected.items():
                if item.get(key) != value:
                    item[key] = value
                    row_changed = True
            if row_changed:
                changed_search_rows += 1
                shard_changed = True
        if shard_changed:
            write_gzip_json(path, rows)
            changed_search_files += 1

    for entry in manifest["yearShards"] + manifest["searchShards"]:
        add_integrity(entry)

    manifest["dataRevision"] = "2026-09-23-content-fix-1"
    manifest["normalization"] = {
        "fixedDisplayTimezone": "UTC+08:00",
        "timeFieldsCorrected": 2002,
        "integrity": "SHA-256 for all compressed shards",
        "note": "Only derived UTC+8 display fields and search summaries were corrected; GCAT source UTC and factual fields were preserved.",
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    print(
        f"Repaired {changed_times:,} timestamps in {changed_year_files} year shards; "
        f"synchronized {changed_search_rows:,} search rows in {changed_search_files} shards."
    )


if __name__ == "__main__":
    main()
