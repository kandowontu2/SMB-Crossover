"""Install the exact qualified pickup/contact composition once, with backups."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = '55bcfb8209b628062ce1f833a2ed386bd6f08426d34fed9fa8b5ba1f90694be7'
FINAL = '220be8247baf877785c91244876038354442e68502b3f837920f39a674a1fa3e'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    proposal = D / 'pickup-contact-fixes-combined-v1'
    out = proposal / 'adoption-v1'
    assert not out.exists(), 'One-shot adopter already ran; inspect retained state.'
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    alias = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    assert sha(installed) == sha(alias) == PARENT
    assert sha(proposal / 'candidate.nes') == FINAL
    build = json.loads((proposal / 'build-proof.json').read_text())
    assert build['passed'] and build['ROM_sha256'] == FINAL and build['changed_bytes'] == 124
    proofs = [proposal / n / 'native-proof.json' for n in
              ['native-14-0', 'native-14-1', 'native-13-0', 'native-15', 'native-19']]
    proofs += [proposal / n / 'proof.json' for n in ['cpu-chip', 'cpu-mac-tmnt', 'routes-affected']]
    for path in proofs:
        q = json.loads(path.read_text())
        assert q['passed'] and q['ROM_sha256'] == FINAL, path
    assert sum(len(json.loads(path.read_text())['cases']) for path in proofs[:5]) == 76
    routes = json.loads((proposal / 'routes-affected/proof.json').read_text())
    assert len(routes['runs']) == 3 and all(r['replay']['passed'] for r in routes['runs'])
    for mapper, expected in build['ordinary_target_hashes'].items():
        assert sha(proposal / ('standard-'+mapper+'.nes')) == expected
    for name, row in build['source_files'].items():
        path = ROOT / name
        assert (sha(path) if path.exists() else None) == row['before_sha256'], name
        assert sha(proposal / 'source' / name) == row['after_sha256'], name
    out.mkdir()
    previous = out / 'previous-source'
    previous.mkdir()
    missing = []
    shutil.copy2(installed, out / 'previous-MMC5.nes')
    oldalias = out / 'previous-default'
    oldalias.mkdir()
    suffixes = ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.build.log']
    for suffix in suffixes:
        path = alias.with_suffix(suffix)
        if path.exists():
            shutil.copy2(path, oldalias / path.name)
    for name in build['source_files']:
        path = ROOT / name
        if path.exists():
            dest = previous / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
        else:
            missing.append(name)
    try:
        for name in build['source_files']:
            shutil.copy2(proposal / 'source' / name, ROOT / name)
        with (out / 'fresh-build.log').open('w') as log:
            subprocess.run([sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'),
                            '--output', str(out / 'candidate.nes')], cwd=ROOT, check=True,
                           stdout=log, stderr=subprocess.STDOUT)
        assert sha(out / 'candidate.nes') == FINAL, 'Fresh ROOT compile differs; restoring sources.'
    except BaseException:
        for path in previous.rglob('*'):
            if path.is_file():
                shutil.copy2(path, ROOT / path.relative_to(previous))
        for name in missing:
            (ROOT / name).unlink()
        raise
    shutil.copy2(out / 'candidate.nes', installed)
    for suffix in suffixes:
        shutil.copy2((out / 'candidate.nes').with_suffix(suffix), alias.with_suffix(suffix))
    assert sha(installed) == sha(alias) == FINAL
    q = dict(adopted=True, goal_complete=False, ROM_sha256=FINAL, parent_ROM_sha256=PARENT,
             fresh_root_compile_exact=True, changed_PRG_banks=[79, 87, 93], changed_ROM_bytes=124,
             preexisting_qualified_PC_RAM_and_CHR_exact=True, new_RAM_bytes=0,
             native_cases=76, independent_affected_1_1_replays=3,
             ordinary_target_hashes=build['ordinary_target_hashes'],
             proofs={str(path): sha(path) for path in proofs},
             build_proof_sha256=sha(proposal / 'build-proof.json'), backup_directory=str(out),
             Downloads_and_default_build_current=True,
             scope='Mac native extra-life/death/new-game state; TMNT full-rise and scrolled/edge actor collision; Chip/Dale legal native fall/throw contact. Kirby unchanged controls. Actual PPU/IRQ/SMC/bank/stack guards and three independent zero-death1-1 replays. Other roster/item/audio/performance/mapper obligations remain open.')
    (out / 'proof.json').write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8')
    target = ROOT / 'build/verification/pickup-contact-fixes'
    target.mkdir(exist_ok=True)
    shutil.copy2(out / 'proof.json', target / 'proof.json')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
