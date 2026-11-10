"""Exercise the corrected Sonic injury result, native recovery and vectors."""
import argparse
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from unittest.mock import patch

import check_ff_head_lifetime_irq_1110 as ISR
import check_sonic_native_controller_1110 as Controller
import check_sonic_native_effects_vectors_1110 as V
import check_sonic_native_injury_tier_1110 as Fix
import check_sonic_public_admission_1110 as Public
import check_roster_powerup_continuation_1110 as Main

Scene, Stage = Fix.Scene, Fix.Stage
T, C, O, E = Scene.T, Scene.C, Scene.O, Scene.E
N, W = T.N, ISR.W
STOP = (0x5b00, 224)


def call_injury(mem, entry, flags=0x31, observe=None):
    assert mem.rawtags[0] == 254
    cpu = N.NesMPU(memory=mem, pc=entry)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 43, 4, 7, flags, 224
    cpu.stPushWord(STOP[0] - 1)
    ISR.finish(mem, cpu, STOP, observe)
    return cpu


def state(mem):
    keys = ('PlayerStatus', 'PlayerSize', 'GameEngineSubroutine', 'TimerControl',
            'InjuryTimer', 'NumberofLives', 'GuestPowerupActive', 'FrameCounter')
    record = {name: N.get(mem, name) for name in keys}
    record.update(x=N.get(mem, 'Player_X_Position') + 256 * N.get(mem, 'Player_PageLoc'),
                  y=N.get(mem, 'Player_Y_Position'), donor_epoch=mem.ram[2][0x92],
                  headers=[header.hex() for header in O.headers(mem)])
    return record


def recovery(gameplay, p):
    outcomes = []
    for tier, entry in ((1, 0x976c), (2, 0x9771)):
        mem = V.clone(gameplay)
        N.put(mem, PlayerStatus=tier, PlayerSize=0, InjuryTimer=0, ObjectOffset=4)
        before = state(mem)
        writes = []

        def observe(mem, cpu):
            if cpu.pc == 0x97a4 and mem.rawtags[0] == 254:
                writes.append((cpu.a, cpu.p & 1))

        call_injury(mem, entry, observe=observe)
        injured = state(mem)
        assert writes == [(0, 0)]
        assert (injured['PlayerStatus'], injured['GameEngineSubroutine'],
                injured['TimerControl'], injured['InjuryTimer']) == (0, 10, 255, 8)
        assert injured['NumberofLives'] == 2 and injured['GuestPowerupActive'] == 0
        timings = []
        for _ in range(80):
            mem.controller_pad = 0
            Main.frame(mem)
            now = state(mem)
            assert now['NumberofLives'] == 2 and now['PlayerStatus'] == 0
            assert now['headers'] == before['headers'] and now['donor_epoch'] == before['donor_epoch']
            timings.append(now['TimerControl'])
            if now['GameEngineSubroutine'] == 8:
                break
            assert now['GameEngineSubroutine'] == 10
        else:
            raise AssertionError(('Native injury failed to recover', tier, state(mem)))
        recovered = state(mem)
        assert timings == list(range(254, 200, -1)) + [0], timings
        for _ in range(24):
            mem.controller_pad = 1
            Main.frame(mem)
        resumed = state(mem)
        assert resumed['GameEngineSubroutine'] == 8 and resumed['PlayerStatus'] == 0
        assert resumed['NumberofLives'] == 2 and resumed['x'] > recovered['x']
        assert (resumed['donor_epoch'] - recovered['donor_epoch']) & 255 == 24
        assert resumed['headers'] == [p['packet']['cookie'].hex()] * 2
        outcomes.append(dict(tier=tier, entry=entry, injured=injured, recovered=recovered,
                             resumed=resumed, recovery_Main_updates=len(timings)))
    return outcomes


def exclusions(old, new, old_p, p, program):
    counts = Counter()
    paired = [(old, old_p), (new, p)]
    old_seed, new_seed = [T.install(C.Current.W.bundle(image), packet, program)
                          for image, packet in paired]
    for tier, timer in ((0, 0), (0, 8), (1, 8), (2, 8)):
        outcomes = []
        for seed in (old_seed, new_seed):
            mem = V.clone(seed)
            T.S.scene(mem, 40, 176)
            N.put(mem, PlayerStatus=tier, InjuryTimer=timer, ObjectOffset=4)
            entered = []

            def observe(mem, cpu):
                if cpu.pc == Fix.START and mem.rawtags[2] == 2:
                    entered.append(cpu.pc)

            cpu = call_injury(mem, 0x976c, observe=observe)
            assert not entered
            observed = state(mem)
            observed.pop('headers')
            outcomes.append((ISR.regs(cpu), observed, bytes(mem[3:11])))
        assert outcomes[0] == outcomes[1], (tier, timer, outcomes)
        counts['tier0_or_native_immunity_exact_pairs'] += 1
    for owner in range(37, 43):
        outcomes = []
        for image, _ in paired:
            mem = O.blank(C.Current.W.bundle(image))
            C.cold(mem, owner, program['new'])
            cpu = Public.public(mem, 5, 7, a=43, x=4)
            outcomes.append((ISR.regs(cpu), ISR.app(mem), tuple(mem.chr_latches)))
        assert outcomes[0] == outcomes[1], owner
        counts['prior_owner_exact_row5_pairs'] += 1
    for bank in (2, 3):
        mem = V.clone(new_seed)
        mem.ram[bank][0x1fe0 + 3] ^= 1
        before = ISR.app(mem)
        cpu = Public.public(mem, 5, 7, a=43, x=4)
        assert not cpu.p & 1 and before == ISR.app(mem)
        counts['each_bad_header_rejects_row5'] += 1
    return dict(counts)


