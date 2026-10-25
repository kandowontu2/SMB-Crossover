"""Install one exact composed Alucard cue after all current native controls."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = '84e55b6d60da4be5550d823f88ee40a9b220dbef5a1e8dd21de3d69aa28cb328'
FINAL = 'ae97d45e5a33b20a399c0b55f241ea933a72eaea6f88e7fc69eae93af85c96e4'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    proposal = D / 'cv3-audio-combined84-v2'
    out = proposal / 'adoption-v1'
    assert not out.exists(), 'One-shot adopter already started; inspect retained state.'
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    alias = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    assert sha(installed) == sha(alias) == PARENT and sha(proposal / 'candidate.nes') == FINAL
    build = json.loads((proposal / 'build-proof.json').read_text())
    qualification = proposal / 'qualification-v1/proof.json'
    tested = json.loads(qualification.read_text())
    assert build['passed'] and build['ROM_sha256'] == FINAL and build['changed_bytes'] == 643
    assert build['producer_all_generated_outputs_exact'] and build['retained_qualified_addresses_exact']
    assert tested['passed'] and tested['ROM_sha256'] == FINAL and tested['candidate_native_cases'] == 22
    assert tested['ordinary_CPU_cases'] == 4160 and tested['restore_CPU_cases'] == 256
    for path, expected in tested['source_receipts'].items():
        assert sha(Path(path)) == expected, path
    for name, row in build['source_files'].items():
        current = ROOT / name
        assert (sha(current) if current.exists() else None) == row['before_sha256'], name
        assert sha(proposal / 'source' / name) == row['after_sha256'], name
    for mapper, expected in build['ordinary_target_hashes'].items():
        assert sha(proposal / ('standard-' + mapper + '.nes')) == expected
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
    for name, row in build['source_files'].items():
        if row['before_sha256'] is not None:
            dest = previous / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, dest)
    try:
        for name in build['source_files']:
            shutil.copy2(proposal / 'source' / name, ROOT / name)
        with (out / 'fresh-build.log').open('w') as log:
            subprocess.run([sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'),
                            '--output', str(out / 'candidate.nes')], cwd=ROOT, check=True,
                           stdout=log, stderr=subprocess.STDOUT)
        assert sha(out / 'candidate.nes') == FINAL, 'Fresh ROOT compile differs; restoring sources.'
    except BaseException:
        for name, row in build['source_files'].items():
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
                 fresh_root_compile_exact=True, changed_ROM_bytes=643, changed_PRG_banks=[27, 28, 82, 84],
                 retained_qualified_PC_RAM_CHR_exact=True,
                 intentionally_removed_private_labels=build['intentionally_removed_private_labels'],
                 new_RAM_bytes=0, native_cases=22, ordinary_CPU_cases=4160, restore_CPU_cases=256,
                 producer_all_generated_outputs_exact=True,
                 ordinary_target_hashes=build['ordinary_target_hashes'],
                 qualification=str(qualification), qualification_sha256=sha(qualification),
                 matched_native_before=tested['matched_native_before'], matched_native_after=tested['matched_native_after'],
                 Downloads_and_default_build_current=True, backup_directory=str(out),
                 scope='Original Alucard primary noise schedule, ownership and ordinary music compatibility. Staged native source/control arenas with nonregressing matched cadence. Grant/Sypha attack DMC, other CV3 cues/music and full-roster/every-item/campaign remain incomplete.')
    (out / 'proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    target = ROOT / 'build/verification/cv3-alucard-audio'
    target.mkdir(exist_ok=True)
    shutil.copy2(out / 'proof.json', target / 'proof.json')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
