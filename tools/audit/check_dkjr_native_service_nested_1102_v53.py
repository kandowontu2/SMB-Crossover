"""Actual native IRQ inside FF lag audio at deepest earned service contexts."""
import argparse, collections, json
from pathlib import Path
import check_dkjr_native_service_fullcuts_1102_v52 as P
A, R, O, W, N = P.A, P.R, P.O, P.W, P.N
fixture, timers, state, branches, audio_sites, AUDIO = P.fixture, P.timers, P.state, P.branches, P.audio_sites, P.AUDIO


text = P.text.replace('nested_shapes = {}', 'nested_shapes = {}; nested_injected = False')
marker = '                c.step()\n            else:\n                raise AssertionError((\'ISR bound\', interrupt))'
replacement = '''                if nested and not nested_injected and (c.pc, c.sp, m.rawtags[1], m.rawtags[2]) == nested:
                    nested_injected = True
                    assert interrupt[0] == 'lagNMI' and not c.p & 4
                    inner = (c.a, c.x, c.y, c.p, c.sp, c.pc)
                    inner_state, inner_maps = state(m), m.rawtags[:]
                    inner_audio = tuple(m[a] for a in AUDIO)
                    c.irq()
                    for ___ in range(200000):
                        low = min(low, c.sp)
                        if (c.pc, c.sp) == (inner[5], inner[4]):
                            break
                        assert m[c.pc] != 0, ('nested IRQ BRK', interrupt, nested, hex(c.pc), c.sp)
                        c.step()
                    else:
                        raise AssertionError(('nested IRQ bound', interrupt, nested))
                    assert inner[:3] == (c.a, c.x, c.y) and inner[3] & 0xef == c.p & 0xef and inner[4:] == (c.sp, c.pc), ('nested IRQ registers', interrupt, nested, low)
                    assert inner_state == state(m) and inner_audio == tuple(m[a] for a in AUDIO), ('nested IRQ state', interrupt, nested, low,
                        {'SMC_before':list(inner_state[2]), 'SMC_after':list(state(m)[2]),
                         'private_exact':inner_state[0] == state(m)[0], 'scratch_exact':inner_state[1] == state(m)[1], 'native_exact':inner_state[3] == state(m)[3]})
                    if inner_maps != m.rawtags:
                        op = bytes(m[c.pc:c.pc+3])
                        assert op in [bytes.fromhex(x) for x in ['8d1551', '8d1651', '8e1651']], ('nested IRQ map', interrupt, nested)
                        win = 1 if op[1] == 0x15 else 2
                        assert m.rawtags[win] == N.get(m, 'CurrentBank' if win == 1 else 'CurrentBankC')
                        assert all(inner_maps[k] == m.rawtags[k] for k in range(4) if k != win)
                c.step()
            else:
                raise AssertionError(('ISR bound', interrupt))'''
assert text.count(marker) == 1
text = text.replace(marker, replacement)
text = text.replace('assert c.sp == 224 and (interrupt is None or injected) and not active',
                    'assert c.sp == 224 and (interrupt is None or injected) and not active and (nested is None or nested_injected)')
exec(compile(text, str(Path(__file__)), 'exec'), globals())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all-cuts', action='store_true')
    args = ap.parse_args()
    b, m, L, q = fixture()
    cohorts = []
    for epoch in range(1, 63):
        N.put(m, FrameCounter=epoch, SavedJoypadBits=0, SavedJoypad1Bits=0,
              VRAM_Buffer1_Offset=0, NmiDisable=255)
        timers(m)
        seed = N.fork(m)
        out = run(m, L)
        if out['cuts']:
            cut = min(out['cuts'], key=lambda z: (z[1], z[0]))
            z = N.fork(seed)
            lag = run(z, L, ('lagNMI', cut))
            assert lag['regs'] == out['regs'] and state(z) == state(m)
            assert lag['nested_shapes']
            cohorts.append((epoch, seed, cut, lag, state(z)))
    results, minimum, rows = collections.Counter(), 255, []
    try:
        for epoch, seed, cut, lag, expected in cohorts:
            shapes = sorted(lag['nested_shapes'], key=lambda z: (z[1], z[0]))
            chosen = shapes if args.all_cuts else shapes[:1]
            print('DK nested service', epoch, 'audio shapes', len(shapes), 'selected', len(chosen), flush=True)
            for index, nested in enumerate(chosen):
                z = N.fork(seed)
                out = run(z, L, ('lagNMI', cut), nested=nested)
                minimum = min(minimum, out['minimum_SP'])
                assert out['regs'] == lag['regs'] and state(z) == expected, ('nested foreground continuation', epoch, cut, nested)
                results['actual_nested_IRQ'] += 1
                if index and index % 200 == 0:
                    print('DK nested service progress', epoch, index, flush=True)
            rows.append(dict(epoch=epoch, foreground_cut=cut, unmasked_native_audio_shapes=len(shapes), independent_nested_IRQ=len(chosen), audio_transitions=lag['audio_transitions']))
    except AssertionError as error:
        report = dict(passed=False, ROM_written=False, native_owner_admitted=False,
            genuine_NmiDisable=255, epoch=epoch, foreground_cut=cut, nested_cut=nested,
            error=repr(error), actual_interrupts=dict(results), minimum_SP=minimum,
            body_SHA256=A.sha((O/'native-registers-v48.bin').read_bytes()))
        (O/'native-service-v53-nested-negative.json').write_text(json.dumps(report, indent=2)+'\n')
        raise
    report = dict(passed=True, qualified=False, ROM_written=False, native_owner_admitted=False,
        historical_v65_matching_header_fixture=True, genuine_NmiDisable=255,
        actual_interrupts=dict(results), minimum_ISR_SP=minimum, cohorts=rows,
        all_nested_cuts=args.all_cuts,
        scope='Independent actual native IRQ inside unmasked real FF lag-NMI/audio at the deepest reached earned-service context in each active epoch. Full outer NMI and native Main continuation preserve private/R0..7/SMC/native state, apart from previously bound outer audio clocks. Every outer NMI asserts INC NmiSkipped once and excludes regular NMI. Historical private owner fixture only; source packet lifetime and final current rebind remain pending.',
        bindings={p.relative_to(R).as_posix(): A.sha(p.read_bytes()) for p in [Path(__file__), Path(P.__file__), Path(P.C.__file__), O/'native-registers-v48.bin', R/'src/reset.s', R/'src/music_drivers/vanilla_sfx.s']})
    (O/'native-service-v53-nested.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['passed', 'actual_interrupts', 'minimum_ISR_SP', 'all_nested_cuts']}))


if __name__ == '__main__':
    main()
