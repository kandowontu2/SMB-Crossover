"""Replay the Scrooge 3-3 helper crossing on the released cartridge bytes."""

import argparse
import json
from pathlib import Path

from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import R, prepare, sha


ROM = R / 'build/mini-contact-platform-combo-native-1110/candidate.nes'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = 'c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48'
TEMPLATE = R / 'build/generic-helper-3-3-native-1110-v7'
PREVIOUS = 'dad683110311fa7925dcc4c2ce0aff3bb645d5c51b1a68b2d5c0731052850e73'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output
    guard = check(NIGHTLY)
    assert guard['passed'] and guard['ROM_sha256'] == sha(ROM) == PIN

    controller, ready = (TEMPLATE / name for name in ('controller.lua', 'ready.json'))
    bound = json.loads(ready.read_text())
    assert bound['ROM_sha256'] == PREVIOUS and not bound['emulated_writes']
    assert bound['bindings'][str(controller)] == sha(controller)
    script = controller.read_text(encoding='utf-8')
    raw = ROM.read_bytes()
    for bank, pc, code in ((26, 0xad0b, 'ad8273'), (26, 0xad56, 'a005b9'),
                           (2, 0xa74f, 'a90095'), (0, 0xb683, 'a57518')):
        at = 16 + bank * 8192 + (pc & 8191)
        assert raw[at:at + 3] == bytes.fromhex(code), (bank, hex(pc))
    replacements = (
        (PREVIOUS, PIN),
        ('["pc"]=44373,["bytes"]={160,5,185}', '["pc"]=44374,["bytes"]={160,5,185}'),
        ('local retainedEntry=not not (entered and b.frame==3190 and b.slot==0\n'
         '   and b.camera_left==2057 and b.camera_right==2312 and b.slots_before_constructor.occupied==5\n'
         '   and v.frame==3276 and v.camera_left==2118 and v.x==2373 and v.x==v.camera_right)',
         'local retainedEntry=not not (entered and b.x>b.camera_right\n'
         '   and v.camera_right-v.x>=0 and v.camera_right-v.x<=3)'),
        ('v6_entry_preserved=retainedEntry', 'first_visible_at_edge=retainedEntry'),
    )
    for old, new in replacements:
        assert script.count(old) == 1, old
        script = script.replace(old, new)
    refs = {Path(__file__), controller, ready, NIGHTLY}
    for name, digest in bound['bindings'].items():
        path = Path(name)
        if 'playthroughs' in path.parts or path.name == 'sound_cheats_menu_native_v1.lua':
            assert sha(path) == digest, path
            refs.add(path)
    prepare(out, ROM, script, refs, expected=PIN, timeout=150, allow_interactive=True,
            scope='Current Easy Scrooge 3-3, real Start Level selection, offscreen constructor, '
                  'edge visibility, moving carry and no-loss stage exit.')


if __name__ == '__main__':
    main()
