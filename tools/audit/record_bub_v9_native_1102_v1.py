"""Preserve the bounded native v9 evidence, including the failed Easy fixture."""
import hashlib
import json
from pathlib import Path
import zipfile

R = Path(__file__).resolve().parents[2]
O = R / 'build/bub-v9-native-1102-v1'
BASE = R / 'build/bub-menu-candidate-1102-v2'
PIN = '613b3300b09e530ec920835b95df53f3115d865ed854e273809d4cafa52407ce'


def main():
    rows, paths = [], []
    for name in ['bub-cold', 'bob-cold', 'bub-controls', 'bob-controls', 'bub-easy', 'bub-pop', 'bub-easy2', 'bub-ride']:
        run = BASE / ('native-event-' + name)
        binding = json.loads((run / 'capture/binding.json').read_text())
        assert binding['ROM_sha256'] == PIN
        result_path = run / 'capture/result.json'
        result = json.loads(result_path.read_text()) if result_path.exists() else None
        if name != 'bub-easy':
            assert binding['exit_code'] == 0 and result and result['passed']
        else:
            assert binding['exit_code'] != 0
        rows.append(dict(name=name, binding=binding, result=result))
        paths.extend(p for p in run.rglob('*') if p.is_file() and p.suffix in {'.json', '.lua', '.csv', '.png', '.log', '.py'})
    assert len(paths) < 200 and sum(p.stat().st_size for p in paths) < 8_000_000
    O.mkdir(exist_ok=True)
    archive = O / 'inputs.zip'
    assert not archive.exists()
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(paths):
            z.write(p, p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        for p in paths:
            assert z.read(p.relative_to(R).as_posix()) == p.read_bytes()
    report = dict(ROM_sha256=PIN, installed=False, runs=rows,
                  archive_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                  files=len(paths), archive_bytes=archive.stat().st_size,
                  scope='Exact native cold/menu, movement, trap/pop, Easy stomp and earned bubble ride evidence. Failed missing-label fixture retained. No full-stage, every-powerup or 60Hz claim.')
    (O / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['files', 'archive_bytes', 'archive_SHA256']}))


if __name__ == '__main__':
    main()
