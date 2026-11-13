"""Bounded, zero-output CPU proofs for the private armor-entry component."""

import argparse
from collections import Counter
from itertools import product
import json
from unittest.mock import patch

from py65.devices.mpu6502 import MPU

import steve_armor_transport_1112 as A
import trace_steve_shatterhand_donor_1111 as D
import check_prince_brick_support_1111 as Host
import check_steve_shatterhand_companion_transport_1111 as Transport

STOP = 0x5000
W = A.U.Jay.W


def call(cpu, entry, *, a=0, x=0, y=0, observe=None):
    cpu.pc, cpu.a, cpu.x, cpu.y, cpu.sp, cpu.p = entry, a, x, y, 0xe0, 0x21
    cpu.stPushWord(STOP-1)
    for _ in range(10000):
        if (cpu.pc, cpu.sp) == (STOP, 0xe0):
            return
        if observe:
            observe(cpu)
        assert cpu.memory[cpu.pc], ('BRK', hex(cpu.pc), hex(entry))
        cpu.step()
    raise AssertionError(('timeout', hex(entry), hex(cpu.pc)))


def cpus():
    old, new = A.link()
    models = [MPU(), MPU()]
    models[0].memory[0xc100:0xc1ef] = old['images']['UPGRADE']
    models[1].memory[0xc100:0xc1ef] = new['images']['ARMOR_TRANSPORT']
    return old, new, models


def matrix():
    old, new, (before, after) = cpus()
    totals = Counter()
    fields = A.FIELDS
    upgrade_fields = [at for name, at in fields.items() if name != 'SteveTokenSymbol' and 0xc1f0 <= at < 0xc200]
    for pattern, token in product(range(256), (1, 2)):
        for cpu in (before, after):
            cpu.memory[0xc1f0:0xc200] = [0x63]*16
            cpu.memory[fields['SteveTokenPattern']] = pattern
        call(before, old['symbols']['SteveTokenPreview'], a=token, x=147, y=93)
        call(after, new['symbols']['SteveTokenPreview'], a=token, x=147, y=93)
        assert before.p & 1 == after.p & 1
        assert before.x == after.x
        assert before.memory[0xc1f0:0xc200] == after.memory[0xc1f0:0xc200]
        if before.p & 1:
            assert before.a == after.a
        totals['preview'] += 1

    def pair(seed, context):
        for cpu in (before, after):
            cpu.memory[0xc1f0:0xc200] = [0x69]*16
            for name, value in seed.items():
                cpu.memory[fields[name]] = value
        call(before, old['symbols']['SteveTokenTick'])
        call(after, new['symbols']['SteveTokenTick'])
        assert all(before.memory[at] == after.memory[at] for at in upgrade_fields), context

    base = dict(SteveTokenPattern=0, SteveTokenCountdown=0, SteveArmorTimer=0, SteveUpgradeState=0)
    patterns = tuple(new['images']['ARMOR_TRANSPORT'][-8:])
    for pattern, actor, face in product(patterns, range(256), (0, 128)):
        pair(base | dict(SteveTokenPattern=pattern, SteveRobotActor=actor,
                         SteveUpgradeFacing=face, SteveTokenCountdown=0x31), (pattern, actor, face))
        totals['grant'] += 1
    for pattern, counter, state, timer in product(range(256), (0, 1, 0x30, 0x31, 0x80, 255), (0, 13, 16), (0, 127)):
        pair(base | dict(SteveTokenPattern=pattern, SteveTokenCountdown=counter,
                         SteveUpgradeState=state, SteveArmorTimer=timer), (pattern, counter, state, timer))
        totals['token_boundaries'] += 1
    return dict(totals)


def underflow():
    donor = D.DONOR.read_bytes()
    assert A.digest(donor) == D.PIN
    _, linked = A.link()
    source, candidate = MPU(), MPU()
    source.memory[0x8000:0xc000] = donor[16+12*8192:16+14*8192]
    # Original support/visual setup and effect allocation are caller-owned here.
    # The original B7B8 punch reset executes unmodified from the cartridge.
    for at in (0xa1c0, 0x8833, 0xc009):
        source.memory[at] = 0x60
    candidate.memory[0xc100:0xc1ef] = linked['images']['ARMOR_TRANSPORT']
    reset = A.FIELDS['StevePunchReset']
    candidate.memory[reset:reset+len(A.PUNCH_RESET)] = A.PUNCH_RESET
    source_fields = A.U.Upgrade.ALIASES | dict(StevePunchSelector=0x5a5, StevePunchDelay=0x5a4, StevePunchPhase=0x5b4)
    compared = ('SteveArmorWindup', 'SteveUpgradeState', 'SteveUpgradeAnim', 'SteveUpgradeCombo',
                'SteveArmorTimer', 'StevePunchSelector', 'StevePunchDelay', 'StevePunchPhase')
    for windup in range(256):
        for name in compared:
            value = {'SteveArmorWindup': windup, 'SteveUpgradeState': 13,
                     'StevePunchSelector': 9, 'StevePunchDelay': 7, 'StevePunchPhase': 2}.get(name, 0x63)
            source.memory[source_fields[name]] = candidate.memory[A.FIELDS[name]] = value
        call(source, 0x97e1)
        call(candidate, linked['symbols']['SteveArmorTransformTick'])
        assert all(source.memory[source_fields[name]] == candidate.memory[A.FIELDS[name]] for name in compared), windup
    return dict(donor_underflows=256, original_punch_reset=True, support_and_effect_calls_stubbed=True)


