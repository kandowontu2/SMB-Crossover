"""Actual admitted/deferred caller results and next-GameLoop Y liveness."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import traceback
from mm_proto_color_rotation_cpu_v3 import P, C, prepare, execute, complete_tail, registers
from link_pit_rygar_sophia_audit_cpu import scoped_load
from mm_proto_cold_palette_cpu_v1 import configured, application
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2) + '\n')

# Actual 6502 opcodes whose effective address/value/control consumes Y.
# LDY and TAY overwrite it. No instruction is patched or skipped.
READ_Y = {0x11, 0x19, 0x31, 0x39, 0x51, 0x59, 0x71, 0x79, 0x84, 0x8c,
          0x91, 0x94, 0x96, 0x98, 0x99, 0xb1, 0xb6, 0xb9, 0xbe, 0xc0,
          0xc4, 0xc8, 0xcc, 0xd1, 0xd9, 0x88, 0xf1, 0xf9}
WRITE_Y = {0xa0, 0xa4, 0xac, 0xa8, 0xb4, 0xbc}


def entry_prefix_pair(qs):
    b = qs[0].b
    cs = []
    for q, y, p in zip(qs, [0, 255], [0xb0, 0xf0]):
        c = NesMPU(memory=q.m, pc=address(b, 'GameLoop'))
        c.a, c.x, c.y, c.p, c.sp = 0, 47, y, p, 253
        c.stPushWord(0x5aff)
        q.m.writes = []
        cs.append(c)
    trace = []
    ywritten = False
    first_y_write = None
    for _ in range(10000):
        c, other = cs
        q = qs[0]
        assert c.pc == other.pc and q.m.banks == qs[1].m.banks
        op = q.m[c.pc]
        if not ywritten and op in READ_Y:
            # Genuine UI ABI prologue preserves incoming Y as TYA/PHA;
            # its matching stack image remains live until PLA/TAY. That
            # is an intentional preservation read, not a gameplay use.
            prologue = bytes(q.m[c.pc-4:c.pc+2])
            owners = [name for name, sym in b['syms'].items() if 'seg' in sym and int(sym['val'], 0) == c.pc-4
                      and (int(b['segs'][sym['seg']]['ooffs'], 0)-16)//8192 == q.m.banks[(c.pc-0x8000)//8192]]
            assert op == 0x98 and prologue == bytes([8, 72, 138, 72, 152, 72]) and owners, ('incoming Y semantic use before overwrite', hex(c.pc), hex(op), trace)
        if (c.p ^ other.p) & 64:
            assert op not in [0x50, 0x70], ('V branch before convergence', hex(c.pc), trace)
        trace.append([c.pc, q.m.banks[(c.pc - 0x8000) // 8192] if c.pc >= 0x8000 else -1, op])
        for cpu in cs:
            cpu.step()
        if op in WRITE_Y and not ywritten and cs[0].y == cs[1].y:
            ywritten = True
            first_y_write = trace[-1]
        assert application(qs[0]) == application(qs[1]), ('application difference before convergence', trace)
        # PHP/PLP may legitimately carry the incoming V through a private
        # helper. Do not call it dead while a differing status byte is live.
        live_stack_exact = c.sp == other.sp and qs[0].m[0x100+c.sp+1:0x200] == qs[1].m[0x100+other.sp+1:0x200]
        if ywritten and registers(c) == registers(other) and live_stack_exact:
            assert qs[0].m.writes == qs[1].m.writes or all(
                0x100 <= at < 0x200 for at in {at for at, _ in qs[0].m.writes} | {at for at, _ in qs[1].m.writes}
                if [(p,v) for p,v in qs[0].m.writes if p==at] != [(p,v) for p,v in qs[1].m.writes if p==at])
            return cs, trace, first_y_write
    raise AssertionError('No complete Y/V/live-stack convergence in actual GameLoop prefix')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    rows, prefixes = [], []
    try:
        bs = [scoped_load(x / 'candidate.nes') for x in [P, C]]
        for offset, color, star, flags in itertools.product([41, 47, 48], range(6), [0, 1, 4, 9], [0x30, 0x71]):
            qs = [prepare(b, offset, color=color) for b in bs]
            cs = [execute(q, flags)[0] for q in qs]
            for q in qs:
                q.put(StarInvincibleTimer=star, IntervalTimerControl=1)
            returns = [complete_tail(q, c)[0] for q, c in zip(qs, cs)]
            old, new = returns
            assert (old.a, old.x, old.p & ~64, old.sp) == (new.a, new.x, new.p & ~64, new.sp)
            assert (old.p ^ new.p) in [0, 64]
            if star:
                assert old.y == new.y
            else:
                assert (old.y, new.y) == (color, 19)
            # Original admitted queue/counter/R0 effects are intentionally
            # deferred. Every other application byte and bank stays exact.
            base = address(bs[0], 'VRAM_Buffer1')
            allowed = {address(bs[0], n) for n in ['VRAM_Buffer1_Offset', 'ColorRotateOffset', 'R0']}
            allowed |= set(range(base + offset, base + offset + 8))
            diffs = []
            left, right = [application(q) for q in qs]
            for i, (x, y) in enumerate(zip(left, right)):
                if x != y:
                    at = i if i < 256 else i + 256
                    assert at in allowed, (hex(at), x, y)
                    diffs.append([at, x, y])
            assert qs[0].m.banks == qs[1].m.banks
            assert qs[0].m.writes == qs[1].m.writes
            rows.append(dict(offset=offset, color=color, star=star, flags=flags,
                old_return=registers(old), new_return=registers(new), exact_expected_RAM_differences=diffs,
                Y_V_scope='For star0, old returns palette-indexY and new retains incoming DrawAllY. Old admitted ADC#7 clearsV while defer preserves it. Exact only these return deltas; next actual caller converges before any semantic use, including all live stacked status bytes.'))
        # GameMode and OperModeExecutionTree both tail-dispatch through
        # JumpEngine. Their GameCore return is exactly GameLoop::PauseSkip.
        b = bs[1]
        gs = (C / 'source/src/game.s').read_text()
        assert gs.count('jsr ColorRotation') == 1
        for word in ['.word GameCoreRoutine', '.word GameMode']:
            assert gs.count(word) == 1
        pause = address(b, 'GameLoop::PauseSkip')
        po = location(b, 'GameLoop::PauseSkip')
        nmi = address(b, 'NmiDisable')
        expected = bytes([0xa9, 0, 0x8d, nmi & 255, nmi >> 8, 0x60]) if nmi >= 256 else bytes([0xa9, 0, 0x85, nmi, 0x60])
        assert b['raw'][po:po + len(expected)] == expected
        # No Y reads in release/IdleLoop before next GameLoop invocation.
        idle = (C / 'source/src/game.s').read_text().split('.proc IdleLoop', 1)[1].split('.endproc', 1)[0]
        assert all(x not in idle.lower() for x in ['ldy', 'sty', 'iny', 'dey', 'tya', 'cpy', '),y'])
        identities = [(ch, 0) for ch in range(20)] + [(ch, 1) for ch in [0, 1, 3, 4, 7, 8, 9, 12, 13, 14, 16, 17, 19]]
        for (char, variant), mode, pause_timer, start in itertools.product(identities, [0, 1], [0, 1], [0, 0x10]):
            qs = [configured(b, char, variant=variant, engine=8, tier=1) for _ in range(2)]
            for q in qs:
                q.put(CrossoverBehaviorVersion=mode, GamePauseTimer=pause_timer, SavedJoypad1Bits=start)
            cs, trace, first_y_write = entry_prefix_pair(qs)
            assert registers(cs[0]) == registers(cs[1])
            assert application(qs[0]) == application(qs[1]) and qs[0].m.writes == qs[1].m.writes
            assert qs[0].m.banks == qs[1].m.banks
            prefixes.append(dict(char=char, variant=variant, mode=mode, pause_timer=pause_timer,
                start=start, first_Y_write=first_y_write, full_Y_V_live_stack_convergence_PC=cs[0].pc, instructions=len(trace),
                actual_all_preoverwrite_instructions_do_not_readY=True, no_V_branch_before_convergence=True,
                poisoned_Y_0_vs255_V0_vs1_converges_full_live_state=True))
        put(a.output / 'actual-tail.json', rows)
        put(a.output / 'next-GameLoop-prefixes.json', prefixes)
        put(a.output / 'proof.json', dict(passed=True, source_only=True, native_run=False,
            baseline_ROM_sha256=sha(P / 'candidate.nes'), candidate_ROM_sha256=sha(C / 'candidate.nes'),
            actual_admitted_vs_deferred_GameCore_tail_cases=len(rows), actual_next_GameLoop_Y_poison_pairs=len(prefixes),
            full_return_AX_SP_NZDIC_exact=True, intentional_dead_Y_V_return='Y oldcolorindex vs incomingrendererY onstar0; V oldADC-cleared0 vs retainedincoming. Actual nextprefix has no Y read before overwrite or V branch before fullAXYP/SP/application/live-stack convergence. No broad flag mask.',
            explicit_queue_R0_counter_differences_only=True, actual_tail_orderedwrites_banks_exact=True,
            actual_release_pause_PC=pause, actual_release_bytes=list(expected), source_single_ColorRotation_call=True,
            caller_dispatch='GameMode/OperModeExecutionTree tail JumpEngine return to GameLoop::PauseSkip. IdleLoop has no Y-consuming instruction; pause/UI prefix readsY only after a genuine LDY/TAY.',
            actual_tail_sha256=sha(a.output / 'actual-tail.json'), prefixes_sha256=sha(a.output / 'next-GameLoop-prefixes.json'), tool_sha256=sha(__file__),
            limits='Finite configured source contexts, not full native scheduler or all identity state cross-product. Explicit dead Y contract, no blanket register mask or unchanged-helper claim.'))
        print((a.output / 'proof.json').read_text())
    except BaseException as e:
        put(a.output / 'failure.json', dict(passed=False, error=repr(e), traceback=traceback.format_exc(), completed=[len(rows), len(prefixes)]))
        (a.output / 'failed-tool.py').write_bytes(Path(__file__).read_bytes())
        raise


if __name__ == '__main__':
    main()
