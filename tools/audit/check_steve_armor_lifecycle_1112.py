"""Compare original Steve armor lifecycle decisions with their linked leaves."""

from collections import Counter
from itertools import product
import argparse
import json

from py65.devices.mpu6502 import MPU

from check_steve_armor_transport_1112 import call
import steve_armor_transport_1112 as Transport
import trace_steve_shatterhand_donor_1111 as Donor


SOURCE = Transport.ROOT/'tools/reference/steve_armor_lifecycle_1112.s'
ORIGIN = 0x6200
ORIGINAL = {
    'SteveArmorTimer': 0x05c2, 'SteveUpgradeState': 0x05a2, 'SteveUpgradeSound': 0xf1,
    'SteveArmorWindup': 0x05ab, 'SteveRobotActor': 0x060c, 'SteveRobotAngle': 0x061c,
    'SteveArmorWarning': 0x43, 'SteveArmorEffectActor': 0x060f, 'SteveArmorExitCount': 0x064c,
    'StevePunchSelector': 0x05a5, 'StevePunchDelay': 0x05a4, 'StevePunchPhase': 0x05b4,
}
FIELDS = {name: Transport.FIELDS[name] if name in Transport.FIELDS else 0x6000+index
          for index, name in enumerate(ORIGINAL)} | {
    'StevePunchReset': 0xdb4b, 'SteveArmorExitAnimation': 0x60e0,
    'SteveArmorResetRobot': 0x60e4, 'SteveArmorAngleStep': 0x60e8,
}


def linked():
    return Transport.U.H.assemble(Transport.bindings(FIELDS)+SOURCE.read_text(),
                                  {'ARMOR_LIFECYCLE': (ORIGIN, 256)})


def advance(source, start, end, *, a=0, x=12, p=0x21):
    source.pc, source.a, source.x, source.p, source.sp = start, a, x, p, 0xe0
    for _ in range(250):
        if source.pc == end:
            assert source.sp == 0xe0
            return
        assert source.memory[source.pc], ('BRK', hex(source.pc), hex(start))
        source.step()
    raise AssertionError((hex(start), hex(source.pc), hex(end)))


def parity(source, candidate, fields, context):
    for name in fields:
        assert source.memory[ORIGINAL[name]] == candidate.memory[FIELDS[name]], (name, context)


