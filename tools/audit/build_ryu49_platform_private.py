"""Build frozen platform lifecycle B over private K; no acceptance claim."""
from pathlib import Path, PurePosixPath
from collections import Counter
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
K = ROOT / 'build/verification/root49-integrated-private-build-k'
PACKET = ROOT / 'build/verification/ryu49k-platform-grapple-implementation-b'
OWN = ROOT / 'build/verification/root49k-ryu-platform-private-build-m'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OWN.exists()
    freeze = PACKET / 'implementation-freeze.json'
    assert sha(freeze) == '4cae97bf26926c2f0a17b32af19e696c3f6d4adc377986d1007e9e580abf98c6'
    proposal = json.loads(freeze.read_text())
    archive = ROOT / proposal['parent_archive']
    assert sha(archive) == proposal['parent_archive_sha256']
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 140_000_000 < 30_000_000_000
    OWN.mkdir()
    source = OWN / 'source'
    source.mkdir()
    with zipfile.ZipFile(archive) as z:
        catalog = json.loads(z.read('archived-file-hashes.json'))
        assert len(catalog) == 407 and len(z.namelist()) == proposal['parent_catalog_files'] == 408
        for n, h in catalog.items():
            part = PurePosixPath(n)
            assert not part.is_absolute() and '..' not in part.parts and '\\' not in n
            data = z.read(n)
            assert hashlib.sha256(data).hexdigest() == h
            target = source / n
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    for n, row in proposal['files'].items():
        target = source / n
        if row['before_sha256'] is None:
            assert n not in catalog and not target.exists()
        else:
            assert catalog[n] == row['before_sha256'] == sha(target)
        replacement = PACKET / row['after_file']
        assert sha(replacement) == row['after_sha256']
        target.write_bytes(replacement.read_bytes())
        catalog[n] = row['after_sha256']
    assert len(catalog) == 408
    out_archive = OWN / 'source-platform-m.zip'
    with zipfile.ZipFile(out_archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(catalog):
            z.writestr(n, (source / n).read_bytes())
        z.writestr('archived-file-hashes.json', json.dumps(catalog, indent=2) + '\n')
    shutil.copytree(ROOT / 'tools/Windows/cc65', source / 'tools/Windows/cc65')
    sys.path.insert(0, str(ROOT / 'build/verification/agent49k-samus-water-up-direction-component-a'))
    from image import Image
    report = dict(status='building-platform-private-only', source408_hashes=catalog,
                  source_archive_sha256=sha(out_archive), proposal_sha256=sha(freeze), script_sha256=sha(Path(__file__)),
                  parent_report_sha256=sha(K / 'report.json'), workspace_before_bytes=used, cases=[], goal_complete=False,
                  proposal_count_qualification='parent_catalog_files408 counts407 source members plus the hash catalog itself.')
    def save():
        (OWN / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    def symbols(im):
        def scope_path(i):
            s = im.scopes[i]
            return (scope_path(s['parent']) if 'parent' in s else ()) + (s.get('name', ''),)
        return Counter((scope_path(s['scope']), s['name'], s['val'], im.segs[s['seg']]['name'])
                       for s in im.data['sym'] if 'scope' in s and 'val' in s and 'seg' in s)
    for mapper in ('mmc3', 'mmc5'):
        with (OWN / f'build-{mapper}.log').open('w', encoding='utf-8') as log:
            done = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=source, stdout=log, stderr=subprocess.STDOUT)
        row = dict(mapper=mapper, exit=done.returncode)
        report['cases'].append(row)
        save()
        assert done.returncode == 0, f'Preserved failed build: {mapper}'
        old = K / f'source/build/smb-crossover-{mapper}.nes'
        new = source / f'build/smb-crossover-{mapper}.nes'
        a, b = Image(old), Image(new)
        assert len(a.raw) == len(b.raw) == 786448
        missing = symbols(a) - symbols(b)
        if missing:
            (OWN / f'legacy-symbol-negative-{mapper}.json').write_text(json.dumps(list(missing.elements()), indent=2) + '\n')
        assert not missing, 'All scoped legacy symbol values must remain'
        assert a.raw[16 + 10 * 8192:16 + 11 * 8192] == b.raw[16 + 10 * 8192:16 + 11 * 8192]
        assert b.ram['RyPlatformSlot'] == a.ram['RyWallScanLast'] + 1
        assert b.ram['RyPlatformCancel'] == b.ram['RyPlatformSlot'] + 1
        assert 0x8000 - (b.ram['RyPlatformCancel'] + 1) == 31
        budgets = {s['name']: dict(start=s['start'], size=s['size']) for s in b.segs.values()
                   if s['name'] in ('ROSTER', 'SPECIAL_ROSTER', 'SAMUS', 'OBJECT', 'COLLISION', 'SRAM')}
        row.update(ROM_sha256=sha(new), DBG_sha256=sha(new.with_suffix('.dbg')), LBL_sha256=sha(new.with_suffix('.lbl')),
                   changed_ROM_bytes=sum(x != y for x, y in zip(a.raw, b.raw)),
                   scoped_legacy_symbol_values_exact=True, SAMUS_bank_exact=True, SRAM_new_bytes=2, SRAM_free_bytes=31,
                   segments=budgets)
        save()
    with (OWN / 'build-original-baseline.log').open('w', encoding='utf-8') as log:
        done = subprocess.run([sys.executable, 'tools/build.py', '--mapper', 'mmc3', '--baseline'], cwd=source, stdout=log, stderr=subprocess.STDOUT)
    assert done.returncode == 0
    baseline = source / 'build/smb-crossover-mmc3-baseline.nes'
    expected = K / 'source/build/smb-crossover-mmc3-baseline.nes'
    assert baseline.read_bytes() == expected.read_bytes()
    assert all(sha(source / n) == h for n, h in catalog.items())
    report.update(status='PASS-platform-build-and-layout-only-not-accepted', source408_exact_after=True,
                  original_baseline_exact=True, original_baseline_sha256=sha(baseline), workspace_after_bytes=workspace_bytes(ROOT))
    save()
    print(json.dumps({k: v for k, v in report.items() if k != 'source408_hashes'}), flush=True)


if __name__ == '__main__':
    main()