def cold(image, p, program):
    bundle = C.Current.W.bundle(image)
    packet = p['packet']
    seed = O.blank(bundle)
    mailbox = bytes(seed.ram[2][0x1fd0:0x1fd3])
    fresh = C.cold(seed, 43, program['new'])
    E.owned(seed, packet)
    assert fresh['PPU_reads'] == 18386 and fresh['descriptor_offsets'] == [0, 1, 2, 3, 4]
    assert bytes(seed.ram[2][0x1fd0:0x1fd3]) == mailbox
    publications = [(bank, value) for bank, at, value in seed.ram_writes if at == 0x1fe0]
    assert publications[-2:] == [(3, 0xa7), (2, 0xa7)]
    warm = V.clone(seed)
    assert C.cold(warm, 43, program['new'])['PPU_reads'] == 0 and warm.ram == seed.ram
    for bank in (2, 3):
        warm.ram[bank][0x1fe0:0x1ff0] = Fix.OLD_COOKIE
    assert not C.invoke(warm, O.AUTH)['P'] & 1
    assert C.cold(warm, 43, program['new'])['PPU_reads'] == 18386
    E.owned(warm, packet)
    faults = (0x1110, 0x1111, 0x131b, 0x131c, 0x131d, 0x131e)
    for offset in faults:
        mem = O.blank(bundle)
        mem.corrupt_at = (2, offset)
        C.cold(mem, 43, program['new'], expect_success=False)
        assert O.headers(mem) == (bytes(16), bytes(16))
        assert not C.invoke(mem, O.AUTH)['P'] & 1
    return dict(fresh=fresh, exact_metadata_readback_bytes=1024, warm_reads=0,
                previous_cookie_reload=True, readback_fault_offsets=faults)


def vectors(gameplay, p):
    counts = Counter()
    expected_pcs = {item['pc'] for item in p['injury_program']['instructions']}
    seen = set()
    ISR.DEEPEST = None
    ISR.PATHS.clear()

    def regs(cpu):
        return cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p & 0xef, cpu.sp

    def live(mem, cpu):
        return (regs(cpu), bytes(mem[3:11]), bytes(mem[0x15a:0x17b]),
                bytes(mem[0x101 + cpu.sp:0x200]), tuple(bytes(row) for row in mem.ram),
                tuple(mem.rawtags))

    def final(mem, cpu):
        return (regs(cpu), ISR.body(mem), bytes(mem[3:11]), bytes(mem[0x15a:0x17b]),
                tuple(bytes(row) for row in mem.ram), tuple(mem.rawtags))

    for tier in (1, 2):
        mem = V.clone(gameplay)
        N.put(mem, PlayerStatus=tier, PlayerSize=0, ObjectOffset=4, InjuryTimer=0,
              DisableScreenFlag=0, NmiDisable=255)
        ref = V.clone(mem)
        reference_return = call_injury(ref, 0x976c)

        def observe(mem, cpu):
            if cpu.pc not in expected_pcs or mem.rawtags[2] != 2:
                return
            seen.add(cpu.pc)
            for kind in ('NMI', 'IRQ'):
                fork, interrupt = V.clone(mem, cpu)
                before = live(fork, interrupt)
                assert ISR.isr(fork, interrupt, kind, STOP) == 'returned'
                assert live(fork, interrupt) == before
                ISR.finish(fork, interrupt, STOP)
                assert final(fork, interrupt) == final(ref, reference_return)
                counts['actual_' + kind] += 1

        with patch.object(ISR, 'regs', side_effect=regs), patch.object(ISR, 'clone', side_effect=V.clone):
            actual = call_injury(mem, 0x976c, observe=observe)
        assert final(mem, actual) == final(ref, reference_return)
    assert seen == expected_pcs and ISR.DEEPEST is not None
    state, parent, outer, stop = ISR.DEEPEST
    fork, interrupt = V.clone(state, parent)
    before = live(fork, interrupt)
    with patch.object(ISR, 'regs', side_effect=regs):
        assert not interrupt.p & 4 and ISR.isr(fork, interrupt, 'IRQ') == 'returned'
    assert live(fork, interrupt) == before
    ref, reference = V.clone(state, parent)
    ISR.finish(fork, interrupt, (outer[0], outer[5]))
    ISR.finish(ref, reference, (outer[0], outer[5]))
    assert live(fork, interrupt) == live(ref, reference)
    ISR.finish(fork, interrupt, stop)
    ISR.finish(ref, reference, stop)
    assert final(fork, interrupt) == final(ref, reference)
    return dict(cases=dict(counts), nested_IRQ=1, nested_parent_SP=parent.sp,
                reached_private_PCs=sorted(seen), actual_handlers=dict(ISR.PATHS))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(Stage.R / 'build') and not args.output.exists()
    old, program, old_p, _ = Stage.reconstruct()
    assert sha256(old).hexdigest() == Fix.PIN
    image, p, record = Fix.proposal(old, old_p)
    with redirect_stdout(io.StringIO()):
        opening, gameplay = Controller.run(image, p, goal_x=80)
    assert opening['passed'] and opening['terminal']['lives'] == 2
    results = dict(passed=True, record=record, recovery=recovery(gameplay, p),
                   scope=exclusions(old, image, old_p, p, program),
                   cold=cold(image, p, program), vectors=vectors(gameplay, p),
                   opening_original_frames=opening['calls']['OriginalSonicFrame'], output_files=0)
    print(json.dumps(results, sort_keys=True), flush=True)
    assert not args.output.exists()


if __name__ == '__main__':
    main()
