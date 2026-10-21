"""Build the disjoint L water-order and D platform changes in a private checkout."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
K = ROOT / 'build/verification/root49-integrated-private-build-k'
L = ROOT / 'build/verification/root49k-samus-water-private-build-l'
D = ROOT / 'build/verification/root49k-ryu-platform-private-build-m-d'
OWN = ROOT / 'build/verification/root49-combined-private-build-n'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OWN.exists()
    reports = [json.loads((p / 'report.json').read_text()) for p in (K, L, D)]
    kc, lc, dc = [r[key] for r, key in zip(reports, ['source407_hashes', 'source407_hashes', 'source408_hashes'])]
    assert [n for n, h in lc.items() if kc.get(n) != h] == ['src/samus.s']
    assert 'src/samus.s' not in [n for n, h in dc.items() if kc.get(n) != h]
    assert lc['src/samus.s'] == '3cd1a48badc2638eed283519497e84782f3d6769e45a5d43a4208f622a0fc639'
    assert sha(D / 'source-platform-m-d.zip') == '6e249587eec2ad04405136a04b04bd00f670da29cdfd89dbc97988d41145909e'
    assert sha(L / 'source-water-l.zip') == '133d5ef3274af7825e80f7da2846f7175ee32e6f588431868c081054df1a3f98'
    for parent, cat in zip((K, L, D), (kc, lc, dc)):
        assert all(sha(parent / 'source' / n) == h for n, h in cat.items())
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 140_000_000 < 30_000_000_000
    OWN.mkdir()
    source = OWN / 'source'
    source.mkdir()
    with zipfile.ZipFile(D / 'source-platform-m-d.zip') as z:
        cat = json.loads(z.read('archived-file-hashes.json'))
        assert cat == dc and len(cat) == 408
        for n, h in cat.items():
            part = PurePosixPath(n)
            assert not part.is_absolute() and '..' not in part.parts and '\\' not in n
            data = z.read(n)
            assert hashlib.sha256(data).hexdigest() == h
            p = source / n
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
    (source / 'src/samus.s').write_bytes((L / 'source/src/samus.s').read_bytes())
    cat['src/samus.s'] = lc['src/samus.s']
    archive = OWN / 'source-combined-n.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(cat):
            z.writestr(n, (source / n).read_bytes())
        z.writestr('archived-file-hashes.json', json.dumps(cat, indent=2) + '\n')
    shutil.copytree(ROOT / 'tools/Windows/cc65', source / 'tools/Windows/cc65')
    report = dict(status='building-private-combination-only', accepted_release=False, goal_complete=False,
                  script_sha256=sha(Path(__file__)), source408_hashes=cat,
                  parents={p.name: sha(p / 'report.json') for p in (K, L, D)},
                  source_archive_sha256=sha(archive), workspace_before_bytes=used, cases=[])
    def save():
        (OWN / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper in ('mmc3', 'mmc5'):
        with (OWN / f'build-{mapper}.log').open('w', encoding='utf-8') as log:
            done = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=source, stdout=log, stderr=subprocess.STDOUT)
        row = dict(mapper=mapper, exit=done.returncode)
        report['cases'].append(row)
        save()
        assert done.returncode == 0
        name = f'build/smb-crossover-{mapper}.nes'
        k, l, d, n = [(p / 'source' / name).read_bytes() for p in (K, L, D, OWN)]
        assert len(k) == len(l) == len(d) == len(n) == 786448
        ld = {i for i, (a, b) in enumerate(zip(k, l)) if a != b}
        dd = {i for i, (a, b) in enumerate(zip(k, d)) if a != b}
        assert len(ld) == 400 and not (ld & dd)
        assert all(16 + 10 * 8192 <= i < 16 + 11 * 8192 for i in ld)
        assert all(not (16 + 10 * 8192 <= i < 16 + 11 * 8192) for i in dd)
        expected = bytearray(k)
        for i in ld:
            expected[i] = l[i]
        for i in dd:
            expected[i] = d[i]
        assert bytes(expected) == n, 'Actual compiled ROM must be the exact disjoint union'
        rom = source / name
        row.update(ROM_sha256=sha(rom), DBG_sha256=sha(rom.with_suffix('.dbg')),
                   LBL_sha256=sha(rom.with_suffix('.lbl')), MAP_sha256=sha(rom.with_suffix('.map')),
                   L_delta_bytes=len(ld), D_delta_bytes=len(dd), combined_delta_bytes=len(ld | dd),
                   exact_disjoint_compiled_union=True, SAMUS_bank_literal_L=True,
                   all_other_ROM_bytes_literal_D=True)
        save()
    with (OWN / 'build-original-baseline.log').open('w', encoding='utf-8') as log:
        done = subprocess.run([sys.executable, 'tools/build.py', '--mapper', 'mmc3', '--baseline'], cwd=source, stdout=log, stderr=subprocess.STDOUT)
    assert done.returncode == 0
    baseline = source / 'build/smb-crossover-mmc3-baseline.nes'
    assert baseline.read_bytes() == (K / 'source/build/smb-crossover-mmc3-baseline.nes').read_bytes()
    assert all(sha(source / n) == h for n, h in cat.items())
    report.update(status='PASS-private-exact-disjoint-combination-build-only', source408_exact_after=True,
                  original_baseline_sha256=sha(baseline), workspace_after_bytes=workspace_bytes(ROOT),
                  qualification='No full regression, ordinary-route, audiovisual, or release acceptance inferred. Audio optimization excluded.')
    save()
    print(json.dumps({k: v for k, v in report.items() if k != 'source408_hashes'}), flush=True)

if __name__ == '__main__':
    main()
