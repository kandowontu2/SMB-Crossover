"""Original jump-transition and actual native event/rare-ingress proof.

The private four-owner dispatcher/header fixture remains historical18; only
the native124 bank is rebound to cf7 here. Current final owner/cold integration
is separate and must not be inferred from these legal typed fixtures.
"""
import collections
import itertools
import json
from pathlib import Path
import check_dkjr_native_bbox_1102_v66 as B
import check_dkjr_native_lifecycle_1102_v31 as D

A, R, O, W, N = B.A, B.R, B.O, B.W, B.N


def fixture():
    b, m, _, _ = B.fixture(True)
    q = json.loads((O / 'native-event-v74-layout.json').read_text())
    L = q['labels']
    m.ram[3][:0x1fe0] = bytes([255]) * 0x1fe0
    part = (O / 'native-event-v74.bin').read_bytes()
    m.ram[3][:len(part)] = part
    for kind, at in [('pause', 0x1540), ('main', 0x165e), ('ports', 0x16a7)]:
        part = (O / f'native-event-{kind}-v74.bin').read_bytes()
        m.ram[2][at:at + len(part)] = part
    current = (R / 'build/bub-initial-tier-1103-v87/bub-initial-tier.nes').read_bytes()
    assert A.sha(current) == 'cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
    raw = bytearray(b['raw'])
    at = 16 + 124 * 8192
    raw[at:at + 8192] = current[at:at + 8192]
    assert raw[at + 0x7cb] == 40
    raw[at + 0x7cb] = 41
    b = dict(b, raw=bytes(raw))
    m.bundle = b
    return b, m, L, q


def source(m):
    return bytes(m.ram[2][:0x800])


