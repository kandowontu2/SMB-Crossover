"""Qualify a bounded shaft, cap and exposed-roof chain at the original F801 call."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import qualify_prince_climb_typed_roof_1110_v2 as R2


M, P, R, N, I, E, V = R2.M, R2.P, R2.R, R2.N, R2.I, R2.E, R2.V
PREVIOUS = R / 'build/prince-tall-native-1110/prince-private.nes'
ROOF = R / 'build/prince-climb-descent-1110/two-row-proof.json'
CAPTURE = R / 'build/prince-full11-native-1110-v3/capture/full11.json'
OLD_GEOMETRY = R / 'build/prince-actor-1101-v1/host-world-compiled-v8.json'
LEVEL = R / 'src/level_tiles.s'


def source():
    edge, descent = R2.source().split('.segment "CLIMB_DESCENT"', maxsplit=1)
    edge = R2.once(edge, ' lda Facing\n beq Left', ' ldx ActorX+1\n lda Facing\n beq Left')
    edge = edge.replace(' lda ActorX\n ldx ActorX+1', ' lda ActorX')
    edge = R2.once(edge, ' clc\n adc #15', ' adc #14                       ; CPY #24 supplies carry.')
    edge = R2.once(edge, ' jmp CommitPage', ' bcs CommitPage                ; Valid right edge is at least 16.')
    edge = R2.once(edge, ''' ; A native pipe cap can be one row above the first solid hand cell.
 ; Extend only across that typed cap and require actual air above it.
 and #$fc
 cmp #$10
 bne Fallback
 lda QueryY
 sbc #16                        ; Equal CMP above already set carry.
 sta QueryY
 jsr ReadPoint
 bcs Fallback''', ''' ; Accept one shaft row only when the next row is a native cap.
 ; Neither a plain wall nor two shaft rows can extend the search.
 and #$fe
 cmp #$14
 bne Cap
 jsr UpRoof
Cap:
 and #$fc
 cmp #$10
 bne Fallback
 jsr UpRoof
 bcs Fallback''')
    edge += '''\nUpRoof:
 lda QueryY
 sbc #16                        ; Exact typed comparison supplies carry.
 sta QueryY
 jmp ReadPoint
'''
    descent = R2.once(descent, ''' cmp #3
 beq Falling
 cmp #4
 bne Original
Falling:''', ''' sec
 sbc #3
 cmp #2
 bcs Original''')
    descent = R2.once(descent, ''' cmp #240
 bcs Original
 adc #15
 and #$f0''', ''' adc #14                         ; CMP #32 left carry set.
 bcs Original                    ; OldFoot+15 cannot wrap the screen.
 and #$f0''')
    descent = R2.once(descent, ''' inc QueryY
 bcs Original
 lda QueryY
 sbc #31                         ; Empty point left carry clear.
 sta NativeY
 bcs Original
NextRow:
 lda QueryY
 clc
 adc #16
 sta QueryY
 cmp Foot
 bcc Probe
Original:''', ''' bcs Original
 lda QueryY                      ; The empty roof was sampled at top-1.
 sbc #30                         ; Empty point left carry clear.
 sta NativeY
Original:''')
    descent = R2.once(descent, '.endscope', '''NextRow:
 lda QueryY
 adc #16                         ; The empty column left carry clear.
 sta QueryY
 cmp Foot
 bcc Probe
 bcs Original
.endscope''')
    return edge + '.segment "CLIMB_DESCENT"' + descent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    old, route, world = (json.loads(path.read_text()) for path in (ROOF, CAPTURE, OLD_GEOMETRY))
    current = PREVIOUS.read_bytes()
    assert P.sha(current) == old['expected_memory_only_SHA256'] == route['ROM_sha256']
    assert not route['passed'] and route['HP'] == 5 and route['route']['index'] == 2
    second, = route['route']['clears']
    assert second['left'] == 608 and second['observed_support']['native_y'] == 128
    hang = route['route']['hang']
    assert (hang['world_x'], hang['physical_foot'], hang['source_mode']) == (713, 203, 2)
    close, = [r for r in route['route']['events'] if r['tag'] == 'pipe-cross' and r['index'] == 2]
    assert (close['world_x'], close['physical_foot'], close['source_action']) == (698, 145, 10)
    old_64, = [r for r in world['results'] if r['pipe_height'] == 64]
    assert old_64['cleared_and_landed'] and old_64['minFoot'] == 145
    assert '.byte $13, $12 ;used by decoration pipes\n      .byte $15, $14' in LEVEL.read_text()

    template = M.image()
    base = dict(template, raw=R2.PARENT.read_bytes())
    assert P.sha(base['raw']) == R2.PARENT_SHA
    previous, _ = P.Q.C.C.cold(dict(template, raw=current), 38)
    seed, _ = P.Q.C.C.cold(base, 38)
    assembly = source()
    with patch.object(R2, 'source', return_value=assembly):
        raw, patches, chunks, cookie, layout, workers = R2.compose(args.output, base, seed,
                                                                  json.loads(R2.OLD.read_text()))
    new, cold = P.Q.C.C.cold(dict(template, raw=raw), 38)
    assert bytes(new.ram[3][:len(chunks[0])]) == P.live(chunks[0])
    assert bytes(new.ram[2][0x800:0x800+len(chunks[1])]) == chunks[1]
    assert all(bytes(new.ram[k][0x1fe0:0x1ff0]) == cookie for k in (2, 3))
    for row in (15, 36):
        warm = N.fork(new)
        assert I.invoke(warm, 193, 0xb08c+3*row)['regs'][3] & 1
        start = layout['edge_half_open'][0] - 0xc000
        assert bytes(warm.ram[2][start:start+len(workers)]) == workers

    outcomes = []
    for top, foot, replacement, roof in ((176,203,None,False),(160,203,None,False),
            (144,193,None,False),(144,203,None,False),(144,203,0x54,False),
            (144,203,0,False),(144,203,None,True),(128,203,None,False)):
        for facing, edge in ((255,736),(0,768)):
            before, after = (R2.prepare(m, edge, top, foot, facing, roof) for m in (previous, new))
            interior = edge if facing else edge - 1
            for m in (before, after):
                if replacement is not None:
                    m[E.block(interior, top)] = replacement
            assert R2.align(before) == R2.align(after)
            a, b = (E.word(m, 0xc60f) for m in (before, after))
            intended = (top, foot, replacement, roof) == (144, 203, None, False)
            assert b == (edge+(-8 if facing else 8) if intended else a), (top, foot, facing, a, b)
            assert bytes(before.ram[2][:0x60f]) == bytes(after.ram[2][:0x60f])
            assert bytes(before.ram[2][0x611:0x800]) == bytes(after.ram[2][0x611:0x800])
            outcomes.append(dict(top=top, foot=foot, facing=facing, cap_replacement=replacement,
                                 roof_blocked=roof, source_x=[a,b]))
    original, _ = P.Q.C.C.cold(template, 38)
    V.exercise(original, new)
    irq = V.Async.stress('actual typed shaft, cap and exposed roof',
        R2.prepare(new,736,144,203,255,False), R2.align,
        [(2,*layout['edge_half_open']),(3,0xb310,0xb369)])
    worker_path = args.output / 'tall-shaft-workers.bin'
    worker_path.write_bytes(workers)
    refs = [Path(__file__), Path(R2.__file__), ROOF, CAPTURE, OLD_GEOMETRY, LEVEL,
            PREVIOUS, worker_path, M.BASE, R2.OLD, R2.PARENT]
    receipt = dict(passed=True, parent_SHA256=M.BASE_PIN, previous_private_SHA256=P.sha(current),
        expected_memory_only_SHA256=P.sha(raw), Prince_cookie=cookie.hex(), patches=patches,
        layout=layout, actual_third_pipe=hang, original_standing_climb_minimum_foot=145,
        outcomes=outcomes, cold_CPU=cold['CPU'], warm_rows=[15,36], descent_cases_reverified=9,
        interrupt=irq, ROM_written=False, Mesen_run=False,
        bindings={str(f.resolve()):P.sha(f.read_bytes()) for f in refs})
    (args.output / 'shaft-proof.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('expected_memory_only_SHA256','layout','outcomes','interrupt')}))


if __name__ == '__main__':
    main()
