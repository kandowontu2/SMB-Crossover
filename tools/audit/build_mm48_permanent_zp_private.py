"""Root-only isolated build of a frozen, nonshipping native-audio proposal."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / 'build/verification/mm48-native-permanent-zp-proposal-b'
CP = ROOT / 'build/checkpoints/roster-audit-v48'
OWN = ROOT / 'build/verification/root-mm48-permanent-zp-build-a'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert sha(PACKET / 'frozen.json') == '41d5bf6ad69df0ce10dbd97aa69689d3ac6d4c6ae134aabc7bf60efcfb24a6b2'
    freeze = json.loads((PACKET / 'frozen.json').read_text(encoding='utf-8'))
    for name, row in freeze['files'].items():
        assert sha(PACKET / name) == row['sha256'], name
    proposal = json.loads((PACKET / 'proposal.json').read_text(encoding='utf-8'))
    for name, row in proposal['input_pins'].items():
        assert sha(ROOT / name) == row['sha256'], name
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 120000000 < 30000000000
    OWN.mkdir(exist_ok=False)
    fresh = OWN / 'source'
    fresh.mkdir()
    archive = CP / 'source-v48a.zip'
    with zipfile.ZipFile(archive) as source:
        catalog = json.loads(source.read('archived-file-hashes.json'))
        assert len(catalog) == 403
        assert set(source.namelist()) == set(catalog) | {'archived-file-hashes.json'}
        for name, digest in catalog.items():
            relative = PurePosixPath(name)
            assert not relative.is_absolute() and '..' not in relative.parts and '\\' not in name
            data = source.read(name)
            assert hashlib.sha256(data).hexdigest() == digest
            target = fresh / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    for name, row in proposal['source_member_pins'].items():
        assert sha(fresh / name) == row['sha256'] == catalog[name]
        candidate = PACKET / 'private' / name
        assert candidate.exists() and name in freeze['files'] or 'private/' + name in freeze['files']
        (fresh / name).write_bytes(candidate.read_bytes())
    expected = {name: sha(fresh / name) for name in catalog}
    changed = {name for name in catalog if expected[name] != catalog[name]}
    assert changed == set(proposal['source_member_pins']) and len(changed) == 4
    shutil.copytree(ROOT / 'tools/Windows/cc65', fresh / 'tools/Windows/cc65')
    report = dict(status='building-nonshipping-prototype', goal_complete=False, source_archive_sha256=sha(archive), proposal_freeze_sha256=sha(PACKET / 'frozen.json'), source403_hashes=expected, workspace_before_bytes=used, cases=[], scope='Isolated accepted48 source clone. Shared runtime/build and49candidate unaffected; no native execution or equivalence/performance claim.')

    def save():
        (OWN / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    save()
    for mapper in ('mmc3', 'mmc5'):
        with (OWN / f'build-{mapper}.log').open('w', encoding='utf-8') as file:
            result = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=fresh, stdout=file, stderr=subprocess.STDOUT)
        rom = fresh / f'build/smb-crossover-{mapper}.nes'
        row = dict(mapper=mapper, exit=result.returncode, rom_sha256=sha(rom) if rom.exists() else None)
        report['cases'].append(row)
        save()
        assert result.returncode == 0, ('Build negative retained', mapper)
        if mapper == 'mmc3':
            row['whole_rom_equal_accepted48'] = rom.read_bytes() == (CP / rom.name).read_bytes()
            assert row['whole_rom_equal_accepted48']
        else:
            native = rom.read_bytes()[16 + 11 * 8192:16 + 12 * 8192]
            row['entire_mm3_bank_matches_guarded_operand_template'] = native == (PACKET / 'expected-mm3-bank0b-operand-template.bin').read_bytes()
            assert row['entire_mm3_bank_matches_guarded_operand_template']
        row.update(dbg_sha256=sha(rom.with_suffix('.dbg')), lbl_sha256=sha(rom.with_suffix('.lbl')))
        save()
    assert all(sha(fresh / name) == digest for name, digest in expected.items()), 'Prepared source drift'
    report.update(status='PASS-build-only-not-shipping', workspace_after_bytes=workspace_bytes(ROOT), source403_exact_after_build=True)
    save()
    print(json.dumps({k: v for k, v in report.items() if k != 'source403_hashes'}), flush=True)


if __name__ == '__main__':
    main()
