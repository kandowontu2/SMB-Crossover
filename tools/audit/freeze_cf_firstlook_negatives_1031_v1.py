"""Preserve the actual CF native failures without claiming an unlock."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
O = R / 'docs/qa/checkpoints/2026-10-31/contra-force-firstlook-negatives-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    files = {Path(__file__)}
    bindings = {}
    rows = []
    for version in [1, 3]:
        base = R / f'build/contra-force-firstlooks-native-1031-v{version}'
        folder = base / 'burns'
        ready = json.loads((folder / 'ready.json').read_text())
        binding = json.loads((folder / 'capture/binding.json').read_text())
        assert binding['exit_code'] == 1 and binding['ready_sha256'] == sha(folder / 'ready.json')
        for name, expected in binding['bindings'].items():
            assert sha(name) == expected, name
            bindings[name] = expected
        files.update(p for p in folder.rglob('*') if p.is_file())
        files.add(base / 'prepared.json')
        files.add(base / 'source-observer-binding.json')
        files.update(Path(n) for n in ready['bindings']
                     if Path(n).is_relative_to(R / 'tools') and Path(n).suffix.lower() in ['.py', '.lua'])
        row = dict(version=version, candidate=binding['ROM_sha256'], native_exit=1)
        result = folder / 'capture/result.json'
        if result.exists():
            data = json.loads(result.read_text())
            assert not data['passed']
            row.update(result=data)
        else:
            row['reason'] = 'Observer asserted descriptor age during a genuine static lives hold; no terminal JSON.'
        rows.append(row)
    assert all(p.suffix.lower() in ['.py', '.json', '.lua', '.csv', '.png', '.log'] for p in files)
    assert sum(p.stat().st_size for p in files) < 4 * 1024 * 1024
    O.mkdir(parents=True)
    archive = O / 'failed-native-and-inputs.zip'
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(files):
            z.write(p, p.relative_to(R).as_posix())
            bindings[str(p)] = sha(p)
    with zipfile.ZipFile(archive) as z:
        for p in files:
            assert z.read(p.relative_to(R).as_posix()) == p.read_bytes()
    description = (
        'Two actual root-launched Burns failures are retained. V1/e538 failed an observer freshness '
        'assumption during a static lives screen; its screenshot independently exposed the genuine '
        'lives-only+56 coordinate defect. The source-built7b7 successor removes that offset. '
        'V3/7b7 has correct selected/lives/body pixels and walking/ground shooting, but no jump or '
        'airborne shot:180 Main updates,363 physical gameplay frames, rise0,45 gameplay body pixel '
        'checks. This is a genuine gameplay failure, not an admitted playable character. Source '
        'parser receipts did not assert jump displacement and must not be interpreted as native '
        'jump qualification. Downloads remains the earlier68 build. No successful CF native '
        'or full-level/powerup completion is claimed.\n'
    )
    (O / 'README.txt').write_text(description, encoding='utf-8', newline='\n')
    bindings[str(O / 'README.txt')] = sha(O / 'README.txt')
    bindings[str(archive)] = sha(archive)
    (O / 'handoff.json').write_text(json.dumps(dict(
        status='NATIVE_REJECTED_DO_NOT_ADMIT', installed=False, passed=False,
        negatives=rows, archive_members=len(files), archive_bytes=archive.stat().st_size,
        bindings=bindings), indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(archive_members=len(files), archive_bytes=archive.stat().st_size,
                          handoff=str(O / 'handoff.json'), sha256=sha(O / 'handoff.json'))))


if __name__ == '__main__':
    main()
