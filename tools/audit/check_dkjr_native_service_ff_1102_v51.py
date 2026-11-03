"""Independent actual FF lag-NMI/IRQ cuts in earned native DK Jr services.

Private historical-v65 owner model, explicit legal fruit/Goomba fixture.
No ROM or shared mutation. Earlier v49 used regular NMI; this is distinct.
"""
import argparse, collections, json, re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R, O, W = A.R, A.O, A.W
AUDIO = (0x7d8, 0x7da, 0x7db)


def fixture():
    path = R/'tools/audit/check_dkjr_native_lifecycle_1102_v31.py'
    text = path.read_text().replace('native-lifecycle-v30', 'native-registers-v48').replace('native-lifecycle-', 'native-registers-').replace('-v30.bin', '-v48.bin')
    env = {'__name__': 'dk_ff_service_fixture', '__file__': str(path)}
    exec(compile(text, str(path), 'exec'), env)
    b, m, L, q = env['fixture']()
    N.put(m, Player_X_Position=48)
    env['direct'](m, L['DkConstruct'])
    N.put(m, CurrentPlayer=0, AreaParserTaskNum=7, GameTimerCtrlTimer=24,
          GameTimerExpiredFlag=0, DisableIntermediate=1, PlayerSize=1,
          Player_BoundBoxCtrl=1, PlayerFacingDir=1, NmiDisable=255)
    for name in ['Block_Buffer_1', 'Block_Buffer_2']:
        for row in [11, 12]:
            m[W.address(b, name)+row*16:W.address(b, name)+row*16+16] = [0x54]*16
    for i, v in enumerate([4, 0, 0]):
        m[W.address(b, 'GameTimerDisplay')+i] = v
    for i, v in enumerate([60, 0, 191, 0]):
        m[W.address(b, 'R0')+i] = v
    c = N.NesMPU(memory=m, pc=L['DkjrNativeFruitSet'])
    c.sp, c.x = 224, 0
    c.stPushWord(0x5ffe)
    for _ in range(10000):
        if c.pc == 0x5fff:
            break
        c.step()
    else:
        raise AssertionError('world-fruit constructor bound')
    for slot, x in [(0, 60), (5, 180)]:
        for name, value in [('Enemy_Flag', 1), ('Enemy_ID', 6), ('Enemy_State', 0),
                            ('Enemy_X_Position', x), ('Enemy_PageLoc', 0),
                            ('Enemy_Y_Position', 184), ('Enemy_Y_HighPos', 1)]:
            m[W.address(b, name)+slot] = value
        N.put(m, ObjectOffset=slot)
        N.invoke(m, 'InitGoomba', x=slot)
    return b, m, L, q


