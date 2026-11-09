"""Coalesce Mini's same-cell misses without adding a hot pixel-load wrapper."""

import argparse
import hashlib
import json
from pathlib import Path

import measure_mini_kernel_transport_1109 as V1


def region(text, start, end):
    return text[text.index(start):text.index(end)]


def transform(original):
    source = V1.transform(original)
    # Keep the three direct coordinate loads on their original hot paths.
    source = V1.replace_one(source,
        region(source,'MiniTempPixel:', 'MiniHostGraphics:'),
        region(original,'MiniHostPixelX:', 'MiniHostGraphics:'))
    old = region(original,'MiniTempPixel:', 'MiniSnap:')
    source = V1.replace_one(source,region(source,'MiniAddBound:', 'MiniSnap:'),old)

    # Seven alignment callers already issue two JSRs. Put the second inside
    # their helper so each call site loses three bytes with identical work.
    old = '    jsr MiniAddBound\n    jsr MiniAlign\n'
    assert source.count(old) == 2
    source = source.replace(old,'    jsr MiniAddBound\n')
    old = '    jsr MiniAddSigned\n    jsr MiniAlign\n'
    assert source.count(old) == 5
    source = source.replace(old,'    jsr MiniAddAligned\n')
    source = V1.replace_one(source,'''MiniAddBound:
    lda MiniBound
MiniAddSigned:''','''MiniAddBound:
    lda MiniBound
MiniAddAligned:
    jsr MiniAddSigned
    lda MiniCoord
    and #$F8
    sta MiniCoord
    rts
MiniAddSigned:''')
    source = V1.replace_one(source,'''MiniAlign:
    lda MiniCoord
    and #$F8
    sta MiniCoord
    rts
''','')
    # All pixel helpers are private and every caller next reloads A.
    source = V1.replace_one(source,region(original,'MiniToPixel:', 'MiniHeadEvent:'),'''MiniToPixel:
    lda MiniCoord+1
    .repeat 4
      lsr a
      ror MiniCoord
    .endrepeat
    sta MiniCoord+1
    ldx #0
    rts

''')
    return V1.replace_one(source,''' lda Player_X_Position
 sta MiniOldX
 lda Player_Y_Position
 sta MiniOldY
 lda Player_X_Position
 sec''',''' lda Player_Y_Position
 sta MiniOldY
 lda Player_X_Position
 sta MiniOldX
 sec''')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert V1.sha(V1.BASE) == V1.PIN
    raw = V1.BASE.read_bytes()
    old = V1.SOURCE.with_suffix('.bin').read_bytes()
    assert len(old) == 5119 and raw[V1.CODE:V1.CODE+5120] == old+b'\xff'
    assert raw[V1.COOKIE+3:V1.COOKIE+16] == hashlib.sha256(raw[V1.CODE:V1.CODE+7168]).digest()[:13]
    args.output.mkdir(exist_ok=True)
    new,labels = V1.compile_source(args.output,transform(V1.SOURCE.read_text()),V1.SOURCE.with_suffix('.cfg'))
    assert len(new) <= 5120 and labels['MiniVectors'] == 0xa000
    candidate = bytearray(raw)
    candidate[V1.CODE:V1.CODE+5120] = new.ljust(5120,b'\xff')
    candidate[V1.COOKIE+3:V1.COOKIE+16] = hashlib.sha256(candidate[V1.CODE:V1.CODE+7168]).digest()[:13]
    rows = V1.check_full_cpu(raw,candidate,{2:[(0x1fe3,0x1ff0)],3:[(0,5120),(0x1fe3,0x1ff0)]})
    patches = [dict(offset=offset,preimage=raw[offset:offset+size].hex(),
                    replacement=candidate[offset:offset+size].hex())
               for offset,size in [(V1.CODE,5120),(V1.COOKIE+3,13)]]
    refs = [Path(__file__),Path(V1.__file__),V1.BASE,V1.SOURCE,V1.SOURCE.with_suffix('.bin'),
            V1.SOURCE.with_suffix('.cfg'),V1.R/'src/reset.s',args.output/'kernel.s',
            args.output/'kernel.bin',args.output/'kernel.lbl']
    proof = dict(passed=True,parent_SHA256=V1.PIN,kernel_size=[len(old),len(new)],
        expected_memory_only_SHA256=hashlib.sha256(candidate).hexdigest(),whole_GameCore=rows,
        no_regression_in_fixtures=all(row['min_saved']>=0 for row in rows),
        patches=patches,ROM_written=False,Mesen_run=False,bindings={str(p.resolve()):V1.sha(p) for p in refs})
    (args.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k not in ('patches','bindings')}))


if __name__ == '__main__':
    main()
