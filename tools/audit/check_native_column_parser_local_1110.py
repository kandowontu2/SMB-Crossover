"""Qualify the native parser's local call and late authored column pass."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_movement_prefix_1110 as M
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at


P,N,Q,D,R = M.P,M.N,M.Q,M.D,M.R
BASE = R/'build/mini-movement-popup-rng-native-1110/candidate.nes'
PIN = 'f5183f7ada374443222dc0b30a0777a8218aac154c04f84855d140245370daaa'
SOURCE = R/'tools/reference/native_column_parser_local_1110.s'
PROFILE = R/'build/mini-six-busy-profile-1110/capture/instruction-sample.json'
HEAD,END,TARGET = 0xa2e4,0xa314,0xbff0
NATIVE,VARIANT = (130,0xa314),(154,0xa012)
OLD = bytes.fromhex('20efbfada00420dc95a200a0008403bca104b936ef293ff00198a403910998186910a8e8e00d90e5ac0260184c7690ea')
FIELDS = frozenset((0x162,0x16c,0x16d,0x179))
STOP = 0x5b00


def link(raw,out):
    assert P.sha(raw)==PIN and len(OLD)==END-HEAD
    D.check_span(raw,2,HEAD,OLD)
    D.check_span(raw,2,0xbfef,bytes.fromhex('a9008d6c01a9a08d6d01a99a4c5a01ffff'))
    D.check_span(raw,26,0xa000,bytes.fromhex('8d6a01a9148d6c01a9a38d6d01a982205a012059ab'))
    D.check_span(raw,126,0x95dc,bytes.fromhex('484a4a4a4aa8b9da95850a68290f1879d895850960'))
    D.check_span(raw,126,0x95d8,bytes.fromhex('00d00303'))
    D.check_span(raw,126,0x9076,bytes.fromhex('d004a8e00d60a509290f09c0a8a20038'))
    source = (R/'src/level_tiles.s').read_text()
    variants = (R/'src/level_variants.s').read_text()
    assert source.count('jsr CrossoverLevelColumnBridge')==1
    assert variants.count('farcall ProcessAreaData')==1 and 'farcall ProcessAreaData\n  LvLoadedAreaA' in variants
    for code in ('4ce4a2','20e4a2','20efbf','20a2e7','4ce7a2'):
        at = D.offset(2,0xa000)
        page = raw[at:at+8192]
        assert page.count(bytes.fromhex(code))==int(code=='20efbf'),code
    cc = R/'tools/Windows/cc65/bin'
    with tempfile.TemporaryDirectory(prefix='column-',dir=out) as folder:
        t = Path(folder)
        cfg,obj,blob = (t/f'column.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY{C:start=$A2E4,size=$30,file=%O;B:start=$BFF0,size=1,file=%O;}\n'
                       'SEGMENTS{COLUMN:load=C,type=ro;VARIANT_TARGET:load=B,type=ro;}\n')
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',blob],check=True)
        data = blob.read_bytes()
    assert len(data)==len(OLD)+1 and data[:6]==bytes.fromhex('2014a320efbf')
    rows = [M.patch(2,HEAD,OLD,data[:-1]),M.patch(2,TARGET,b'\0',data[-1:])]
    return install(raw,rows),rows


class PacketBus(Q.DispatchBus):
    tracked = False
    pending = frozenset()
    site = None

    def __getitem__(self, at):
        if self.tracked and isinstance(at,int) and at in self.pending:
            raise AssertionError(('Unpublished parser transport operand read',self.site,hex(at)))
        return super().__getitem__(at)

    def __setitem__(self, at, value):
        if self.tracked and isinstance(at,int) and at in self.pending:
            self.pending -= {at}
        super().__setitem__(at,value)


def raw_byte(m,at):
    return list.__getitem__(m,at)


def difference(a,b):
    return frozenset(at for at in FIELDS if raw_byte(a.memory,at)!=raw_byte(b.memory,at))


def apply_watch(a,b):
    pending = difference(a,b)
    for c in (a,b):
        c.memory.tracked,c.memory.pending = True,pending
    return pending


def step_to(c, stop, visit=None):
    def trace(z):
        z.memory.site = D.bank_pc(z)
        if visit:
            visit(z)
    run(c,stop,trace)


def equal(a,b, *, exact_stack=True, exact_registers=True, hardware=False):
    delta = difference(a,b)
    m = b.memory
    values = {at:raw_byte(m,at) for at in delta}
    watched = a.memory.tracked,b.memory.tracked
    for c in (a,b):
        c.memory.tracked = False
    for at in delta:
        list.__setitem__(m,at,raw_byte(a.memory,at))
    try:
        left,right = Q.state(a),Q.state(b)
        # This tuple starts with registers. The local parser is already past
        # its original epilogue at the first two synchronization points.
        if not exact_registers:
            left,right = (left[0][5:],*left[1:]),(right[0][5:],*right[1:])
        assert left==right,(D.bank_pc(a),D.bank_pc(b),sorted(delta),
            [(i,[(j,x,y) for j,(x,y) in enumerate(zip(v,w,strict=True)) if x!=y][:12]
                 if isinstance(v,bytes) and isinstance(w,bytes) else (type(v).__name__,type(w).__name__))
             for i,(v,w) in enumerate(zip(left[0],right[0],strict=True)) if v!=w])
        if exact_stack:
            assert live_stack(a)==live_stack(b)
        if hardware:
            assert M.IRQ.hardware(a)==M.IRQ.hardware(b)
    finally:
        for at,value in values.items():
            list.__setitem__(m,at,value)
        a.memory.tracked,b.memory.tracked = watched
    return delta


def promote(m):
    m.__class__ = PacketBus
    return m


def native_column(a,b,stop):
    roles = []
    for c in (a,b):
        step_to(c,lambda z:D.bank_pc(z)==NATIVE)
    roles.append(('native',sorted(equal(a,b,exact_stack=False,exact_registers=False))))
    apply_watch(a,b)
    for c in (a,b):
        step_to(c,lambda z:D.bank_pc(z)==VARIANT)
    roles.append(('variants',sorted(equal(a,b,exact_stack=False,exact_registers=False))))
    apply_watch(a,b)
    # VariantBridge has published its own packet; no consumer is allowed to
    # use the differing old native packet between the authored pass and exit.
    for i,c in enumerate((a,b)):
        step_to(c,lambda z:D.bank_pc(z)==(130,0xa2e7+3*i))
    roles.append(('postpass',sorted(equal(a,b,exact_registers=False))))
    apply_watch(a,b)
    for c in (a,b):
        step_to(c,stop)
    roles.append(('return',sorted(equal(a,b))))
    return roles


def done(c):
    return (c.pc,c.sp)==(STOP,232)


def prepare_column(image, area, column, owner, mode):
    m = promote(N.Bus(image))
    N.put(m,AreaPointer=area,SelectedCharacter=owner)
    N.invoke(m,'GetAreaDataAddrs')
    N.put(m,CurrentPageLoc=0,CurrentColumnPos=column&15,BlockBufferColumnPos=column,
          CurrentBank=130,NmiDisable=255,VRAM_Buffer1_Offset=0)
    m[0x5115] = 130
    if mode!='native':
        # The unchanged native row-$D parser consumes these valid source
        # object encodings. Exercise both real native banked handlers.
        m[0xd6:0xd8] = [0xe0,7]
        m[0x7e0:0x7e4] = [0x0d,0x42 if mode=='axe' else 0x45,0xfd,0]
        N.put(m,CurrentColumnPos=0,AreaDataOffset=0)
        m[0x0733:0x0736] = [255]*3
    m.writes.clear()
    m.ram_writes.clear()
    m.ppu_log.clear()
    c = cpu_at(m,P.address(image,'AreaParserCore'),232,0x21,x=71,y=109)
    c.a = 83
    step_to(c,lambda z:D.bank_pc(z)==(130,HEAD))
    return c


def foreground(before,after):
    images = [P.bundle(raw) for raw in (before,after)]
    modes = [(area,col,owner,'native') for area,col,owner in product(
        (0x20,0x23,0x25,0x27,0x2c,0x31,0x40,0x41,0x61),(0,7,15,16,23,31),(0,4,25,41))]
    modes += [(area,column,owner,mode) for area,column,owner,mode in product(
        (0x25,0x61),(0,31),(0,41),('warp','axe'))]
    savings, shape = Counter(), set()
    for area,column,owner,mode in modes:
        a,b = [prepare_column(image,area,column,owner,mode) for image in images]
        for role,fields in native_column(a,b,done):
            shape.add((role,tuple(fields)))
        savings[mode,a.processorCycles-b.processorCycles] += 1
    return dict(cases=len(modes),shapes=sorted(shape),cycles_saved=[[*k,v] for k,v in sorted(savings.items())])


def whole(before,after):
    seeds = M.cold_seeds(before,after)
    scene = Q.read_scene(PROFILE)
    rows = []
    for owner,column in product(seeds,(0,15,16,31)):
        pair = [Q.Edge.prepare(seed,scene,False) for seed in seeds[owner]]
        for c in pair:
            promote(c.memory)
            N.put(c.memory,AreaParserTaskNum=4,BlockBufferColumnPos=column)
            step_to(c,lambda z:D.bank_pc(z)==(130,HEAD))
        roles = native_column(*pair,Q.at_end)
        saved = pair[0].processorCycles-pair[1].processorCycles
        pending = apply_watch(*pair)
        pair = [cpu_at(c.memory,P.address(c.memory.bundle,'GameLoop'),252,0x21,x=0,y=0) for c in pair]
        for c in pair:
            c.memory.writes.clear()
            c.memory.ram_writes.clear()
            c.memory.ppu_log.clear()
            step_to(c,Q.at_end)
        assert not equal(*pair) and not any(c.memory.pending for c in pair)
        rows.append(dict(owner=owner,column=column,savings=saved,roles=roles,
                         pending_at_loop_return=sorted(pending),next_full_GameLoop_exact=True))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'foreground.json').exists()
    out.mkdir(exist_ok=True)
    before = BASE.read_bytes()
    after,patches = link(before,out)
    print('Bound exact f518 spans.',flush=True)
    columns = foreground(before,after)
    print(columns,flush=True)
    frames = whole(before,after)
    refs = (Path(__file__),SOURCE,PROFILE,R/'src/level_tiles.s',R/'src/level_variants.s')
    result = dict(foreground_passed=True,qualified=False,parent_SHA256=PIN,
                  expected_memory_only_SHA256=P.sha(after),patches=patches,column_cases=columns,
                  whole_GameLoop=frames,ROM_written=False,
                  bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in refs})
    (out/'foreground.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
