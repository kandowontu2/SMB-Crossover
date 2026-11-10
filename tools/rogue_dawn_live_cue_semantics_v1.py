"""Finite real source-NMI cue cuts and c159 phase0 queue semantics; no native."""
from pathlib import Path
import json
import re
import sys

R = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / 'tools'), str(R / 'tools/audit')]
import rogue_dawn_map_v1 as ref
import rogue_dawn_audio_driver_controls_v4 as old
from verify_native_relocation import NesMPU

OUT = R / 'docs/qa/rogue-dawn-live-cue-semantics-2026-10-29.json'
BASE = R / 'build/rogue-dawn-audio-driver-v4'
STOP = 0x5b00


def call(m, pc, a=0x36, x=0x57, y=0x98, observe=None):
    c = NesMPU(memory=m, pc=pc)
    c.a, c.x, c.y, c.p, c.sp = a, x, y, 0x61, 0xfd
    c.stPushWord(STOP - 1)
    for _ in range(20000):
        if c.pc == STOP:
            assert c.sp == 0xfd
            return c
        if observe:
            observe(c)
        assert m[c.pc] != 0, ('BRK', hex(c.pc))
        c.step()
    raise AssertionError(('Nonreturn', hex(c.pc)))


def source(raw, mode):
    m = old.Source(raw)
    # Actual initialized source scalar context. 1A=1 takes the genuine busy
    # display-skip branch; the complete real NMI/audio code still executes.
    for p, v in [(0x1a, 1), (0x1e, mode), (0x23, 0), (0x2f, 0x1d),
                 (0x7805, 0), (0x7828, 2), (0x7829, 61),
                 (0x7820, 7), (0x7821, 61), (0x106, 0x99), (0x107, 9)]:
        m[p] = v
    return m


def nmi(m, c):
    before = (c.pc, c.sp, c.a, c.x, c.y, c.p & 0xcf)
    cycles = c.processorCycles
    c.nmi()  # Real vector FFFA=CAB7; never replace or stub the NMI body.
    assert c.pc == 0xcab7
    pcs = []
    for _ in range(20000):
        if (c.pc, c.sp) == before[:2]:
            break
        assert m[c.pc] != 0, ('NMI BRK', hex(c.pc))
        pcs.append(c.pc)
        c.step()
    else:
        raise AssertionError(('NMI nonreturn', hex(c.pc)))
    assert (c.pc, c.sp, c.a, c.x, c.y, c.p & 0xcf) == before
    assert {0xc0d9, 0xc0fd, 0xc215, 0xa770, 0xb3b4, 0xcae9} <= set(pcs)
    assert m.banks == [2, 61, 62, 63]
    assert m[0x6ef] == 0
    return dict(instructions=len(pcs), cycles=c.processorCycles-cycles,
                source_root='62:CAB7 real vector through C0D9/C215/49:B3B4/RTI',
                clear_pcs=[f'{p:04X}' for p in pcs if 0xb3d8 <= p <= 0xb3e7])


def source_tick(m):
    call(m, 0xc000)  # Explicit one completed-source-foreground RNG fixture.
    m.requests = []
    c = NesMPU(memory=m, pc=STOP)
    c.sp, c.a, c.x, c.y, c.p = 0xed, 0x36, 0x57, 0x98, 0x61
    result = nmi(m, c)
    # 4014 is the genuine NMI DMA, not a source audio register request.
    return [q for q in m.requests if q[0] != 0x4014], result


