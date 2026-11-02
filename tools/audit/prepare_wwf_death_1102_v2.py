"""Bind WWF's missing death tick to the existing native guest-life sequence."""
import json
import os
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

O = R / 'build/wwf-death-1102-v2'
BASE = R / 'build/metal-reservation-1102-v42/candidate.nes'
PIN = '1cd8e192ee4bee33dfe0d9c737bec097e1cf2339e0b9f77353fd5194f2530f55'


def main():
    O.mkdir(exist_ok=True)
    assert sha(BASE) == PIN
    b = scoped_load(BASE)
    table = location(b, 'WfResolveTargets')
    at = table + 8 * 3
    old = b['raw'][at:at + 3]
    reject = address(b, 'WfNoop')
    reject_bank = ((location(b, 'WfNoop') - 16) // 8192) | 128
    assert old == bytes([reject & 255, reject >> 8, reject_bank])
    assert address(b, 'WfResolveTargets') == 0xb7dc and (at - 16) // 8192 == 96
    target = address(b, 'MegaManDeathUpdate')
    target_bank = ((location(b, 'MegaManDeathUpdate') - 16) // 8192) | 128
    assert target == 0xaf3a and target_bank == 136
    # Bind the real current life-loss worker and the readable native source;
    # do not add a timer, source-game endurance behavior or a new RAM owner.
    worker = b['raw'][location(b, 'MegaManDeathUpdate'):location(b, 'MegaManDeathUpdate') + int(b['syms']['MegaManDeathUpdate']['size'])]
    assert worker[0] == 0xee and worker[-1] == 0x60
    source = (R / 'build/wwf-roster-native-1101-v1/runtime.s').read_text(encoding='utf-8')
    table_source = source.split('WfResolveTargets:\n', 1)[1].split(';', 1)[0]
    rows = [line.strip().split()[1] for line in table_source.splitlines() if line.strip().startswith('Target ')]
    assert len(rows) == 36 and rows[8] == 'WfNoop'
    rows[8] = 'MegaManDeathUpdate'
    (O / 'death-row.s').write_text('; Existing WWF row8 is the guest death-tick contract.\n'
        '; Replace Target WfNoop with Target MegaManDeathUpdate; all other35 rows stay exact.\n'
        + f'MegaManDeathUpdate=${target:04x}\nNativeDeathBank=${target_bank:02x}\n'
        + '.word MegaManDeathUpdate\n.byte NativeDeathBank\n', encoding='utf-8', newline='\n')
    raw = bytearray(b['raw'])
    new = bytes([target & 255, target >> 8, target_bank])
    raw[at:at + 3] = new
    candidate = O / 'candidate.nes'
    candidate.write_bytes(raw)
    for suffix in ['.lbl', '.dbg']:
        os.link(BASE.with_suffix(suffix), candidate.with_suffix(suffix))
    q = dict(assembled=True, installed=False, native=False, parent_ROM_SHA256=PIN,
             ROM_SHA256=sha(candidate), patch=dict(offset=at, old=old.hex(), new=new.hex(),
                 physical_PRG=96, CPU=address(b, 'WfResolveTargets') + 24, service_row=8),
             new_ROM_or_RAM_bytes=0, affected_WWF_alternates=6,
             existing_worker=dict(physical_PRG=8, CPU=target, exact_bytes=worker.hex()),
             scope='Only existing WWF death-tick row8 changes. Native pit/death start already initializes '
                   'MmDeathAge/Pit; real existing update completes life loss. No source endurance/animation claim.',
             bindings={str(p.relative_to(R)): sha(p) for p in [Path(__file__), BASE,
                 R / 'src/megaman_death.s', R / 'build/wwf-roster-native-1101-v1/runtime.s', O / 'death-row.s']})
    (O / 'assembly.json').write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in q.items() if k not in ['bindings', 'existing_worker']}))


if __name__ == '__main__':
    main()
