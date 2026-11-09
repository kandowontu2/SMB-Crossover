"""Qualify the actual native Goomba flat-ground fast path at the left page seam."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at, checkpoint
from check_mini_visibility_dispatch_1110_v1 import memory
from measure_mini_shared_offscreen_1110_v1 import N, P, PIN, PROFILE, R, ROM


SOURCE=R/'tools/reference/mini_goomba_page_seam_1110_v1.s'
START,END=0xbf45,0xbf5a
OFFSET=16+(START&8191)
OLD=bytes.fromhex('b57629f0f00fc9f0f00bbd3f05c901f007c902f003')
ENTRY,FALLBACK,QUERY,STOP=0xbf1e,0xa017,0xbf5d,0x5b00


def assemble(out):
    with tempfile.TemporaryDirectory(prefix='seam-',dir=out) as folder:
        tmp=Path(folder)
        cfg,obj,binary=(tmp/f'seam.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY{ M:start=$bf45,size=$15,file=%O; } '
                       'SEGMENTS{ GOOMBA_SEAM:load=M,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        return binary.read_bytes()


def map_cell(x,page,row):
    world=x+256*page
    column=(world>>4)&31
    return 0x300+(0xd0 if column>=16 else 0)+(column&15)+row


def actor(m,x,page,slot,direction,y,foot,side,owner=41,enemy=6,state=0):
    N.put(m,ObjectOffset=slot,SelectedCharacter=owner,ScreenLeft_X_Pos=0,
          ScreenLeft_PageLoc=page,ScreenRight_X_Pos=255,ScreenRight_PageLoc=page,FrameCounter=2)
    fields=dict(Enemy_ID=enemy,Enemy_Flag=1,Enemy_X_Position=x,Enemy_PageLoc=page,
                Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_MovingDir=direction,
                Enemy_State=state,Enemy_X_Speed=8 if direction==1 else 248,Enemy_BoundBoxCtrl=3)
    for n,v in fields.items():
        m[P.address(m.bundle,n)+slot]=v
    m[map_cell(x+8,page,y&0xf0)]=foot
    m[map_cell(x+(16 if direction==1 else 0),page,((y+20)&0xf0)-32)]=side


def execute(seed,params):
    m=slim_fork(seed)
    actor(m,*params[:-1])
    p=params[-1]
    slot=params[2]
    c=cpu_at(m,ENTRY,236,p,x=slot,y=73)
    pcs=set()
    run(c,lambda z:(z.pc,z.sp)==(STOP,236),lambda z:pcs.add(z.pc))
    return registers(c),live_stack(c),memory(m),QUERY in pcs and FALLBACK not in pcs,c.processorCycles


def foreground(images):
    seeds=[P.fixture(b,0,False,False) for b in images]
    for m in seeds:
        m.raw_page(1,128)
        N.put(m,CurrentBank=128)
        m.writes.clear()
    counts=Counter()

    def compare(params):
        a,z=[execute(s,params) for s in seeds]
        assert a[:3]==z[:3],(params,a[:2],z[:2],
            [i for i,(old,new) in enumerate(zip(a[2],z[2],strict=True)) if old!=new])
        counts[params[0]<16,a[3],z[3],a[-1]-z[-1]]+=1

    for x,page,direction,foot,side in product(range(16),(0,1,128,255),(0,1,2,3,255),
                                                (0,0x54,0xc3),(0,0x10,0xc2,0xc4)):
        compare((x,page,(x+direction)%6,direction,40 if x&1 else 184,foot,side,
                 (x+page+direction)%42,6,0,(0x20,0x71,0xe5)[x%3]))
    for x,dir,kind in product(range(16,256),(1,2),((6,0),(0,0),(6,0x20),(6,2),(6,0x80))):
        enemy,state=kind
        compare((x,x&1,x%6,dir,184,0x54,0,x%42,enemy,state,0x21))
    assert any(seam and new and saved>=337 for seam,_,new,saved in counts)
    return [[*row,count] for row,count in sorted(counts.items())]


def vectors(images):
    old,new=images
    seed=P.fixture(new,0,False,False)
    seed.raw_page(1,128)
    N.put(seed,CurrentBank=128,NmiDisable=255)
    lag,regular=lag_pcs(seed)
    counts=Counter()
    deepest={}
    minima=[255,255]

    def clone(c,baseline=False):
        m=slim_fork(c.memory)
        if baseline:
            m.bundle=old
            m.raw_page(1,m.rawtags[1])
        cpu=N.NesMPU(memory=m,pc=c.pc)
        cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=registers(c)
        return cpu

    def interrupt(c,kind):
        before=checkpoint(c)
        owner=N.get(c.memory,'SelectedCharacter')
        states=[]
        for baseline in (False,True):
            z=clone(c,baseline)
            m=z.memory
            hits=0
            if kind=='lag_FF':
                z.nmi()
            else:
                assert not z.p&4
                z.irq()

            def visit(q):
                nonlocal hits
                minima[1]=min(minima[1],q.sp)
                if kind=='lag_FF':
                    hits+=int(q.pc==lag)
                    assert q.pc!=regular
                    if not baseline and not q.p&4 and (owner not in deepest or q.sp<deepest[owner].sp):
                        deepest[owner]=clone(q)

            run(z,lambda q:(q.pc,q.sp)==(c.pc,c.sp),visit)
            assert hits==(kind=='lag_FF')
            assert checkpoint(z)==before,(kind,owner,hex(c.pc))
            assert bytes(z.memory[3:7])==bytes(c.memory[3:7])
            states.append((memory(m),m.writes,m.ram_writes,z.processorCycles))
        assert states[0]==states[1],(kind,owner,hex(c.pc))
        counts[kind]+=1

    for who,x,direction,foot,side in (
        *((who,8,1,0x54,0) for who in range(42)),
        *((41,x,direction,foot,side) for x,direction,(foot,side) in
          product((0,8,15,16,240),(1,2),((0x54,0),(0,0),(0x54,0xc2))))):
        m=slim_fork(seed)
        actor(m,x,1,0,direction,184,foot,side,who)
        c=cpu_at(m,ENTRY,232,0x21)
        c.x=0
        seen=set()

        def watch(z):
            pc=z.pc
            if m.rawtags[1]!=128 or not ENTRY<=pc<0xbfc2 or pc in seen:
                return
            seen.add(pc)
            minima[0]=min(minima[0],z.sp)
            interrupt(z,'lag_FF')
            if not z.p&4:
                interrupt(z,'IRQ')

        run(c,lambda z:(z.pc,z.sp)==(STOP,232),watch)
        assert seen
    for c in deepest.values():
        interrupt(c,'nested_IRQ')
    assert len(deepest)==42 and minima[1]>0x7a
    return dict(cuts=dict(counts),minimum_foreground_SP=minima[0],minimum_ISR_SP=minima[1],raw_owners=42)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(exist_ok=True)
    raw=ROM.read_bytes()
    assert P.sha(raw)==PIN
    code=assemble(args.output)
    assert len(code)==len(OLD)==END-START
    patch=dict(physical_PRG=0,start=START,end_exclusive=END,file_offset=OFFSET,
               old_hex=OLD.hex(),new_hex=code.hex())
    image=install(raw,[patch])
    images=[P.bundle(r) for r in (raw,image)]
    hist=foreground(images)
    print('Native seam timings:',hist,flush=True)
    irq=vectors(images)
    sample=json.loads(PROFILE.read_text())
    assert sample['scene']['frame']==1971 and sample['foreground_opcodes']['0:bf49']==5
    q=dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(image),
           patches=[patch],cases=sum(row[-1] for row in hist),timings=hist,interrupts=irq,
           peak=dict(frame=1971,world_x=1511,old_seam_branch_taken=1,foot_side_tiles_sampled=False),
           bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),SOURCE,ROM,PROFILE)},
           scope='Exact linked native actor leaf. Both map pages, seam and foreign states, complete AXYP/SP '
                 'and application/OAM/map equality, plus actual IRQ and lag-NMI cuts. A native peak sample '
                 'must confirm the newly attempted flat cells. Terrain-rejected seam calls may cost more.')
    (args.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=q['cases'],image=q['expected_memory_only_SHA256'],vectors=irq)),flush=True)


if __name__=='__main__':
    main()
