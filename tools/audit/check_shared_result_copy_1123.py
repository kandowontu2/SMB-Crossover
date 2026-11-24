"""Compare the shorter MMC5 result copy in the linked game and in Mesen."""

import argparse
from functools import cache
import json
from unittest.mock import patch

from py65.devices.mpu6502 import MPU

import check_prince_epoch_current_1123 as Linked
import check_prince_pipe_controls_1123 as Prince
import run_roster_empty_cadence_current_1123 as Cadence


CANDIDATES = {
    Prince.Reverse.CANDIDATE: '99aca8f42e10266ef205c1e3a7e631108e71788a28daed2c42a051928b143125',
    Prince.CapSupport.CANDIDATE: '50ddd9b19e0185a3e8c436f09bed28e6d110fa675af3d433ff6439fb4b3d8d05',
}
START = 0xAB38
OFFSET = 16 + 65 * 8192 + (START & 8191)
OLD = bytes.fromhex('08488a489848baa004bd01019d0b01e888d0f69a4c58ab')
SOURCE = '''
 php
 pha
 txa
 tsx
 ; SP is two below its value on return from the service. The shared
 ; restore tail expects Y, X, A, and P in the original four argument slots.
 sta $010a,x
 tya
 sta $0109,x
 pla
 sta $010b,x
 pla
 sta $010c,x
 jmp $ab58
 nop
'''


@cache
def replacement():
    assemble = Prince.Reverse.Pipe.Cold.Lift.assemble
    return assemble(SOURCE, {}, START)[0]


def compose(raw):
    expected = CANDIDATES[Prince.H(raw)]
    end = OFFSET + len(OLD)
    code = replacement()
    assert len(code) == len(OLD) and raw[OFFSET:end] == OLD
    image = raw[:OFFSET] + code + raw[end:]
    assert Prince.H(image) == expected
    return image


def inverse(image):
    digest = Prince.H(image)
    (parent,) = (old for old, trial in CANDIDATES.items() if trial == digest)
    code = replacement()
    end = OFFSET + len(code)
    assert image[OFFSET:end] == code
    raw = image[:OFFSET] + OLD + image[end:]
    assert Prince.H(raw) == parent
    return raw


def component_controls():
    machines = [MPU(memory=bytearray(65536)) for _ in range(2)]
    for cpu, code in zip(machines, (OLD, replacement()), strict=True):
        cpu.memory[START:START + len(code)] = code
    durations = [set(), set()]
    checks = 0
    for stack in (12, 57, 127, 128, 185, 206, 226, 243):
        for flags in range(256):
            for a, x, y in ((0, 127, 128), (1, 254, 255), (128, 255, 0), (255, 0, 127)):
                outcomes = []
                for i, cpu in enumerate(machines):
                    mem = cpu.memory
                    mem[0x100:0x200] = bytes(range(256))
                    cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = START, a, x, y, flags, stack
                    before = cpu.processorCycles
                    for _ in range(45):
                        if cpu.pc == 0xAB58:
                            break
                        assert mem[cpu.pc]
                        cpu.step()
                    else:
                        raise AssertionError('Shared restore tail was not reached')
                    assert cpu.sp == stack
                    slots = bytes(mem[0x101 + stack:0x200])
                    assert slots[6:10] == bytes((y, x, a, flags | 0x30))
                    outcomes.append(slots)
                    durations[i].add(cpu.processorCycles - before)
                assert outcomes[0] == outcomes[1]
                checks += 1
    return dict(cases=checks, old_cycles=sorted(durations[0]), new_cycles=sorted(durations[1]))


def linked_controls(raw, image):
    def enter(rom, owner):
        if owner == 'Prince':
            from probe_prince_hidden_life_current_1123 import clone, cold

            cookie = Prince.authenticate(rom)['cookie']
            return clone(cold, dict(authenticate=Prince.authenticate, COOKIE=cookie))(rom)
        return Linked.Existing.enter(rom, owner)

    with patch.object(Linked, 'enter', enter):
        for name in Linked.OWNER_CASES:
            phases = Linked.paired(raw, image, name, 18)
            print(json.dumps(dict(character=name, phases={phase: dict(updates=row['updates'],
                saved_per_update=row['saved_per_update']) for phase, row in phases.items()}),
                separators=(',', ':')), flush=True)


def interrupt_controls(image):
    from probe_prince_hidden_life_current_1123 import clone, cold

    boot = clone(cold, dict(authenticate=Prince.authenticate, COOKIE=Prince.authenticate(image)['cookie']))
    model = boot(image)
    for _ in range(4):
        Linked.B.main_step(model, 0)
    cuts = {}

    class Collect:
        def run(self, cpu, stop):
            model.combined_terminal = stop
            for _ in range(180000):
                if (cpu.pc, cpu.sp) == stop:
                    return
                if model.rawtags[1] == 193 and START <= cpu.pc < START + len(OLD):
                    key = cpu.pc, cpu.p & 4
                    if key not in cuts:
                        cuts[key] = Linked.Existing.clone(cpu)
                assert model[cpu.pc]
                cpu.step()
            raise AssertionError('Linked interrupt sample did not finish')

    Linked.B.main_step(model, 0, Collect())
    assert len({pc for pc, _ in cuts}) == 12
    result = Linked.Existing.interrupts(cuts)
    assert all(result['returns'].get(name) for name in ('IRQ', 'busyNMI'))
    print(json.dumps(result), flush=True)


def native(raw, image, names):
    base = Cadence.Previous
    timing = base.Timing
    roster = base.roster(raw)
    anchor = Cadence.reference(raw)
    work = timing.SHARED
    candidate, script = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {candidate, script} and candidate.read_bytes() == raw
    guard = base.check(timing.ROM)
    assert not guard['matching_patch_files']
    base.require_free_workspace(timing.R, timing.ROM, allow_interactive=True)
    original = script.read_bytes()
    baseline_hash, trial_hash = map(Prince.H, (raw, image))
    try:
        candidate.write_bytes(image)
        for name in names:
            for path, digest in ((timing.ROM, baseline_hash), (candidate, trial_hash)):
                assert base.check(path)['ROM_sha256'] == digest
                controller = Cadence.controller(anchor, roster[name])
                assert controller.count(timing.PIN) == 1
                script.write_bytes(controller.replace(timing.PIN, digest, 1).encode())
                result = base.run(script, path, work / 'capture', digest, 100, long_no_capture=True)
                assert result['passed'], result['receipt']['reason']
                assert not result['images'] and result['outputs_written'] == 0
                receipt = result['receipt']
                keys = ('inclusive_video_frames', 'measured_Main', 'Main_return_histogram',
                        'native_lag_NMI', 'inclusive_Main_costs')
                print(json.dumps(dict(character=name, ROM=digest, receipt_SHA256=result['receipt_SHA256'],
                    cadence={key: receipt[key] for key in keys}), separators=(',', ':')), flush=True)
    finally:
        candidate.write_bytes(raw)
        script.write_bytes(original)
        assert base.check(timing.ROM) == guard and set(work.iterdir()) == {candidate, script}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--native', nargs='+', metavar='CHARACTER')
    mode.add_argument('--interrupts', action='store_true')
    args = parser.parse_args()
    raw = Prince.ROM.read_bytes()
    image = compose(raw)
    if args.native:
        native(raw, image, args.native)
    elif args.interrupts:
        interrupt_controls(image)
    else:
        print(json.dumps(component_controls()), flush=True)
        linked_controls(raw, image)