def runtime(raw, image, info):
    bundle = Host.C.Start.W.bundle(raw)
    totals = Counter()
    for robot, pattern, facing, pause in product((1, 3), (0x15,), (1, 2), (False, True)):
        pattern = 0x25 if robot == 3 else pattern
        pair = []
        for candidate in (False, True):
            m = A.resident(image if candidate else raw)
            for name, value in dict(GamePauseStatus=0, PlayerFacingDir=facing, Player_X_Position=64,
                                    Player_PageLoc=0, Player_Y_Position=176, Player_Y_HighPos=1,
                                    Player_State=0, SavedJoypadBits=0).items():
                m[W.address(bundle, name)] = value
            m[0xc1f6], m[0xc1f1] = robot, pattern
            m[0x5c80:0x5c83] = (9, 7, 2)
            cpu = MPU(memory=m)
            calls = Counter()

            def observe(q):
                if q.pc == info['linked']['symbols']['SteveArmorTransformTick']:
                    calls['transform'] += 1

            frozen = None
            for age in range(1, 180):
                paused = pause and 90 <= age < 100
                m[W.address(bundle, 'GamePauseStatus')] = int(paused)
                if age == 90 and pause:
                    frozen = tuple(m[at] for at in range(0xc1f0, 0xc200))
                call(cpu, 0xca00, observe=observe if candidate else None)
                if paused:
                    assert tuple(m[at] for at in range(0xc1f0, 0xc200)) == frozen
                effective = age-10 if pause and age >= 100 else age
                if effective == 80:
                    assert (m[0xc1f4], m[0xc1f9], m[0xc1f2]) == (13, 127, 0)
                if effective == 81:
                    assert (m[0xc1f4], m[0xc1f9], m[0xc1f3]) == (13, 123 if candidate else 127, 47)
                if effective == 128:
                    assert (m[0xc1f4], m[0xc1f9], m[0xc1f3]) == (13, 123 if candidate else 127, 0)
                if effective == 159:
                    assert (m[0xc1f4], m[0xc1f9], m[0xc1f2]) == ((0, 3, 127) if candidate else (13, 127, 0))
                    if candidate:
                        assert m[0x5c80:0x5c83] == [0, 0, 0]
            assert calls['transform'] == (32 if candidate else 0)
            pair.append((m[0xc1f4], m[0xc1f2]))
            totals['actual_CA00_calls'] += 179
        assert pair == [(13, 0), (0, 127)]
        totals['episodes'] += 1
    return dict(totals, matching_pattern_and_robot_seeded=True, native_farcalls_render_ISR=False)


def cold(image, info):
    common, vector, cold_vector = Transport.C.Common, Transport.C.Vector, Transport.C.ColdVector
    stop = Transport.T.Weapon.Stock.STOP
    source = Host.C.Start.W.bundle(image)
    wrapper = Transport.compact_cold(info['cookie'], extended=True, upgrade=A.U.descriptor(371))
    at = A.prg(65, Transport.T.COLD)
    assert image[at:at+161] == wrapper['images']['COLD65']
    target = wrapper['symbols']['JaySceneOrRetire']
    cuts = set()

    def seed():
        memory = common.blank(source)
        common.scene(memory, 16)
        memory[0x730b] = 0x40
        return memory

    def load(memory, *, interrupts=False, fault=False):
        cpu = cold_vector.entry(memory)
        memory[0x16c], memory[0x16d] = target & 255, target >> 8

        def observe(m, c):
            if m.rawtags[1:3] != [3, 2] or not 0xb102 <= c.pc <= 0xb110:
                return
            assert c.p & 4 and all(header != info['cookie'] for header in common.headers(m))
            if fault and c.pc == 0xb108 and c.y == 0xee:
                m.corrupt_at = (2, 0x1ee)
            key = (c.pc, c.y in (0, 0xee))
            if interrupts and key not in cuts:
                cuts.add(key)
                _, branch = vector.clone(m, c)
                cold_vector.interrupt(branch, 'FF')

        vector.finish(memory, cpu, stop, observe)
        assert (cpu.a, cpu.x, cpu.y, cpu.p & 0xef, cpu.sp) == (83, 71, 109, 0x21, 224)

    memory = seed()
    load(memory, interrupts=True)
    assert common.headers(memory) == (info['cookie'],)*2 and memory.ppu_reads == 32800
    code = info['linked']['images']['ARMOR_TRANSPORT']
    assert bytes(memory.ram[2][0x100:0x1ef]) == code
    assert bytes(memory.ram[3][0xb7c:0xb7f]) == image[A.CHR+304*1024+0x7c:A.CHR+304*1024+0x7f]
    assert bytes(memory.ram[2][0x1b0b:0x1b0e]) == bytes.fromhex('adf2c1')
    assert memory.ram[2][0x1ef:0x1f1] == b'\x9d\x9d'
    load(memory)
    assert common.headers(memory) == (info['cookie'],)*2 and memory.ppu_reads == 32800
    corrupt = seed()
    load(corrupt, fault=True)
    assert corrupt.corrupt_at == (2, 0x1ee) and not any(header[0] for header in common.headers(corrupt))
    return dict(ppu_reads=memory.ppu_reads, worker_readback_bytes=len(code),
                warm_extra_reads=0, forced_blank_lag_NMI_cuts=len(cuts), final_byte_fault_rejected=True)


