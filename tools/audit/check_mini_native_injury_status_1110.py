"""Repair only Mini's unhandled native injury return value."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import tempfile

import check_mini_helper_injury_1110 as I
import check_mini_helper_injury_irq_1110 as Existing
import check_mini_lift_admission_async_1108_v1 as Q
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from measure_mini_kernel_transport_1109 import compile_source, replace_one


H,L,M,N,R = I.H,I.L,I.M,I.N,I.R
ROM = R/'build/mini-helper-injury-column-native-1110/candidate.nes'
PIN = 'bca98ddef87633c4d2e83cfc188115572803b4fc58962108abf3ed505aa4af2f'
KERNEL = R/'build/mini-helper-activation-offscreen-1110/kernel.bin'
WITNESS = R/'build/mini-injury-helper-v4-native-1110/capture/result.json'
ENTRY, LEAF, STORE = 0xa00f,0xac82,0x97a4
FORCE, STOP = 0x9771,0x5b00
STATUS = 0x075b


def transform(source):
    source = replace_one(source,' jmp MiniHostNo           ;5 native injury fallback',
                         ' jmp MiniHostInjury       ;5 native injury fallback returns small tier')
    return replace_one(source,'    .res $8c5-(*-MiniStep),$ea\nMiniWorldEnd:', '''    .export MiniHostInjury
MiniHostInjury:
    ; ForceInjury stores A as the new native tier on an unhandled return.
    ; Keep the native blink and movement timeline. HostMain syncs its own
    ; collision and animation tier at the first active source update.
    lda #0
    clc
    rts

    .res $8c5-(*-MiniStep),$ea
MiniWorldEnd:''')


def build(raw, output):
    start,end = L.CODE,L.CODE+5120
    cookie = L.COOKIE
    old_kernel = KERNEL.read_bytes()
    source = KERNEL.with_suffix('.s').read_text()
    assert raw[start:end]==old_kernel
    assert raw[cookie:cookie+16]==bytes((167,41,1))+H.A.digest(raw[start:start+7168])
    assert raw[H.offset(126,0x97a2):H.offset(126,0x97a7)]==bytes.fromhex('b02f8d5b07')
    with tempfile.TemporaryDirectory(dir=output,prefix='link-') as name:
        rebuilt,prior_labels = compile_source(Path(name),source,L.CONFIG)
    new,labels = compile_source(output,transform(source),L.CONFIG)
    assert rebuilt==old_kernel and len(new)==len(old_kernel)==5120
    assert labels.pop('MiniHostInjury')==LEAF and labels==prior_labels
    a,b = ENTRY-0xa000,LEAF-0xa000
    assert old_kernel[a:a+3]==bytes.fromhex('4cedae')
    assert old_kernel[b:0x0caa]==b'\xea'*40
    assert new[a:a+3]==bytes.fromhex('4c82ac') and new[b:b+4]==bytes.fromhex('a9001860')
    assert all(old==after or a<=i<a+3 or b<=i<b+4
               for i,(old,after) in enumerate(zip(old_kernel,new,strict=True)))
    payload = new+raw[end:start+7168]
    patches = [L.patch(raw,start+a,new[a:a+3],'Mini private service5 vector'),
               L.patch(raw,start+b,new[b:b+4],'retired Mini code padding, native status return'),
               L.patch(raw,cookie+3,H.A.digest(payload),'Mini authenticated payload digest')]
    after = install(raw,patches)
    assert after[start:end]==new
    cold,masks = H.A.exact_cold(raw,after,[(a,a+3),(b,b+4)])
    return after,patches,cold,masks


def force(m, status, *, owner=41, flags=0x21, immunity=0, visit=None, entry=FORCE):
    m.raw_page(0,254)
    m.raw_page(1,128)
    N.put(m,SelectedCharacter=owner,CurrentBank=128,PlayerStatus=status,
          PlayerSize=int(status==0),InjuryTimer=immunity)
    m.ram[2][0x244] = status
    m.ram[2][0x256] = 1 if status==0 else 0xf9
    m.writes.clear()
    m.ram_writes.clear()
    m.ppu_log.clear()
    c = N.NesMPU(memory=m,pc=entry)
    c.a,c.x,c.y,c.p,c.sp = 6,0,0,flags,245
    c.stPushWord(STOP-1)
    stores = []

    def watch(z):
        if (Q.tags(z),z.pc)==(254,STORE):
            stores.append((z.a,z.p&1))
        if visit is not None:
            visit(z)

    run(c,lambda z:(z.pc,z.sp)==(STOP,245),watch)
    return c,stores


def canonical(m,masks,*,status=False):
    main,zc,work,smc,tags,ram,*ppu = I.memory(m)
    if status:
        zc = zc[:STATUS-0x200]+b'\0'+zc[STATUS-0x200+1:]
    resident = [bytearray(bank) for bank in ram]
    for bank,intervals in masks.items():
        for start,end in intervals:
            resident[bank][start:end] = bytes(end-start)
    return main,zc,work,smc,tags,tuple(map(bytes,resident)),*ppu


def foreground(before,after,masks):
    pair = L.bundles(before,after)
    seeds = [L.fixture(bundle,0,False,False) for bundle in pair]
    stats = Counter()
    force_rows = []
    for status,mode,flags in product((0,1,2,41),range(2),(0x21,0x70,0xa1)):
        buses = [I.setup(m,854,0,engine=8) for m in seeds]
        for m in buses:
            N.put(m,CrossoverBehaviorVersion=mode,SecondaryHardMode=mode)
        old,new = [force(m,status,flags=flags) for m in buses]
        assert registers(old[0])==registers(new[0])
        if status:
            assert old[1]==[(41,0)] and new[1]==[(0,0)]
            for m,tier in zip(buses,(41,0),strict=True):
                assert (N.get(m,'PlayerStatus'),N.get(m,'GameEngineSubroutine'),
                        N.get(m,'TimerControl'),N.get(m,'InjuryTimer'))==(tier,10,255,8)
                assert m.ram[2][0x244]==status and m.ram[2][0x256]==0xf9
            assert canonical(buses[0],masks,status=True)==canonical(buses[1],masks,status=True)
        else:
            assert not old[1] and not new[1]
            assert canonical(buses[0],masks)==canonical(buses[1],masks)
        force_rows.append([status,mode,flags,old[1],new[1]])
    for status in (0,1,2):
        buses = [I.setup(m,854,0,engine=8) for m in seeds]
        results = [force(m,status,immunity=8,entry=0x976c) for m in buses]
        assert not any(stores for _,stores in results)
        assert canonical(buses[0],masks)==canonical(buses[1],masks)
        assert registers(results[0][0])==registers(results[1][0])
        stats['already_immune'] += 1

    for owner,status,mode in product((0,1,2,6,7,12,15,19,25,28,29,32,35,36,37,38,39,40,51),
                                    (0,1,2),range(2)):
        buses = [I.setup(m,854,0,owner=owner,engine=8) for m in seeds]
        reached = []
        def watch(z):
            if Q.tags(z)==3 and z.pc in (ENTRY,LEAF):
                reached.append((owner,status,z.pc))
        for m in buses:
            N.put(m,CrossoverBehaviorVersion=mode,SecondaryHardMode=mode)
        old,new = [force(m,status,owner=owner,visit=watch) for m in buses]
        assert not reached
        assert registers(old[0])==registers(new[0]) and old[1]==new[1],(owner,status,mode)
        assert canonical(buses[0],masks)==canonical(buses[1],masks),(owner,status,mode)
        assert buses[0].writes==buses[1].writes
        stats['foreign_force'] += 1
    return dict(force_rows=force_rows,counts=stats)


def lifecycle(raw, status, expected):
    bundle = L.bundles(raw,raw)[0]
    m = I.setup(L.fixture(bundle,0,False,False),854,0,engine=8)
    for right in H.MINIMA[:2]:
        L.spawn(m,right)
    L.camera(m,854)
    lives = N.get(m,'NumberofLives')
    _,stores = force(m,status)
    assert stores==[(expected,0)]
    N.put(m,NmiDisable=0)
    idle = M.address(bundle,'IdleLoop')
    rows,source = [],[]
    for _ in range(68):
        c = Existing.start(m,idle)
        if N.get(m,'NmiDisable')==0:
            at = c.pc,c.sp
            c.nmi()
            run(c,lambda z:(z.pc,z.sp)==at)
            N.put(m,SavedJoypadBits=1,SavedJoypad1Bits=1)
        visits = Counter()

        def watch(z):
            point = Q.tags(z),z.pc
            if point==(3,0xb255) and N.get(m,'GameEngineSubroutine')==8:
                source.append((m.ram[2][0x244],m.ram[2][0x256],m.ram[2][0x310]))
            if point==(129,I.CONTROL) and N.get(m,'GameEngineSubroutine')==10:
                visits[point] += 1
            if point in ((206,0xbcc7),(3,0xaf4d)):
                visits[point] += 1

        run(c,lambda z:(z.pc,z.sp)==(idle+12,252),watch)
        assert N.get(m,'NumberofLives')==lives
        if visits[129,I.CONTROL]:
            rows.append([N.get(m,'TimerControl'),I.camera_right(m),m.ram[2][0x30c],m.ram[2][0x244]])
        if visits[3,0xaf4d]:
            assert len(rows)==39 and N.get(m,'GameEngineSubroutine')==8,(
                status,expected,len(rows),N.get(m,'GameEngineSubroutine'),N.get(m,'TimerControl'),visits,source)
            assert len(source)>0
            pose = m.ram[2][0x310]
            address = M.address(bundle,'BoundingBox_UL_Corner')
            ulx,uly,lrx,lry = m[address:address+4]
            assert (lrx-ulx)&255==5 and (lry-uly)&255==(6 if not expected else 14)
            assert m.ram[2][0x244]==expected and m.ram[2][0x256]==(1 if not expected else 0xf9)
            assert (pose<39)==(expected==0),(status,expected,pose,source)
            return dict(injury_frames=rows,first_source_body=[ulx,uly,lrx,lry],first_source_pose=pose,
                        first_source_tier=m.ram[2][0x244],lives=lives)
    raise AssertionError(('Mini native injury did not resume source movement',status,expected))


def vectors(after):
    bundle = L.bundles(after,after)[0]
    seed = Existing.guarded_seed(bundle)
    lag,normal = Q.lag_pcs(seed)
    m = I.setup(seed,854,0,engine=8)
    cases,deepest = Counter(),None

    def inject(c,kind,retain=False):
        nonlocal deepest
        z = fork(c)
        bus = z.memory
        expected = Q.live(z)
        stop = z.pc,z.sp
        skipped = N.get(bus,'NmiSkipped')
        bus.vector_floor,bus.written_stack = 0x100+z.sp,set()
        if kind=='lag_FF':
            assert N.get(bus,'NmiDisable')==255
            z.nmi()
        else:
            assert not z.p&4
            z.irq()
            assert (Q.tags(z),z.pc)==(254,0x8000)
        hits = 0

        def watch(cut):
            nonlocal hits,deepest
            hits += cut.pc==lag
            assert cut.pc!=normal
            if retain and not cut.p&4 and (deepest is None or cut.sp<deepest.sp):
                deepest = fork(cut)
                deepest.memory.vector_floor = None

        run(z,lambda q:(q.pc,q.sp)==stop,watch)
        bus.vector_floor = None
        assert Q.live(z)==expected,(kind,stop)
        assert hits==int(kind=='lag_FF') and N.get(bus,'NmiSkipped')==(skipped+hits)&255
        assert not any(0x200<=a<0x304 or a==0x4014 for a,_ in bus.writes)
        cases[kind] += 1
        return z

    resumes = []
    def visit(c):
        t,p = Q.tags(c),c.pc
        if (t==3 and p in (ENTRY,LEAF,LEAF+2,LEAF+3)) or (t,p)==(254,STORE):
            for kind in ('IRQ','lag_FF'):
                resumes.append((inject(c,kind,kind=='lag_FF'),kind))
    original,stores = force(m,2,visit=visit)
    assert stores==[(0,0)] and len(resumes)==10 and deepest is not None
    for z,kind in resumes:
        run(z,lambda q:(q.pc,q.sp)==(STOP,245))
        assert registers(z)==registers(original)
        if kind=='lag_FF':
            assert N.get(z.memory,'NmiSkipped')==N.get(m,'NmiSkipped')+1
        for field,value in [('PlayerStatus',0),('GameEngineSubroutine',10),('TimerControl',255),('InjuryTimer',8)]:
            assert N.get(z.memory,field)==N.get(m,field)==value
    inject(deepest,'nested_IRQ')
    return dict(cuts=cases,full_force_resumes=len(resumes),deepest_nested_SP=deepest.sp)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    out.mkdir(exist_ok=True)
    before = ROM.read_bytes()
    assert M.sha(before)==PIN
    native = json.loads(WITNESS.read_text(encoding='utf-8'))
    assert native['passed'] and native['ROM_sha256']==PIN
    assert native['injury_helper']['native_status_anomaly']==dict(before=1,during=41,expected=0)
    after,patches,cold,masks = build(before,out)
    fg = foreground(before,after,masks)
    print(json.dumps(dict(foreground=fg['counts'])),flush=True)
    sequences = []
    for status in (1,2):
        old,new = (lifecycle(raw,status,tier) for raw,tier in ((before,41),(after,0)))
        assert old['injury_frames']==new['injury_frames'] and old['lives']==new['lives']
        assert new['injury_frames'][-1][2]==7
        sequences.append(dict(previous_tier=status,old=old,new=new))
    irq = vectors(after)
    refs = (Path(__file__),ROM,KERNEL,KERNEL.with_suffix('.s'),KERNEL.with_suffix('.lbl'),L.CONFIG,WITNESS,
            R/'src/collision.s',R/'src/player.s',Path(Existing.__file__),out/'kernel.s',out/'kernel.bin')
    proof = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),
                 patches=patches,cold=cold,foreground=fg,lifecycle=sequences,vectors=irq,
                 source_bindings={str(p.resolve().relative_to(R)):M.sha(p.read_bytes()) for p in refs},
                 scope='Only Mini service 5 changes. Mode10 source pose/body remain frozen and sync on the first mode8 HostMain.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,memory_SHA256=M.sha(after),vectors=irq)),flush=True)


if __name__=='__main__':
    main()
