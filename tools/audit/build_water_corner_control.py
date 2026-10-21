"""Make an isolated diagnostic ROM using canonical generic Water corners.

Never use this control ROM as playthrough evidence. Only two optimizations are
disabled: the Water candidate JSR is redirected to the retained generic
four-corner routine, and the per-update empty-envelope shortcut is bypassed.
All movement, exact native block collision/rewards and drawing remain original.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    a = p.parse_args()
    source = a.rom.resolve()
    symbols = {m[2]: int(m[1], 16) for line in source.with_suffix('.lbl').read_text().splitlines()
               if (m := re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)', line))}
    raw = bytearray(source.read_bytes())
    assert raw[:4] == b'NES\x1a' and not raw[6] & 4
    base = 16 + 60 * 8192
    data = bytearray(raw[base:base+8192])
    old = bytes((0x20, symbols['WaterCollisionCandidate'] & 255,
                 symbols['WaterCollisionCandidate'] >> 8))
    new = bytes((0x20, symbols['CollisionCandidate'] & 255,
                 symbols['CollisionCandidate'] >> 8))
    patches = []
    start = 0
    while (offset := data.find(old, start)) >= 0:
        patches.append({'bank': 60, 'cpu': hex(0xa000+offset),
                        'before': old.hex(), 'after': new.hex(),
                        'reason': 'Use retained canonical generic radius-4 corner filter'})
        data[offset:offset+3] = new
        start = offset + 3
    assert len(patches) == 2, 'Expected both ordinary and fast Water candidate calls'
    empty = symbols['SsWaterEmpty']
    needle = bytes((0xad, empty & 255, empty >> 8))
    assert data.count(needle) == 1, 'Expected one per-ball envelope shortcut load'
    offset = data.find(needle)
    patches.append({'bank': 60, 'cpu': hex(0xa000+offset),
                    'before': needle.hex(), 'after': 'a900ea',
                    'reason': 'Force exact per-ball generic corners; do not trust the optimized envelope'})
    data[offset:offset+3] = b'\xa9\x00\xea'
    raw[base:base+8192] = data
    mapper = 'mmc5' if 'mmc5' in source.name else 'mmc3'
    out = ROOT/'build/verification/water-generic-control'/mapper
    out.mkdir(parents=True, exist_ok=True)
    rom = out/source.name
    rom.write_bytes(raw)
    for suffix in ('.lbl', '.dbg'):
        shutil.copyfile(source.with_suffix(suffix), rom.with_suffix(suffix))
    wrapper = out/'control-corners.lua'
    wrapper.write_text('dofile('+json.dumps((ROOT/'tests/menu-bootstrap.lua').as_posix())+')\n'+
                       'dofile('+json.dumps((ROOT/'tests/water-corner-differential.lua').as_posix())+')\n')
    manifest = {'diagnostic_control_only': True, 'not_playthrough_evidence': True,
                'source_rom_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'control_rom_sha256': hashlib.sha256(raw).hexdigest(),
                'patches': patches, 'canonical_radius': 4,
                'excludes': 'Only isolated collision arenas are run on this modified diagnostic ROM.'}
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'rom': str(rom), 'script': str(wrapper), 'patches': len(patches)}))


if __name__ == '__main__':
    main()
