"""Actual cold readback, native ABI and interrupt cuts for the Sonic scene tail."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_ff_head_lifetime_irq_1110 as ISR
import check_sonic_native_effects_vectors_1110 as V
import check_sonic_native_scene_1110 as Proposal

C, E, O, T = Proposal.C, Proposal.E, Proposal.O, Proposal.T
S = T.S
STOP = (S.STOP, 224)
SCENES = (4, 5, 7, 8)


def cold(image, p, program):
    bundle = C.Current.W.bundle(image)
    packet = p['packet']
    seed = O.blank(bundle)
    mailbox = bytes(seed.ram[2][0x1fd0:0x1fd3])
    clean = C.cold(seed, 43, program['new'])
    E.owned(seed, packet)
    assert clean['PPU_reads'] == 18386
    assert clean['descriptor_offsets'] == [0, 1, 2, 3, 4]
    assert bytes(seed.ram[2][0x1fd0:0x1fd3]) == mailbox
    publication = [(bank, value) for bank, at, value in seed.ram_writes if at == 0x1fe0]
    assert publication[-2:] == [(3, 0xa7), (2, 0xa7)]

    warm = V.clone(seed)
    assert C.cold(warm, 43, program['new'])['PPU_reads'] == 0
    assert warm.ram == seed.ram
    old = V.clone(seed)
    for bank in (2, 3):
        old.ram[bank][0x1fe0:0x1ff0] = Proposal.OLD_COOKIE
    assert not C.invoke(old, O.AUTH)['P'] & 1
    assert C.cold(old, 43, program['new'])['PPU_reads'] == 18386
    E.owned(old, packet)

    tail_offsets = [0x12e9, 0x12f4, 0x12f5, 0x1300, 0x1301, 0x130f, 0x1310, 0x131a]
    vector_offsets = [0x1100 + 3 * row + 1 for row in Proposal.Scene.ROWS]
    for offset in tail_offsets + vector_offsets:
        broken = O.blank(bundle)
        broken.corrupt_at = (2, offset)
        C.cold(broken, 43, program['new'], expect_success=False)
        assert O.headers(broken) == (bytes(16), bytes(16))
        assert not C.invoke(broken, O.AUTH)['P'] & 1
    return dict(clean=clean, exact_metadata_readback_bytes=1024,
                warm_zero_reads=True, old_cookie_rejected_and_reloaded=True,
                tail_and_row_readback_faults=tail_offsets + vector_offsets)


def regs(cpu):
    return cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p & 0xef, cpu.sp


def live(mem, cpu):
    return (regs(cpu), bytes(mem[3:11]), bytes(mem[0x15a:0x17b]),
            bytes(mem[0x101 + cpu.sp:0x200]), tuple(bytes(row) for row in mem.ram),
            tuple(mem.rawtags))


def start(mem, pc, y, flags):
    cpu = O.NesMPU(memory=mem, pc=pc)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 85, 73, y, flags, 224
    cpu.stPushWord(S.STOP - 1)
    return cpu


def effects_and_vectors(seed, p):
    table = p['service']['symbols']['SonicServices']
    symbols = p['scene_program']['symbols']
    counts = Counter()
    min_sp = 224
    head_fields = dict(HeadPending=1, HeadTile=0x61, HeadRow=128,
                       HeadPhase=15, HeadColumn=2, HeadPage=1)
    raw_getters = {10: 'BlockBufferColli_Head', 14: 'BlockBufferColli_Side',
                   35: 'BlockBufferColli_Feet'}
    inputs = {10: 0, 14: 3, 16: 0, 35: 0}
    planned = {instruction['pc'] for instruction in p['scene_program']['instructions']}
    reached = set()
    ISR.DEEPEST = None
    ISR.PATHS.clear()
    for scene in SCENES:
        for row, (ordinary, wrapper) in Proposal.Scene.ROWS.items():
            for flags in (0x21, 0xe0):
                actual = T.clone(seed, p)
                S.scene(actual, 40, 176)
                S.set_native(actual, GameEngineSubroutine=scene, DisableScreenFlag=0,
                             NmiDisable=255, PlayerSize=0, Player_Rel_XPos=80,
                             Player_Rel_YPos=176)
                actual[0xc030] = 0x0c
                actual[0xc074] = 131
                actual[0xc042] = 32
                for name, value in head_fields.items():
                    actual[p['context'][name]] = value
                for y in (180, 184, 208):
                    actual[T.pointer(40, y)] = 0x54
                expected = T.clone(actual, p)
                y = inputs[row]
                cpu = start(actual, table + 3 * row, y, flags)
                expected_pc = symbols[ordinary] if scene == 8 else (
                    S.host(expected, raw_getters[row]) if row != 16 else symbols['NativeBounds'])
                ref = start(expected, expected_pc, y, flags)
                ISR.finish(expected, ref, STOP)
                uninterrupted, expected_return = V.clone(actual, cpu)
                ISR.finish(uninterrupted, expected_return, STOP)
                scene_before = bytes(actual.ram[2][:0x900])

                def observe(mem, cpu):
                    nonlocal min_sp
                    pc = cpu.pc
                    if flags != 0x21 or mem.rawtags[2] != 2 or pc not in planned:
                        return
                    reached.add(pc)
                    for kind in ('NMI', 'IRQ'):
                        fork, copy = V.clone(mem, cpu)
                        before = live(fork, copy)
                        with patch.object(ISR, 'clone', side_effect=V.clone):
                            assert ISR.isr(fork, copy, kind, STOP) == 'returned'
                        assert live(fork, copy) == before, (scene, wrapper, kind, hex(pc))
                        ISR.finish(fork, copy, STOP)
                        # Native NMI audio/telemetry can change, but the
                        # foreground ABI, scratch, bounding box and private RAM match.
                        assert regs(copy) == regs(expected_return)
                        assert bytes(fork[3:11]) == bytes(uninterrupted[3:11])
                        bounds = actual.bounds_base
                        assert bytes(fork[bounds:bounds + 4]) == bytes(uninterrupted[bounds:bounds + 4])
                        assert fork.ram == uninterrupted.ram and fork.rawtags == uninterrupted.rawtags
                        counts['actual_tail_' + kind] += 1
                        min_sp = min(min_sp, cpu.sp)

                ISR.finish(actual, cpu, STOP, observe)
                if scene != 8 and row == 16:
                    assert not cpu.p & 1
                    assert cpu.x == ref.x and cpu.y == ref.y
                else:
                    assert regs(cpu) == regs(ref), (scene, wrapper, regs(cpu), regs(ref))
                assert actual.ram == expected.ram and actual.rawtags == expected.rawtags
                assert bytes(actual[3:11]) == bytes(expected[3:11])
                if scene != 8:
                    assert bytes(actual.ram[2][:0x900]) == scene_before
                counts['ordinary_exact_pairs' if scene == 8 else 'native_scene_pairs'] += 1
    assert reached == planned
    assert ISR.DEEPEST is not None
    state, cpu, outer, stop = ISR.DEEPEST
    nested, copy = V.clone(state, cpu)
    before = live(nested, copy)
    assert not copy.p & 4 and ISR.isr(nested, copy, 'IRQ') == 'returned'
    assert live(nested, copy) == before
    reference, ref = V.clone(state, cpu)
    ISR.finish(nested, copy, (outer[0], outer[5]))
    ISR.finish(reference, ref, (outer[0], outer[5]))
    assert live(nested, copy) == live(reference, ref)
    ISR.finish(nested, copy, stop)
    ISR.finish(reference, ref, stop)
    assert live(nested, copy) == live(reference, ref)
    return dict(cases=dict(counts), all_tail_instruction_PCs_reached=len(reached),
                handlers=dict(ISR.PATHS), deepest_nested_parent_SP=cpu.sp,
                minimum_foreground_cut_SP=min_sp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(E.R / 'build') and not args.output.exists()
    image, program, p, record = Proposal.combined()
    bundle = C.Current.W.bundle(image)
    seed = T.install(bundle, p, program)
    with patch.object(ISR, 'regs', side_effect=regs):
        vectors = effects_and_vectors(seed, p)
    result = dict(passed=True, image_SHA256=sha256(image).hexdigest(), record=record,
                  vectors=vectors, cold=cold(image, p, program), outputs_written=0)
    print(json.dumps(result, sort_keys=True), flush=True)
    assert not args.output.exists()


if __name__ == '__main__':
    main()