def check(raw):
    assert Transport.digest(raw) == Donor.PIN
    program = linked()
    symbols = program['symbols']
    source, candidate = MPU(), MPU()
    source.memory[0x8000:0xc000] = raw[16+12*8192:16+14*8192]
    code = program['images']['ARMOR_LIFECYCLE']
    candidate.memory[ORIGIN:ORIGIN+len(code)] = code
    at = FIELDS['StevePunchReset']
    candidate.memory[at:at+len(Transport.PUNCH_RESET)] = Transport.PUNCH_RESET
    # Only the animation call and robot constructor are modeled. The
    # original branch, countdown and state bytes execute unmodified.
    source.memory[0xb7c6:0xb7ca] = bytes.fromhex('8d000260')
    source.memory[0x935c:0x9360] = bytes.fromhex('ee010260')
    candidate.memory[0x60e0:0x60e8] = bytes.fromhex('8d000260ee010260')
    counts = Counter()

    def seed(**values):
        for name, address in ORIGINAL.items():
            source.memory[address] = candidate.memory[FIELDS[name]] = values.get(name, 0x6d)
        for cpu in (source, candidate):
            cpu.memory[0x200:0x202] = [0x98, 0]

    for frame, timer, state in product((0, 16, 240, 255, *range(1, 16)),
                                       (0, 1, 2, 3, 126, 127, 255), (0, 3, 13, 15, 16, 17, 18, 255)):
        seed(SteveArmorTimer=timer, SteveUpgradeState=state)
        source.memory[0x0c] = frame
        advance(source, 0x9191, 0x91c1)
        call(candidate, symbols['SteveArmorClock'], a=frame)
        parity(source, candidate, ORIGINAL, (frame, timer, state))
        counts['clock'] += 1

    for timer, state in product((0, 1, 2, 127), (0x0f, 0x10, 0xff)):
        seed(SteveArmorTimer=timer, SteveUpgradeState=state)
        call(source, 0x9829)
        call(candidate, symbols['SteveArmorExitBegin'])
        parity(source, candidate, ORIGINAL, (timer, state))
        counts['exit_begin'] += 1

    # Original exit calls the hurt publisher before the support probe. Supply
    # the same support result to the host leaf and compare the animation input.
    source.memory[0xa1c0:0xa1c3] = bytes.fromhex('a50360')
    for support, actor, angle, windup, count in product((0, 128), (0, 1, 3),
            (0, 23, 24, 39, 40, 63, 64, 255), (0, 3, 123, 124, 127, 128, 255), (0, 1, 2, 16)):
        seed(SteveUpgradeState=16, SteveRobotActor=actor, SteveRobotAngle=angle,
             SteveArmorWindup=windup, SteveArmorExitCount=count)
        source.memory[3] = support
        call(source, 0x983b)
        candidate.pc, candidate.p, candidate.sp = symbols['SteveArmorExitStep'], 0x21|support, 0xe0
        candidate.stPushWord(0x4fff)
        for _ in range(100):
            if candidate.pc == 0x5000:
                break
            candidate.step()
        else:
            raise AssertionError('Armor exit did not return')
        assert candidate.sp == 0xe0
        parity(source, candidate, ORIGINAL, (support, actor, angle, windup, count))
        assert source.memory[0x200:0x202] == candidate.memory[0x200:0x202]
        counts['exit_step'] += 1
        counts['robot_reset_calls'] += candidate.memory[0x201]

    source.memory[0xae27] = 0x60
    for angle, windup in product(range(256), (0, 3, 15, 16, 31, 64, 112, 127, 128, 255)):
        seed(SteveRobotAngle=angle, SteveArmorWindup=windup)
        for source_pc, end, host_name in ((0xa5e6, 0xa5f9, 'SteveArmorEntryOrbit'),
                                         (0xa603, 0xa620, 'SteveArmorExitOrbit')):
            source.memory[0x061c] = candidate.memory[FIELDS['SteveRobotAngle']] = angle
            advance(source, source_pc, end)
            call(candidate, symbols[host_name])
            assert source.memory[0x061c] == candidate.memory[FIELDS['SteveRobotAngle']]
            assert source.memory[0x90] == candidate.a
            counts['orbit'] += 1

    for bank, source_pc, end, host_name in ((12, 0x9fbe, 0x9fce, 'SteveArmorDamage8'),
                                             (8, 0x8360, 0x8370, 'SteveArmorDamage16')):
        source.memory[0x8000:0xa000] = raw[16+bank*8192:16+(bank+1)*8192]
        for timer in range(1, 256):
            seed(SteveArmorTimer=timer)
            advance(source, source_pc, end)
            call(candidate, symbols[host_name], x=12)
            parity(source, candidate, ORIGINAL, (bank, timer))
            assert candidate.x == 12
            counts['damage_arithmetic'] += 1
    return dict(donor=Donor.PIN, leaf_bytes=len(code), leaf_sha256=Transport.digest(code),
                release_qualified=False, output_files=0, **counts)


