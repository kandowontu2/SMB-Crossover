"""Qualify shared MMC5 terrain palette packing with real interrupt vectors."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import measure_column_graphics_1109 as C
from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from check_mini_funded_actor_1108_v3 import live_stack, registers, run, slim_fork
from check_mini_visibility_dispatch_1110_v1 import memory
from measure_mini_audio_1108_v1 import seed
from prepare_mini_mario_native_smoke_1103_v25 import GLOBALS


M, R, N = C.M, C.ROOT, C.M.N
ROM = R/'build/mini-contact-lag-native-1110/candidate.nes'
PIN = 'd998e71bb6b6aacb7cd3f7f055cf74a791ba68de84347918c8ba27a2bf6fc300'
HISTORICAL = R/'build/mini-column-graphics-1109/proof.json'
START, END, TAG, STOP = 0xb989, 0xba3e, 131, 0x5b00

PALETTE = '''@UpdateAttributes:
  ; Hold row parity in C and the two-bit palette in A. Both tests retain C.
  lda R1
  lsr a
  tax
  lda MTileAttribute,y
  and #$c0
  beq NoPalette
  ldy R5
  bne RightCheck
  bcs LLeft
  rol a
  rol a
  rol a
  bcc SetAttrib
RightCheck:
  bcs SetAttrib
  lsr a
  lsr a
  lsr a
  lsr a
  bcc SetAttrib
LLeft:
  lsr a
  lsr a
SetAttrib:
  sta R3
  ora AttributeBuffer,x
  sta AttributeBuffer,x
  bne EndRow
NoPalette:
  ; Preserve the final scratch value and omit an idempotent attribute store.
  sta R3
'''


def compile_patch(image, output):
    lo, hi = (M.address(image, n) for n in ('RenderAreaGraphics', 'RenderAttributeTables'))
    at = M.location(image, 'RenderAreaGraphics')
    assert (lo, hi, at) == (START, END, 31129)
    historical = json.loads(HISTORICAL.read_text())['patches'][0]
    assert historical['file_offset'] == at and historical['CPU_half_open'] == [lo, hi]
    source = C.SOURCE.read_text()
    source = source[source.index('\nRenderAreaGraphics:')+1:source.index('\nRenderAttributeTables:')]
    lines = (line.split(';')[0].rstrip() for line in source.splitlines())
    source = '\n'.join(line for line in lines if line.strip())+'\n'
    source = C.transform(source, hi-lo)
    prefix = ''.join(f'{n}=${M.address(image,n):04x}\n' for n in C.NAMES) + '.segment "CODE"\n'
    old, _ = C.assemble(output/'column-parent', prefix+source, lo, hi-lo)
    raw = image['raw']
    assert bytes.fromhex(historical['new_hex']) == old == raw[at:at+hi-lo]
    source = C.replace(source, '  lda #$00\n  tax\nDrawMTLoop:', '  ldx #$00\nDrawMTLoop:')
    source = C.replace(source, '    jmp @UpdateAttributes', '    bcs @UpdateAttributes')
    source = source[:source.index('@UpdateAttributes:\n')]+PALETTE+source[source.index('EndRow:\n'):]
    new, _ = C.assemble(output/'column-palette', prefix+source, lo, hi-lo)
    assert len(old) == len(new) == hi-lo and old != new
    patch = dict(physical_PRG=TAG&127, CPU_half_open=[lo,hi], file_offset=at,
                 old_hex=old.hex(), new_hex=new.hex())
    return raw[:at]+new+raw[at+len(new):], patch


def setup(m, column, task, tiles, *, dest=0x80, palettes=None):
    N.put(m, CurrentColumnPos=column, AreaParserTaskNum=task, CurrentNTAddr_Low=dest,
          CurrentNTAddr_High=0x20+(column&4), VRAM_Buffer2_Offset=0,
          VRAM_Buffer_AddrCtrl=0, NmiDisable=255, Sprite0HitDetectFlag=1)
    start = M.address(m.bundle,'MetatileBuffer')
    m[start:start+13] = bytes(tiles)
    if palettes is not None:
        start = M.address(m.bundle,'AttributeBuffer')
        m[start:start+7] = bytes(palettes)


def publication(m):
    at = M.address(m.bundle,'VRAM_Buffer2')
    offset = N.get(m,'VRAM_Buffer2_Offset')
    assert N.get(m,'VRAM_Buffer_AddrCtrl') == 6 and m[at+offset] == 0
    payload, writes = [], {}
    cursor = at
    while cursor < at+offset:
        hi, lo, control = m[cursor:cursor+3]
        assert hi and control in (0x9a,1)
        cursor += 3
        count = control & 0x3f
        increment = 32 if control & 0x80 else 1
        for i,v in enumerate(m[cursor:cursor+count]):
            payload.append(v)
            writes[(hi<<8|lo)+i*increment] = v
        cursor += count
    assert cursor == at+offset and payload
    m.writes.clear()
    m.ppu_log.clear()
    N.consume(m)
    assert [v for a,v in m.ppu_log if a==0x2007] == payload
    assert all(m.vram[a]==v for a,v in writes.items())
    assert N.get(m,'VRAM_Buffer2_Offset') == N.get(m,'VRAM_Buffer_AddrCtrl') == m[at] == 0
    return tuple(m.ppu_log), tuple(m.writes)


def foreground(before, after):
    images = tuple(map(M.bundle,(before,after)))
    normal = C.compare(*images)
    assert min(normal['left']['cycle_savings']) > 0 and min(normal['right']['cycle_savings']) > 0
    assert normal['attributes']['cycle_savings'] == {0:normal['attributes']['cases']}
    uniform = {k:Counter() for k in ('left','right')}
    for tile, column, task in product(range(256),range(2),(7,6)):
        result = []
        for image in images:
            m = N.Bus(image)
            setup(m,column,task,[tile]*13,palettes=range(0,224,32))
            m.writes.clear()
            out = N.invoke(m,'RenderAreaGraphics',a=23,x=67,y=91,p=0x31)
            result.append((out,C.state(m)))
        a,b = result
        assert a[1]==b[1] and all(a[0][r]==b[0][r] for r in 'AXYP'), (tile,column,task)
        uniform['left' if task&1 else 'right'][a[0]['CPU']-b[0]['CPU']] += 1
    assert all(min(hist)>0 for hist in uniform.values())

    counts = Counter()
    for owner, area, dest in product((0,7,25,32,41,51),range(4),(0x80,0x9e)):
        buses = [seed(image,owner,area) for image in images]
        for m in buses:
            N.put(m,CurrentNTAddr_Low=dest,CurrentNTAddr_High=0x20,
                  VRAM_Buffer2_Offset=0,VRAM_Buffer_AddrCtrl=0)
        for index,task in enumerate((7,6,3,2,0)):
            traces = []
            for m in buses:
                column = index//2
                if task:
                    tiles = [(owner*7+area*29+column*61+i*19)&255 for i in range(13)]
                    setup(m,column,task,tiles,dest=N.get(m,'CurrentNTAddr_Low'),
                          palettes=[0]*7 if index==0 else None)
                    symbol = 'RenderAreaGraphics'
                else:
                    symbol = 'RenderAttributeTables'
                N.invoke(m,symbol)
                traces.append(publication(m))
            assert traces[0]==traces[1] and memory(buses[0])==memory(buses[1]), (owner,area,dest,task)
            counts[str(owner)] += 1
    return dict(column_and_attribute=normal, uniform_metatile_cycles=uniform, genuine_normal_NMI=counts)


def cpu(m, pc):
    c = N.NesMPU(memory=m,pc=pc)
    c.a,c.x,c.y,c.p,c.sp = 23,17,31,0x21,250
    c.stPushWord(STOP-1)
    return c


def clone(c, image):
    m = slim_fork(c.memory)
    m.bundle = image
    m.raw_page(1,TAG)
    other = N.NesMPU(memory=m,pc=c.pc)
    other.a,other.x,other.y,other.p,other.sp = registers(c)
    return other


def vectors(before, after):
    images = tuple(map(M.bundle,(before,after)))
    lag, normal = lag_pcs(N.fresh(images[1]))
    counts, sites, deepest = Counter(), set(), {}
    scratch = ('R0','MetatileBuffer','AttributeBuffer','VRAM_Buffer2')
    watched = {p for n,k in zip(scratch,(6,13,7,35))
               for p in range(M.address(images[1],n),M.address(images[1],n)+k)}

    def live(c):
        m = c.memory
        return (c.pc, registers(c,0xef), live_stack(c), tuple(m.rawtags),
                bytes(m[0x15a:0x17b]), tuple(m[a] for a in sorted(watched)))

    def inject(c, kind, retain=None):
        m = c.memory
        snapshot = live(c)
        stop = c.pc,c.sp
        lag_hits = 0
        skipped = N.get(m,'NmiSkipped')
        if kind=='lag_FF':
            assert N.get(m,'NmiDisable') == 255
            c.nmi()
        else:
            assert not c.p&4
            c.irq()
            assert (c.pc,m.rawtags[0]) == (0x8000,254)

        def watch(z):
            nonlocal lag_hits
            lag_hits += int(z.pc==lag)
            assert z.pc!=normal and not (z.memory.rawtags[1]==TAG and START<=z.pc<END)
            if retain is not None and not z.p&4:
                if retain not in deepest or z.sp<deepest[retain].sp:
                    deepest[retain] = clone(z,images[1])

        run(c,lambda z:(z.pc,z.sp)==stop,watch)
        assert live(c)==snapshot, (kind,hex(c.pc))
        assert lag_hits==int(kind=='lag_FF')
        assert N.get(m,'NmiSkipped')==(skipped+lag_hits)&255
        assert all(a not in watched and a not in (0x2007,0x4014) for a,_ in m.writes)

    def paired(c, kind, retain=None):
        outcomes = []
        for image in images:
            z = clone(c,image)
            inject(z,kind,retain if image is images[1] else None)
            outcomes.append((memory(z.memory),tuple(z.memory.writes),z.processorCycles))
        assert outcomes[0]==outcomes[1], (kind,hex(c.pc))
        counts[kind if retain is not None or kind=='lag_FF' else 'IRQ'] += 1

    for owner in (0,7,25,32,41,51):
        initial = seed(images[1],owner)
        initial.raw_page(1,TAG)
        N.put(initial,CurrentBank=TAG,AreaMusicQueue=1)
        for column, task, tiles in product(range(2),(7,6),([0]*13,[0x40,0x80,0xc0]*4+[0xc0])):
            m = slim_fork(initial)
            setup(m,column,task,tiles,palettes=[19]*7)
            visited = set()

            def visit(z):
                if not START<=z.pc<END or z.pc in visited:
                    return
                visited.add(z.pc)
                sites.add(z.pc)
                paired(z,'lag_FF',owner)
                paired(z,'IRQ')

            run(cpu(m,START),lambda z:(z.pc,z.sp)==(STOP,250),visit)
            assert visited
    for c in deepest.values():
        paired(c,'IRQ')
        counts['nested_IRQ'] += 1
    assert len(sites)>68 and counts['lag_FF']>1800 and counts['nested_IRQ']==6
    return dict(counts=counts, candidate_instruction_cuts=len(sites), foreground_SP=248,
                deepest_unmasked_lag_SP=min(c.sp for c in deepest.values()))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    before = ROM.read_bytes()
    assert M.sha(before)==PIN
    args.output.mkdir(exist_ok=True)
    after, patch = compile_patch(M.bundle(before),args.output)
    cases = foreground(before,after)
    print(json.dumps(cases),flush=True)
    irq = vectors(before,after)
    references = (Path(__file__),C.SOURCE,Path(C.__file__),R/'src/reset.s',R/'src/level_tiles.s',
                  HISTORICAL,GLOBALS.with_suffix('.dbg'),ROM)
    sources = {str(p.resolve().relative_to(R)):M.sha(p.read_bytes()) for p in references}
    for p in args.output.glob('column-*.s'):
        sources[str(p.resolve().relative_to(R))] = M.sha(p.read_bytes())
    proof = dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),
                 patches=[patch],source_bindings=sources,foreground=cases,vectors=irq,
                 scope='Exact shared foreground and real NMI terrain publication. CPU fixture only.')
    (args.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(irq),flush=True)


if __name__=='__main__':
    main()
