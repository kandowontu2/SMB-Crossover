"""Compare a direct shared projectile draw route with the installed MMC5 code."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from unittest.mock import patch

from check_contra_force_fast_worker_1122 import assemble
import check_dkjr_side_epoch_fast_1123 as Compare
import profile_sonic_empty_cpu_1110 as Opening
import run_roster_empty_cadence_1122 as Cadence


W, N, UI = Opening.W, Opening.N, Opening.UI
DRAW_BANK = 4
ENTRY = 0xA0F5
SPECIAL_BANK = 60
FAST = 0xA582
LIMIT = 0xA5AD
OLD_ENTRY = bytes.fromhex('8d6a01a9c58d6c01a9bb8d6d01a9ce205a01')
PARENT = 'ffd7081036bca9cb165d9f4c5527e909126df70f993b4ebec75b7dd7ac83a6b1'
CANDIDATE = '27e01af3ad9e581ac1b77227bc4ba491af76eaf9c7995c3a6eea10d891087866'


def offset(bank, pc):
    return 16 + bank * 8192 + (pc & 8191)


def proposal(raw):
    assert sha256(raw).hexdigest() == PARENT
    Cadence.cadence_reference(raw)
    begin, room = offset(DRAW_BANK, ENTRY), offset(SPECIAL_BANK, FAST)
    assert raw[begin:begin + len(OLD_ENTRY)] == OLD_ENTRY
    assert raw[begin - 3:begin] == bytes.fromhex('8ede06')  # STX CurrentOAMOffset
    assert raw[begin + len(OLD_ENTRY):begin + len(OLD_ENTRY) + 5] == bytes.fromhex('ad0260c901')
    # RushDispatchSpan ends its executable code with RTS immediately before
    # this padding. ShootPose starts at LIMIT and is left untouched.
    assert raw[room - 1:room + LIMIT - FAST] == b'\x60' + b'\xea' * (LIMIT - FAST)

    # DrawAllMetasprites supplies X=0 from its OAM reservation. On return
    # it immediately reloads and compares SelectedCharacter, so A, N, Z and
    # carry from the old dispatcher are dead. None of the guards changes X/Y.
    fast = assemble(FAST, '''
        LDA $6002
        CMP #$13
        BEQ ${turtle:04x}
        CMP #$04
        BEQ ${link:04x}
        CMP #$09
        BEQ ${bass:04x}
        AND #$FE
        CMP #$10
        BEQ ${done:04x}
    draw:
        JMP $B72C
    link:
        LDA $73F8
        CMP #$01
        BNE ${draw:04x}
        RTS
    bass:
        LDA $5FEB
        BEQ ${draw:04x}
    done:
        RTS
    turtle:
        STX $7E05
        RTS
    ''')
    assert len(fast) <= LIMIT - FAST
    result = bytearray(raw)
    redirect = bytes.fromhex('8d6a01a9828d6c01a9a58d6d01a9bc205a01')
    assert len(redirect) == len(OLD_ENTRY)
    result[begin:begin + len(redirect)] = redirect
    result[room:room + len(fast)] = fast
    candidate = bytes(result)
    assert sha256(candidate).hexdigest() == CANDIDATE
    return candidate, len(fast)


def inverse(candidate):
    assert sha256(candidate).hexdigest() == CANDIDATE
    original = bytearray(candidate)
    begin, room = offset(DRAW_BANK, ENTRY), offset(SPECIAL_BANK, FAST)
    original[begin:begin + len(OLD_ENTRY)] = OLD_ENTRY
    original[room:room + LIMIT - FAST] = b'\xea' * (LIMIT - FAST)
    parent = bytes(original)
    assert sha256(parent).hexdigest() == PARENT and proposal(parent)[0] == candidate
    return parent


def boot(raw, row, source_bundle):
    bundle = dict(source_bundle, raw=raw)
    with patch.object(N, 'Bus', W.ControllerBus):
        machine = UI.seed(bundle, row['slot'])
    for _ in range(row['cycle']):
        UI.key(machine, 32)
    assert UI.menu_name(machine)[0] == row['name']
    assert N.get(machine, 'SelectedCharacter') == row['raw']
    assert all(machine[v['address']] == v['value'] for v in row['checks'])
    start = UI.key(machine, 16)
    assert N.get(machine, 'CrossoverMenuState') == 0
    N.invoke(machine, 'NativeRareGameMenuRoutineCore::ChkContinue',
             a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    N.invoke(machine, 'PauseRoutine', a=0)
    for _ in range(300):
        if tuple(N.get(machine, field) for field in ('OperMode', 'OperMode_Task',
                'GameEngineSubroutine', 'Player_Y_Position')) == (1, 3, 8, 176):
            break
        Opening.main_step(machine, 0)
    else:
        raise AssertionError(('Did not reach ordinary 1-1', row['name']))
    return machine


def compare_frames(raw, candidate, names):
    rows = Cadence.roster(raw)
    symbols = Cadence.Authority.scoped_load(Cadence.Authority.AUTHORITY)
    output = {}
    for name in names:
        parent, changed = [boot(image, rows[name], symbols) for image in (raw, candidate)]
        Compare.foreground_equal(parent, changed, (name, 'entry'))
        cases = {}
        for phase, pad, count in (('settle', 0, 4), ('idle', 0, 16), ('right', 1, 16)):
            savings = Counter()
            for index in range(count):
                assert not any(Opening.flags(parent))
                before, before_nmi = Opening.main_step(parent, pad)
                after, after_nmi = Opening.main_step(changed, pad)
                Compare.foreground_equal(parent, changed, (name, phase, index))
                assert before_nmi == after_nmi
                savings[before - after] += 1
            cases[phase] = dict(savings=dict(savings), x=Opening.position(changed))
        output[name] = cases
        print('SHARED DRAW ' + json.dumps(dict(character=name, phases=cases)), flush=True)
    return output


def compare_attacks(raw, candidate, names):
    rows = Cadence.roster(raw)
    symbols = Cadence.Authority.scoped_load(Cadence.Authority.AUTHORITY)
    shot_types = W.address(symbols, 'RgShotType')
    output = {}
    for name in names:
        parent, changed = [boot(image, rows[name], symbols) for image in (raw, candidate)]
        costs = Counter()
        projectile_updates = 0
        for index in range(72):
            pad = 0x40 if index % 12 < 6 else 0
            if 24 <= index < 48:
                pad |= 1
            if index in range(48, 55):
                pad |= 0x80
            before, before_nmi = Opening.main_step(parent, pad)
            after, after_nmi = Opening.main_step(changed, pad)
            Compare.foreground_equal(parent, changed, (name, 'attack inputs', index))
            assert before_nmi == after_nmi
            costs[before - after] += 1
            projectile_updates += any(changed[shot_types:shot_types + 10])
        if name == 'BASS':
            assert projectile_updates, 'Bass must fire a real projectile during the input sample'
        output[name] = dict(savings=dict(costs), x=Opening.position(changed), projectile_updates=projectile_updates)
        print('SHARED DRAW ' + json.dumps(dict(character=name, attacks=output[name])), flush=True)
    return output


def verify_interrupts(raw, candidate, names):
    rows = Cadence.roster(raw)
    symbols = Cadence.Authority.scoped_load(Cadence.Authority.AUTHORITY)
    cuts = {}

    class ReachedDraw:
        def run(self, cpu, stop):
            def capture(state):
                bank, pc = Compare.point(state)
                in_caller = bank == DRAW_BANK | 0x80 and ENTRY <= pc < ENTRY + len(OLD_ENTRY)
                in_draw = bank == SPECIAL_BANK | 0x80 and FAST <= pc < LIMIT - 1
                if in_caller or in_draw:
                    assert state.x == 0 and N.get(state.memory, 'NmiDisable') & 0x80
                    key = (bank, pc)
                    if key not in cuts:
                        cuts[key] = (Compare.Q.clone(state), stop)

            Compare.finish(cpu, stop, capture)

    for name in names:
        machine = boot(candidate, rows[name], symbols)
        for _ in range(4):
            Opening.main_step(machine, 0, ReachedDraw())
    assert cuts
    counts = Counter()
    for saved, stop in cuts.values():
        origin = (saved.pc, saved.sp)
        registers = Compare.registers(saved, 0xEF)
        stack = Compare.live_stack(saved)
        smc = bytes(saved.memory[0x15A:0x17B])
        mapped = tuple(saved.memory.rawtags)
        for event in ('IRQ', 'busy NMI'):
            if event == 'IRQ' and saved.p & 4:
                continue
            prior, changed = [Compare.rebound(saved, image) for image in (raw, candidate)]
            for model in (prior, changed):
                before = N.get(model.memory, 'NmiSkipped')
                (model.irq if event == 'IRQ' else model.nmi)()
                assert (model.pc, model.sp) != origin
                Compare.finish(model, origin)
                assert Compare.registers(model, 0xEF) == registers and Compare.live_stack(model) == stack
                assert bytes(model.memory[0x15A:0x17B]) == smc and tuple(model.memory.rawtags) == mapped
                assert (N.get(model.memory, 'NmiSkipped') - before) & 255 == int(event == 'busy NMI')
            Compare.equal(prior, changed, (origin, event))
            Compare.finish(changed, stop)
            counts[event] += 1
    return dict(cuts=len(cuts), returned=dict(counts))


def compare_native(raw, candidate, names):
    reference = Cadence.cadence_reference(raw)
    rows = Cadence.roster(raw)
    out = Cadence.Timing.SHARED
    target, controller = out/'candidate.nes', out/'controller.lua'
    assert set(out.iterdir()) == {target, controller} and target.read_bytes() == raw
    Cadence.require_free_workspace(Cadence.Timing.R, target, allow_interactive=True)
    previous = controller.read_bytes()
    parent_guard = Cadence.check(Cadence.Timing.ROM)
    digest = sha256(candidate).hexdigest()
    reports = {}
    try:
        target.write_bytes(candidate)
        guard = Cadence.check(target)
        assert guard['ROM_sha256'] == digest and not guard['matching_patch_files']
        for name in names:
            lua = Cadence.controller(reference, rows[name]).replace(Cadence.Timing.PIN, digest, 1)
            controller.write_bytes(lua.encode())
            result = Cadence.run(controller, target, out/'capture', digest, 90)
            assert result['outputs_written'] == 0 and not result['images']
            fields = ('passed', 'reason', 'character', 'phases', 'inclusive_video_frames', 'measured_Main',
                      'no_controller_read_frames', 'native_lag_NMI', 'inclusive_Main_costs', 'Main_return_histogram')
            report = {key: result['receipt'][key] for key in fields if key in result['receipt']}
            report.update(script_SHA256=result['script_SHA256'], receipt_SHA256=result['receipt_SHA256'])
            reports[name] = report
            print('SHARED DRAW NATIVE ' + json.dumps(report, separators=(',', ':')), flush=True)
            assert result['passed'], result['receipt']['reason']
            assert Cadence.check(target) == guard
    finally:
        controller.write_bytes(previous)
        target.write_bytes(raw)
        assert Cadence.check(Cadence.Timing.ROM) == parent_guard
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('characters', nargs='+', type=str.upper)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--native', action='store_true', help='Run the private test ROM in Mesen')
    mode.add_argument('--attacks', action='store_true', help='Compare controller-driven attack inputs')
    mode.add_argument('--interrupts', action='store_true', help='Test reached IRQ and busy-NMI cuts')
    args = parser.parse_args()
    raw = Cadence.Timing.ROM.read_bytes()
    assert Cadence.check(Cadence.Timing.ROM)['ROM_sha256'] == sha256(raw).hexdigest()
    candidate, size = proposal(raw)
    compare = compare_frames
    if args.native:
        compare = compare_native
    elif args.attacks:
        compare = compare_attacks
    elif args.interrupts:
        compare = verify_interrupts
    result = dict(parent=sha256(raw).hexdigest(), candidate=sha256(candidate).hexdigest(),
                  code_bytes=size, source_only=not args.native, results=compare(raw, candidate, args.characters))
    digest = sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    print('SHARED DRAW ' + json.dumps(dict(result, receipt_SHA256=digest)), flush=True)


if __name__ == '__main__':
    main()
