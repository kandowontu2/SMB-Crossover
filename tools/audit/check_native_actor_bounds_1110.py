"""Measure the source-funded visible actor bounds path on 90a8."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_shared_draw_retarget_1110 as D
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_shared_offscreen_irq_1110_v1 import STOP, cpu_at
from check_native_relative_offscreen_irq_1110 import StackGuard


R, P, N, M = D.R, D.P, D.N, D.Match
ROM = R/'build/mini-edges-draw-offscreen-native-1110/candidate.nes'
PIN = '90a8ac32d51acd29965a45aa5fd512b0b2d77d1c01b03982b62e6d9bed1d1d82'
SOURCE = R/'tools/reference/native_actor_bounds_1110.s'
KERNEL = R/'build/mini-step-edges-1110/kernel.bin'
KERNEL_PIN = 'b1d602f014ca42c42c10110c2ff6cc54ce9bbb7e9940a2e57240e3ab82345069'
PEAK = R/'build/mini-991b-player-profile-1110/capture/instruction-sample.json'
LATE = R/'build/mini-90a8-late-profile-1110/capture/instruction-sample.json'
POSE, RETURN, FAST, TAIL, END, STOCK = 0xba1e, 0xba3e, 0xba3f, 0xba4b, 0xba4e, 0xa504
SCRATCH = frozenset((3,4,5,6))
POSE_OLD = bytes.fromhex('ac5307c003f010acca06d00ba056ae4607f00da05ad009a054ae4607f002a058a60da'
                         '50e29018505981865059de20660')
STOCK_OLD = bytes.fromhex('b517c914f055ad1f07b417c005f004c00dd0026938e9488504ad1d07e9008503ad2007'
                          '69488506ad1e0769008505b576c504b55de5033020b576c506b55de5053019b51fc905'
                          'f013c00df00fc030f00bc031f007c032f0034c2f8d60')


class BoundsBus(StackGuard):
    bounds_pending = frozenset()

    def __getitem__(self, at):
        if isinstance(at,int):
            assert at not in self.bounds_pending, ('Unpublished bounds scratch read',self.bounds_pc,at)
        return super().__getitem__(at)

    def __setitem__(self, at, value):
        if isinstance(at,int) and at in self.bounds_pending:
            self.bounds_pending -= {at}
            self.kills[self.bounds_pc,at] += 1
        super().__setitem__(at,value)


def link(raw,out):
    D.check_span(raw,0,STOCK,STOCK_OLD)
    D.check_span(raw,0,0xb44a,bytes.fromhex('20a08a201eba4c04a5'))
    D.check_span(raw,126,0x8aa0,bytes.fromhex('8603e8a001d012'))
    D.check_span(raw,126,0x8ac7,bytes.fromhex('a60d60'))
    bank = raw[16:8208]
    assert [(0xa000+i,op) for i,op in enumerate(bank[:-2]) if op in (0x20,0x4c)
            and POSE<=bank[i+1]+256*bank[i+2]<END]==[(0xb44d,0x20)]
    with tempfile.TemporaryDirectory(prefix='bounds-link-',dir=out) as td:
        tmp=Path(td)
        cfg,obj,binary,labels=(tmp/f'bounds.{ext}' for ext in ('cfg','o','bin','lbl'))
        cfg.write_text('MEMORY { W:start=$ba1e,size=$30,file=%O; } SEGMENTS { WORKER:load=W,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',labels],check=True)
        data = binary.read_bytes()
        syms = {line.split()[2][1:]:int(line.split()[1],16) for line in labels.read_text().splitlines()}
    assert syms==dict(DrawLargePlatform=POSE,VisibleActorBounds=FAST,BoundsStock=TAIL,WorkerEnd=END),syms
    patches = []
    for pc,old,new in ((POSE,POSE_OLD,data),(0xa493,b'\x4c\x04\xa5',bytes((0x4c,FAST&255,FAST>>8))),
                       (0xb450,b'\x4c\x04\xa5',bytes((0x4c,FAST&255,FAST>>8)))):
        D.check_span(raw,0,pc,old)
        assert len(old)==len(new)
        patches.append(dict(file_offset=D.offset(0,pc),physical_PRG=0,
                            CPU_half_open=[pc,pc+len(old)],old_hex=old.hex(),new_hex=new.hex()))
    return install(raw,patches),patches


def edge_cases(before,after):
    raw = [before,after]
    cpus = []
    for im in raw:
        m = bytearray(65536)
        m[0xa000:0xc000] = im[16:8208]
        m[0x8d2f] = 0x60      # Stop before this independently bound erase leaf.
        cpus.append(N.NesMPU(memory=m))
    counts = Counter()
    lefts = (0,1,56,71,72,73,127,198,199,200,254,255,256,257,582,32767,32768,65480,65535)
    rels = (-32769,-32768,-32767,-329,-274,-273,-256,-74,-73,-72,-71,-18,-17,-16,-1,0,1,15,
            71,72,127,128,254,255,256,271,327,328,329,330,511,32767,32768,32769)
    for left,rel,eid,state in product(lefts,rels,(0,5,6,0xc,0xd,0xe,0x14,0x25,0x30,0x31,0x32,0x33,255),(0,5,255)):
        right, x = (left+255)&65535, (left+rel)&65535
        slot = (left+eid+rel)%6
        row = []
        for pc,c in zip((STOCK,FAST),cpus,strict=True):
            m = c.memory
            m[:16] = bytes(range(16))
            m[0x0d] = (slot+1)%6    # Bounds use actual X, including stale ObjectOffset.
            m[0x071d:0x0721] = bytes((left>>8,right>>8,left&255,right&255))
            m[0x17+slot],m[0x1f+slot],m[0x76+slot],m[0x5d+slot] = eid,state,x&255,x>>8
            c.a,c.x,c.y,c.p,c.sp,c.pc = 99,slot,15,0x21,248,pc
            c.processorCycles = 0
            c.stPushWord(STOP-1)
            run(c,lambda z:z.pc in (STOP,0x8d2f))
            row.append((c.pc,registers(c,0xef),bytes(m[:16]),c.processorCycles))
        a,b = row
        shortcut = ((x-left)&65535)<256
        assert a[0]==b[0],(left,rel,eid,state,row)
        if shortcut:
            assert a[0]==STOP and a[1][1]==b[1][1]==slot
            assert all(a[2][i]==b[2][i] for i in range(16) if i not in SCRATCH)
        else:
            if eid==0x14:
                # The Cheep fast return alone does no native arithmetic and
                # retains incoming V. The scoped actor tail has no V consumer.
                assert a[1][:3]==b[1][:3] and a[1][3]&0xbf==b[1][3]&0xbf and a[1][4]==b[1][4]
                assert a[2]==b[2],(left,rel,eid,state,row)
            else:
                assert a[:3]==b[:3],(left,rel,eid,state,row)
        counts['visible' if shortcut else 'stock',a[3]-b[3]]+=1
    return [[role,delta,n] for (role,delta),n in sorted(counts.items())]


def scene_seed(m,scene):
    actual = [r for r in scene['actors'] if r['flag']==1]
    M.arena(m,dict(scene,actors=actual),True)
    for slot in set(range(6))-{r['slot'] for r in actual}:
        M.place(m,'Enemy_Flag',slot,0)
        M.place(m,'EnemyMetasprite',slot,0)
    N.put(m,FrameCounter=(scene['frame']-1)&255)
    return m


def trace_bounds(c):
    m = c.memory
    tag,pc = m.bounds_pc = D.bank_pc(c)
    if tag!=128:
        return
    if pc==POSE:
        assert c.x==m[0x0d],('Caller X does not match ObjectOffset',c.x,m[0x0d])
    if pc==FAST:
        m.in_bounds = True
    if m.in_bounds and pc in (RETURN,TAIL):
        m.in_bounds = False
        m.hits[pc] += 1
        if pc==RETURN:
            m.bounds_pending |= SCRATCH


def cold_pair(images,owners):
    old,old_kernel = N.Bus,D.KERNEL
    assert P.sha(KERNEL.read_bytes())==KERNEL_PIN
    N.Bus = BoundsBus
    D.KERNEL = KERNEL
    try:
        for image in images:
            D.verify_payload(image['raw'],KERNEL)
        return {owner:[D.cold(bundle,owner)[0] for bundle in images] for owner in owners}
    finally:
        N.Bus = old
        D.KERNEL = old_kernel


def state(a,b):
    m = b.memory
    pending = m.bounds_pending
    left,right = [bytes(list.__getitem__(c.memory,slice(0,256))) for c in (a,b)]
    different = {i for i in range(256) if left[i]!=right[i]}
    assert different<=pending,(different,pending)
    m.bounds_pending = frozenset()
    for at in different:
        list.__setitem__(m,at,left[at])
    try:
        assert semantic(a)==semantic(b) and a.memory[D.SMC]==m[D.SMC]
    finally:
        for at in different:
            list.__setitem__(m,at,right[at])
        m.bounds_pending = pending
    return sorted(different)


def whole(before,after):
    images = [P.bundle(q) for q in (before,after)]
    owners = (0,2,25,32,41)
    seeds = cold_pair(images,owners)
    reports = []
    for owner,profile in product(owners,(PEAK,LATE)):
        scene = json.loads(profile.read_text())['scene']
        pair = [scene_seed(slim_fork(m),scene) for m in seeds[owner]]
        cycles = []
        for i,key in enumerate((scene['keys'],0,192,192,1,1,0,193,0)):
            cpus=[]
            for side,m in enumerate(pair):
                m.writes.clear()
                m.ram_writes.clear()
                m.ppu_log.clear()
                m.kills,m.hits,m.in_bounds=Counter(),Counter(),False
                M.controls(m,key)
                c=cpu_at(m,P.address(m.bundle,'GameLoop'),252,0x21,x=0,y=0)
                run(c,lambda z:(z.pc,z.sp)==(STOP,252),trace_bounds if side else None)
                cpus.append(c)
            a,b=cpus
            try:
                remaining = state(a,b)
            except AssertionError as error:
                raise AssertionError((owner,profile,i,b.memory.bounds_pending,error)) from error
            assert [(i,v) for i,v in a.memory.writes if 0x200<=i<0x300]==[
                    (i,v) for i,v in b.memory.writes if 0x200<=i<0x300],(owner,profile,i)
            cycles.append([a.processorCycles,b.processorCycles,a.processorCycles-b.processorCycles,
                           b.memory.hits[RETURN],b.memory.hits[TAIL],remaining])
            for m in pair:
                N.consume(m)
        reports.append(dict(owner=owner,scene=profile.parent.parent.name,updates=cycles))
    return reports


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args()
    raw=ROM.read_bytes()
    assert P.sha(raw)==PIN
    args.output.mkdir(exist_ok=True)
    image,patches=link(raw,args.output)
    leaves=edge_cases(raw,image)
    print('Bounds matrix',leaves,flush=True)
    loops=whole(raw,image)
    for row in loops:
        print(row['owner'],row['scene'],[(r[2],r[3],r[4]) for r in row['updates']],flush=True)
    files=(Path(__file__),SOURCE,ROM,PEAK,LATE,R/'src/object.s',R/'src/common.s',R/'src/game.s',
           R/'src/level_tiles.s',R/'src/sprite_render.s',KERNEL)
    out=dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(image),ROM_written=False,
             patches=patches,edge_cases=leaves,whole_GameLoop=loops,
             bindings={str(p):P.sha(p.read_bytes()) for p in files})
    (args.output/'proof.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':
    main()