def main():
    b, seed, L, q = fixture()
    calls, checks = collections.Counter(), collections.Counter()
    original_cpu = N.NesMPU
    points = {(3, L['DkNativeBounce']): 'private_event', (3, L['DkjrJumpRestart']): 'original_D257'}
    for name in ['MegaManBounceVelocity', 'EnemyStomped']:
        points[(((W.location(b, name) - 16) // 8192) | 128, W.address(b, name))] = name
    class Trace(original_cpu):
        def step(self):
            if self.pc >= 0x8000:
                key = (self.memory.rawtags[(self.pc - 0x8000) // 8192], self.pc)
                if key in points:
                    calls[points[key]] += 1
            return super().step()
    N.NesMPU = Trace
    try:
        # A genuine native event restarts the unchanged donor transition even
        # when donor current/previous state are both already3.
        for state, direction, velocity, flags in itertools.product(
                [1, 2, 3, 4], [0, 3, 4], [0, 1, 252, 253, 255], [0x30, 0x71, 0xfe]):
            m = N.fork(seed)
            m.ram[2][0x6b] = m.ram[2][0x6c] = state
            m.ram[2][0x54], m.ram[2][0x68] = direction, 0
            oracle = D.D.Bus()
            oracle[:0x800] = source(m)
            oracle[0x6b] = 3
            D.original_call(oracle, 0xd257)
            N.put(m, Player_Y_Speed=velocity)
            before = dict(calls)
            native_coords = [N.get(m, n) for n in ['Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'Player_Y_HighPos']]
            scratch, maps = bytes(m[3:11]), list(m.rawtags)
            z = N.invoke(m, 'MegaManBounceVelocity', a=velocity, x=3, y=199, p=flags)
            expected_p = ((flags | 0x30) & ~0x82) | (2 if velocity == 0 else velocity & 128)
            assert [z[n] for n in ['A', 'X', 'Y', 'P']] == [velocity, 3, 199, expected_p], ('event AXYP', state, direction, velocity, flags, z)
            assert source(m) == bytes(oracle[:0x800]), ('original transition', state, direction, velocity, flags)
            assert native_coords == [N.get(m, n) for n in ['Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'Player_Y_HighPos']]
            assert scratch == bytes(m[3:11]) and maps == m.rawtags
            assert calls['private_event'] == before.get('private_event', 0) + 1
            assert calls['original_D257'] == before.get('original_D257', 0) + 1
            checks['actual_event_original_D257_once'] += 1
        for ready, hit, state in [(0, 0, 1), (1, 1, 1), (1, 60, 3), (1, 0, 5)]:
            m = N.fork(seed)
            m.ram[2][0x8fe], m.ram[2][0x68], m.ram[2][0x6b] = ready, hit, state
            before, old = source(m), dict(calls)
            N.invoke(m, 'MegaManBounceVelocity', a=253, x=3, y=199, p=0x31)
            assert before == source(m) and calls['original_D257'] == old.get('original_D257', 0)
            checks['unconstructed_hitstop_defeat_guard'] += 1
        # The actual native body bridge and Easy contact decision must reach
        # EnemyStomped, then the fixed event; no synthetic source jump is seeded.
        stomps = []
        for enemy in [0, 6]:
            m = N.fork(seed)
            N.invoke(m, 'InitGoomba', x=0)
            N.put(m, Enemy_ID=enemy, Enemy_Flag=1, Enemy_State=0,
                Enemy_X_Position=64, Enemy_PageLoc=0, Enemy_Y_Position=208, Enemy_Y_HighPos=1,
                CrossoverBehaviorVersion=0, Player_Y_Speed=1, ObjectOffset=0,
                AreaType=1, InjuryTimer=0, Enemy_CollisionBits=0, EnemyOffscrBitsMasked=0)
            m.ram[2][0x6b] = m.ram[2][0x6c] = 4
            before = dict(calls)
            N.invoke(m, 'HandlePECollisions', a=0, x=0, y=enemy, p=0x30)
            assert calls['EnemyStomped'] == before.get('EnemyStomped', 0) + 1, ('actual Easy native contact', enemy, dict(calls))
            assert calls['private_event'] == before.get('private_event', 0) + 1
            assert calls['original_D257'] == before.get('original_D257', 0) + 1
            assert m.ram[2][0x6b] == m.ram[2][0x6c] == 3 and N.get(m, 'NumberofLives') == 2
            stomps.append(dict(enemy_ID=enemy, actual_native_stomp=True, original_source_transition=True))
        # Ordinary source Main never interprets a native speed as an event.
        for velocity in [0, 1, 252, 253, 255]:
            m = N.fork(seed)
            B.P.P.direct(m, L['DkjrNativeFruitReset'])
            for i in range(6):
                m[W.address(b, 'Enemy_Flag') + i] = 0
            before = dict(calls)
            for epoch in range(6):
                N.put(m, Player_Y_Speed=velocity, FrameCounter=epoch, SavedJoypadBits=0,
                    SavedJoypad1Bits=0, VRAM_Buffer1_Offset=0, NmiDisable=255)
                N.invoke(m, 'GameCoreRoutine', a=85, x=0, y=0, p=0x31)
            assert calls['private_event'] == before.get('private_event', 0), ('speed inference', velocity)
            checks['ordinary_Main_native_speed_no_event'] += 6
    finally:
        N.NesMPU = original_cpu
    out = dict(passed=True, qualified=False, ROM_written=False, native_owner_admitted=False,
        historical_four_owner_header_fixture=True, actual_native124_from_cf7=True,
        checks=dict(checks), actual_Easy_contact=stomps,
        source_mechanics='Unchanged original D257 jump restart, same latched air direction/position/displacement/timing; ordinary Main has no event/speed inference.',
        assembly=dict(body_bytes=q['body_bytes'], body_spare=q['header_spare'], metadata_end=q['metadata_end'], metadata_spare=q['metadata_spare']),
        scope='Legal direct native contact/event fixtures execute current cf7 PRG124 with measured raw40 threshold in memory. Complete original2048 bytes versus genuine originalROM D257 and actual fixed MegaManBounceVelocity/EnemyStomped chain. Private manager/header fixture remains historical18; current final owner/cold/cookie, full movement/head/item/ISR and native controller remain pending.',
        bindings={p.relative_to(R).as_posix(): A.sha(p.read_bytes()) for p in [Path(__file__), Path(B.__file__), Path(D.__file__),
            O / 'native-event-v74-layout.json', O / 'native-event-v74.bin', O / 'native-event-ports-v74.bin',
            O / 'native-rare-gate-v71.json', R / 'src/collision.s', R / 'src/megaman_environment.s']})
    (O / 'native-event-v75-CPU.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ['passed', 'checks', 'actual_Easy_contact', 'assembly']}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        (O / 'native-event-v75-negative.json').write_text(json.dumps(dict(passed=False, exception=repr(error), ROM_written=False, native_owner_admitted=False), indent=2) + '\n')
        raise
