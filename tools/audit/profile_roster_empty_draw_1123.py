"""Profile full-draw gameplay updates from the current MMC5 roster in memory."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from unittest.mock import patch

import compose_prince_side_current_1123 as Nightly
import profile_dkjr_empty_current_1123 as Profile


B, N, W = Profile.Opening, Profile.N, Profile.W
ROSTER = {'BASS': (9, 0), 'DONKEY KONG': (27, 0), 'STEVE HERMANN': (15, 2),
          'MINI MARIO': (0, 8), 'MARIO': (0, 0), 'SAMUS ARAN': (2, 0)}


def start(image, bundle, name):
    if name == 'STEVE HERMANN':
        from replay_steve_natural_pickups_1113 import opening

        model, _ = opening(image)
    else:
        slot, cycle = ROSTER[name]
        with patch.object(N, 'Bus', W.ControllerBus):
            model = B.UI.seed(dict(bundle, raw=image), slot)
        for _ in range(cycle):
            B.UI.key(model, 32)
        assert B.UI.menu_name(model)[0] == name
        state = B.UI.key(model, 16)
        assert N.get(model, 'CrossoverMenuState') == 0
        N.invoke(model, 'NativeRareGameMenuRoutineCore::ChkContinue',
                 a=state['A'], x=state['X'], y=state['Y'], p=state['P'])
        N.invoke(model, 'PauseRoutine', a=0)
    for _ in range(300):
        if tuple(N.get(model, n) for n in ('OperMode', 'OperMode_Task',
                    'GameEngineSubroutine', 'Player_Y_Position')) == (1, 3, 8, 176):
            break
        B.main_step(model, 0)
    else:
        raise AssertionError(('Player did not settle after ordinary Start', name))
    for _ in range(4):
        B.main_step(model, 0)
    return model


class DrawTrace(Profile.Trace):
    def __init__(self, model):
        super().__init__(model)
        self.sections = Counter()
        self.hit = Counter()
        self.rows = Counter()
        self.balance = Counter()
        b = model.bundle
        self.object_start = W.address(b, 'ObjectMetasprite')
        self.bank = 128 | (W.location(b, 'DrawAllMetasprites') - 16) // 8192
        self.opening = W.address(b, 'DrawAllMetasprites::InitObjectLoop')
        self.ending = W.address(b, 'DrawAllMetasprites::HandleFloateyNumbers')
        self.farcall = W.address(b, 'FarCallCommon')
        self.bank_a = W.address(b, 'CurrentBank')

    def run(self, cpu, stop):
        model = self.m
        step = cpu.step
        object_pass = None

        def trace_step():
            nonlocal object_pass
            point = Profile.point(model, cpu.pc)
            if point == (self.bank, self.opening):
                assert object_pass is None
                object_pass = cpu.processorCycles
                self.rows[tuple(model[self.object_start + i] for i in range(1, 24))] += 1
            if point == (self.bank, self.ending):
                assert object_pass is not None
                self.sections['shuffled_objects'] += cpu.processorCycles - object_pass
                self.hit['shuffled_objects'] += 1
                object_pass = None
            if cpu.pc == self.farcall:
                self.balance['same_bank' if model[self.bank_a] == cpu.a else 'changes_bank'] += 1
            return step()

        cpu.step = trace_step
        try:
            super().run(cpu, stop)
        finally:
            cpu.step = step
        assert object_pass is None


def measure(model, count):
    report = {}
    for phase, pad in (('idle', 0), ('walking', 1)):
        trace, rows = DrawTrace(model), []
        for _ in range(count):
            before = B.position(model)
            assert not any(B.flags(model)) and N.get(model, 'NumberofLives') == 2
            main, nmi = B.main_step(model, pad, trace)
            assert not any(B.flags(model)) and N.get(model, 'GameEngineSubroutine') == 8
            rows.append(dict(x_before=before, x_after=B.position(model), main_cycles=main, NMI_cycles=nmi))
        full = trace.summary(rows)
        assert trace.hit['shuffled_objects'] == count
        assert not pad or rows[-1]['x_after'] > rows[0]['x_before']
        report[phase] = {key: full[key] for key in ('updates', 'first', 'last',
                          'mean_main_cycles', 'mean_logical_NMI_cycles')}
        report[phase].update(shuffled_object_cycles=trace.sections['shuffled_objects']/count,
                             empty_shuffled_passes=sum(n for r, n in trace.rows.items() if not any(r)),
                             same_bank_calls=trace.balance['same_bank']/count,
                             changed_bank_calls=trace.balance['changes_bank']/count,
                             regions=full['hot_regions'][:10], far_calls=full['hot_FarCallCommon'][:14])
    return report


def main():
    from run_sonic_current_empty_cadence_1122 import ROM

    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('characters', nargs='+', choices=tuple(ROSTER))
    cli = args.parse_args()
    raw = ROM.read_bytes()
    assert sha256(raw).hexdigest() == Nightly.CORRECTED
    bundle = W.Symbols.bundle()
    for name in cli.characters:
        report = measure(start(raw, bundle, name), 16)
        result = dict(ROM=Nightly.CORRECTED, character=name, observations=report, outputs=0)
        digest = sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        print('ROSTER EMPTY DRAW ' + json.dumps(dict(result, receipt_SHA256=digest),
                                                separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
