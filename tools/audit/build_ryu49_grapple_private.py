"""Build the exact frozen lower-grapple proposal in an isolated G source clone."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
CP = ROOT / 'build/checkpoints/roster-audit-v49-provisional-g'
PACKET = ROOT / 'build/verification/ryu49g-grapple-adjust-proposal-a'
OWN = ROOT / 'build/verification/root49g-grapple-private-build-a'
digest = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda path: digest(path.read_bytes())


def labels(path):
    result = {}
    for line in path.read_text().splitlines():
        if line.startswith('al '):
            _, value, name = line.split()
            result[name] = int(value, 16)
    return result


def main():
    assert sha(PACKET / 'freeze.json') == 'eb6878281e614c9542febaba0e771c02a0e307c4361da6c93034590732f4a4ad'
    frozen = json.loads((PACKET / 'freeze.json').read_text())
    for name, row in frozen['files'].items():
        assert sha(PACKET / name) == row['sha256'], name
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 120_000_000 < 30_000_000_000, used
    OWN.mkdir(exist_ok=False)
    fresh = OWN / 'source'
    fresh.mkdir()
    archive = CP / 'source-v49.zip'
    assert sha(archive) == '418b526aa5227e9f3f593be43809d60d7afae48520efc282af5a4075574d0624'
    with zipfile.ZipFile(archive) as source:
        catalog = json.loads(source.read('archived-file-hashes.json'))
        assert len(catalog) == 404
        for name, expected in catalog.items():
            p = PurePosixPath(name)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in name
            data = source.read(name)
            assert digest(data) == expected
            target = fresh / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    wall = fresh / 'src/ryu_wall.s'
    needle = b'  jsr RyuWallCanAttach\r\n  bcc Next\r\n  lda RyWallResolved\r\n  sta RyWallSide'
    assert wall.read_bytes().count(needle) == 1
    wall.write_bytes(wall.read_bytes().replace(needle, b'  jsr RyuWallCanAttach\r\n  bcc Next\r\n  jmp RyuWallAdjustGrab\r\n::RyuWallGrabContinue:\r\n  sta RyWallSide'))
    entry = fresh / 'src/entrypoint.s'
    ending = b'\r\n; Append after all SPECIAL_ROSTER contributors; preserve every old code PC.\r\n.if ::ENABLE_CROSSOVER\r\n.include "ryu_grapple_adjust.s"\r\n.endif\r\n'
    entry.write_bytes(entry.read_bytes() + ending)
    extra = fresh / 'src/ryu_grapple_adjust.s'
    extra.write_bytes((PACKET / 'ryu_grapple_adjust.s').read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
    material = json.loads((PACKET / 'materialization.json').read_text())
    for name, row in material.items():
        assert catalog.get(name) == row['before_sha256']
        assert sha(fresh / name) == row['after_sha256']
    expected = {name: sha(fresh / name) for name in set(catalog) | set(material)}
    assert len(expected) == 405
    assert {name for name in catalog if expected[name] != catalog[name]} == {'src/ryu_wall.s', 'src/entrypoint.s'}
    source_archive = OWN / 'source-grapple-h.zip'
    with zipfile.ZipFile(source_archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for name in sorted(expected):
            out.writestr(name, (fresh / name).read_bytes())
        out.writestr('archived-file-hashes.json', json.dumps(expected, indent=2) + '\n')
    shutil.copytree(ROOT / 'tools/Windows/cc65', fresh / 'tools/Windows/cc65')
    report = dict(status='building-isolated-proposal', goal_complete=False,
                  source405_hashes=expected, source_archive_sha256=sha(source_archive),
                  parent_source_archive_sha256=sha(archive), proposal_freeze_sha256=sha(PACKET / 'freeze.json'),
                  script_sha256=sha(Path(__file__)), workspace_before_bytes=used, cases=[],
                  scope='Static lower-grapple correction only; conservative platform bailout remains qualified. Shared runtime and audio prototype unaffected. Build-only evidence.')

    def save():
        (OWN / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    save()
    for mapper in ('mmc3', 'mmc5'):
        with (OWN / f'build-{mapper}.log').open('w', encoding='utf-8') as output:
            result = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=fresh, stdout=output, stderr=subprocess.STDOUT)
        rom = fresh / f'build/smb-crossover-{mapper}.nes'
        row = dict(mapper=mapper, exit=result.returncode, rom_sha256=sha(rom) if rom.exists() else None)
        report['cases'].append(row)
        save()
        assert result.returncode == 0, ('Build negative retained', mapper)
        before = (CP / rom.name).read_bytes()
        after = rom.read_bytes()
        assert len(before) == len(after) == 786448
        changed = [i for i, (old, new) in enumerate(zip(before, after)) if old != new]
        assert changed and all(16 + 61 * 8192 <= i < 16 + 62 * 8192 for i in changed), 'Unexpected ROM bank delta'
        prior_labels = labels((CP / rom.name).with_suffix('.lbl'))
        new_labels = labels(rom.with_suffix('.lbl'))
        assert all(new_labels[name] == value for name, value in prior_labels.items() if name in new_labels), 'An old label moved'
        helper = new_labels['.RyuWallAdjustGrab']
        assert helper + 339 <= 0xC000
        assert after[16 + 10 * 8192:16 + 11 * 8192] == before[16 + 10 * 8192:16 + 11 * 8192]
        row.update(dbg_sha256=sha(rom.with_suffix('.dbg')), lbl_sha256=sha(rom.with_suffix('.lbl')),
                   only_bank61_changed=True, old_labels_preserved=True, complete_SAMUS_bank_exact=True,
                   helper_start=helper, predicted_helper_bytes=339, free_bytes_after_helper=0xC000-helper-339,
                   changed_rom_bytes=len(changed))
        save()
    assert all(sha(fresh / name) == value for name, value in expected.items())
    report.update(status='PASS-build-only-not-accepted', source405_exact_after_build=True,
                  workspace_after_bytes=workspace_bytes(ROOT))
    save()
    print(json.dumps({name: value for name, value in report.items() if name != 'source405_hashes'}), flush=True)


if __name__ == '__main__':
    main()
