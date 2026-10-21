"""Losslessly store the exact233 old positive label copies in frozen inventory S.

Uses existing exact canonical gzip bytes. All route/native/current48/49 data,
source, ROMs and prior receipts remain untouched. Restore raw paths before reuse.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT/'build/verification/mm48-old-label-storage-inventory-s'
OWN = ROOT/'build/verification/root-old-positive-labels49-compaction-a'
FREEZE = '9b4ed03c0840b1520ba326fee8b77e438745834f8e960b00b3a5a7fe28fe37d4'
HELPER = ROOT/'tools/audit/compact_old_canonical_metadata49.py'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = lambda b: hashlib.sha256(b).hexdigest()
spec = importlib.util.spec_from_file_location('old_storage_composition', HELPER)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
old.OWN = OWN


def source():
    assert sha(PACKET/'frozen.json') == FREEZE
    f = json.loads((PACKET/'frozen.json').read_text())
    assert f['summary'] == dict(files=233,raw_bytes=119377328,known_archive_bytes=32231507,known_savings_bytes=87145821)
    for n,r in f['files'].items():
        assert (PACKET/n).stat().st_size == r['bytes'] and sha(PACKET/n) == r['sha256']
    for n,r in f['inputs'].items():
        assert (ROOT/n).stat().st_size == r['bytes'] and sha(ROOT/n) == r['sha256'], n
    return f


def raw_target(row):
    p = ROOT/row['raw']
    assert p.suffix == '.lbl' and p.resolve().is_relative_to(ROOT.resolve())
    assert row['raw'].startswith(('build/profiling/','build/verification/'))
    assert not re.search(r'route|roster-through-2-2|controller|playthrough|capture|recording|native|negative|failure|failed|rejected|sourceproof|(?<!\d)(?:48|49)(?!\d)',row['raw'],re.I)
    assert row['archive'] == row['raw']+'.gz'
    return p


def verify(plan):
    assert sha(Path(__file__)) == plan['script_sha256'] and sha(HELPER) == plan['helper_sha256']
    source()
    old.verify_protected(plan)
    old.verify_composition(plan)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=('prepare','compact','verify','restore-one'))
    ap.add_argument('--plan-sha256')
    ap.add_argument('--path')
    a = ap.parse_args()
    target = OWN/'plan.json'
    if a.action == 'prepare':
        assert not OWN.exists()
        f = source()
        rows = f['allowlist']
        assert len(rows) == len({r['raw'] for r in rows}) == 233
        for r in rows:
            p = raw_target(r)
            assert p.is_file() and not (ROOT/r['archive']).exists()
            assert p.stat().st_size == r['raw_bytes'] and sha(p) == r['raw_sha256']
            payload = (ROOT/r['canonical_label_archive']).read_bytes()
            assert len(payload) == r['known_archive_bytes'] and digest(payload) == r['known_archive_sha256']
            assert gzip.decompress(payload) == p.read_bytes() and p.read_bytes().startswith(b'al ')
        plan = dict(status='prepared-not-applied',script_sha256=sha(Path(__file__)),helper_sha256=sha(HELPER),
                    source_freeze_sha256=FREEZE,scope=__doc__,rows=rows,summary=f['summary'],
                    protected=old.protected(rows),earlier_immutable_plan_composition=old.old_plan_overlaps(rows))
        OWN.mkdir()
        target.write_text(json.dumps(plan,indent=2)+'\n')
        verify(plan)
        print(json.dumps(dict(plan_sha256=sha(target),**f['summary'])),flush=True)
        return
    assert a.plan_sha256 and sha(target) == a.plan_sha256
    plan = json.loads(target.read_text())
    verify(plan)
    if a.action == 'compact':
        assert not (OWN/'receipt.json').exists()
        sys.path.insert(0,str(ROOT/'tools/playthroughs'))
        from roster_run import workspace_bytes
        used = workspace_bytes(ROOT)
        assert used+plan['summary']['known_archive_bytes']+2_000_000 < 30_000_000_000
        stage = OWN/'stage'
        stage.mkdir()
        for i,r in enumerate(plan['rows']):
            p = raw_target(r)
            assert p.stat().st_size == r['raw_bytes'] and sha(p) == r['raw_sha256']
            assert not (ROOT/r['archive']).exists()
            payload = (ROOT/r['canonical_label_archive']).read_bytes()
            assert digest(payload) == r['known_archive_sha256']
            with (stage/f'{i}.gz').open('xb') as f:
                f.write(payload);f.flush();os.fsync(f.fileno())
            assert digest(gzip.decompress((stage/f'{i}.gz').read_bytes())) == r['raw_sha256']
        verify(plan)  # Every backup exists durably before any raw path changes.
        for i,r in enumerate(plan['rows']):
            p = raw_target(r)
            assert sha(p) == r['raw_sha256'] and not (ROOT/r['archive']).exists()
            (stage/f'{i}.gz').replace(ROOT/r['archive'])
            assert sha(ROOT/r['archive']) == r['known_archive_sha256']
            assert digest(gzip.decompress((ROOT/r['archive']).read_bytes())) == r['raw_sha256']
            p.unlink()
        stage.rmdir()  # Empty only; no recursive removal.
    elif a.action == 'restore-one':
        matches = [r for r in plan['rows'] if r['raw'] == a.path]
        assert len(matches) == 1
        r = matches[0];p = raw_target(r)
        assert not p.exists() and sha(ROOT/r['archive']) == r['known_archive_sha256']
        raw = gzip.decompress((ROOT/r['archive']).read_bytes())
        assert len(raw) == r['raw_bytes'] and digest(raw) == r['raw_sha256']
        with p.open('xb') as f:
            f.write(raw);f.flush();os.fsync(f.fileno())
        os.chmod(p,r['mode']);os.utime(p,ns=(r['mtime_ns'],r['mtime_ns']))
    verify(plan)
    for r in plan['rows']:
        assert sha(ROOT/r['archive']) == r['known_archive_sha256']
        raw = gzip.decompress((ROOT/r['archive']).read_bytes())
        assert len(raw) == r['raw_bytes'] and digest(raw) == r['raw_sha256']
        if (ROOT/r['raw']).exists():
            assert sha(ROOT/r['raw']) == r['raw_sha256']
    output = OWN/('receipt.json' if a.action == 'compact' else 'verification.json' if a.action == 'verify' else 'restore-receipt.json')
    assert not output.exists()
    receipt = dict(status='PASS_EXACT_REVERSIBLE_OLD_POSITIVE_LABEL_STORAGE',action=a.action,
                   plan_sha256=sha(target),summary=plan['summary'],all233_roundtrips_exact=True,
                   durable_backups_before_raw_unlink=True,earlier_plan_logical_hashes_exact=True,
                   historical_raw_restore_required=True,route_native_source_ROM_current48_49_changes=0,
                   previous_receipts_modified=0,completion_scope_not_upgraded=True)
    if a.action == 'restore-one':
        receipt['restored_path'] = a.path
    output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt),flush=True)


if __name__ == '__main__':
    main()
