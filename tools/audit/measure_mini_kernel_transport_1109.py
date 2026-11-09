"""Coalesce exact Mini collision reads within one native metatile."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from compose_mini_frame_budget_1108 import check_full_cpu
from prepare_selected_native_packet_v1 import R, sha


BASE = R/'build/mini-parser-lift-1109/candidate.nes'
PIN = 'a08d839b187fc6866a3fd3658200c2f26b8e3724b3b4de3b5e7d2a65702598d2'
SOURCE = R/'build/mini-fireball-gbc-1108/mini-lift.s'
CODE = 1048592+962*1024
COOKIE = 16+65*8192+0x1003


def replace_one(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new)


def transform(source):
    # The current native transport identifies X by its16-pixel column and Y
    # by its16-pixel row. Reuse only the immediately preceding *miss* when
    # advancing from the first half to the second half of that same cell.
    for axis, coordinate, finish in [('x', 'Y', 'beq'), ('y', 'X', 'jeq')]:
        label = '@'+axis
        scan = 'MiniScan'+coordinate
        source = replace_one(source, f'''    bne {label}hit
    lda {scan}+1''', f'''    bne {label}hit
{label}miss:
    lda {scan}+1''')
        source = replace_one(source, f'''    {finish} {label}finished
{label}next:
    clc
    lda {scan}
    adc #8
    sta {scan}
    bcc {label}loop
    inc {scan}+1
    jmp {label}loop''', f'''    {finish} {label}finished
{label}next:
    clc
    lda {scan}
    adc #8
    sta {scan}
    bcc :+
    inc {scan}+1
    jmp {label}loop
:
    and #8
    bne {label}miss
    beq {label}loop''')

    # Factor identical coordinate loading. The converter retains A and
    # returns X=0 after consuming the index. The wrappers all return Y intact.
    source = replace_one(source, '''MiniTempPixel:
    lda MiniTemp
    sta MiniCoord
    lda MiniTemp+1
    sta MiniCoord+1
    jmp MiniToPixel
''', '')
    source = replace_one(source, '''MiniHostPixelX:
 lda MiniX
 sta MiniCoord
 lda MiniX+1
 sta MiniCoord+1
 jmp MiniToPixel
MiniHostPixelY:
 lda MiniY
 sta MiniCoord
 lda MiniY+1
 sta MiniCoord+1
 jmp MiniToPixel''', '''MiniTempPixel:
 ldx #<MiniTemp
 bne MiniPixelAtX
MiniHostPixelX:
 ldx #<MiniX
 bne MiniPixelAtX
MiniHostPixelY:
 ldx #<MiniY
MiniPixelAtX:
 lda $c200,x
 sta MiniCoord
 lda $c201,x
 sta MiniCoord+1
 jmp MiniToPixel''')
    # A is dead at the three callers. Preserve carry, X=0, Y and N/Z.
    return replace_one(source, '''MiniHostToSubpixel:
 ldx #4
@shift:
 asl MiniCoord
 rol MiniCoord+1
 dex
 bne @shift
 rts''', '''MiniHostToSubpixel:
 ldx #2
 lda MiniCoord
@shift:
 asl a
 rol MiniCoord+1
 asl a
 rol MiniCoord+1
 dex
 bne @shift
 sta MiniCoord
 rts''')


def compile_source(output, source, config):
    compiler = R/'tools/Windows/cc65/bin'
    asm, obj, binary, labels = (output/f'kernel.{ext}' for ext in ('s','o','bin','lbl'))
    asm.write_text(source, encoding='utf-8', newline='\n')
    for command in ([compiler/'ca65.exe',asm,'-o',obj],
                    [compiler/'ld65.exe','-C',config,obj,'-o',binary,'-Ln',labels]):
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    obj.unlink()
    entries = {name:int(pc,16) for pc,name in
               re.findall(r'^al ([0-9A-Fa-f]+) \.(\w+)$', labels.read_text(), re.M)}
    return binary.read_bytes(), entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert sha(BASE) == PIN
    raw = BASE.read_bytes()
    original = SOURCE.with_suffix('.bin').read_bytes()
    assert raw[CODE:CODE+len(original)] == original and len(original) == 5119
    assert raw[CODE+len(original)] == 255
    assert raw[COOKIE:COOKIE+3] == bytes([167,41,1])
    assert raw[COOKIE+3:COOKIE+16] == hashlib.sha256(raw[CODE:CODE+7168]).digest()[:13]
    args.output.mkdir(exist_ok=True)
    successor, labels = compile_source(args.output,transform(SOURCE.read_text()),SOURCE.with_suffix('.cfg'))
    assert len(successor) <= 5120 and labels['MiniVectors'] == 0xa000
    candidate = bytearray(raw)
    candidate[CODE:CODE+5120] = successor.ljust(5120,b'\xff')
    candidate[COOKIE+3:COOKIE+16] = hashlib.sha256(candidate[CODE:CODE+7168]).digest()[:13]
    rows = check_full_cpu(raw,candidate,{2:[(0x1fe3,0x1ff0)],3:[(0,5120),(0x1fe3,0x1ff0)]})
    patches = [dict(offset=offset, preimage=raw[offset:offset+size].hex(),
                    replacement=candidate[offset:offset+size].hex())
               for offset,size in [(CODE,5120),(COOKIE+3,13)]]
    refs = [Path(__file__),BASE,SOURCE,SOURCE.with_suffix('.bin'),SOURCE.with_suffix('.cfg'),
            R/'src/reset.s',args.output/'kernel.s',args.output/'kernel.bin',args.output/'kernel.lbl']
    proof = dict(passed=True,parent_SHA256=PIN,kernel_size=[len(original),len(successor)],
        expected_memory_only_SHA256=hashlib.sha256(candidate).hexdigest(),whole_GameCore=rows,
        patches=patches,ROM_written=False,Mesen_run=False,bindings={str(p.resolve()):sha(p) for p in refs})
    (args.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k not in ('patches','bindings')}))


if __name__ == '__main__':
    main()
