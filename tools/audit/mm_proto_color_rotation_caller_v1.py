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


def entry_prefix(q, y):
    b = q.b
    c = NesMPU(memory=q.m, pc=address(b, 'GameLoop'))
    c.a, c.x, c.y, c.p, c.sp = 0, 47, y, 0xb0, 253
    c.stPushWord(0x5aff)
    q.m.writes = []
    trace = []
    for _ in range(10000):
        op = q.m[c.pc]
        assert op not in READ_Y, ('incoming Y consumed before overwrite', hex(c.pc), hex(op), trace)
        trace.append([c.pc, q.m.banks[(c.pc - 0x8000) // 8192] if c.pc >= 0x8000 else -1, op])
        c.step()
        if op in WRITE_Y:
            return c, trace
    raise AssertionError('No Y overwrite in actual GameLoop prefix')


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
            assert (old.a, old.x, old.p, old.sp) == (new.a, new.x, new.p, new.sp)
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
                Y_scope='For star0, old returns palette-indexY and new retains incoming DrawAllY. It is dead until next first write, tested below. Other full physical registers exact.'))
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
            cs, traces = [], []
            for q, y in zip(qs, [0, 255]):
                c, trace = entry_prefix(q, y)
                cs.append(c)
                traces.append(trace)
            assert registers(cs[0]) == registers(cs[1])
            assert application(qs[0]) == application(qs[1]) and qs[0].m.writes == qs[1].m.writes
            assert qs[0].m.banks == qs[1].m.banks and traces[0] == traces[1]
            prefixes.append(dict(char=char, variant=variant, mode=mode, pause_timer=pause_timer,
                start=start, first_Y_write=traces[0][-1], instructions=len(traces[0]),
                actual_all_preoverwrite_instructions_do_not_readY=True, poisoned_Y_0_vs255_converges_full_state=True))
        put(a.output / 'actual-tail.json', rows)
        put(a.output / 'next-GameLoop-prefixes.json', prefixes)
        put(a.output / 'proof.json', dict(passed=True, source_only=True, native_run=False,
            baseline_ROM_sha256=sha(P / 'candidate.nes'), candidate_ROM_sha256=sha(C / 'candidate.nes'),
            actual_admitted_vs_deferred_GameCore_tail_cases=len(rows), actual_next_GameLoop_Y_poison_pairs=len(prefixes),
            all_full_return_AXP_SP_exact=True, intentional_star0_dead_Y_return='oldcolorindex vs incomingrendererY; every actual tested preoverwrite path proves no Y read, full converged state exact',
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
