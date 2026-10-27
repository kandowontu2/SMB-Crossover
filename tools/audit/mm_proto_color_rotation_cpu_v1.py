"""Exact ColorRotation admission, real caller, pending47B NMI and retry controls."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import traceback
from mm_proto_cold_palette_cpu_v1 import configured, application, palette
from mm_proto_base_palette_cpu_v1 import nmi_seed
from current3cee_postdma_mask_cpu_v4 import run as nmi_run
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'robot-base-palette-candidate-v2'
C = D / 'robot-color-rotation-candidate-v3'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2) + '\n')


def flags(n):
    return 0x30 | sum(1 << bit for j, bit in enumerate([0, 1, 2, 3, 6, 7]) if n >> j & 1)


def prepare(b, offset=47, frame=0, color=3, area=1, variant=1, mode=1):
    q = configured(b, 1, variant=variant, engine=8, tier=2)
    q.put(CrossoverBehaviorVersion=mode, VRAM_Buffer1_Offset=offset,
          FrameCounter=frame, ColorRotateOffset=color, AreaType=area,
          R0=0xa7, NmiDisable=255, A_B_Buttons=0xc0, Left_Right_Buttons=3,
          AreaParserTaskNum=0, ScrollThirtyTwo=0)
    # Direct-admission tests use deliberately arbitrary queue bytes. Only the
    # linked producer/NMI controls below represent valid parser packets.
    q.array('VRAM_Buffer1', [(i * 17 + 5) & 255 for i in range(84)])
    return q


def execute(q, p=0x30, start=None, interrupt=None, target=None):
    b = q.b
    pc = address(b, 'ColorRotation') if start is None else start
    q.m.writes = []
    c = NesMPU(memory=q.m, pc=pc)
    c.a, c.x, c.y, c.p, c.sp = 90, 37, 19, p, 253
    c.stPushWord(0x5aff)
    before = application(q)
    live_stack = bytes(q.m[0x1fc:0x200])
    smc = [address(b, n) + 1 for n in ['NextBank_SMC', 'SafecallA_SMC',
           'SafereturnA_SMC', 'FarcallJmpTarget_SMC']] + [address(b, 'FarcallJmpTarget_SMC') + 2]
    sites = []
    hit = False
    for _ in range(100000):
        if c.pc == 0x5b00:
            break
        if interrupt and not hit and c.pc == target:
            old = (c.a, c.x, c.y, c.p & 0xcf, c.sp, c.pc)
            owners = (q.m.banks[:], q.get('CurrentBank'), q.get('CurrentBankC'), [q.m[x] for x in smc])
            if interrupt == 'irq':
                assert not c.p & 4
                c.irq()
            else:
                assert q.get('NmiDisable') == 255
                c.nmi()
            for _ in range(100000):
                if (c.a, c.x, c.y, c.p & 0xcf, c.sp, c.pc) == old:
                    break
                c.step()
            else:
                raise AssertionError(('IRQ/NMI resume timeout', old, hex(c.pc)))
            assert owners == (q.m.banks[:], q.get('CurrentBank'), q.get('CurrentBankC'), [q.m[x] for x in smc])
            hit = True
        sites.append(c.pc)
        c.step()
    else:
        raise AssertionError(('execution timeout', hex(pc), hex(c.pc)))
    assert c.sp == 253 and bytes(q.m[0x1fc:0x200]) == live_stack
    return c, before, sorted(set(sites)), hit


def registers(c):
    return [c.a, c.x, c.y, c.p, c.sp]


def complete_tail(q, c):
    b = q.b
    # Prove the actual sole callsite and resume immediately after its JSR.
    start, end = location(b, 'GameCoreRoutine'), location(b, 'SaveAB')
    target = address(b, 'ColorRotation')
    needle = bytes([0x20, target & 255, target >> 8])
    span = b['raw'][start:end]
    assert span.count(needle) == 1
    pc = address(b, 'GameCoreRoutine') + span.index(needle) + 3
    off = start + span.index(needle) + 3
    yhigh = address(b, 'Player_Y_HighPos')
    assert b['raw'][off:off+3] == bytes([0xad, yhigh & 255, yhigh >> 8])
    # That LDA and following CMP#2 overwrite comparison N/Z/C before any
    # consumer; CMP preserves V/D/I, already unchanged by the admission CPX.
    assert b['raw'][off+3:off+5] == bytes([0xc9, 2])
    q.m.writes = []
    cpu = NesMPU(memory=q.m, pc=pc)
    cpu.a, cpu.x, cpu.y, cpu.p = c.a, c.x, c.y, c.p
    cpu.sp = 253
    cpu.stPushWord(0x5aff)
    for _ in range(100000):
        if cpu.pc == 0x5b00:
            break
        cpu.step()
    else:
        raise AssertionError(('real GameCore tail timeout', hex(cpu.pc)))
    assert cpu.sp == 253
    return cpu, pc


def actual_packet(b, variant=1, mode=1):
    q = configured(b, 1, variant=variant, engine=8, tier=2, cache=0)
    q.put(CrossoverBehaviorVersion=mode, InvDirty=1, DisableScreenFlag=0,
          FrameCounter=240, ColorRotateOffset=3, AreaType=1, NmiDisable=255)
    from mm_proto_cold_palette_cpu_v1 import invoke
    for name in ['InventoryHud', 'SpecialPalette', 'PlayerGfxHandler']:
        invoke(q, name)
    assert q.get('VRAM_Buffer1_Offset') == 47
    return q


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    counts = dict(direct=0, unchanged=0, deferred=0, callers=0, flow=0, interrupts=0)
    flows, irqs, callers = [], [], []
    try:
        assert sha(P / 'candidate.nes') == 'dfbdca24019776262c4388e3ea782fb989e24b8fc0e3cf0bfe0bbb84a9f480ad'
        assert sha(C / 'candidate.nes') == 'ca9a1c13e4f25a834ac665c4c9a6d67cf0be3c19ee7dc2af284a432e359be1fe'
        bs = [scoped_load(x / 'candidate.nes') for x in [P, C]]
        specs = [(o, f, 3, 1, flags(p)) for o, f, p in itertools.product(range(84), [0, 1], range(64))]
        specs += [(o, 248, k, ar, 0x71) for o, k, ar in itertools.product(range(84), range(6), range(4))]
        for offset, frame, color, area, p in specs:
            qs = [prepare(b, offset, frame, color, area) for b in bs]
            cs = [execute(q, p)[0] for q in qs]
            eligible = frame & 7 == 0
            if not eligible or offset < 41:
                assert registers(cs[0]) == registers(cs[1])
                assert application(qs[0]) == application(qs[1]) and qs[0].m.writes == qs[1].m.writes
                assert cs[0].processorCycles == cs[1].processorCycles
                counts['unchanged'] += 1
            else:
                # Literal existing early-return contract, now with CPX#41.
                before = prepare(bs[1], offset, frame, color, area)
                assert application(qs[1]) == application(before)
                assert not [(x, v) for x, v in qs[1].m.writes if not 0x100 <= x < 0x200]
                value = (offset - 41) & 255
                expected_p = (p & ~0x83) | int(offset >= 41) | (2 if value == 0 else 0) | (value & 128)
                assert registers(cs[1]) == [0, offset, 19, expected_p, 253]
                assert qs[1].get('ColorRotateOffset') == color
                counts['deferred'] += 1
                if offset >= 49:
                    assert application(qs[0]) == application(qs[1])
                    assert registers(cs[0])[:3] == registers(cs[1])[:3]
                    assert (cs[0].p & ~0x83) == (cs[1].p & ~0x83)
                    assert cs[0].processorCycles == cs[1].processorCycles
            assert qs[0].m.banks == qs[1].m.banks
            counts['direct'] += 1
        # Already-busy paths have only CPX flags differences. For newly busy
        # 41..48, compare the real tail to an explicitly existing defer-state
        # old call (offset49), then restore its known pending offset/queue only
        # BEFORE execution; direct oracle above separately checks no writes.
        # No return register masks: verify the full actual tail output.
        for offset, star, yhigh, p in itertools.product([41, 47, 48, 49, 83], [0, 1, 4, 9], [1, 2], [0x30, 0x71]):
            qs = [prepare(b, offset, frame=1) for b in bs]
            # Frame1 makes both original calls defer without queue changes.
            # Set the exact different eligible CPX result at the real return;
            # all A/X/Y/V/D/I effects are already bound by the direct oracle.
            cs = [execute(q, p)[0] for q in qs]
            for q in qs:
                q.put(Player_Y_HighPos=yhigh, StarInvincibleTimer=star, IntervalTimerControl=1)
            for cpu, threshold in zip(cs, [49, 41]):
                v = (offset - threshold) & 255
                cpu.a, cpu.x, cpu.y = 0, offset, 19
                cpu.p = (p & ~0x83) | int(offset >= threshold) | (2 if v == 0 else 0) | (v & 128)
            results = [complete_tail(q, c) for q, c in zip(qs, cs)]
            assert registers(results[0][0]) == registers(results[1][0])
            assert application(qs[0]) == application(qs[1]) and qs[0].m.writes == qs[1].m.writes
            assert qs[0].m.banks == qs[1].m.banks
            callers.append(dict(offset=offset, star=star, yhigh=yhigh, flags=p,
                real_resume_PC=results[0][1], full_AXYP_SP_RAM_orderedwrites_banks_exact=True,
                scope='Explicit CPX return-state liveness, not a false unchanged newly-deferred helper claim.'))
            counts['callers'] += 1
        # Source-produced47B actual993 queue, then regular NMI, then the next
        # eligible eighth-update retry. Initial counter is never advanced by
        # this fixture between attempts: only compiled ColorRotation does so.
        native = json.loads((D / 'robot-balancer-budget-review-v1/actual993-evidence.json').read_text())
        entry = next(x for x in native if x['kind'] == 'NMI-entry' and x['stamp']['frame'] == 993)
        actual_prefix = entry['queues']['buffer1'][:47]
        for variant, mode, stall in itertools.product([0, 1], [0, 1], [None, 0, 1]):
            qs = [actual_packet(b, variant, mode) for b in bs]
            packets = []
            for q in qs:
                before = bytes(q.m[address(q.b, 'VRAM_Buffer1'):address(q.b, 'VRAM_Buffer1') + 48])
                if variant == 1:
                    assert list(before[:47]) == actual_prefix
                execute(q)
                packets.append(list(q.m[address(q.b, 'VRAM_Buffer1'):address(q.b, 'VRAM_Buffer1') + q.get('VRAM_Buffer1_Offset') + 1]))
            assert len(packets[0]) == 55 and len(packets[1]) == 48
            assert packets[0][47:] == [63, 12, 4, 15, 23, 23, 15, 0]
            assert qs[0].get('ColorRotateOffset') == 4 and qs[1].get('ColorRotateOffset') == 3
            for q in qs:
                nmi_seed(q)
                q.put(InvHudActive=1, InvHudPhysical=243)
            result = [nmi_run(b, q, stall=stall) for b, q in zip(bs, qs)]
            for key in ['regs', 'banks', 'serial', 'reads']:
                assert result[0][key] == result[1][key], key
            oldpp, newpp = [palette(z['writes']) for z in result]
            assert {k: v for k, v in oldpp.items() if not 0x3f0c <= k < 0x3f10} == newpp
            assert {k: v for k, v in oldpp.items() if 0x3f0c <= k < 0x3f10} == {0x3f0c: 15, 0x3f0d: 23, 0x3f0e: 23, 0x3f0f: 15}
            hw = [[(at, v) for at, v in z['writes'] if at >= 0x4000] for z in result]
            assert hw[0] == hw[1]
            assert result[1]['cycles'] - result[0]['cycles'] == -168
            # Model complete-NMI RAM with explicit exact-value owners rather
            # than hiding all changed scratch/buffer bytes.
            differences = []
            for at in list(range(256)) + list(range(0x200, 0x800)) + list(range(0x5c00, 0x8000)):
                # run() owns a copied Bus; its exact final app RAM is returned.
                index = at if at < 256 else at - 256 if at < 0x800 else at - 21760
                x, y = result[0]['ram'][index], result[1]['ram'][index]
                if x != y:
                    differences.append(dict(address=at, old=x, new=y))
            allowed = {address(bs[0], 'ColorRotateOffset'), address(bs[0], 'R0'), address(bs[0], 'NmiR0')}
            base = address(bs[0], 'VRAM_Buffer1')
            allowed |= set(range(base + 47, base + 55))
            assert all(z['address'] in allowed for z in differences), differences
            # Retry the preserved pending counter on a native-cleared queue.
            retry = configured(bs[1], 1, variant=variant, engine=8, tier=2)
            retry.put(FrameCounter=248, AreaType=1, ColorRotateOffset=qs[1].get('ColorRotateOffset'), VRAM_Buffer1_Offset=0)
            sequence = []
            for i in range(7):
                assert retry.get('VRAM_Buffer1_Offset') == 0
                execute(retry)
                sequence.append(retry.m[address(bs[1], 'VRAM_Buffer1') + 4])
                nmi_seed(retry)
                rr = nmi_run(bs[1], retry, stall=stall)
                assert palette(rr['writes'])[0x3f0d] == sequence[-1]
                # Carry back only the actual NMI-owned returned application
                # image, not a fixture-assigned palette counter or outcome.
                for at in list(range(256)) + list(range(0x200, 0x800)) + list(range(0x5c00, 0x8000)):
                    ix = at if at < 256 else at - 256 if at < 0x800 else at - 21760
                    list.__setitem__(retry.m, at, rr['ram'][ix])
                assert retry.get('VRAM_Buffer1_Offset') == 0
                retry.set('FrameCounter', (248 + 8 * (i + 1)) & 255)
            assert sequence == [23, 7, 23, 39, 39, 39, 23]
            flows.append(dict(variant=variant, mode=mode, DMA_stall_model=stall,
                old_packet=packets[0], new_packet=packets[1], complete_NMI_cycle_delta=-168,
                exact_owned_RAM_differences=differences, next_eligible_world_color_sequence=sequence,
                palette_robot_HUD_and_all_APU_mapper_input_regs_banks_exact=True))
            counts['flow'] += 1
        # Real IRQ and lag NMI at every visited instruction of the admitted,
        # newly-deferred and already-deferred compiled routines. No runtime
        # observer callbacks, no physical-PPU scheduling claim.
        for bi, b in enumerate(bs):
            for offset in [0, 47, 83]:
                _, _, sites, _ = execute(prepare(b, offset))
                for kind in ['irq', 'nmi']:
                    qr = prepare(b, offset)
                    ref, _, _, hit = execute(qr, interrupt=kind, target=address(b, 'ColorRotation'))
                    assert hit
                    expected = application(qr)
                    for pc in sites:
                        q = prepare(b, offset)
                        c, _, _, hit = execute(q, interrupt=kind, target=pc)
                        assert hit and (c.a, c.x, c.y, c.p & 0xcf, c.sp) == (ref.a, ref.x, ref.y, ref.p & 0xcf, ref.sp)
                        assert application(q) == expected and q.m.banks == qr.m.banks
                        irqs.append(dict(ROM=bi, offset=offset, kind=kind, PC=pc))
                        counts['interrupts'] += 1
        put(a.output / 'flows.json', flows)
        put(a.output / 'callers.json', callers)
        put(a.output / 'interrupts.json', irqs)
        put(a.output / 'proof.json', dict(passed=True, source_only=True, native_run=False,
            baseline_ROM_sha256=sha(P / 'candidate.nes'), candidate_ROM_sha256=sha(C / 'candidate.nes'),
            counts=counts, offsets_0_through83_all64_physical_flag_patterns_eligible_and_ineligible=True,
            all6counter_values_all4areas=True, direct_accepted_and_ineligible_full_state_and_cycles_exact=True,
            intentional_busy_contract='Offsets41..48 now take existing no-write early return. No R0 or color-counter advance. CPX NZC is literal#41; real sole caller overwrites flags before use, full caller checked.',
            all_complete_NMI_APU_mapper_regs_banks_input_reads_exact=True,
            exact_delayed_world_command='3F0C len4 remains pending as unchanged ColorRotateOffset, not a retained VRAM command. Next eligible update recreates it in order after NMI clears busy packet.',
            removed_parser_cycles=168, previous_actual993_literal_deficit_CPU=155,
            no_native_recovery_or_generic_all_packet_safety_claim=True,
            flows_sha256=sha(a.output / 'flows.json'), callers_sha256=sha(a.output / 'callers.json'),
            interrupts_sha256=sha(a.output / 'interrupts.json'), tool_sha256=sha(__file__),
            limits='Finite assembled source controls and modeled full NMI. Configured legal actors/packets, not natural acquisition. Busy-frame world palette animation delay is intentional; no frame/input/source-audio rate change. Original native993 false retained. No native launch.'))
        print((a.output / 'proof.json').read_text())
    except BaseException as e:
        put(a.output / 'failure.json', dict(passed=False, native_run=False, error=repr(e), traceback=traceback.format_exc(), counts=counts))
        (a.output / 'failed-tool.py').write_bytes(Path(__file__).read_bytes())
        raise


if __name__ == '__main__':
    main()
