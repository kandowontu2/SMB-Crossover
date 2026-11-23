"""Compare the early Donkey Kong side route through actual linked gameplay."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from unittest.mock import patch

import check_donkey_side_shortcut_1123 as Previous
import compose_donkey_side_early_1123 as Shortcut
import profile_first_goomba_1123 as Goomba


B, W, CPU, Profiles = Previous.B, Previous.W, Previous.CPU, Previous.Profiles


class Trace:
    def __init__(self, *, snapshot=None, cuts=None):
        self.snapshot, self.cuts = snapshot, cuts
        self.calls = Counter()

    def run(self, cpu, stop):
        cpu.memory.combined_terminal = stop

        def visit(c):
            m = c.memory
            tag, pc = Profiles.Profile.point(m, c.pc)
            if (tag, pc) == (255, 0xE497) and self.snapshot is not None and not self.snapshot:
                self.snapshot.append(CPU.clone(c))
            if (tag, pc) == (217, Shortcut.Old.ENTRY):
                self.calls['turtle_dispatch'] += 1
            if (tag, pc) == (161, Shortcut.START) and m[pc] == 0xC9:
                assert m[0x16C] == 0xB0 and m[0x16D] == 0xBF
                self.calls['owner_test'] += 1
            if (tag, pc) == (161, 0xBFB5):
                self.calls['jr_side_setup'] += 1
            if (tag, pc) == (193, 0xBFD8):
                self.calls['dk_side_guard'] += 1
            if self.cuts is not None and tag == 161 and Shortcut.START <= pc < Shortcut.END:
                key = pc, c.sp, c.p & 5
                if key not in self.cuts:
                    self.cuts[key] = CPU.clone(c)

        CPU.run(cpu, lambda c: (c.pc, c.sp) == stop, visit)


def occupied(images, bundle):
    models = [Profiles.start(image, bundle, 'DONKEY KONG') for image in images]
    for model in models:
        Goomba.approach(model)
    Previous.Compare.compare(*models, 'first Goomba visible')
    totals = [0, 0]
    calls = [Counter(), Counter()]
    for update in range(48):
        for i, model in enumerate(models):
            assert Goomba.active_goomba(model) - B.position(model) >= 24
            trace = Trace()
            cycles, _ = B.main_step(model, 0, trace)
            totals[i] += cycles
            calls[i].update(trace.calls)
        Previous.Compare.compare(*models, ('occupied', update))
    assert calls[0]['turtle_dispatch'] and not calls[1]['turtle_dispatch']
    assert calls[0]['dk_side_guard'] == calls[1]['dk_side_guard'] == 48 * 4
    return dict(updates=48, CPU_cycles=totals, cycles_saved_per_update=(totals[0] - totals[1]) / 48,
                path=list(map(dict, calls)))


def main():
    from run_sonic_current_empty_cadence_1122 import ROM

    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('characters', nargs='+', choices=(*Profiles.ROSTER, 'DONKEY KONG JR'))
    args.add_argument('--occupied', action='store_true')
    cli = args.parse_args()
    parent = ROM.read_bytes()
    if sha256(parent).hexdigest() == Shortcut.CANDIDATE:
        parent = Shortcut.inverse(parent)
    candidate = Shortcut.compose(parent)
    assert Shortcut.inverse(candidate) == parent
    digest = sha256(candidate).hexdigest()
    bundle = W.Symbols.bundle()
    cuts, seed = {}, None
    with patch.object(Previous, 'Trace', Trace), patch.dict(Profiles.ROSTER, {'DONKEY KONG JR': (27, 1)}):
        for owner in cli.characters:
            phases, first = Previous.paired(parent, candidate, bundle, owner, cuts if owner == 'DONKEY KONG' else None)
            if owner == 'DONKEY KONG':
                seed = first
            if owner == 'DONKEY KONG JR':
                for phase in phases.values():
                    before, after = phase['path']
                    assert before.get('jr_side_setup', 0) == after.get('jr_side_setup', 0) == phase['samples'] * 4
            print('EARLY DK SIDE ' + json.dumps(dict(character=owner, ROM=digest, phases=phases),
                                               separators=(',', ':')), flush=True)
        q = dict(ROM=digest, outputs=0)
        if seed is not None:
            q.update(terrain=Previous.directed(seed, (parent, candidate)), interrupts=CPU.interrupts(cuts))
        if cli.occupied:
            q['occupied'] = occupied((parent, candidate), bundle)
    print('EARLY DK PROOF ' + json.dumps(q, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
