"""Compose native-qualified Samus wave repairs onto the accepted pickup build."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from check_tmnt_audio_fallback_oc import qualified

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = '220be8247baf877785c91244876038354442e68502b3f837920f39a674a1fa3e'
DONOR = '3eabe05b1259b3f1c764528559f5e9c1baba5771e5539380475d1d02e9c681a4'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    base = D / 'pickup-contact-fixes-combined-v1'
    donor = D / 'samus-contra-source-v1/proposal-v2'
    parent = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    assert sha(parent) == sha(base / 'candidate.nes') == PARENT
    assert sha(donor / 'candidate.nes') == DONOR
    source = out / 'source'
    shutil.copytree(base / 'source', source)
    # Restore the same canonical LF source text used by the accepted ROOT build.
    shutil.copy2(ROOT / 'src/chip_dale_boxes.s', source / 'src/chip_dale_boxes.s')
    files = {}
    for name in ['samus.s', 'samus_weapons.s']:
        original, target = ROOT / 'src' / name, source / 'src' / name
        shutil.copy2(donor / 'source/src' / name, target)
        files['src/'+name] = dict(before_sha256=sha(original), after_sha256=sha(target))
    command = [sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
               '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe')]
    target = out / 'candidate.nes'
    with (out / 'host-build.log').open('w') as log:
        subprocess.run(command + ['--output', str(target)], check=True, cwd=ROOT,
                       stdout=log, stderr=subprocess.STDOUT)
    old, raw, repaired = parent.read_bytes(), target.read_bytes(), (donor / 'candidate.nes').read_bytes()
    assert old[:16] == raw[:16] and old[16+1048576:] == raw[16+1048576:]
    for bank in range(128):
        span = slice(16+bank*8192, 16+(bank+1)*8192)
        assert raw[span] == (repaired if bank in [10, 127] else old)[span], bank
    before, after = qualified(parent), qualified(target)
    assert all(after.get(n) == value for n, value in before.items())
    ordinary = {}
    for mapper, expected in [
        ('mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
        ('mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        path = out / ('standard-'+mapper+'.nes')
        with (out / ('standard-'+mapper+'-host.log')).open('w') as log:
            subprocess.run(command + ['--flag-off', mapper, '--output', str(path)],
                           cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
        ordinary[mapper] = sha(path)
        assert ordinary[mapper] == expected
    q = dict(passed=True, adopted=False, goal_complete=False, ROM_sha256=sha(target),
             parent_ROM_sha256=PARENT, donor_ROM_sha256=DONOR,
             changed_PRG_banks=[10, 127], changed_bytes=sum(x != y for x, y in zip(old, raw)),
             all_old_qualified_addresses_exact=True, qualified_symbols=len(before),
             all_other_ROM_bytes_parent_exact=True, CHR_exact=True, new_RAM_bytes=0,
             source_files=files, ordinary_target_hashes=ordinary,
             scope='Exact complete Samus repaired-bank composition. Current-hash native rerun required before adoption.')
    (out / 'build-proof.json').write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
