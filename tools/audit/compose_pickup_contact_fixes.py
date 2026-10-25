"""Compose disjoint native pickup/contact repairs without installing them."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = '55bcfb8209b628062ce1f833a2ed386bd6f08426d34fed9fa8b5ba1f90694be7'
MAC = 'db72553449649a911c025b2bf5816d49c49c16810e714fad9f61e297b4248949'
CHIP = 'bc67153ebf740182276cd60a5485ffb59d616d080c719f02d49b51ada4214d98'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    mac = D / 'mac-tmnt-native-v1'
    chip = D / 'kirby-chip-native-v1/candidate-v2'
    parent = mac / 'baseline.nes'
    assert sha(parent) == sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == PARENT
    assert sha(mac / 'candidate.nes') == MAC
    assert sha(chip / 'candidate.nes') == CHIP
    source = out / 'source'
    shutil.copytree(mac / 'source', source)
    for name in ['chip_dale_boxes.s', 'cd_contact_y_window.s']:
        shutil.copy2(chip / 'source/src' / name, source / 'src' / name)
    entry = source / 'src/entrypoint.s'
    with entry.open('a', encoding='utf-8') as f:
        f.write('\n.if ::ENABLE_MMC5_EXPANDED\n.include "cd_contact_y_window.s"\n.endif\n')
    command = [sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'),
               '--workspace', str(source), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe')]
    rom = out / 'candidate.nes'
    with (out / 'host-build.log').open('w') as log:
        subprocess.run(command + ['--output', str(rom)], cwd=ROOT, check=True,
                       stdout=log, stderr=subprocess.STDOUT)
    raw, old = rom.read_bytes(), parent.read_bytes()
    m, c = (mac / 'candidate.nes').read_bytes(), (chip / 'candidate.nes').read_bytes()
    assert raw[:16] == old[:16] and raw[16+1048576:] == old[16+1048576:]
    for bank in range(128):
        donor = m if bank in [87, 93] else c if bank == 79 else old
        span = slice(16+bank*8192, 16+(bank+1)*8192)
        assert raw[span] == donor[span], bank
    from check_tmnt_audio_fallback_oc import qualified
    before, after = qualified(parent), qualified(rom)
    assert all(after.get(n) == v for n, v in before.items())
    files = {}
    patch = ''
    for name in ['tmnt_equipment.s', 'little_mac_core.s', 'mac_tmnt_lifecycle.s',
                 'chip_dale_boxes.s', 'cd_contact_y_window.s', 'entrypoint.s']:
        target, original = source / 'src' / name, ROOT / 'src' / name
        oldtext = original.read_text(encoding='utf-8') if original.exists() else ''
        patch += ''.join(difflib.unified_diff(oldtext.splitlines(True),
                         target.read_text(encoding='utf-8').splitlines(True),
                         fromfile='a/src/'+name if oldtext else '/dev/null', tofile='b/src/'+name))
        files['src/'+name] = dict(before_sha256=sha(original) if original.exists() else None,
                                  after_sha256=sha(target))
    (out / 'implementation.patch').write_text(patch, encoding='utf-8')
    ordinary = {}
    for mapper, expected in [
        ('mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
        ('mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        target = out / ('standard-'+mapper+'.nes')
        with (out / ('standard-'+mapper+'-host.log')).open('w') as log:
            subprocess.run(command + ['--flag-off', mapper, '--output', str(target)],
                           cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
        ordinary[mapper] = sha(target)
        assert ordinary[mapper] == expected
    q = dict(passed=True, adopted=False, goal_complete=False, ROM_sha256=sha(rom),
             parent_ROM_sha256=PARENT, changed_PRG_banks=[79, 87, 93],
             changed_bytes=sum(x != y for x, y in zip(raw, old)),
             all_preexisting_qualified_addresses_exact=True, qualified_symbols=len(before),
             header_and_CHR_exact=True, new_RAM_bytes=0,
             exact_complete_bank_donors={'79': CHIP, '87,93': MAC},
             ordinary_target_hashes=ordinary, source_files=files,
             implementation_patch_sha256=sha(out / 'implementation.patch'),
             scope='Fresh composition of three disjoint repaired banks. All other bytes equal current55. Native combined-build rerun remains required before adoption.')
    (out / 'build-proof.json').write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
