"""Exact reversible storage for completed old positive-fixture compiler DBGs.

Native logs, traces, summaries, ROMs, source, and all route evidence stay literal.
"""
from pathlib import Path
import gzip
import hashlib
import json
import sys

import compact_old_checkpoint_debug49 as engine

ROOT = Path(__file__).resolve().parents[2]
OWN = ROOT / 'build/verification/root-old-positive-fixture-debug49-compaction-a'
BASE = ROOT / 'build/checkpoint-tests'
POSITIVE_FOLDERS = {
    'root-menu-gold-v32-positive-a', 'root-source-v29-outline-cache-b',
    'root-source-v29-render-controls-c', 'root-source-v30-focused-a',
    'root-source-v31-focused-a', 'root-v32-fixture-migrations-a',
    'root-v32-fixture-migrations-confirm-b',
}
sha = engine.sha

def prepare():
    assert not OWN.exists()
    inventory = ROOT / 'build/verification/root-old-debug49-storage-inventory-b.json'
    rows = []
    for r in json.loads(inventory.read_text())['rows']:
        raw = ROOT / r['path']
        if not raw.resolve().is_relative_to(BASE.resolve()) or not r['exact_debug_counterpart']:
            continue
        if raw.parent.parent != BASE or raw.parent.name not in POSITIVE_FOLDERS:
            continue
        canonical = [x for x in r['canonical'] if 1 <= x['version'] <= 32 and x['debug_sha256'] == r['sha256']]
        if not canonical:
            continue
        summary = raw.parent / 'summary.json'
        assert summary.is_file()
        data = json.loads(summary.read_text(encoding='utf-8-sig'))
        assert isinstance(data, list) and data and all(x['exit'] == 0 for x in data)
        assert any(x['rom_sha256'] == r['ROM_sha256'] for x in data)
        sibling = ROOT / r['sibling_ROM']
        assert sha(raw) == r['sha256'] and sha(sibling) == r['ROM_sha256']
        c = canonical[0]
        manifest = ROOT / c['manifest']
        assert sha(manifest) == c['manifest_sha256']
        assert sha(ROOT / c['ROM']) == r['ROM_sha256']
        canonical_gzip = ROOT / c['debug']
        assert c['debug_storage'] == 'gzip'
        assert hashlib.sha256(gzip.decompress(canonical_gzip.read_bytes())).hexdigest() == sha(raw)
        target = Path(str(raw) + '.gz')
        assert not target.exists()
        payload = raw.read_bytes()
        compressed = gzip.compress(payload, compresslevel=9, mtime=0)
        assert gzip.decompress(compressed) == payload
        stat = raw.stat()
        rows.append(dict(raw=str(raw.relative_to(ROOT)), archive=str(target.relative_to(ROOT)),
                         raw_bytes=len(payload), raw_sha256=sha(raw), gzip_bytes=len(compressed),
                         gzip_sha256=hashlib.sha256(compressed).hexdigest(),
                         mtime_ns=stat.st_mtime_ns, mode=stat.st_mode, version=c['version'],
                         manifest=str(manifest.relative_to(ROOT)), manifest_sha256=sha(manifest),
                         sibling_rom=str(sibling.relative_to(ROOT)), sibling_rom_sha256=sha(sibling),
                         summary=str(summary.relative_to(ROOT)), summary_sha256=sha(summary),
                         canonical_debug=str(canonical_gzip.relative_to(ROOT)),
                         canonical_gzip_sha256=sha(canonical_gzip),
                         completion='Every recorded fixture exit zero; sibling ROM/DBG exactly bound to old canonical checkpoint. No broader acceptance inferred.'))
    assert rows
    selected = {r['raw'] for r in rows}
    protected = {str(p.relative_to(ROOT)): sha(p)
                 for parent in sorted({(ROOT / r['raw']).parent for r in rows})
                 for p in parent.rglob('*') if p.is_file() and str(p.relative_to(ROOT)) not in selected}
    for r in rows:
        for n in ('manifest', 'canonical_debug'):
            protected[r[n]] = sha(ROOT / r[n])
    plan = dict(status='prepared-not-applied', script_sha256=sha(Path(engine.__file__)),
                preparation_script_sha256=sha(Path(__file__)), inventory_sha256=sha(inventory),
                rows=rows, protected=protected, scope=__doc__,
                historical_dependency='Restore exact raw from sibling gzip before any historical caller needs it; existing receipts unchanged.')
    plan['summary'] = dict(files=len(rows), raw_bytes=sum(r['raw_bytes'] for r in rows), gzip_bytes=sum(r['gzip_bytes'] for r in rows))
    plan['summary']['saved_bytes'] = plan['summary']['raw_bytes'] - plan['summary']['gzip_bytes']
    OWN.mkdir()
    path = OWN / 'plan.json'
    path.write_text(json.dumps(plan, indent=2) + '\n')
    print(json.dumps(dict(plan_sha256=sha(path), **plan['summary'])), flush=True)

if __name__ == '__main__':
    if sys.argv[1:] == ['prepare']:
        prepare()
    else:
        engine.OWN = OWN
        engine.CP = BASE
        engine.main()
