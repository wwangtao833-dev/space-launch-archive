"""Check the migrated snapshot without changing records."""
import gzip
import json
from pathlib import Path
project = Path(__file__).resolve().parents[1]
for root in (project / 'archive', project / 'publish_archive'):
    if (root / 'manifest.json').exists():
        manifest = json.loads((root / 'manifest.json').read_text())
        if 'yearShards' in manifest:
            break
else:
    raise AssertionError('No sharded archive manifest found')
ids = set()
counts = {str(row['year']): row['count'] for row in manifest['years']}
for shard in manifest['yearShards']:
    grouped = json.loads(gzip.decompress((root / shard['file']).read_bytes()))
    assert sorted(map(int, grouped)) == shard['years']
    for year, rows in grouped.items():
        assert len(rows) == counts[year], year
        for row in rows:
            assert row['id'] not in ids, row['id']
            ids.add(row['id'])
assert len(ids) == manifest['total']
indexed = set()
for shard in manifest['searchShards']:
    rows = json.loads(gzip.decompress((root / shard['file']).read_bytes()))
    assert len(rows) == shard['count']
    for row in rows:
        assert row['id'] not in indexed, row['id']
        indexed.add(row['id'])
assert indexed == ids
print(f'PASS: {len(ids):,} unique records; all yearly files and search indexes agree.')
