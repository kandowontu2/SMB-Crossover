"""Qualify the left-only same-page Goomba terrain admission."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_goomba_page_seam_1110_v1 as S
import check_native_enemy_ordinary_dispatch_1110 as Q
import check_native_enemy_ordinary_dispatch_irq_1110 as IRQ
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at, lag_pcs
from prepare_mini_helper_injury_native_1110 import strict_dispatch_kernel


P,N,R,D = Q.P,Q.N,Q.R,Q.D
BASE = R/'build/mini-helper-injury-parser-native-1110/candidate.nes'
PIN = '1fdee6633e5c2885ff5f0b127632ace0ccb44c83d43593f7ef99364e549134f2'
SOURCE = R/'tools/reference/native_goomba_left_high_x_1110.s'
WITNESS = R/'build/mini-offscreen-late-profile-1110/capture/instruction-sample.json'
ENTRY, START, NATIVE, QUERY, STOP = S.ENTRY,S.START,S.END,S.QUERY,S.STOP
OLD = bytes.fromhex('b576c9f0b00fbd3f05c901f00bc902f007d002eaea')


def link(raw,out):
    assert P.sha(raw)==PIN and len(OLD)==NATIVE-START
    D.check_span(raw,0,START,OLD)
    D.check_span(raw,0,NATIVE,bytes.fromhex('4c17a0b55d2901a8a903850ab5761869088508'))
    D.check_span(raw,0,0xbf82,bytes.fromhex('b5762908f002c609bd3f05c901d008e609b576690fd002b5768508'))
    assert D.offset(0,START)==8021 and P.address(P.bundle(raw),'Enemy_MovingDir')==0x053f
    cc = R/'tools/Windows/cc65/bin'
    with tempfile.TemporaryDirectory(prefix='goomba-',dir=out) as folder:
        t = Path(folder)
        cfg,obj,binary = (t/f'goomba.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY { C:start=$BF45,size=$15,file=%O; } SEGMENTS { GOOMBA_SEAM:load=C,type=ro; }\n')
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        new = binary.read_bytes()
    assert len(new)==len(OLD)
    patch = dict(physical_PRG=0,CPU_half_open=[START,NATIVE],file_offset=D.offset(0,START),
                 old_hex=OLD.hex(),new_hex=new.hex())
    return install(raw,[patch]),patch


def finite(before,after):
    cpus = []
    for image in (before,after):
        m = bytearray(65536)
        lo,hi = D.offset(0,START),D.offset(0,NATIVE)
        m[START:NATIVE] = image[lo:hi]
        cpus.append(N.NesMPU(memory=m))
    counts = Counter()
    for low,direction in product(range(256),repeat=2):
        stops = []
        for c in cpus:
            slot = (low+direction)%6
            m = c.memory
            m[0x76+slot],m[0x053f+slot] = low,direction
            flags = (0x20,0x65,0xec)[(low+direction)%3]
            c.a,c.x,c.y,c.p,c.sp,c.pc = 7,slot,173,flags,244,START
            c.processorCycles = 0
            run(c,lambda q:q.pc in (NATIVE,QUERY))
            assert c.x==slot and c.y==173 and c.sp==244 and (c.p^flags)&0x4c==0
            stops.append((c.pc,c.processorCycles))
        old,new = stops
        expected = direction in (1,2) and low<0xf0
        added = direction==2 and 0xf0<=low<0xf8
        assert (old[0]==QUERY)==expected and (new[0]==QUERY)==(expected or added)
        counts['new_left' if added else 'unchanged_fast' if expected else 'unchanged_native',old[1]-new[1]] += 1
    return [[role,saving,count] for (role,saving),count in sorted(counts.items())]


def prepared(seed,params):
    m = slim_fork(seed)
    m.__class__ = Q.DispatchBus
    S.actor(m,*params[:-1])
    m.raw_page(1,128)
    N.put(m,CurrentBank=128,NmiDisable=255,AreaMusicQueue=1)
    m.writes.clear()
    m.ram_writes.clear()
    m.ppu_log.clear()
    c = cpu_at(m,ENTRY,236,params[-1],x=params[2],y=73)
    return c


def done(c):
    return (c.pc,c.sp)==(STOP,236)


def state(c):
    return registers(c,0xef),live_stack(c),S.memory(c.memory),IRQ.hardware(c)


def actor_cases(before,after):
    seeds = [S.P.fixture(P.bundle(q),0,False,False) for q in (before,after)]
    counts = Counter()

    def check(params):
        low,page,slot,direction,y,foot,side,owner,eid,actor_state,flags = params
        outcomes = []
        for seed in seeds:
            c = prepared(seed,params)
            seen = set()
            def visit(z):
                seen.add(z.pc)
                if z.pc==0xbf7c:
                    assert z.memory[9]+256*z.memory[10]+z.y==S.map_cell(low+8,page,y&0xf0)
                if z.pc==0xbfaa:
                    assert z.memory[9]+256*z.memory[10]+z.y==S.map_cell(
                        low+(16 if direction==1 else 0),page,((y+20)&0xf0)-32)
            run(c,done,visit)
            # Foreground probe scratch writes can differ in number, but all
            # observable memory/mapper state, live registers/stack are exact.
            final = state(c)
            outcomes.append((final[:3],QUERY in seen and S.FALLBACK not in seen,QUERY in seen,c.processorCycles))
        a,b = outcomes
        assert a[0]==b[0],(params,a[0][:2],b[0][:2])
        role = 'new_left' if direction==2 and 0xf0<=low<0xf8 and eid==6 and actor_state==0 else 'unchanged'
        counts[role,a[1],b[1],b[2],a[3]-b[3]] += 1

    for low,direction,(foot,side) in product(range(256),(0,1,2,3,255),((0x54,0),(0,0),(0x54,0xc3))):
        check((low,low&1,low%6,direction,184,foot,side,low%42,6,0,(0x20,0x65,0xec)[low%3]))
    for low,page,y,foot,side in product(range(0xf0,0xf8),(0,1,127,128,255),range(40,185,16),
                                       (0,0x54,0xc3),(0,0x10,0xc2)):
        check((low,page,(low+y)%6,2,y,foot,side,(page+y)%42,6,0,(0x20,0x65,0xec)[page%3]))
    for low,direction,(eid,actor_state,y) in product((0,0x80,0xef,0xf0,0xf7,0xf8,0xff),(1,2),
            ((6,0x20,184),(6,2,184),(6,0x80,184),(0,0,184),(6,0,24),(6,0,176),(6,0,200))):
        check((low,1,2,direction,y,0x54,0,41,eid,actor_state,0x21))
    return [[*k,n] for k,n in sorted(counts.items())]


def vectors(before,after):
    images = [P.bundle(q) for q in (before,after)]
    with strict_dispatch_kernel():
        seeds = Q.cold(images)
    simple = [S.P.fixture(b,0,False,False) for b in images]
    lag,normal = lag_pcs(seeds[41][1])
    counts,nested,sites = Counter(),{},set()

    def inject(c,kind,mirror=None,record=False):
        owner = N.get(c.memory,'SelectedCharacter')
        pair = [fork(c)] if mirror is None else [fork(c),fork(c,mirror)]
        rows = []
        for i,z in enumerate(pair):
            m = z.memory
            if kind=='normal':
                N.put(m,NmiDisable=0)
            m.writes.clear()
            m.ram_writes.clear()
            m.ppu_log.clear()

            def observe(q):
                if not i and record and kind=='FF' and not q.p&4:
                    key = owner,tuple(q.memory.rawtags)
                    if key not in nested or q.sp<nested[key].sp:
                        nested[key] = fork(q)
                        nested[key].memory.vector_floor = None

            cycles = IRQ.interrupt(z,kind,lag,normal,observe)
            rows.append((cycles,state(z)))
        if mirror is not None:
            assert rows[0]==rows[1],(owner,kind,D.bank_pc(c))
        return pair[0]

    cases = [(1,n,0xf5,2,0x54,0,False) for n in range(42)]
    cases += [(side,owner,low,dir,foot,cell,True)
              for side,owner,(low,dir,foot,cell) in product((0,1),Q.OWNERS,
                    ((0xf0,2,0x54,0),(0xf7,2,0x54,0),(0xf8,2,0x54,0),
                     (0xf5,2,0x54,0xc3),(0xf5,2,0,0),(0xf5,1,0x54,0)))]
    for side,owner,low,dir,foot,cell,deep in cases:
        seed = seeds[owner][side] if deep else simple[side]
        c = prepared(seed,(low,low&1,2,dir,184,foot,cell,owner,6,0,0x21 if low&1 else 0x25))
        seen = set()

        def visit(z):
            tag,pc = D.bank_pc(z)
            if tag!=128 or pc in seen or not (ENTRY<=pc<0xbfc2 if deep else pc==START):
                return
            seen.add(pc)
            sites.add((side,pc))
            for kind in ('FF','IRQ','normal'):
                if kind=='IRQ' and z.p&4 or kind=='normal' and pc!=START:
                    continue
                replay = inject(z,kind,images[1-side],record=side==1)
                run(replay,done)
                counts[kind]+=1

        run(c,done,visit)
        assert seen
    resumes = []
    for owner,low,direction,kind in product(Q.OWNERS,(0xef,0xf5,0xf8),(1,2),('FF','IRQ','normal')):
        values = (low,1,2,direction,184,0x54,0,owner,6,0,0x21)
        rows = []
        for seed in seeds[owner]:
            c = prepared(seed,values)
            run(c,lambda z:D.bank_pc(z)==(128,START))
            resumed = inject(c,kind)
            hw = IRQ.hardware(resumed)
            run(resumed,done)
            rows.append((state(resumed)[:3],hw))
        assert rows[0]==rows[1],(owner,low,direction,kind)
        resumes.append([owner,low,direction,kind])
    for c in nested.values():
        inject(c,'IRQ',images[0])
        counts['nested']+=1
    assert all(counts[k] for k in ('FF','IRQ','normal','nested'))
    return dict(cuts=dict(counts),sites=sorted(sites),matched_native_actor_resumes=resumes,
                actual_lag_PC=lag,actual_normal_NMI_PC=normal)


def whole(before,after):
    with strict_dispatch_kernel():
        return Q.whole(before,after)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--vectors-only',action='store_true')
    args = ap.parse_args()
    args.output.mkdir(exist_ok=True)
    before = BASE.read_bytes()
    proof = args.output/'proof.json'
    if args.vectors_only:
        q = json.loads(proof.read_text())
        assert q['passed'] and q['parent_SHA256']==P.sha(before)==PIN
        for file,digest in q['bindings'].items():
            assert P.sha(Path(file).read_bytes())==digest,file
        after = install(before,q['patches'])
        assert P.sha(after)==q['expected_memory_only_SHA256']
        receipt = vectors(before,after)
        receipt.update(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),ROM_written=False,
                       bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in (Path(__file__),proof,R/'src/reset.s')})
        (args.output/'irq.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(receipt['cuts'],flush=True)
        return
    after,patch = link(before,args.output)
    dispatcher = finite(before,after)
    print('65536 low/direction cases',flush=True)
    actors = actor_cases(before,after)
    print('Actor cases',sum(row[-1] for row in actors),flush=True)
    frames = whole(before,after)
    observed = Q.read_scene(WITNESS)
    assert observed['actors'][4]['x']==2037 and observed['x']==1999
    inputs = (Path(__file__),SOURCE,R/'src/ground_goomba_terrain.s',WITNESS)
    receipt = dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),ROM_written=False,
                   patches=[patch],all_low_direction_bytes=dispatcher,actor_cases=actors,whole_GameLoop=frames,
                   profile=dict(frame=observed['frame'],player_x=1999,actor_x=2037,direction_observed=False,
                                native_floor_and_side_tile_values_observed=False),
                   bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in inputs})
    proof.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