def natural_footprint(raw):
    """Earn the first robot and cross the real parser into active 1-2."""
    import check_steve_shatterhand_token_ingress_1111 as Ingress
    import replay_steve_route_1111 as Route

    live = A.U.Steve.Live
    bundle = Host.C.Start.W.bundle(raw)
    local = bundle['syms']['ChkContinue']
    assert int(local['val'], 0) == 0xbc14
    bundle['syms']['NativeRareGameMenuRoutineCore::ChkContinue'] = local
    linked, punch = Ingress.link(bundle, lifecycle_tick=0xca00, token_draw=0xc480)
    cookie = raw[A.prg(94, 0xb2ef):A.prg(94, 0xb2ef)+16]
    native_frame = live.C.Game.frame
    calls = Counter()
    frames = 0

    def opening(_, variant):
        memory = live.Scene.menu(bundle, variant)
        for age in range(480):
            if live.mode(memory) == live.S.PLAY:
                return memory, age
            live.C.Game.frame(memory)
        raise AssertionError('Steve did not enter active 1-1')

    def frame(memory, observe=None):
        nonlocal frames
        frames += 1

        def visit(m, cpu):
            if m.rawtags[1] == 3 and 0xa000 <= cpu.pc < 0xab00 and A.U.C.Common.headers(m) == (cookie,)*2:
                calls[cpu.pc] += 1
            if observe:
                observe(m, cpu)

        native_frame(memory, visit)

    info = dict(cookie=cookie, punch=punch, symbols=linked['symbols'])
    with patch.object(live, 'opening', opening), patch.object(live.C.Game, 'frame', frame):
        memory, earned = Ingress.third_block(raw, info, third_beta=True)
        for _ in range(55):
            earned['frame'](0)
        assert memory.ram[2][0x1f6] == 3 and memory.ram[2][0x1f1] == 0
        terminal = Route.continue_route(memory, target=3200, max_updates=3200)
    assert (terminal['level'], terminal['x'], terminal['lives'], terminal['health']) == (1, 40, 2, 6)
    assert memory.ram[2][0x1f6] == 3 and memory.ram[2][0x1f1] == 0 and not calls
    return dict(updates=frames, naturally_earned_actor=3, token_world_x=[336, 1248, 1744],
                active_level=terminal['level'], world_x=terminal['x'], health=6, lives=2,
                robot_retained=True, pattern=0, authenticated_A000_AAFF_executions=0,
                route_coverage_only=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix', action='store_true')
    parser.add_argument('--underflow', action='store_true')
    parser.add_argument('--runtime', action='store_true')
    parser.add_argument('--cold', action='store_true')
    parser.add_argument('--natural-footprint', action='store_true')
    args = parser.parse_args()
    raw = D.HOST.read_bytes()
    image, info = A.transform(raw)
    assert A.transform(image, reverse=True)[0] == raw
    allowed = {at+i for at, before, after in A.edits()[0] for i in range(len(before))}
    assert all(before == after or at in allowed for at, (before, after) in enumerate(zip(raw, image, strict=True)))
    report = dict(parent=A.digest(raw), candidate=A.digest(image), exact_reverse=True,
                  worker_bytes=239, worker_sha256=A.digest(info['linked']['images']['ARMOR_TRANSPORT']),
                  cookie=info['cookie'].hex(), release_qualified=False, output_files=0)
    if args.matrix:
        report['matrix'] = matrix()
    if args.underflow:
        report['underflow'] = underflow()
    if args.runtime:
        report['runtime'] = runtime(raw, image, info)
    if args.cold:
        report['cold'] = cold(image, info)
    if args.natural_footprint:
        report['natural_footprint'] = natural_footprint(raw)
    report['receipt_sha256'] = A.digest(json.dumps(report, sort_keys=True).encode())
    print(json.dumps(report, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
