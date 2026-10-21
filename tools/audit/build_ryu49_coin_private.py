"""Build the frozen coin-as-wall fix on the isolated lower-grapple H source."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'build/verification/root49g-grapple-private-build-a'
PACKET = ROOT / 'build/verification/ryu49h-coin-wall-proposal-a'
OWN = ROOT / 'build/verification/root49h-coin-private-build-a'
digest = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda path: digest(path.read_bytes())


def labels(path):
    return {parts[2]: int(parts[1], 16) for line in path.read_text().splitlines()
            if (parts := line.split()) and parts[0] == 'al'}


def main():
    assert sha(PACKET / 'freeze.json') == '95194cd62d7715d228cb736f7fe9582294d9e8beb653d1ba422e182c70d016b5'
    frozen = json.loads((PACKET / 'freeze.json').read_text())
    for name, row in frozen['files'].items():
        assert sha(PACKET / name) == row['sha256'], name
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 120_000_000 <= 30_000_000_000, used
    OWN.mkdir(exist_ok=False)
    fresh = OWN / 'source'
    fresh.mkdir()
    archive = BASE / 'source-grapple-h.zip'
    assert sha(archive) == 'e0c8e20a18bd0538e23295fc83ba82e9aef7df0aa79f01295c0c3a026fb4c90c'
    with zipfile.ZipFile(archive) as source:
        catalog = json.loads(source.read('archived-file-hashes.json'))
        assert len(catalog) == 405
        for name, expected in catalog.items():
            p = PurePosixPath(name)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in name
            data = source.read(name)
            assert digest(data) == expected
            dest = fresh / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    material = json.loads((PACKET / 'materialization.json').read_text())
    for name, row in material['files'].items():
        assert catalog[name] == row['before_sha256']
        data = (PACKET / row['after_file']).read_bytes()
        assert digest(data) == row['after_sha256']
        (fresh / name).write_bytes(data)
    new = material['new_file']
    data = (PACKET / new['artifact']).read_bytes()
    assert digest(data) == new['sha256']
    (fresh / new['path']).write_bytes(data)
    expected = {name: sha(fresh / name) for name in set(catalog) | {new['path']}}
    assert len(expected) == 406
    assert {name for name in catalog if expected[name] != catalog[name]} == {'src/ryu_wall.s', 'src/entrypoint.s'}
    out_archive = OWN / 'source-coin-j.zip'
    with zipfile.ZipFile(out_archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for name in sorted(expected):
            out.writestr(name, (fresh / name).read_bytes())
        out.writestr('archived-file-hashes.json', json.dumps(expected, indent=2) + '\n')
    shutil.copytree(ROOT / 'tools/Windows/cc65', fresh / 'tools/Windows/cc65')
    report = dict(status='building-private-proposal', goal_complete=False, source406_hashes=expected,
                  source_archive_sha256=sha(out_archive), baseline_source_archive_sha256=sha(archive),
                  proposal_freeze_sha256=sha(PACKET / 'freeze.json'), script_sha256=sha(Path(__file__)),
                  workspace_before_bytes=used, cases=[], scope='Ryu lower grapple H plus coin-only wall membership correction. No Samus crouch or private audio change. Not accepted.')

    def save():
        (OWN / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    save()
    for mapper in ('mmc3', 'mmc5'):
        with (OWN / f'build-{mapper}.log').open('w', encoding='utf-8') as log:
            result = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=fresh, stdout=log, stderr=subprocess.STDOUT)
        rom = fresh / f'build/smb-crossover-{mapper}.nes'
        row = dict(mapper=mapper, exit=result.returncode, rom_sha256=sha(rom) if rom.is_file() else None)
        report['cases'].append(row)
        save()
        assert result.returncode == 0, mapper
        before = (BASE / 'source/build' / rom.name).read_bytes()
        after = rom.read_bytes()
        assert len(before) == len(after) == 786448
        changed = [i for i, pair in enumerate(zip(before, after)) if pair[0] != pair[1]]
        assert changed and len(changed) <= 19 and all(16 + 61 * 8192 <= i < 16 + 62 * 8192 for i in changed)
        old_labels = labels((BASE / 'source/build' / rom.name).with_suffix('.lbl'))
        new_labels = labels(rom.with_suffix('.lbl'))
        assert all(new_labels.get(name) == value for name, value in old_labels.items())
        assert after[16 + 10 * 8192:16 + 11 * 8192] == before[16 + 10 * 8192:16 + 11 * 8192]
        row.update(dbg_sha256=sha(rom.with_suffix('.dbg')), lbl_sha256=sha(rom.with_suffix('.lbl')),
                   old_labels_preserved=True, complete_SAMUS_bank_exact=True, changed_rom_bytes=len(changed),
                   helper_address=new_labels['.RyuWallMapAttribute'], helper_bytes=16,
                   remaining_bank61_bytes=0xc000-new_labels['.RyuWallMapAttribute']-16)
        save()
    assert all(sha(fresh / name) == value for name, value in expected.items())
    report.update(status='PASS-build-only-not-accepted', source406_exact_after_build=True, workspace_after_bytes=workspace_bytes(ROOT))
    save()
    print(json.dumps({k: v for k, v in report.items() if k != 'source406_hashes'}), flush=True)


if __name__ == '__main__':
    main()