def main():
    assert not OUT.exists(), 'Preserve this exact finite result'
    raw = ref.ROM.read_bytes()
    assert ref.digest(raw) == ref.EXPECTED
    candidate = (BASE / 'candidate.nes').read_bytes()
    assert ref.digest(candidate) == 'c159cf3c68066d5d72a7ba50f836b33125b8d368431e249a6c7a241a072bfb5b'
    s = old.labels(BASE / 'candidate.lbl')
    s.update({n: int(a, 16) for n, a in re.findall(
        r'^(\w+)=\$([0-9a-f]+)$', (BASE / 'src/driver-imports.inc').read_text(), re.M)})
    graph = json.loads((R / 'docs/qa/rogue-dawn-audio-source-closure-2026-10-28.json').read_text())['graph']
    sites = {}
    for row in graph['instructions']:
        b = bytes.fromhex(row['bytes'])
        if len(b) == 3 and 0x4000 <= int.from_bytes(b[1:], 'little') <= 0x4017:
            sites[row['pc'] + 0x2000] = (row['instruction'].split()[0], int.from_bytes(b[1:], 'little'), row['mode'])

    def observe(m, c):
        if c.pc >= 0x8000 and m.banks[(c.pc-0x8000)//8192] == 97:
            if c.pc in sites:
                op, at, mode = sites[c.pc]
                value = c.y if op == 'STY' else c.x if op == 'STX' else c.a
                m.requests.append([at + (c.y if mode == 'aby' else 0), value])
            elif c.pc == 0xd386:
                at = m[0xe0] + 256*m[0xe1] + c.y
                assert 0x4000 <= at < 0x4010
                m.requests.append([at, c.a])

    rows = []
    images = [('empty', [0]*6), ('jump', [0, 2, 0, 0, 0, 0]),
              ('spring-direct2', [0, 0, 0, 2, 0, 0]),
              ('mixed-with-unread-q2-canary', [0x42, 0x12, 0xa5, 2, 0x40, 0x10]),
              ('init-priority', [1, 0x12, 0xa5, 2, 0x40, 0x10])]
    for mode in [3, 5]:
        for name, image in images:
            src, host = source(raw, mode), old.Host(candidate, s)
            src[0x680] = 1
            call(host, s['RdaAudioInit'])
            call(host, s['RdaAudioSetMode'], a=mode)
            req, _ = source_tick(src)
            host.requests = []
            call(host, s['RdaAudioTick'], observe=lambda c: observe(host, c))
            assert req == host.requests
            src[0x680:0x686] = image
            host[s['RdaState']+0x80:s['RdaState']+0x86] = image
            req, witness = source_tick(src)
            host.requests = []
            call(host, s['RdaAudioTick'], observe=lambda c: observe(host, c))
            expected = [0]*6 if mode == 3 or image[0]&1 else image
            assert list(src[0x680:0x686]) == expected
            assert list(host[s['RdaState']+0x80:s['RdaState']+0x86]) == expected
            assert req == host.requests
            rows.append(dict(mode=mode, image=name, before=image, after=expected,
                             actual_source_and_compiled_requests_equal=True, **witness))

    cuts = []
    for mode in [3, 5]:
        for init in [False, True]:
            for cut in range(3):  # beforeORA, afterORA/beforeSTA, afterSTA
                m = source(raw, mode)
                m[0x680] = 1
                source_tick(m)
                m[0x680:0x686] = [int(init), 2, 0, 0, 0, 0]
                c = NesMPU(memory=m, pc=0xcbe8)
                c.a, c.x, c.y, c.p, c.sp = 0x10, 1, 0x51, 0x61, 0xfd
                c.stPushWord(STOP-1)
                for _ in range(cut):
                    c.step()
                suspended = dict(pc=f'{c.pc:04X}', a=c.a, before_queue=m[0x681])
                w = nmi(m, c)
                for _ in range(4):
                    if c.pc == STOP:
                        break
                    c.step()
                assert c.pc == STOP and c.sp == 0xfd
                expected = (0x10 if cut == 0 else 0x12 if cut == 1 else 0) if mode == 3 or init else 0x12
                assert m[0x681] == expected
                cuts.append(dict(mode=mode, init=init, suspended=suspended,
                                 final_queue1=m[0x681], **w))

    # Actual source direct Spring STA: no split inside this instruction.
    direct = []
    for mode in [3, 5]:
        for after_store in [False, True]:
            m = source(raw, mode)
            m[0x680] = 1
            source_tick(m)
            m[0x683] = 0x80
            c = NesMPU(memory=m, pc=0xa2cd)
            c.a, c.x, c.y, c.p, c.sp = 2, 0, 0x51, 0x61, 0xed
            if after_store:
                c.step()
            w = nmi(m, c)
            if not after_store:
                c.step()
            expected = 0 if mode == 3 and after_store else 2
            assert m[0x683] == expected
            direct.append(dict(mode=mode, NMI_after_real_STA=after_store,
                               source_PC='61:A2CD', value=2, final_queue3=m[0x683], **w))

    # Symbolic transport negatives use the measured original operations.
    # These are no emulator/ROM changes and are not claims of an installed adapter.
    negatives = [
        dict(name='clear-six-STA-unconditionally-during-pause', original_pending=[0, 2, 0, 0, 0, 0],
             wrong_mailbox=[0]*6, next_real_OR10_original=0x12, wrong=0x10, rejected=True),
        dict(name='busy-normal-consumes-Q-but-leaves-stale-P', paused_P1=2,
             normal_after_measured_tick_Q1=0, stale_later_P_to_Q1=2,
             rejected=True, requires='Violates the old proposal by changing cached mode before stable P assignment/writeback; must not assume impossible without that protocol guard.')]
    inputs = [Path(__file__), ref.ROM, BASE/'candidate.nes', BASE/'candidate.lbl',
              BASE/'src/driver-imports.inc', R/'tools/rogue_dawn_audio_driver_controls_v4.py',
              R/'tools/audit/rogue_dawn_audio_owner_v1.py', R/'tools/audit/verify_native_relocation.py',
              R/'docs/qa/rogue-dawn-audio-source-closure-2026-10-28.json',
              R/'docs/qa/rogue-dawn-ui890-authentic-audio-integration-plan-2026-10-29.json']
    proof = dict(passed=True, source_CPU_only=True, native_run=False,
        preparation_negative=dict(old_tool_sha256='c91dcc0f23522141814e4f5923df357713d8dfcce b6d1ac82f17e8bfa1306bf8'.replace(' ', ''),
          fixture='Initial7805=2 entered the unrelated real palette transaction on its second NMI.',
          actual_failure='Existing original.Memory mapper assertion selected in[6,7] rejected a CHR-bank write; no model or product change.',
          correction='Initial7805=0 takes the genuine DEC0→FF countdown branch and stays outside that unrelated palette transaction for these bounded NMIs. Old helper behavior is not relabeled an audio or ROM failure.'),
        actual_compiled_phase0_cases=rows, real_original_NMI_OR_cuts=cuts,
        real_original_NMI_direct_STA_cuts=direct, rejected_transport_rules=negatives,
        findings=[
          'Normal phase0 returning through B3D8..B3E7 clears every source queue; pause mode5 bypasses all six. Initbit0 takes priority even in mode5 and clears all six.',
          'Genuine hardware-vector NMI between CBE8 ORA0680,X and CBEB STA0680,X can restore already-consumed prior bits after NMI. The measured original final queue is12, not10; do not silently repair that source-visible interleaving.',
          'The prior busy/stable proposal avoids stale-P replay only conditionally: cached mode cannot become normal until stable assignment, prior normal returnedQ is0, prior pause retainedQ is not consumed, and initbit0 cannot remain retained. This adds unnecessary proof/implementation surface for cues.',
          'Prefer live source cue image: every nonreentrant NMI copies live P→privateQ, runs genuine source phase0, writes resulting Q→P before Main resumes. Pause retains image; normal/init clears it. No cue busy flag, event ring, queue OR merge or unconditional mailbox clear.',
          'Keep completed-Main RNG count and genuine multi-byte lifecycle/theme commitment separate. Four authentic one-byte weapon selectors are independently atomic; live NMI-time reads reproduce original cuts more closely than withholding cues behind a stale selector cache. Any committed-context adaptation must state its changed first-effect timing.',
          'This does not implement a host transport. Existing source/ROM/driver/model files remain unchanged; only this tool and report are owned.'],
        scope='Finite logicalarea0 initialized scalar context, authentic source normal/pause/init paths, existing actual c159 assembled driver and genuine full original CAB7 vector. Source1A=1 explicitly selects its real busy display-skip path; no PPU timing or native listening claim.',
        limitations=['No full source transition pass; original area3phase1 failure remains excluded/open.',
          'No whole hostNMI, original room itinerary, native timing, lowHP storage, mixer or atomic-lifecycle qualification.',
          'P comparison ignores only nonphysical6502 B/U representations, matching existing source controls; actual C/V/D/I/Z/N, AXY/SP and true restored bank pair are asserted.',
          'Mixed queue2A5 is explicitly an unread-byte canary for six-byte clear/retention, not a genuine acquired gameplay cue.'],
        bindings=[ref.binding(p) for p in inputs])
    OUT.write_text(json.dumps(proof, indent=2)+'\n')
    assert all(ref.binding(q['path']) == q for q in proof['bindings'])
    print(json.dumps(dict(proof=ref.binding(OUT), compiled_cases=len(rows), original_OR_cuts=len(cuts), original_STA_cuts=len(direct))))


if __name__ == '__main__':
    main()
