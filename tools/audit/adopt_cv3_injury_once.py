"""Install the exact independently qualified Grant/Alucard injury sound once."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = 'ae97d45e5a33b20a399c0b55f241ea933a72eaea6f88e7fc69eae93af85c96e4'
FINAL = '52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    packet = D / 'cv3-dmc-followup-v1'
    proposal = packet / 'proposal-v1'
    tested_path = D / 'cv3-dmc-root529-v1/proof.json'
    out = D / 'cv3-dmc-root529-v1/adoption-v1'
    assert not out.exists(), 'One-shot adopter already started; inspect retained state.'
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    alias = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    assert sha(installed) == sha(alias) == PARENT and sha(proposal / 'candidate.nes') == FINAL
    tested = json.loads(tested_path.read_text())
    assert tested['passed'] and tested['ROM_sha256'] == FINAL and tested['candidate_native_cases'] == 14
    assert tested['public_DMC_cases'] == 1728 and tested['ordinary_AudioUpdate_CPU_cases'] == 5024
    for path, expected in (tested['tools'] | tested['receipts']).items():
        assert sha(path) == expected, path
    meta = json.loads((proposal / 'prepare.json').read_text())
    sources = {}
    for name, expected in meta['source_files'].items():
        old, new = proposal / 'baseline-source' / name, proposal / 'source' / name
        assert sha(new) == expected
        current = ROOT / name
        if old.exists():
            assert current.is_file() and sha(current) == sha(old), name
            before = sha(current)
        else:
            assert not current.exists(), name
            before = None
        sources[name] = dict(before_sha256=before, after_sha256=expected)
    ordinary = json.loads((packet / 'flagoff-v1/proof.json').read_text())
    assert ordinary['passed']
    for row in ordinary['results']:
        assert row['passed'] and row['byte_identical']
        assert sha(packet / ('flagoff-v1/candidate-' + row['mapper'] + '.nes')) == row['hashes']['candidate']
    out.mkdir()
    previous = out / 'previous-source'
    previous.mkdir()
    shutil.copy2(installed, out / 'previous-MMC5.nes')
    old_alias = out / 'previous-default'
    old_alias.mkdir()
    suffixes = ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.build.log']
    for suffix in suffixes:
        path = alias.with_suffix(suffix)
        if path.exists():
            shutil.copy2(path, old_alias / path.name)
    for name, row in sources.items():
        if row['before_sha256'] is not None:
            dest = previous / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, dest)
    try:
        for name in sources:
            shutil.copy2(proposal / 'source' / name, ROOT / name)
        with (out / 'fresh-build.log').open('w') as log:
            subprocess.run([sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'),
                            '--output', str(out / 'candidate.nes')], cwd=ROOT, check=True,
                           stdout=log, stderr=subprocess.STDOUT)
        assert sha(out / 'candidate.nes') == FINAL, 'Fresh ROOT compile differs; restoring sources.'
    except BaseException:
        for name, row in sources.items():
            if row['before_sha256'] is None:
                (ROOT / name).unlink(missing_ok=True)
            else:
                shutil.copy2(previous / name, ROOT / name)
        raise
    staged = installed.with_name(installed.stem + '.staging-' + FINAL[:8] + '.nes')
    assert not staged.exists()
    shutil.copy2(out / 'candidate.nes', staged)
    assert sha(staged) == FINAL
    staged.replace(installed)
    for suffix in suffixes:
        shutil.copy2((out / 'candidate.nes').with_suffix(suffix), alias.with_suffix(suffix))
    assert sha(installed) == sha(alias) == FINAL
    proof = dict(adopted=True, goal_complete=False, ROM_sha256=FINAL, parent_ROM_sha256=PARENT,
                 fresh_root_compile_exact=True, changed_ROM_bytes=68, changed_PRG_banks=[7, 82, 127],
                 retained_PC_RAM_CHR_exact=True, sample_bytes_addresses_lengths_exact=True, new_RAM_bytes=0,
                 candidate_native_cases=14, public_DMC_CPU_cases=1728, injury_owner_CPU_cases=144,
                 ordinary_AudioUpdate_CPU_cases=5024, original_injury_to_APU_CPU_chains=2,
                 public_DMC_start_added_CPU_cycles=tested['public_DMC_start_added_CPU_cycles'],
                 native_pressure=[dict(character=row['character'], before=row['pressure_before'], after=row['pressure_after'])
                                  for row in tested['native'] if row['character'] in ['grant', 'alucard']],
                 source_files=sources, qualification=str(tested_path), qualification_sha256=sha(tested_path),
                 ordinary_target_hashes={row['mapper']: row['hashes']['candidate'] for row in ordinary['results']},
                 Downloads_and_default_build_current=True, backup_directory=str(out),
                 scope='Authentic Grant/Alucard injury sample/rates via actual enemy contact, pressure/pending attack/Start pause. One extra Alucard pressure lag frame, unchanged updates/draws, explicitly retained. Sypha distinct sample, primary72 storage/priority and whole-roster goal remain open.')
    (out / 'proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    receipt = ROOT / 'build/verification/cv3-injury'
    receipt.mkdir(exist_ok=True)
    shutil.copy2(out / 'proof.json', receipt / 'proof.json')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
