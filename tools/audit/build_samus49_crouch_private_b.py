"""Build the additive two-gap Samus geometry proposal on exact G."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'build/checkpoints/roster-audit-v49-provisional-g'
PACKET = ROOT / 'build/verification/agent49g-samus-crouch-fix-proposal-b'
OWN = ROOT / 'build/verification/root49g-samus-crouch-private-build-b'
digest = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda path: digest(path.read_bytes())


def labels(path):
    return {parts[2]: int(parts[1], 16) for line in path.read_text().splitlines()
            if (parts := line.split()) and parts[0] == 'al'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze-sha256', required=True)
    args = parser.parse_args()
    assert sha(PACKET / 'freeze.json') == args.freeze_sha256
    frozen = json.loads((PACKET / 'freeze.json').read_text())
    files = frozen['files']
    iterator = files.values() if isinstance(files, dict) else files
    for row in iterator:
        path = Path(row['path'])
        assert path.resolve().is_relative_to(PACKET.resolve())
        assert sha(path) == row['sha256'], path
    contract = json.loads((PACKET / 'contract.json').read_text())
    assert contract['estimated_byte_budget']['new_FIXED_bytes'] == 88
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    before_size = workspace_bytes(ROOT)
    assert before_size + 120_000_000 <= 30_000_000_000, before_size
    OWN.mkdir(exist_ok=False)
    fresh = OWN / 'source'
    fresh.mkdir()
    archive = BASE / 'source-v49.zip'
    assert sha(archive) == '418b526aa5227e9f3f593be43809d60d7afae48520efc282af5a4075574d0624'
    with zipfile.ZipFile(archive) as source:
        catalog = json.loads(source.read('archived-file-hashes.json'))
        assert len(catalog) == 404
        for name, expected in catalog.items():
            name_path = PurePosixPath(name)
            assert not name_path.is_absolute() and '..' not in name_path.parts and '\\' not in name
            data = source.read(name)
            assert digest(data) == expected
            dest = fresh / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    for name, row in contract['source_members'].items():
        assert catalog[name] == row['sha256'], name
    for name, row in contract['materialization'].items():
        supplied = Path(row['path'])
        assert supplied.resolve().is_relative_to(PACKET.resolve())
        assert sha(supplied) == row['sha256']
        dest = fresh / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(supplied.read_bytes())
    expected = {name: sha(fresh / name) for name in set(catalog) | set(contract['materialization'])}
    assert len(expected) == 405
    assert {name for name in catalog if expected[name] != catalog[name]} == {'src/entrypoint.s', 'src/megaman_weapons.s', 'src/water.s', 'smb1base.cfg'}
    out_archive = OWN / 'source-crouch-i-b.zip'
    with zipfile.ZipFile(out_archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for name in sorted(expected):
            out.writestr(name, (fresh / name).read_bytes())
        out.writestr('archived-file-hashes.json', json.dumps(expected, indent=2) + '\n')
    shutil.copytree(ROOT / 'tools/Windows/cc65', fresh / 'tools/Windows/cc65')
    report = dict(status='building-private-proposal', goal_complete=False, source405_hashes=expected,
                  source_archive_sha256=sha(out_archive), baseline_source_archive_sha256=sha(archive),
                  proposal_freeze_sha256=args.freeze_sha256, script_sha256=sha(Path(__file__)),
                  workspace_before_bytes=before_size, cases=[], scope='Samus crouch geometry in two exact resident gaps, with unchanged DPCM addresses; not Ryu H/J or private audio C. Not accepted; water first-update ordering remains a separate qualification.')

    def save():
        (OWN / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    save()
    for mapper in ('mmc3', 'mmc5'):
        with (OWN / f'build-{mapper}.log').open('w', encoding='utf-8') as log:
            completed = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=fresh, stdout=log, stderr=subprocess.STDOUT)
        rom = fresh / f'build/smb-crossover-{mapper}.nes'
        row = dict(mapper=mapper, exit=completed.returncode, rom_sha256=sha(rom) if rom.is_file() else None)
        report['cases'].append(row)
        save()
        assert completed.returncode == 0, mapper
        old_labels = labels((BASE / rom.name).with_suffix('.lbl'))
        new_labels = labels(rom.with_suffix('.lbl'))
        assert all(new_labels.get(name) == value for name, value in old_labels.items()), 'An existing label moved or disappeared'
        before, after = (BASE / rom.name).read_bytes(), rom.read_bytes()
        assert len(before) == len(after) == 786448
        changes = [i for i, pair in enumerate(zip(before, after)) if pair[0] != pair[1]]
        assert len(changes) <= 99 and changes
        assert after[16 + 10 * 8192:16 + 11 * 8192] == before[16 + 10 * 8192:16 + 11 * 8192], 'SAMUS bank changed'
        row.update(dbg_sha256=sha(rom.with_suffix('.dbg')), lbl_sha256=sha(rom.with_suffix('.lbl')),
                   old_labels_preserved=True, complete_SAMUS_bank_exact=True, changed_rom_bytes=len(changes),
                   helper_labels={name: value for name, value in new_labels.items() if name.startswith('.SamusCrouch')})
        save()
    assert all(sha(fresh / name) == value for name, value in expected.items())
    report.update(status='PASS-build-only-not-accepted', source405_exact_after_build=True, workspace_after_bytes=workspace_bytes(ROOT))
    save()
    print(json.dumps({k: v for k, v in report.items() if k != 'source405_hashes'}), flush=True)


if __name__ == '__main__':
    main()
