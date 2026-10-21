"""Build frozen Ryu source-overlap candidate privately over N; no promotion."""
from pathlib import Path, PurePosixPath
from collections import Counter
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
N = ROOT / 'build/verification/root49-combined-private-build-n'
PACKET = ROOT / 'build/verification/ryu49n-platform-source-admission-h2'
OWN = ROOT / 'build/verification/root49n-ryu-overlap-private-build-o2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def segment(debug, name):
    rows = [line for line in debug.read_text().splitlines()
            if line.startswith('seg\t') and f'name="{name}"' in line]
    assert len(rows) == 1
    return {k: int(re.search(rf'(?:^|,){k}=([^,]+)', rows[0].split('\t', 1)[1])[1], 0)
            for k in ('start', 'size', 'ooffs')}


def label_pairs(path):
    return Counter(tuple(line.split()) for line in path.read_text().splitlines() if line.strip())


def main():
    assert not OWN.exists()
    frozen = PACKET / 'implementation-freeze.json'
    assert sha(frozen) == 'fc4c1fcebf6ffe485f145e5d990c7b1a540c9e4472442823c4db7154e2849d63'
    f = json.loads(frozen.read_text())
    for n, pin in f['files'].items():
        assert sha(PACKET/n) == pin['sha256'] and (PACKET/n).stat().st_size == pin['bytes']
    contract = json.loads((PACKET/'contract.json').read_text())
    assert sha(N/'report.json') == contract['parent_report_sha256']
    built = json.loads((N/'report.json').read_text())
    cat = built['source408_hashes']
    assert len(cat) == 408 and cat == contract['parent_source408']
    assert all(sha(N/'source'/n) == h for n, h in cat.items())
    archive = N/'source-combined-n.zip'
    assert sha(archive) == contract['parent_archive_sha256']
    sys.path.insert(0, str(ROOT/'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 140_000_000 < 30_000_000_000
    OWN.mkdir()
    source = OWN/'source'
    source.mkdir()
    with zipfile.ZipFile(archive) as z:
        assert json.loads(z.read('archived-file-hashes.json')) == cat
        for n, h in cat.items():
            part = PurePosixPath(n)
            assert not part.is_absolute() and '..' not in part.parts and '\\' not in n
            data = z.read(n)
            assert hashlib.sha256(data).hexdigest() == h
            p = source/n
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
    done = subprocess.run([sys.executable, str(PACKET/'materialize_private.py'), '--source-root', str(source), '--apply'], cwd=ROOT)
    assert done.returncode == 0
    cat = dict(cat)
    cat.update(contract['source_after'])
    assert len(cat) == 409 and all(sha(source/n) == h for n, h in cat.items())
    saved = OWN/'source-overlap-o.zip'
    with zipfile.ZipFile(saved, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(cat):
            z.writestr(n, (source/n).read_bytes())
        z.writestr('archived-file-hashes.json', json.dumps(cat, indent=2)+'\n')
    shutil.copytree(ROOT/'tools/Windows/cc65', source/'tools/Windows/cc65')
    report = dict(status='building-private-overlap-only', accepted_release=False, goal_complete=False,
                  script_sha256=sha(Path(__file__)), frozen_packet_sha256=sha(frozen),
                  parent_report_sha256=sha(N/'report.json'), source409_hashes=cat,
                  source_archive_sha256=sha(saved), workspace_before_bytes=used, cases=[])
    def save():
        (OWN/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    save()
    for mapper in ('mmc3', 'mmc5'):
        with (OWN/f'build-{mapper}.log').open('w', encoding='utf-8') as log:
            result = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=source, stdout=log, stderr=subprocess.STDOUT)
        row = dict(mapper=mapper, exit=result.returncode)
        report['cases'].append(row)
        save()
        assert result.returncode == 0, str(OWN/f'build-{mapper}.log')
        old = N/'source/build'/f'smb-crossover-{mapper}.nes'
        new = source/'build'/old.name
        a, b = old.read_bytes(), new.read_bytes()
        assert len(a) == len(b) == 786448
        roster = segment(old.with_suffix('.dbg'), 'ROSTER')
        current = segment(new.with_suffix('.dbg'), 'ROSTER')
        obj = segment(old.with_suffix('.dbg'), 'OBJECT')
        assert current['ooffs'] == roster['ooffs'] and 0 < current['size']-roster['size'] <= 768
        assert segment(new.with_suffix('.dbg'), 'OBJECT') == obj
        changed = [i for i, (x,y) in enumerate(zip(a,b)) if x != y]
        assert changed and all(obj['ooffs'] <= i < obj['ooffs']+obj['size'] or
                               roster['ooffs']+roster['size'] <= i < current['ooffs']+current['size']
                               for i in changed)
        assert a[16+10*8192:16+11*8192] == b[16+10*8192:16+11*8192]
        assert not (label_pairs(old.with_suffix('.lbl')) - label_pairs(new.with_suffix('.lbl'))), 'Old flat label/address pairs must all remain; not a scoped DBG assertion.'
        row.update(ROM_sha256=sha(new), DBG_sha256=sha(new.with_suffix('.dbg')), LBL_sha256=sha(new.with_suffix('.lbl')),
                   MAP_sha256=sha(new.with_suffix('.map')), changed_bytes=len(changed),
                   changed_physical_PRG_banks=sorted({(i-16)//8192 for i in changed}),
                   old_flat_label_pairs_retained=True, SAMUS_bank10_literal=True,
                   OBJECT_segment_size_unchanged=True, ROSTER_appended_bytes=current['size']-roster['size'],
                   all_other_ROM_bytes_literal_N=True)
        save()
    with (OWN/'build-original-baseline.log').open('w', encoding='utf-8') as log:
        result = subprocess.run([sys.executable, 'tools/build.py', '--mapper', 'mmc3', '--baseline'], cwd=source, stdout=log, stderr=subprocess.STDOUT)
    assert result.returncode == 0
    baseline = source/'build/smb-crossover-mmc3-baseline.nes'
    assert baseline.read_bytes() == (N/'source/build/smb-crossover-mmc3-baseline.nes').read_bytes()
    assert all(sha(source/n) == h for n, h in cat.items())
    report.update(status='PASS-private-Ryu-overlap-build-only', original_baseline_sha256=sha(baseline),
                  source409_exact_after=True, workspace_after_bytes=workspace_bytes(ROOT),
                  qualification='No targeted native/source, full regression, ordinary route or release acceptance. Shared/root N unchanged; audio optimization excluded.')
    save()
    print(json.dumps({k:v for k,v in report.items() if k!='source409_hashes'}), flush=True)


if __name__ == '__main__':
    main()
