"""Verify the live R0 scroll handoff under real IRQ and lag-NMI vectors."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_lift_admission_async_1108_v1 as Q
import check_native_post_scroll_offscreen_1110 as T
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import lag_pcs, memory
from check_native_relative_offscreen_irq_1110 import StackGuard


P,N,R = T.P,T.N,T.R


def vectors(before,after):
    old,new = [P.bundle(im) for im in (before,after)]
    previous = N.Bus
    N.Bus = StackGuard
    try:
        generic = N.fresh(new)
        gameplay = [P.fixture(new,n,False,n==6) for n in (0,6)]
    finally:
        N.Bus = previous
    lag,regular = lag_pcs(generic)
    idle,loop,core = [P.address(new,name) for name in ('IdleLoop','GameLoop','GameCoreRoutine')]
    assert bytes(generic[0xe339:0xe33c])==bytes((0x20,idle&255,idle>>8))
    assert bytes(generic[idle+9:idle+12])==bytes((0x20,loop&255,loop>>8))
    sites,counts,deepest = set(),Counter(),{}
    minima = [255,255]
    reached_scroll_sp = set()

    def clone(c,baseline=False):
        m = slim_fork(c.memory)
        if baseline:
            m.bundle = old
            for i in (0,1):
                m.raw_page(i,m.rawtags[i])
        z = N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp = registers(c)
        return z

    def interrupt(c,kind):
        parent = Q.live(c)
        scratch = bytes(c.memory[:11])
        entry = c.pc,c.sp
        states = []
        for base in (False,True):
            z = clone(c,base)
            m = z.memory
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

            def inspect(q):
                nonlocal hits
                minima[1] = min(minima[1],q.sp)
                if kind!='lag_FF':
                    return
                assert q.pc!=regular
                hits += q.pc==lag
                if not base and not q.p&4:
                    key = Q.tags(q),q.pc
                    if key not in deepest or q.sp<deepest[key].sp:
                        deepest[key] = clone(q)
                        deepest[key].memory.vector_floor = None

            run(z,lambda q:(q.pc,q.sp)==entry,inspect)
            m.vector_floor = None
            actual = Q.live(z)
            changes = [i for i,(a,b) in enumerate(zip(parent,actual,strict=True)) if a!=b]
            if changes:
                # The existing lag audio epilogue can finish an A-map
                # shadow write one instruction early. The exact pending
                # bus store still executes on resumed foreground.
                assert kind=='lag_FF' and changes==[1],(kind,entry,changes)
                assert bytes(c.memory[c.pc-3:c.pc+3])==bytes.fromhex('8d45018d1551')
                assert parent[1][1]!=parent[2]==actual[1][1]==c.a
                assert parent[1][:1]+parent[1][2:]==actual[1][:1]+actual[1][2:]
                if not base:
                    counts['same_pending_A_commit'] += 1
            assert hits==int(kind=='lag_FF') and bytes(m[:11])==scratch,(kind,entry)
            assert N.get(m,'NmiSkipped')==(skipped+int(kind=='lag_FF'))&255
            assert not any(0x200<=at<0x304 or at==0x4014 for at,_ in m.writes)
            states.append((z,memory(m),tuple(m.writes),tuple(m.ram_writes)))
        assert states[0][1:]==states[1][1:],(kind,entry)
        counts[kind] += 1
        return states[0][0]

    def exercise(name,c,stop,whole):
        seen,resume,entries = set(),[],{}
        active = False

        def visit(z):
            nonlocal active
            tag,pc = Q.tags(z),z.pc
            if (tag,pc)==(129,0xa13c):
                active = True
                if whole:
                    reached_scroll_sp.add(z.sp)
            if (tag,pc)==(129,0xa142):
                active = False
            if tag==254 and pc in (loop,core):
                entries[pc] = z.sp
            after_publish = active and (tag==129 and (0xaa41<=pc<0xaa74 or pc==0xa13f) or
                                       0x15a<=pc<0x17b or tag==254 and 0x8ace<=pc<0x8b1a)
            private = tag==254 and 0x8b73<=pc<0x8bdb
            if not (after_publish or private):
                return
            key = tag,pc,z.sp,z.p&4,tuple(z.memory.rawtags)
            if key in seen:
                return
            seen.add(key)
            sites.add((tag,pc))
            minima[0] = min(minima[0],z.sp)
            resume.append(interrupt(z,'lag_FF'))
            if not z.p&4:
                resume.append(interrupt(z,'IRQ'))

        run(c,stop,visit)
        assert seen and any(tag==129 and pc==0xa13f for tag,pc,*_ in seen),name
        if whole:
            assert entries=={loop:250,core:248},entries

        def final(z):
            return Q.final(z),bytes(z.memory[:11]),bytes(z.memory[0x500:0x6c0])

        expected = final(c)
        for z in resume:
            run(z,stop)
            assert final(z)==expected,(name,'resumed path',hex(z.pc))
        counts['resumed'] += len(resume)

    for index,seed in enumerate(gameplay):
        m = slim_fork(seed)
        N.put(m,SavedJoypadBits=193,SavedJoypad1Bits=193,NmiDisable=255,VRAM_Buffer1_Offset=0)
        c = N.NesMPU(memory=m,pc=idle)
        c.sp,c.p = 255,0x31 if index==0 else 0x35
        c.stPushWord(0xe33b)
        exercise(f'GameLoop_{index}',c,lambda z:(z.pc,z.sp)==(idle+12,252),True)
    sp, = reached_scroll_sp

    # Real bridge/native producer at the measured PlayerCtrl stack depth.
    # The title/scene and all other public users retain the general leaf.
    for owner in range(42):
        m = slim_fork(generic)
        m.raw_page(1,129)
        N.put(m,CurrentBank=129,SelectedCharacter=owner,OperMode=1,OperMode_Task=3,
              NmiDisable=255,GameEngineSubroutine=8,DisableScreenFlag=0,Mirror_PPUMASK=30,
              ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,
              Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=164,Player_Y_HighPos=1,
              Player_X_Scroll=1,Player_Pos_ForScroll=112)
        c = N.NesMPU(memory=m,pc=0xa13c)
        c.sp,c.a,c.x,c.y,c.p = sp,0x42,0x14,0x76,0x31
        exercise(f'owner_{owner}',c,lambda z:(z.pc,z.sp)==(0xa142,sp),False)

    for cut in deepest.values():
        interrupt(cut,'nested_IRQ')
    assert all(counts[k] for k in ('IRQ','lag_FF','nested_IRQ','resumed'))
    assert (129,0xaa44) in sites and (254,0x8b73) in sites and minima[1]>0x7a
    return dict(cuts=dict(counts),actual_FF_PC=lag,minimum_foreground_SP=minima[0],
                minimum_ISR_SP=minima[1],actual_GameLoop_SP=250,actual_GameCore_SP=248,
                exact_PlayerCtrl_scroll_SP=sp,observed_sites=len(sites),raw_owners=42)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert not (out/'irq.json').exists()
    path = out/'proof.json'
    proof = json.loads(path.read_text())
    before = T.BASE.read_bytes()
    assert proof['passed'] and P.sha(before)==T.PIN==proof['parent_SHA256']
    for name,digest in proof['bindings'].items():
        assert P.sha((R/name).read_bytes())==digest,name
    after = install(before,proof['patches'])
    assert P.sha(after)==proof['expected_memory_only_SHA256']
    result = vectors(before,after)
    receipt = result|dict(passed=True,ROM_written=False,parent_SHA256=T.PIN,
                          expected_memory_only_SHA256=P.sha(after),
                          bindings={p.resolve().relative_to(R).as_posix():P.sha(p.read_bytes())
                                    for p in (Path(__file__),path,Path(Q.__file__),R/'src/reset.s')})
    (out/'irq.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
