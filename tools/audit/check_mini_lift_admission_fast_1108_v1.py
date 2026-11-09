"""Verify a source-assembled Mini lift admission fast path on installed fc7d."""

import argparse
from collections import defaultdict
import itertools
import json
from pathlib import Path
import subprocess

from check_mini_lift_admission_1108_v1 import SPANS
from check_mini_lift_spawn_1108_v1 import N, ROOT, address, bundle, sha
from profile_mini_busy_1108_v1 import fixture


ROM = ROOT / 'build/mini-fireball-gbc-1108/candidate.nes'
PIN = 'fc7d4554fed204e8efa4c4489ee70cd5c6529ce95e0d606ffee1cda525188ec5'
SOURCE = ROOT / 'tools/reference/mini_lift_admission_fast_1108_v1.s'
OLD_PROOF = ROOT / 'build/mini-lift-admission-cpu-1108/proof.json'
ROLES = {'SCAN', 'SCAN_CALL', 'SCOPE'}


def compile_spans(out, old):
    spans = [span for span in SPANS if span[0] in ROLES]
    cfg = out/'admission.cfg'
    cfg.write_text('MEMORY {\n' + ''.join(
        f'{name}:start=${pc:04x},size={length},file="{(out/(name+".bin")).as_posix()}";\n'
        for name, _, pc, length, _ in spans) + '}\nSEGMENTS {\n' + ''.join(
        f'MINI_LIFT_{name}:load={name},type=ro;\n' for name, *_ in spans) + '}\n')
    cc = ROOT/'tools/Windows/cc65/bin'
    obj = out/'admission.o'
    subprocess.run([cc/'ca65.exe', SOURCE, '-o', obj], check=True)
    subprocess.run([cc/'ld65.exe', '-C', cfg, obj, '-o', out/'unused.bin'], check=True)
    manifest = {patch['role']: patch for patch in json.loads(OLD_PROOF.read_text())['patch_spans']}
    new = bytearray(old)
    patches = []
    for name, bank, pc, capacity, fill in spans:
        data = (out/(name+'.bin')).read_bytes()
        preimage = bytes.fromhex(manifest[name]['after']).ljust(capacity, bytes([fill]))
        start = 16 + bank * 8192 + (pc & 8191)
        assert len(data) <= capacity and old[start:start+capacity] == preimage
        new[start:start+capacity] = data.ljust(capacity, bytes([fill]))
        patches.append(dict(role=name, bank=bank, pc=pc, file_offset=start, used_bytes=len(data),
                            old_hex=preimage.hex(), new_hex=new[start:start+capacity].hex()))
    return bytes(new), patches


def state(bus):
    # Farcall SMC and stack are native volatile storage. Compare gameplay RAM,
    # all four overlay banks, PPU-visible memory, and actual final mappings.
    return (bytes(bus[:0x100]), bytes(bus[0x200:0x800]), bytes(bus[0x6000:0x8000]),
            tuple(map(bytes, bus.ram)), bytes(bus.vram), tuple(bus.rawtags), tuple(bus.chr_latches),
            bus.ppu_addr, bus.ppuctrl, bus.toggle, bus.buffer, tuple(bus.protection))


def setup_main(bus, px, seen, mode, area, world=0, level=0):
    camera = max(0, px-104)
    N.put(bus, Player_X_Position=px&255, Player_PageLoc=px>>8,
          ScreenLeft_X_Pos=camera&255, ScreenLeft_PageLoc=camera>>8,
          ScreenRight_X_Pos=(camera+255)&255, ScreenRight_PageLoc=(camera+255)>>8,
          FrameCounter=2, SavedJoypadBits=0, SavedJoypad1Bits=0,
          CrossoverBehaviorVersion=mode, SecondaryHardMode=mode, AreaAddrsLOffset=area,
          WorldNumber=world, LevelNumber=level)
    bus.ram[2][0x30c] = seen


