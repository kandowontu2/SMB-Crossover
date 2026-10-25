"""Install the exact Samus wave composition once after native replay checks."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = '220be8247baf877785c91244876038354442e68502b3f837920f39a674a1fa3e'
FINAL = '84e55b6d60da4be5550d823f88ee40a9b220dbef5a1e8dd21de3d69aa28cb328'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    proposal = D / 'samus-wave-combined220-v1'
    out = proposal / 'adoption-v1'
    assert not out.exists(), 'One-shot adopter already ran; inspect retained state.'
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    alias = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    assert sha(installed) == sha(alias) == PARENT and sha(proposal / 'candidate.nes') == FINAL
    build = json.loads((proposal / 'build-proof.json').read_text())
    assert build['passed'] and build['ROM_sha256'] == FINAL and build['changed_bytes'] == 34
    proofs = [proposal / p for p in ['native-v1/native-proof.json', 'cpu-wave/proof.json',
                                    'route-samus/proof.json', 'route-samus/samus-easy-direct/proof.json']]
    for path in proofs:
        q = json.loads(path.read_text())
        assert q['passed'] and q['ROM_sha256'] == FINAL, path
    native = json.loads(proofs[0].read_text())
    assert len(native['cases']) == 16
    assert native['fixture_sha256'] == '736c4be6e5e5b8080892064685da00287ac8ee44f4858ede59c687b405d7297a'
    route = json.loads(proofs[3].read_text())
    assert route['result']['deaths'] == 0 and route['fixed_inputs_and_trace_exact']
    for mapper, expected in build['ordinary_target_hashes'].items():
        assert sha(proposal / ('standard-'+mapper+'.nes')) == expected
    for name, row in build['source_files'].items():
        assert sha(ROOT / name) == row['before_sha256'], name
        assert sha(proposal / 'source' / name) == row['after_sha256'], name
    out.mkdir()
    previous = out / 'previous-source'
    previous.mkdir()
    shutil.copy2(installed, out / 'previous-MMC5.nes')
    oldalias = out / 'previous-default'
    oldalias.mkdir()
    suffixes = ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.build.log']
    for suffix in suffixes:
        path = alias.with_suffix(suffix)
        if path.exists():
            shutil.copy2(path, oldalias / path.name)
    for name in build['source_files']:
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
        for path in previous.rglob('*'):
            if path.is_file():
                shutil.copy2(path, ROOT / path.relative_to(previous))
        raise
    shutil.copy2(out / 'candidate.nes', installed)
    for suffix in suffixes:
        shutil.copy2((out / 'candidate.nes').with_suffix(suffix), alias.with_suffix(suffix))
    assert sha(installed) == sha(alias) == FINAL
    q = dict(adopted=True, goal_complete=False, ROM_sha256=FINAL, parent_ROM_sha256=PARENT,
             fresh_root_compile_exact=True, changed_ROM_bytes=34, changed_PRG_banks=[10, 127],
             preexisting_PC_RAM_CHR_exact=True, new_RAM_bytes=0, native_cases=16,
             independent_SamusEasy_1_1_replay_frames=route['direct_frames'],
             proofs={str(path): sha(path) for path in proofs},
             ordinary_target_hashes=build['ordinary_target_hashes'],
             Downloads_and_default_build_current=True, backup_directory=str(out),
             scope='Source-centered upward Wave world-page arithmetic and terrain policy from its actual bridged type. Sixteen staged native cases, real Hard Wave collision (base/Long seeded), Easy tier seeded, CPU controls and independent zero-death Easy1-1 replay. No natural all-item/all-character/audio/performance completion claim.')
    (out / 'proof.json').write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8')
    target = ROOT / 'build/verification/samus-wave-fixes'
    target.mkdir(exist_ok=True)
    shutil.copy2(out / 'proof.json', target / 'proof.json')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
