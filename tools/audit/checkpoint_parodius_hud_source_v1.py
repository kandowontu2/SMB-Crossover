"""Preserve the uninstalled HUD candidate and independent exact layout review."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'parodius-visibility-current50b5-v1'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ready = P / 'hud-readiness-v1'
    assert sha(ready / 'proof.json') == '9f0000279e984f5ae7f510b92f3d967b35f6a01a301a086fef6bcf5280177880'
    assert sha(ready / 'manifest.json') == 'dfd5de6ecd11d1b4e5cd9015a5af4de4b512bbaae22ba5d5eea1c47867cecab4'
    receipt = json.loads((ready / 'proof.json').read_text())
    manifest = json.loads((ready / 'manifest.json').read_text())
    assert receipt['source_CPU_readiness_passed'] and not receipt['adopted']
    assert len(manifest['bindings']) == manifest['binding_count'] == 88
    tools = {}
    for name, row in manifest['bindings'].items():
        path = Path(name)
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
        if path.resolve().is_relative_to((ROOT / 'tools').resolve()):
            tools[path.relative_to(ROOT).as_posix()] = row['sha256']
    candidate = P / 'hud-candidate-v11'
    layout = json.loads((candidate / 'proof.json').read_text())
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == receipt['baseline_ROM_sha256']
    assert sha(candidate / 'candidate.nes') == receipt['candidate_ROM_sha256']
    old = (ROOT / 'build/smb-crossover-mmc5-expanded.nes').read_bytes()
    new = (candidate / 'candidate.nes').read_bytes()
    assert len(old) == len(new) and old[:16] == new[:16] and old[1048592:] == new[1048592:]
    allowed = set()
    for hook in layout['hooks']:
        lo = hook['offset']
        before, after = bytes.fromhex(hook['before']), bytes.fromhex(hook['after'])
        assert len(before) == len(after) == 3
        assert old[lo:lo+3] == before and new[lo:lo+3] == after
        allowed.update(range(lo, lo+3))
    for tail in layout['tails']:
        lo, size = tail['offset'], tail['size']
        assert old[lo:lo+size] == bytes([255])*size
        allowed.update(range(lo, lo+size))
    diff = [i for i, (a, b) in enumerate(zip(old, new)) if a != b]
    assert len(diff) == layout['differing_bytes'] == 1392 and set(diff) <= allowed
    banks = {n: sum((i-16)//8192 == n for i in diff) for n in range(128)}
    banks = {str(n): count for n, count in banks.items() if count}
    assert banks == {'3': 26, '59': 17, '77': 99, '116': 1245, '126': 5}
    erratum = P / 'hud-readiness-bank126-erratum-v1/proof.json'
    assert sha(erratum) == '9f5ea644fe38ac3fdf8dc137affdb9dda3e4b2514b333160ebb65194730392fe'
    frozen = json.loads((D / 'tmnt-native-storage-current50b5-v1/current-baseline-v1/frozen-source.json').read_text())
    assert all(sha(ROOT / name) == value for name, value in frozen['source_files'].items())
    out = ROOT / 'docs/qa/checkpoints/2026-10-25/parodius-hud-v11-source'
    out.mkdir(parents=True, exist_ok=False)
    for name, original in {'readiness.json': ready / 'proof.json', 'readiness-bindings.json': ready / 'manifest.json',
                           'bank126-erratum.json': erratum, 'layout.json': candidate / 'proof.json',
                           'implementation.patch': candidate / 'sourcepatch.patch'}.items():
        shutil.copyfile(original, out / name)
    for name, value in layout['changed_source'].items():
        source = candidate / 'source' / name
        assert sha(source) == value
        target = out / 'changed-source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    report = ROOT / 'docs/qa/parodius-nmi-hud-2026-10-25.txt'
    assert sha(report) == receipt['report_sha256']
    tools[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    result = dict(goal_complete=False, adopted=False, production_changes=False,
                  candidate_ROM_sha256=receipt['candidate_ROM_sha256'],
                  independently_verified_PRG_deltas=banks, immutable_bindings_checked=88,
                  frozen_production_inputs_unchanged=len(frozen['source_files']),
                  files={p.relative_to(out).as_posix(): sha(p) for p in out.rglob('*') if p.is_file()},
                  tools=tools, report={report.relative_to(ROOT).as_posix(): sha(report)},
                  external_archive=P.as_posix(),
                  limits='Source/CPU checkpoint only. Frozen report omitted bank126 in one layout '
                         'sentence; additive erratum and independent byte review explicitly include '
                         'its5 changed bytes. Native tests have separate receipts; no adoption is granted here.')
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(checkpoint=out.as_posix(), banks=banks, source_files=len(layout['changed_source']))))


if __name__ == '__main__':
    main()
