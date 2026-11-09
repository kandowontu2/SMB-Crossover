"""Qualify the offscreen-only Mini helper experiment at real GameLoop cuts."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_helper_activation_1110 as H
import check_mini_lift_seen_fast_irq_1110 as Existing
from check_mini_funded_actor_1108_v3 import install, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_visibility_dispatch_1110_v1 import memory


A,L,M,N,R = H.A,H.L,H.M,H.N,H.R
Q,Sweep = Existing.Q,Existing.Sweep


def seed(bundle, right, prior, occupied, owner=41):
    saved = N.Bus
    N.Bus = Existing.LiftGuard
    try:
        m = L.fixture(bundle,0,False,False)
    finally:
        N.Bus = saved
    x = right-143
    L.setup_main(m,x,0,0,5)
    for index,trigger in enumerate(H.MINIMA[:prior]):
        L.spawn(m,trigger)
        assert m.ram[2][0x30c] == (1<<(index+1))-1
    if occupied:
        for slot in range(6-prior):
            actor_x = x+56+16*slot
            fields = dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=actor_x&255,
                          Enemy_PageLoc=actor_x>>8,Enemy_Y_Position=184,Enemy_Y_HighPos=1,
                          Enemy_MovingDir=2,Enemy_BoundBoxCtrl=3)
            for field,value in fields.items():
                m[M.address(bundle,field)+slot] = value
    Sweep.setup(m,x,160,4,0,256,0,0)
    L.camera(m,right)
    N.put(m,SelectedCharacter=owner)
    return m


def qualify(before,after,proof):
    old,new = L.bundles(before,after)
    cases = (
        ('before_offscreen_window',H.MINIMA[0]-1,0,False,0,False),
        ('first_constructor',H.MINIMA[0],0,False,1,True),
        ('second_constructor',H.MINIMA[1],1,False,3,True),
        ('third_full_pool',H.MINIMA[2],2,True,3,False),
        ('third_last_offscreen_pixel',H.MINIMA[2]+7,2,False,7,True),
        ('third_window_closed',H.MINIMA[2]+8,2,False,3,False),
        ('all_seen_third_window',H.MINIMA[2],3,False,7,False),
    )
    lag,regular = Q.lag_pcs(seed(new,H.MINIMA[0],0,False))
    idle,loop,core = (M.address(new,name) for name in ('IdleLoop','GameLoop','GameCoreRoutine'))
    stop = lambda z:(z.pc,z.sp)==(idle+12,252)
    at = lambda tag,lo,hi:(tag,lo,hi)
    worker = int.from_bytes(after[L.CODE+Existing.Helper.CALL-0xa000+1:
                                  L.CODE+Existing.Helper.CALL-0xa000+3],'little')
    ranges = (at(3,worker,worker+64),at(152,0xbbcf,0xbc00),at(152,0xae6e,0xae80),
              at(189,0xb39c,0xb3c3),at(164,0xb6d0,0xb700),at(206,0xbcc7,0xbd00))
    counts,minima,nested = Counter(),[255,255],{}

    def vector(z,kind,collect):
        m = z.memory
        entry,live = (z.pc,z.sp),Q.live(z)
        skipped = N.get(m,'NmiSkipped')
        m.vector_floor,m.written_stack = 0x100+z.sp,set()
        if kind=='lag_FF':
            assert N.get(m,'NmiDisable')==255
            z.nmi()
        else:
            assert not z.p&4
            z.irq()
            assert (Q.tags(z),z.pc)==(254,0x8000)
        hits = 0

        def visit(c):
            nonlocal hits
            minima[1] = min(minima[1],c.sp)
            if kind=='lag_FF':
                assert c.pc!=regular
                hits += c.pc==lag
                key = Q.tags(c),c.pc
                if collect and not c.p&4 and (key not in nested or c.sp<nested[key].sp):
                    nested[key] = fork(c)
                    nested[key].memory.vector_floor = None

        run(z,lambda c:(c.pc,c.sp)==entry,visit)
        m.vector_floor = None
        assert hits==int(kind=='lag_FF') and Q.live(z)==live,(kind,entry)
        assert N.get(m,'NmiSkipped')==(skipped+int(kind=='lag_FF'))&255
        assert not any(0x200<=address<0x304 or address==0x4014 for address,_ in m.writes)

    def pair(z,kind,key=None):
        a,b = fork(z,old),fork(z)
        vector(a,kind,False)
        vector(b,kind,True)
        assert memory(a.memory)==memory(b.memory) and a.processorCycles==b.processorCycles
        assert a.memory.writes==b.memory.writes and a.memory.ram_writes==b.memory.ram_writes
        counts[key or kind] += 1
        return b

    result = {}
    for name,right,prior,occupied,seen,construct in cases:
        m = seed(new,right,prior,occupied)
        c = N.NesMPU(memory=m,pc=idle)
        c.sp,c.p = 255,0x31
        c.stPushWord(0xe33b)
        entries,visited = {},set()
        resumed = []

        def watch(z):
            tag,pc = Q.tags(z),z.pc
            if tag==254 and pc in (loop,core):
                entries[pc] = z.sp
            key = tag,pc,z.sp,z.p&4
            if key in visited or not any(tag==t and lo<=pc<hi for t,lo,hi in ranges):
                return
            visited.add(key)
            minima[0] = min(minima[0],z.sp)
            resumed.append(pair(z,'lag_FF'))
            if not z.p&4:
                resumed.append(pair(z,'IRQ'))

        run(c,stop,watch)
        assert entries=={loop:250,core:248} and m.ram[2][0x30c]==seen,(name,entries,m.ram[2][0x30c])
        assert any(t==3 and p==worker for t,p,*_ in visited),name
        assert any(t==206 and p==0xbcc7 for t,p,*_ in visited)==construct,name
        for cut in resumed:
            run(cut,stop)
            assert Q.final(cut)==Q.final(c),(name,cut.pc)
        result[name] = dict(actual_cuts=len(visited),full_resumptions=len(resumed))

    for cut in nested.values():
        pair(cut,'IRQ','nested_IRQ')
    assert counts['nested_IRQ'] and minima[1]>0x7a
    _,masks = A.exact_cold(before,after,proof['exact_changed_code'])
    cold_approach = A.P.check_full_cpu(before,after,masks)
    return dict(cases=result,cuts=dict(counts),min_foreground_SP=minima[0],min_handler_SP=minima[1],
                actual_FF_PC=lag,GameLoop_SP=250,GameCore_SP=248,whole_GameCore_before_windows=cold_approach)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    path = out/'proof.json'
    proof = json.loads(path.read_text())
    before = H.BASE.read_bytes()
    assert proof['passed'] and proof['strict_offscreen_retry'] and proof['width']==8
    assert M.sha(before)==H.PIN==proof['parent_SHA256'] and not (out/'irq.json').exists()
    for source,digest in proof['bindings'].items():
        assert M.sha(Path(source).read_bytes())==digest,source
    after = install(before,proof['patches'])
    assert M.sha(after)==proof['expected_memory_only_SHA256']
    report = qualify(before,after,proof)
    report.update(passed=True,ROM_written=False,parent_SHA256=H.PIN,memory_image_SHA256=M.sha(after),
                  bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in
                            (Path(__file__),Path(Existing.__file__),Path(Q.__file__),path,R/'src/reset.s')})
    (out/'irq.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    main()
