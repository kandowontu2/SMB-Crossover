"""Keep native column packets and avoid the second attribute pass on MMC5."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import measure_mini_parser_health_1108_v1 as M
from prepare_mini_mario_chr_override_1103_v39 import assemble


ROOT = M.R
BASE = ROOT / 'build/mini-parser-lift-1109/candidate.nes'
PIN = 'a08d839b187fc6866a3fd3658200c2f26b8e3724b3b4de3b5e7d2a65702598d2'
SOURCE = ROOT / 'src/screen_render.s'
NAMES = ('R0', 'R1', 'R3', 'R4', 'R5', 'CurrentColumnPos', 'VRAM_Buffer2_Offset',
         'VRAM_Buffer2', 'CurrentNTAddr_Low', 'CurrentNTAddr_High', 'MetatileBuffer',
         'AreaParserTaskNum', 'MTileTopLeft', 'MTileBotLeft', 'MTileTopRight', 'MTileBotRight',
         'MTileAttribute', 'AttributeBuffer', 'SetVRAMCtrl')


def replace(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new)


def transform(source, extent):
    source = replace(source, '  sta R4\n  tax\nDrawMTLoop:', '  tax\nDrawMTLoop:')
    source = replace(source, '@UpdateAttributes:', '''    ; Task 7/3 already ORed the attributes for this same column.
    ; Recompute its final scratch value on the last row only.
    lda R1
    cmp #12
    bne EndRow
@UpdateAttributes:''')
    source = replace(source, '  ldy R4\n  lda R5\n  bne RightCheck\n    lda R1\n    lsr\n    bcs LLeft',
                     '  lda R1\n  lsr\n  tay\n  lda R5\n  bne RightCheck\n    bcs LLeft')
    source = replace(source, '      jmp SetAttrib\nRightCheck:\n  lda R1\n  lsr\n  bcs NextMTRow',
                     '      bcc SetAttrib\nRightCheck:\n  bcs SetAttrib')
    source = replace(source, '    jmp SetAttrib\nLLeft:', '    bcc SetAttrib\nLLeft:')
    source = replace(source, 'NextMTRow:\n    inc R4\nSetAttrib:', 'SetAttrib:')
    source = replace(source, '  inc R0\n  inc R0', 'EndRow:\n  inc R0\n  inc R0')
    source = replace(source, '            ldy R0\n            iny', '            ldy #6\n            sty R4\n            ldy R0\n            iny')
    return source + f'\n.res {extent}-(*-RenderAreaGraphics),$ea\n'


def compile_patch(old, out):
    lo, hi = (M.address(old, n) for n in ('RenderAreaGraphics', 'RenderAttributeTables'))
    at = M.location(old, 'RenderAreaGraphics')
    extent = hi - lo
    full = SOURCE.read_text()
    full = full[full.index('\nRenderAreaGraphics:')+1:full.index('\nRenderAttributeTables:')]
    full = '\n'.join(line.split(';')[0].rstrip() for line in full.splitlines() if line.split(';')[0].strip()) + '\n'
    prefix = ''.join(f'{n}=${M.address(old,n):04x}\n' for n in NAMES) + '.segment "CODE"\n'
    stock, _ = assemble(out/'column-original', prefix+full, lo, extent)
    faster, _ = assemble(out/'column-successor', prefix+transform(full, extent), lo, extent)
    assert len(stock) == len(faster) == extent
    assert stock == old['raw'][at:at+extent]
    replacement = old['raw'][:at] + faster + old['raw'][at+extent:]
    return replacement, dict(physical_PRG=(at-16)//8192, CPU_half_open=[lo, hi], file_offset=at,
                             old_hex=stock.hex(), new_hex=faster.hex())


def state(m):
    vram = M.address(m.bundle,'VRAM_Buffer2')
    io = tuple((a,v) for a,v in m.writes if a >= 0x2000 or vram <= a < vram+0x40)
    return (bytes(m[:0x100]), bytes(m[0x200:0x800]), bytes(m[0x15a:0x17b]),
            tuple(map(bytes,m.ram)), tuple(m.rawtags), io)


def compare(original, successor):
    N = M.N
    savings = {'left': Counter(), 'right': Counter(), 'attributes': Counter()}
    for column, start, tiles, pair, flags in product(range(32), (0x80, 0x9e, 0x9f, 0xfe, 0xff), range(8), (7, 3), (0x21, 0xf1)):
        seed = []
        for image in (original, successor):
            m = N.Bus(image)
            m.raw_page(1, 131)
            N.put(m, CurrentBank=131, CurrentColumnPos=column, CurrentNTAddr_Low=start,
                  CurrentNTAddr_High=0x20+(column&4), VRAM_Buffer2_Offset=0)
            at = M.address(image, 'MetatileBuffer')
            m[at:at+13] = bytes((column*41+tiles*53+i*19)&255 for i in range(13))
            at = M.address(image, 'AttributeBuffer')
            m[at:at+7] = bytes((i*tiles*column+17)&255 for i in range(7))
            seed.append(m)
        for name, task, symbol in [('left',pair,'RenderAreaGraphics'), ('right',pair-1,'RenderAreaGraphics'),
                                   ('attributes',0,'RenderAttributeTables')]:
            outputs = []
            for m in seed:
                N.put(m, AreaParserTaskNum=task)
                m.writes.clear()
                info = N.invoke(m,symbol,a=23,x=67,y=91,p=flags)
                outputs.append((info,state(m)))
            a,b = outputs
            assert tuple(a[0][k] for k in ('A','X','Y','P')) == tuple(b[0][k] for k in ('A','X','Y','P'))
            assert a[1] == b[1], (column,start,tiles,pair,flags,name,
                [(i, [(j,x,y) for j,(x,y) in enumerate(zip(p,q)) if x!=y][:12],len(p),len(q))
                 for i,(p,q) in enumerate(zip(a[1],b[1])) if p!=q])
            savings[name][a[0]['CPU']-b[0]['CPU']] += 1
    return {name: dict(cases=sum(hist.values()), cycle_savings=hist) for name,hist in savings.items()}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    raw = BASE.read_bytes()
    assert M.sha(raw) == PIN
    old = M.bundle(raw)
    args.output.mkdir(exist_ok=True)
    candidate, patch = compile_patch(old,args.output)
    results = compare(old,M.bundle(candidate))
    assert min(results['right']['cycle_savings']) > 300
    assert min(results['left']['cycle_savings']) >= 0
    proof = dict(passed=True, base_SHA256=PIN, expected_memory_only_SHA256=M.sha(candidate),
                 patches=[patch], paired_cases=results,
                 scope='Paired native left/right terrain tasks and attribute publication. Same collision and VRAM stream.')
    (args.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(results),flush=True)


if __name__ == '__main__':
    main()