def timers(m):
    q = json.loads((O/'native-pause-v16-CPU.json').read_text())['actual_timer_block']
    lo, hi = q['PC_half_open']
    maps = m.rawtags[:]
    m.raw_page((lo-0x8000)//8192, q['physical_PRG'] | 128)
    c = N.NesMPU(memory=m, pc=lo)
    for _ in range(1000):
        if c.pc == hi:
            break
        c.step()
    else:
        raise AssertionError('real timer block bound')
    for i, tag in enumerate(maps):
        m.raw_page(i, tag)


def state(m):
    native = bytearray(m[0x200:0x800])
    for a in AUDIO:
        native[a-0x200] = 0
    return ([bytes(z) for z in m.ram], bytes(m[3:11]),
            bytes(m[0x15a:0x17b]), bytes(native))


def branches(m):
    code = bytes(m[0xe000:0x10000])
    hits = [i for i in range(len(code)-8)
            if code[i:i+4] == bytes.fromhex('ad390110')
            and code[i+5:i+8] == bytes.fromhex('ee3a01')]
    assert len(hits) == 1, hits
    i = hits[0]
    d = code[i+4] - (256 if code[i+4] & 128 else 0)
    return 0xe000+i+5, 0xe000+i+5+d


def audio_sites(b):
    sites = {}
    rows = [('Fthrow', 2, '8dd807'), ('DecrementSfx1Length', 0, 'ced807'),
            ('GrowItemRegs', 0, '8dda07'), ('GrowItemRegs', 10, '8ddb07'),
            ('ContinueGrowItems', 0, 'eedb07')]
    for prefix in ['GuestSharedSfx::', 'SoundEngine::']:
        for suffix, delta, code in rows:
            name = prefix+suffix
            at, pc = W.location(b, name)+delta, W.address(b, name)+delta
            assert b['raw'][at:at+3] == bytes.fromhex(code), (name, delta)
            sites[(((at-16)//8192) | 128, pc)] = (name, delta, code)
    return sites


def run(m, L, interrupt=None, nested=None):
    b = m.bundle
    target = W.address(b, 'GameCoreRoutine')
    m[W.address(b, 'SafecallA_SMC')+1] = 85
    m[W.address(b, 'FarcallJmpTarget_SMC')+1] = target & 255
    m[W.address(b, 'FarcallJmpTarget_SMC')+2] = target >> 8
    c = N.NesMPU(memory=m, pc=W.address(b, 'FarCallCommon'))
    c.a, c.x, c.y, c.p, c.sp = 254, 0, 0, 0x31, 224
    c.stPushWord(0x5aff)
    cuts, active, low, injected = {}, [], c.sp, False
    calls, writers, transitions = collections.Counter(), collections.Counter(), collections.Counter()
    sites, lag, regular = audio_sites(b), *branches(m)
    service_names = ['DkjrNativeAwardSourcePoints', 'DkjrNativeFruitCollision']
    entries = {L[name]: name for name in service_names}
    nested_shapes = {}
    for _ in range(100000):
        if c.pc == 0x5b00:
            break
        low = min(low, c.sp)
        bank = m.rawtags[(c.pc-0x8000)//8192] if c.pc >= 0x8000 else -1
        if active and (c.pc, c.sp) == active[-1][:2]:
            active.pop()
        if bank == 3 and c.pc in entries:
            calls[entries[c.pc]] += 1
            active.append((m[0x101+c.sp]+256*m[0x102+c.sp]+1, c.sp+2, entries[c.pc]))
        here = (c.pc, c.sp, m.rawtags[1], m.rawtags[2])
        if active and not c.p & 4:
            key = (c.pc, m.rawtags[1], m.rawtags[2])
            if key not in cuts or c.sp < cuts[key][1]:
                cuts[key] = here
        if interrupt and not injected and here == interrupt[1]:
            injected = True
            regs = (c.a, c.x, c.y, c.p, c.sp, c.pc)
            before, maps = state(m), m.rawtags[:]
            skipped, audio_before = N.get(m, 'NmiSkipped'), tuple(m[a] for a in AUDIO)
            lh = rh = 0
            assert not c.p & 4 and N.get(m, 'NmiDisable') == 255
            c.irq() if interrupt[0] == 'IRQ' else c.nmi()
            for __ in range(200000):
                low = min(low, c.sp)
                if (c.pc, c.sp) == (regs[5], regs[4]):
                    break
                lh += int(c.pc == lag)
                rh += int(c.pc == regular)
                assert m[c.pc] != 0, ('ISR BRK', interrupt, hex(c.pc), c.sp)
                ins = bytes(m[c.pc:c.pc+3])
                if ins in [bytes.fromhex(z[2]) for z in sites.values()]:
                    tag = m.rawtags[(c.pc-0x8000)//8192]
                    assert (tag, c.pc) in sites, ('unbound audio writer', tag, hex(c.pc), ins.hex())
                    writers[f'{tag:02x}:{c.pc:04x}:'+sites[tag, c.pc][0]] += 1
                # Record all real unmasked audio-in-NMI positions for a
                # distinct nested-IRQ successor. No nested injection here.
                if interrupt[0] == 'lagNMI' and not c.p & 4:
                    k = (c.pc, m.rawtags[1], m.rawtags[2])
                    z = (c.pc, c.sp, m.rawtags[1], m.rawtags[2])
                    if k not in nested_shapes or c.sp < nested_shapes[k][1]:
                        nested_shapes[k] = z
                c.step()
            else:
                raise AssertionError(('ISR bound', interrupt))
            assert regs[:3] == (c.a, c.x, c.y) and regs[3] & 0xef == c.p & 0xef and regs[4:] == (c.sp, c.pc), ('ISR registers', interrupt, low)
            after = state(m)
            if before != after:
                raise AssertionError(('ISR state', interrupt, low,
                    dict(private=[(k, i, a, z) for k, (aa, zz) in enumerate(zip(before[0], after[0])) for i, (a, z) in enumerate(zip(aa, zz)) if a != z][:8],
                         scratch=[list(before[1]), list(after[1])], SMC=[list(before[2]), list(after[2])],
                         native=[(hex(i+0x200), a, z) for i, (a, z) in enumerate(zip(before[3], after[3])) if a != z][:12])))
            audio_after = tuple(m[a] for a in AUDIO)
            if interrupt[0] == 'IRQ':
                assert lh == rh == 0 and audio_after == audio_before
            else:
                assert lh == 1 and rh == 0 and N.get(m, 'NmiSkipped') == (skipped+1) & 255
                transitions[str(audio_before)+'->'+str(audio_after)] += 1
            if maps != m.rawtags:
                ins = bytes(m[c.pc:c.pc+3])
                assert ins in [bytes.fromhex(x) for x in ['8d1551', '8d1651', '8e1651']], ('ISR maps', interrupt, maps, m.rawtags)
                window = 1 if ins[1] == 0x15 else 2
                assert m.rawtags[window] == N.get(m, 'CurrentBank' if window == 1 else 'CurrentBankC')
                assert all(maps[k] == m.rawtags[k] for k in range(4) if k != window)
        assert m[c.pc] != 0, ('foreground BRK', hex(c.pc), c.sp, m.rawtags)
        c.step()
    else:
        raise AssertionError(('foreground bound', hex(c.pc)))
    assert c.sp == 224 and (interrupt is None or injected) and not active
    return dict(regs=[c.a, c.x, c.y, c.p, c.sp], minimum_SP=low,
                cuts=sorted(cuts.values()), calls=dict(calls), audio_writers=dict(writers),
                audio_transitions=dict(transitions), nested_shapes=sorted(nested_shapes.values()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--deepest-only', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()
    b, m, L, q = fixture()
    epochs, shapes, minimum, results = {}, {}, 255, collections.Counter()
    writers, transitions = collections.Counter(), collections.Counter()
    for epoch in range(1, 63):
        N.put(m, FrameCounter=epoch, SavedJoypadBits=0, SavedJoypad1Bits=0, VRAM_Buffer1_Offset=0, NmiDisable=255)
        timers(m)
        seed = N.fork(m)
        out = run(m, L)
        if out['cuts']:
            epochs[epoch] = (seed, out, state(m))
            for cut in out['cuts']:
                key = (cut[0], cut[2], cut[3])
                if key not in shapes or cut[1] < shapes[key][1][1]:
                    shapes[key] = (epoch, cut)
    assert N.get(m, 'NumberofLives') == 2 and not m.ram[2][0x68] and not m.ram[2][0x440]
    cuts = sorted(shapes.values(), key=lambda z: (z[1][1], z[0], z[1][0]))
    selected = cuts[:1] if args.deepest_only else cuts[:args.limit] if args.limit else cuts
    completed = []
    print('DK FF service cuts', len(cuts), 'epochs', sorted(epochs), 'selected', len(selected), flush=True)
    try:
        for kind in ['IRQ', 'lagNMI']:
            for index, (epoch, cut) in enumerate(selected):
                seed, ref, expected = epochs[epoch]
                z = N.fork(seed)
                out = run(z, L, (kind, cut))
                minimum = min(minimum, out['minimum_SP'])
                assert out['regs'] == ref['regs'] and state(z) == expected, ('resumed foreground', kind, epoch, cut)
                results[kind] += 1
                writers.update(out['audio_writers'])
                transitions.update(out['audio_transitions'])
                if index and index % 200 == 0:
                    print('DK FF service progress', kind, index, flush=True)
            completed.append(kind)
    except AssertionError as error:
        negative = dict(passed=False, ROM_written=False, native_owner_admitted=False, genuine_NmiDisable=255,
            epoch=epoch, interrupt=kind, cut=cut, error=repr(error), completed=completed,
            actual_interrupts=dict(results), minimum_SP=minimum, body_SHA256=A.sha((O/'native-registers-v48.bin').read_bytes()))
        (O/'native-service-v51-FF-negative.json').write_text(json.dumps(negative, indent=2)+'\n')
        raise
    report = dict(passed=True, qualified=False, ROM_written=False, native_owner_admitted=False,
        historical_v65_matching_header_fixture=True, genuine_NmiDisable=255,
        distinct_service_PC_A_C_pairs=len(cuts), independently_tested_per_kind=len(selected), actual_interrupts=dict(results),
        minimum_ISR_SP=minimum, source_bound_audio_writers=dict(writers), audio_transitions=dict(transitions),
        deepest_only=args.deepest_only, sample_limited=bool(args.limit),
        scope='Independent fresh-epoch replay at each selected PC/A/C-map pair, using its deepest reached SP. Actual native IRQ and genuine FF lag NMI; every lag reaches INC NmiSkipped once and never regular NMI. Complete private arrays, R0..7,33liveSMC bytes,native0200..07FF except three exact source-owned SFX clocks and resumed foreground match. This is a historical matching-header fixture, not latest owner authentication/native admission. Nested IRQ-in-lag/audio, packet reader/writer/lifetime closure and17unfinishedAPIs remain pending.',
        bindings={p.relative_to(R).as_posix(): A.sha(p.read_bytes()) for p in [Path(__file__), R/'tools/audit/check_dkjr_native_lifecycle_1102_v31.py', O/'native-registers-v48.bin', O/'native-registers-v48.s', R/'src/reset.s', R/'src/music_drivers/vanilla_sfx.s']})
    (O/'native-service-v51-FF.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['passed', 'distinct_service_PC_A_C_pairs', 'actual_interrupts', 'minimum_ISR_SP', 'deepest_only']}))


if __name__ == '__main__':
    main()
