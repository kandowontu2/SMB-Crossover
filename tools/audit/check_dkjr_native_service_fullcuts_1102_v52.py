"""All I0/I1 FF NMI service cuts; I0 IRQ cuts and bound smack audio.

Extends retained v51's deliberately finite audio oracle without changing it.
"""
import argparse, collections, inspect, json
from pathlib import Path
import check_dkjr_native_service_ff_1102_v51 as C
A, R, O, W, N = C.A, C.R, C.O, C.W, C.N
fixture, timers, state, branches, AUDIO = C.fixture, C.timers, C.state, C.branches, C.AUDIO


def audio_sites(b):
    sites = C.audio_sites(b)
    for prefix in ['GuestSharedSfx::', 'SoundEngine::']:
        name, delta, code = prefix+'PlaySmackEnemy', 6, '8dd807'
        at, pc = W.location(b, name)+delta, W.address(b, name)+delta
        assert b['raw'][at:at+3] == bytes.fromhex(code)
        # The exact original source sequence binds this additional writer,
        # rather than permitting arbitrary stores to the sound clock.
        assert b['raw'][at-6:at] == bytes.fromhex('a90ea0cba29f')
        sites[(((at-16)//8192) | 128, pc)] = (name, delta, code)
    return sites


text = inspect.getsource(C.run)
text = text.replace('here = (c.pc, c.sp, m.rawtags[1], m.rawtags[2])',
                    'here = (c.pc, c.sp, m.rawtags[1], m.rawtags[2], c.p & 4)')
text = text.replace('if active and not c.p & 4:', 'if active:')
text = text.replace('key = (c.pc, m.rawtags[1], m.rawtags[2])',
                    'key = (c.pc, m.rawtags[1], m.rawtags[2], c.p & 4)')
text = text.replace("assert not c.p & 4 and N.get(m, 'NmiDisable') == 255",
                    "assert (interrupt[0] != 'IRQ' or not c.p & 4) and N.get(m, 'NmiDisable') == 255")
exec(compile(text, str(Path(__file__)), 'exec'), globals())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--deepest-only', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()
    b, m, L, q = fixture()
    epochs, shapes = {}, {}
    for epoch in range(1, 63):
        N.put(m, FrameCounter=epoch, SavedJoypadBits=0, SavedJoypad1Bits=0,
              VRAM_Buffer1_Offset=0, NmiDisable=255)
        timers(m)
        seed = N.fork(m)
        out = run(m, L)
        if out['cuts']:
            epochs[epoch] = (seed, out, state(m))
            for cut in out['cuts']:
                key = (cut[0], cut[2], cut[3], cut[4])
                if key not in shapes or cut[1] < shapes[key][1][1]:
                    shapes[key] = (epoch, cut)
    assert N.get(m, 'NumberofLives') == 2 and not m.ram[2][0x68] and not m.ram[2][0x440]
    cuts = sorted(shapes.values(), key=lambda z: (z[1][1], z[0], z[1][0]))
    results, writers, transitions = collections.Counter(), collections.Counter(), collections.Counter()
    minimum, completed = 255, []
    print('DK FF full service cuts', len(cuts), 'I1', sum(bool(z[1][4]) for z in cuts), flush=True)
    try:
        for kind in ['IRQ', 'lagNMI']:
            available = [z for z in cuts if kind != 'IRQ' or not z[1][4]]
            selected = available[:1] if args.deepest_only else available[:args.limit] if args.limit else available
            for index, (epoch, cut) in enumerate(selected):
                seed, ref, expected = epochs[epoch]
                z = N.fork(seed)
                out = run(z, L, (kind, cut))
                minimum = min(minimum, out['minimum_SP'])
                assert out['regs'] == ref['regs'] and state(z) == expected, ('resumed foreground', kind, epoch, cut)
                results[kind] += 1
                results[kind+'-I1' if cut[4] else kind+'-I0'] += 1
                writers.update(out['audio_writers'])
                transitions.update(out['audio_transitions'])
                if index and index % 200 == 0:
                    print('DK FF full service progress', kind, index, flush=True)
            completed.append(kind)
    except AssertionError as error:
        report = dict(passed=False, ROM_written=False, native_owner_admitted=False,
            genuine_NmiDisable=255, epoch=epoch, interrupt=kind, cut=cut,
            error=repr(error), completed=completed, actual_interrupts=dict(results),
            minimum_SP=minimum, body_SHA256=A.sha((O/'native-registers-v48.bin').read_bytes()))
        (O/'native-service-v52-FF-negative.json').write_text(json.dumps(report, indent=2)+'\n')
        raise
    report = dict(passed=True, qualified=False, ROM_written=False, native_owner_admitted=False,
        historical_v65_matching_header_fixture=True, genuine_NmiDisable=255,
        distinct_service_PC_A_C_I_shapes=len(cuts), I0_shapes=sum(not z[1][4] for z in cuts), I1_shapes=sum(bool(z[1][4]) for z in cuts),
        actual_interrupts=dict(results), minimum_ISR_SP=minimum,
        source_bound_audio_writers=dict(writers), audio_transitions=dict(transitions),
        deepest_only=args.deepest_only, sample_limited=bool(args.limit),
        retained_oracle_negative='native-service-v51-FF-negative.json',
        scope='Independent fresh-epoch continuation at every selected PC/A-map/C-map/I pair using its deepest reached SP. IRQ only I0; hardware NMI at I0 and I1. Every FF lag NMI reaches INC NmiSkipped exactly once and never regular NMI. AXYP/SP/private arrays/R0..7/33liveSMC/native0200..07FF exact apart from three sound clocks with source-bound writers. No original abilities changed. Nested IRQ in lag/audio, full packet writer/lifetime and latest-owner rebind remain pending.',
        bindings={p.relative_to(R).as_posix(): A.sha(p.read_bytes()) for p in [Path(__file__), Path(C.__file__), O/'native-service-v51-FF-negative.json', O/'native-registers-v48.bin', O/'native-registers-v48.s', R/'src/reset.s', R/'src/music_drivers/vanilla_sfx.s']})
    (O/'native-service-v52-FF.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['passed', 'distinct_service_PC_A_C_I_shapes', 'I1_shapes', 'actual_interrupts', 'minimum_ISR_SP', 'deepest_only']}))


if __name__ == '__main__':
    main()
