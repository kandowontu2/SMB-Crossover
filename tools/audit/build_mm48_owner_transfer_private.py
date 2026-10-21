"""Root-only build of the frozen isolated48 audio ownership source repair."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / 'build/verification/mm48-native-owner-transfer-proposal-c'
CP = ROOT / 'build/checkpoints/roster-audit-v48'
OWN = ROOT / 'build/verification/root-mm48-owner-transfer-build-a'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert sha(PACKET / 'frozen.json') == '3e737d0443f1c0341dcf1f469ec924e00f26a34f255297dcc095672c39562f42'
    frozen = json.loads((PACKET / 'frozen.json').read_text())
    for name, row in frozen['files'].items():
        assert sha(PACKET / name) == row['sha256'], name
    proposal = json.loads((PACKET / 'proposal.json').read_text())
    for name, row in proposal['input_pins'].items():
        assert sha(ROOT / name) == row['sha256'], name
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 120_000_000 < 30_000_000_000, used
    OWN.mkdir(exist_ok=False)
    fresh = OWN / 'source'
    fresh.mkdir()
    archive = CP / 'source-v48.zip'
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
    members = proposal['all_member_old_new_pins']
    assert len(members) == 7 and len(proposal['source_member_pins']) == 6
    assert proposal['added_source_members'] == ['src/mm3_audio_ownership.inc']
    for name, row in members.items():
        old = row['old']
        if old.get('absent_in_archive'):
            assert name not in catalog and not (fresh / name).exists()
        else:
            assert sha(fresh / name) == old['sha256'] == catalog[name]
            assert old == proposal['source_member_pins'][name]
        candidate = PACKET / 'private' / name
        assert sha(candidate) == row['new']['sha256'] == frozen['files']['private/' + name]['sha256']
        assert candidate.stat().st_size == row['new']['bytes']
        (fresh / name).write_bytes(candidate.read_bytes())
    expected = {name: sha(fresh / name) for name in set(catalog) | set(members)}
    assert len(expected) == 404
    assert {name for name in catalog if expected[name] != catalog[name]} == set(proposal['source_member_pins'])
    shutil.copytree(ROOT / 'tools/Windows/cc65', fresh / 'tools/Windows/cc65')
    report = dict(status='building-nonshipping-prototype', goal_complete=False,
                  source_archive_sha256=sha(archive), proposal_freeze_sha256=sha(PACKET / 'frozen.json'),
                  script_sha256=sha(Path(__file__)), source404_hashes=expected,
                  workspace_before_bytes=used, cases=[],
                  scope='Isolated accepted48 clone plus frozen ownership source repair. Shared G runtime/build unaffected. Build evidence only, no CPU/native equivalence or performance claim.')

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
            raw = rom.read_bytes()
            for bank, filename in ((11, 'expected-mm3-bank0b-operand-template.bin'), (29, 'expected-bank29-owner-transfer.bin')):
                actual = raw[16 + bank * 8192:16 + (bank + 1) * 8192]
                assert actual == (PACKET / filename).read_bytes(), (bank, filename)
            row['both_complete_8k_bank_templates_exact'] = True
            assert sha(rom) == proposal['independent_guards']['expected_whole_mmc5_rom_sha256']
            row['whole_rom_matches_independent_prediction'] = True
        row.update(dbg_sha256=sha(rom.with_suffix('.dbg')), lbl_sha256=sha(rom.with_suffix('.lbl')))
        save()
    assert all(sha(fresh / name) == digest for name, digest in expected.items()), 'Prepared source drift'
    report.update(status='PASS-build-only-not-shipping', workspace_after_bytes=workspace_bytes(ROOT), source404_exact_after_build=True)
    save()
    print(json.dumps({key: value for key, value in report.items() if key != 'source404_hashes'}), flush=True)


if __name__ == '__main__':
    main()
