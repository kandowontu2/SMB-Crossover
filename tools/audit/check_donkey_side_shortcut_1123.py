"""Verify the classic Donkey Kong terrain forwarding against the linked game."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json

import check_dkjr_sonic_dispatch_1123 as CPU
import check_prince_epoch_current_1123 as Compare
import compose_donkey_side_shortcut_1123 as Shortcut
import profile_roster_empty_draw_1123 as Profiles


B, N, W = Profiles.B, Profiles.N, Profiles.W


class Trace:
    def __init__(self, *, snapshot=None, cuts=None):
        self.snapshot, self.cuts = snapshot, cuts
        self.calls = Counter()

    def run(self, cpu, stop):
        cpu.memory.combined_terminal = stop

        def visit(c):
            point = Profiles.Profile.point(c.memory, c.pc)
            if point == (255, 0xE497) and self.snapshot is not None and not self.snapshot:
                self.snapshot.append(CPU.clone(c))
            if point == (217, Shortcut.ENTRY):
                assert c.memory[0x16C] == 0x58 and c.memory[0x16D] == 0xBC
                self.calls['native_entry'] += 1
            if point == (217, Shortcut.TAIL):
                self.calls['direct'] += 1
            if point == (193, 0xBCE6):
                self.calls['owner_probe'] += 1
            tag, pc = point
            if self.cuts is not None and tag == 217 and (Shortcut.ENTRY <= pc <= Shortcut.END
                                                     or Shortcut.TAIL <= pc <= Shortcut.TAIL + 9):
                key = pc, c.sp, c.p & 5
                if key not in self.cuts:
                    self.cuts[key] = CPU.clone(c)

        CPU.run(cpu, lambda c: (c.pc, c.sp) == stop, visit)


def paired(parent, candidate, bundle, owner, cuts):
    models = [Profiles.start(raw, bundle, owner) for raw in (parent, candidate)]
    Compare.compare(*models, owner)
    snapshots, phases = [], {}
    for label, pad, count in (('idle', 0, 8), ('walk', 1, 24), ('jump', 0x81, 12), ('land', 0, 16)):
        totals, calls = [0, 0], [Counter(), Counter()]
        for _ in range(count):
            for index, model in enumerate(models):
                trace = Trace(snapshot=snapshots if index == 0 else None,
                              cuts=cuts if index == 1 and label == 'idle' else None)
                cycles, _ = B.main_step(model, pad, trace)
                totals[index] += cycles
                calls[index].update(trace.calls)
            Compare.compare(*models, (owner, label))
        phases[label] = dict(samples=count, cycles_saved_per_update=(totals[0] - totals[1])/count,
                             path=list(map(dict, calls)))
    return phases, snapshots[0] if snapshots else None


def directed(seed, images):
    tests = Counter()
    for engine, y_select, world_x, height, terrain in product((4, 5, 8, 9, 11), range(3, 7),
                                              (7, 254, 279), (32, 176, 232), (0, 0x54, 0x25)):
        cpus = []
        for raw in images:
            c = CPU.clone(seed)
            m = c.memory
            m.bundle = dict(m.bundle, raw=raw)
            N.put(m, GameEngineSubroutine=engine, Player_X_Position=world_x & 255,
                  Player_PageLoc=world_x >> 8, Player_Y_Position=height)
            c.y = y_select
            start = W.address(m.bundle, 'Block_Buffer_1')
            for addr in range(start, start+416):
                m[addr] = terrain
            ret = m[0x101+c.sp]+256*m[0x102+c.sp]+1
            Trace().run(c, (ret, c.sp+2))
            cpus.append(c)
        old, new = cpus
        case = (engine, y_select, world_x, height, terrain)
        assert CPU.registers(old) == CPU.registers(new), (case, CPU.registers(old), CPU.registers(new))
        assert CPU.live_stack(old) == CPU.live_stack(new), case
        Compare.compare(old.memory, new.memory, case)
        tests[engine] += 1
    return dict(tests)


def main():
    from run_sonic_current_empty_cadence_1122 import ROM

    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('--directed', action='store_true')
    args.add_argument('--interrupts', action='store_true')
    args.add_argument('characters', nargs='+', choices=tuple(Profiles.ROSTER))
    cli = args.parse_args()
    raw = ROM.read_bytes()
    if sha256(raw).hexdigest() == Shortcut.CANDIDATE:
        raw = Shortcut.inverse(raw)
    candidate, digest = Shortcut.compose(raw)
    assert Shortcut.inverse(candidate) == raw
    bundle = W.Symbols.bundle()
    cuts, seed = {} if cli.interrupts else None, None
    for name in cli.characters:
        phases, first = paired(raw, candidate, bundle, name, cuts)
        if name == 'DONKEY KONG':
            seed = first
        print('DONKEY SIDE ' + json.dumps(dict(character=name, ROM=digest, phases=phases),
                                           separators=(',', ':')), flush=True)
    report = dict(ROM=digest, outputs=0)
    if cli.directed:
        assert seed is not None, 'Select Donkey Kong for the directed probes'
        report['directed_cases'] = directed(seed, (raw, candidate))
    if cli.interrupts:
        assert cuts
        report['interrupts'] = CPU.interrupts(cuts)
    print('DONKEY SIDE PROOF ' + json.dumps(report, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