def compare(buses, label, name, result_rows):
    measurements = []
    outputs = []
    for bus in buses:
        begin = len(bus.writes)
        result = N.invoke(bus, name, a=0, x=0, y=0, p=0x31)
        maps = [v for a,v in bus.writes[begin:] if a == 0x5115]
        measurements.append((result['CPU'], len(maps)))
        outputs.append((result['A'], result['X'], result['Y'], result['P']))
    assert state(buses[0]) == state(buses[1]), (label, name, 'observable state changed')
    if name == 'GameCoreRoutine':
        assert outputs[0] == outputs[1], (label, name, outputs)
    result_rows[label].append([*measurements[0], *measurements[1]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=True)
    old = ROM.read_bytes()
    assert sha(old) == PIN
    new, patches = compile_spans(out, old)
    bundles = (bundle(old), bundle(new))
    for b in bundles:
        b['segs']['mini_lift_tick'] = dict(start=str(0xbbcf), ooffs=str(16+24*8192+0x1bcf))
        b['syms']['MiniLiftTick'] = dict(val=str(0xbbcf), seg='mini_lift_tick')
    bases = [fixture(b, 0, False, False) for b in bundles]
    assert all(bus.ram[2][0x300] == 2 for bus in bases)

    manager = defaultdict(list)
    cases = itertools.product((0, 1), (0, 7), range(8),
                              (527,528,560,607,608,655,656,688,735,736,831,832,864,911,912))
    for mode, occupied, seen, px in cases:
        pair = [N.fork(base) for base in bases]
        bit = 1 if 528<=px<=607 else 2 if 656<=px<=735 else 4 if 832<=px<=911 else 0
        for bus in pair:
            setup_main(bus, px, seen, mode, 5)
            N.put(bus, CurrentBankC=2)
            bus[0x5116] = 2
            if occupied:
                for slot in range(6):
                    bus[address(bus.bundle, 'Enemy_Flag')+slot] = 1
                    bus[address(bus.bundle, 'Enemy_ID')+slot] = 6
        label = 'no_window' if not bit else 'seen' if seen&bit else 'all_busy' if occupied else 'spawn'
        compare(pair, label, 'MiniLiftTick', manager)

    game = defaultdict(list)
    for mode, raw, area, px, seen in itertools.product((0, 1), (41,), (0, 5),
            (400,527,528,560,607,608,656,688,735,832,864,911,912,1518,2031), (0, 7)):
        pair = [N.fork(base) for base in bases]
        for bus in pair:
            setup_main(bus, px, seen, mode, area)
            N.put(bus, SelectedCharacter=raw)
        bit = 1 if 528<=px<=607 else 2 if 656<=px<=735 else 4 if 832<=px<=911 else 0
        label = ('outside_pages' if not 512<=px<=1023 else 'no_window' if not bit else
                 'seen' if seen else 'spawn' if area==5 else 'foreign_area')
        compare(pair, label, 'GameCoreRoutine', game)
    for raw, px in itertools.product((0, 5, 6), (560, 688, 864)):
        pair = [N.fork(base) for base in bases]
        for bus in pair:
            setup_main(bus, px, 0, 0, 5)
            N.put(bus, SelectedCharacter=raw)
        compare(pair, 'foreign_character', 'GameCoreRoutine', game)

    def summarize(rows):
        return {label: dict(cases=len(group), CPU_saved=sorted({r[0]-r[2] for r in group}),
                            A_window_mapper_writes_saved=sorted({r[1]-r[3] for r in group}))
                for label, group in rows.items()}

    report = dict(passed=True, source_CPU_only=True, ROM_written=False, parent_SHA256=PIN,
                  expected_memory_only_SHA256=sha(new), patches=patches,
                  direct_admission=summarize(manager), actual_game_core=summarize(game),
                  bindings={str(f):sha(f.read_bytes()) for f in (ROM, SOURCE, OLD_PROOF, Path(__file__))},
                  scope='Finite exact linked CPU parity. Existing allocation, spawn, native motion, '
                        'Mini kernel and graphics remain byte-identical. No native or interrupt qualification.')
    (out/'proof.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('passed','direct_admission','actual_game_core')}))


if __name__ == '__main__':
    main()