def bank1(raw):
    import check_prince_brick_support_1111 as Host
    import check_steve_shatterhand_companion_transport_1111 as Cold

    C = Cold.C
    bundle = Host.C.Start.W.bundle(raw)
    fields = dict(FIELDS)
    fields.update(SteveArmorWarning=0xc97a, SteveArmorEffectActor=0xc97b,
                  SteveArmorExitCount=0xc97c, SteveArmorAngleStep=0xc97d,
                  SteveArmorExitAnimation=0xa300, SteveArmorResetRobot=0xa310)
    program = Transport.U.H.assemble(Transport.bindings(fields)+SOURCE.read_text(),
                                     {'ARMOR_LIFECYCLE': (0xa000, 512)})
    code, symbols = program['images']['ARMOR_LIFECYCLE'], program['symbols']
    counts, cuts = Counter(), set()

    def seed():
        memory = C.Common.blank(bundle)
        C.Common.scene(memory, 16)
        memory[0x730b] = 0x40
        memory.raw_page(1, 3)
        Cold.N.put(memory, CurrentBank=3, CurrentBankC=2)
        memory.ram[1][:len(code)] = code
        # This fixture checks native bank transport and source clock. The
        # animation/constructor callbacks remain outside the exercised path.
        memory.ram[1][0x300:0x304] = bytes.fromhex('8dfec160')
        memory.ram[1][0x310] = 0x60
        memory.ram[2][0x1b4b:0x1b4b+len(Transport.PUNCH_RESET)] = Transport.PUNCH_RESET
        return memory

    for frame, timer, state in product((0, 1, 15, 16, 255), (0, 1, 2, 3, 127), (0, 13, 16, 17)):
        memory = seed()
        memory[fields['SteveArmorTimer']] = timer
        memory[fields['SteveUpgradeState']] = state
        memory[0x16a] = frame
        target = symbols['SteveArmorClock']
        memory[0x16c], memory[0x16d] = target&255, target>>8
        cpu = Cold.N.NesMPU(memory=memory, pc=0x15a)
        cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 1, 71, 109, 0x21, 224
        cpu.stPushWord(0x5aff)

        def observe(m, current):
            if m.rawtags[1] != 1 or not target <= current.pc < target+45:
                return
            assert m.rawtags[2] == 2
            key = current.pc
            if key not in cuts:
                cuts.add(key)
                for kind in ('FF', 'IRQ'):
                    _, branch = C.Vector.clone(m, current)
                    C.ColdVector.interrupt(branch, kind)
                    counts[kind] += 1

        C.Vector.finish(memory, cpu, Cold.T.Weapon.Stock.STOP, observe)
        expected = timer
        if frame&15 == 0 and timer >= 2 and (state < 17 or timer == 2):
            expected -= 1
        assert memory[fields['SteveArmorTimer']] == expected
        assert memory.rawtags[1:3] == [3, 2] and memory[Cold.W.address(bundle, 'CurrentBank')] == 3
        assert cpu.sp == 224 and cpu.x == 71 and cpu.y == 109
        counts['native_farcalls'] += 1
    return dict(parent=Transport.digest(raw), runtime_bank=1, runtime_start=0xa000,
                runtime_bytes=len(code), raw2_fields_preserved_by_mapping=True,
                runtime_loaded_by_fixture=True, cold_transport_mounted=False, **counts)


def donor_controls(raw):
    Upgrade = Transport.U.Upgrade
    seed = Upgrade.initialized_companion(Donor.boot(raw))
    seed.memory[0x05c4] = 0x15
    for age in range(1, 251):
        Donor.frame(seed, 0)
        if seed.memory[0x05c2]:
            break
    assert age == 159 and seed.memory[0x05c2] == 127
    worker = Donor.assemble_punch()
    sequences = {'tap': [2]+[0]*35, 'hold': [2]*36, 'combo': [2, 0]*38,
                 'down_b': [32]*4+[34, 32]*36, 'up_b': [16]*4+[18, 16]*36,
                 'air': [1]*6+[3]*10+[0]*30}
    traces = {name: Donor.controller_episode(seed, worker, pads) for name, pads in sequences.items()}
    assert traces['tap'] == traces['hold']
    assert traces['tap']['births'] == [(11, 1, 10)]
    assert traces['combo']['births'] == [(11, 1, 10), (39, 1, 10), (67, 1, 10)]
    assert traces['down_b']['births'] == [(15, 9, 10), (43, 9, 10), (71, 9, 10)]
    assert traces['up_b']['births'] == [(15, 1, 10), (43, 1, 10), (71, 1, 10)]
    assert traces['air']['births'] == [(11, 8, 10)]
    return dict(matching_pattern_fixture=True, first_active_age=age,
                paired_controller_updates=sum(trace['paired_updates'] for trace in traces.values()),
                births={name: trace['births'] for name, trace in traces.items()},
                held_B_single_attack=True, current_punch_worker_matches=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank1', action='store_true')
    parser.add_argument('--donor-controls', action='store_true')
    args = parser.parse_args()
    result = check(Donor.DONOR.read_bytes())
    if args.bank1:
        result['bank1'] = bank1(Donor.HOST.read_bytes())
    if args.donor_controls:
        result['donor_controls'] = donor_controls(Donor.DONOR.read_bytes())
    print(json.dumps(result, sort_keys=True), flush=True)
