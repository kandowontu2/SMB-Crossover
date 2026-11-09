"""Run the native Mini injury ingress on the actual GameLoop and vectors."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_helper_injury_1110 as I
import check_mini_lift_admission_async_1108_v1 as Q
import check_mini_lift_seen_fast_irq_1110 as LiftIRQ
from check_mini_funded_actor_1108_v3 import install, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork


H,L,M,N,R = I.H,I.L,I.M,I.N,I.R


def guarded_seed(bundle):
    saved = N.Bus
    N.Bus = LiftIRQ.LiftGuard
    try:
        return L.fixture(bundle,0,False,False)
    finally:
        N.Bus = saved


def start(m,idle):
    N.put(m,SavedJoypadBits=1,SavedJoypad1Bits=1)
    c = N.NesMPU(memory=m,pc=idle)
    c.sp,c.p = 255,0x31
    c.stPushWord(0xe33b)
    return c


def lifecycle(before,after):
    """Reproduce the skipped-window negative and the repair after real injury."""
    worlds = [L.fixture(bundle,0,False,False) for bundle in L.bundles(before,after)]
    rows = []
    for seed in worlds:
        m = I.setup(seed,854,0,seen=0,engine=8)
        for right in H.MINIMA[:2]:
            L.spawn(m,right)
        L.camera(m,854)
        assert m.ram[2][0x30c]==3
        N.put(m,PlayerStatus=1,PlayerSize=0,InjuryTimer=0)
        m.ram[2][0x244]=1
        N.invoke(m,'ForceInjury',x=0,y=0)
        assert N.get(m,'GameEngineSubroutine')==10 and N.get(m,'TimerControl')==255
        injury_status = N.get(m,'PlayerStatus')
        # Treat the native injury call as a completed foreground action.
        # The first real normal NMI must drain any queued VRAM2 packet.
        N.put(m,NmiDisable=0)
        idle = M.address(m.bundle,'IdleLoop')
        first,updates,steps = None,0,[]
        for epoch in range(60):
            old = I.camera_right(m)
            cpu = start(m,idle)
            if N.get(m,'NmiDisable')==0:
                entry = cpu.pc,cpu.sp
                cpu.nmi()
                run(cpu,lambda z:(z.pc,z.sp)==entry)
                assert N.get(m,'NmiDisable')==255
                # The CPU model has no physical controller device. Supply
                # the same held Right at the native polled-input boundary.
                N.put(m,SavedJoypadBits=1,SavedJoypad1Bits=1)
            points = Counter()

            def visit(z):
                tag,pc = Q.tags(z),z.pc
                if (tag,pc) in ((129,I.CONTROL),(152,H.WORKER),(206,0xbcc7),(128,0xa260)):
                    points[tag,pc] += 1
                if (tag,pc)==(206,0xbcc7) and first is None:
                    assert not points[128,0xa260],('birth must precede real enemy loop',epoch)

            run(cpu,lambda z:(z.pc,z.sp)==(idle+12,252),visit)
            right = I.camera_right(m)
            if points[129,I.CONTROL]:
                assert 0<=right-old<=3,(epoch,old,right)
                updates += 1
            if points[206,0xbcc7]:
                assert first is None and m.ram[2][0x30c]==7
                first = dict(epoch=epoch,right=right,relative=H.LEFTS[2]-right+255,
                             slot=m.ram[2][0x30b]-1)
                assert 256<=first['relative']<=263
            steps.append(right)
            if N.get(m,'GameEngineSubroutine')==8:
                break
        assert updates==39 and N.get(m,'GameEngineSubroutine')==8
        assert max(steps)>=H.LEFTS[2]
        rows.append(dict(injury_movement_updates=updates,camera_right_at_resume=steps[-1],birth=first,
                         seen_after_injury=m.ram[2][0x30c],lives=N.get(m,'NumberofLives'),
                         native_status_after_force_injury=injury_status))
    assert rows[0]['birth'] is None and rows[0]['seen_after_injury']==3
    assert rows[1]['birth'] and rows[1]['seen_after_injury']==7
    assert rows[0]['camera_right_at_resume']==rows[1]['camera_right_at_resume']
    assert rows[0]['lives']==rows[1]['lives']
    assert rows[0]['native_status_after_force_injury']==rows[1]['native_status_after_force_injury']
    return dict(strict8_missed_window=rows[0],post_scroll_repair=rows[1])


def vectors(before,after):
    old,new = L.bundles(before,after)
    seed = guarded_seed(new)
    lag,regular = Q.lag_pcs(seed)
    idle,loop,core = (M.address(new,name) for name in ('IdleLoop','GameLoop','GameCoreRoutine'))
    assert bytes(seed[0xe339:0xe33c])==bytes((0x20,idle&255,idle>>8))
    assert bytes(seed[idle+9:idle+12])==bytes((0x20,loop&255,loop>>8))
    stop = lambda z:(z.pc,z.sp)==(idle+12,252)
    counts,minima,nested = Counter(),[255,255],{}
    source_windows = {bytes.fromhex('8d45018d1551'):(1,'CurrentBank'),
                      bytes.fromhex('8da17d8d1651'):(2,'CurrentBankC')}
    ranges = [(bank|128,pc,pc+length) for _,bank,pc,length,_ in I.SPANS]
    ranges += [(212,0xb49f,0xb4ae),(152,H.WORKER,H.END),(152,0xae6e,0xae80),
               (189,0xb39c,0xb3c4),(164,0xb6d0,0xb700),(206,0xbcc7,0xbd00)]

    def vector(z,kind,record):
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
                if record and not c.p&4 and (key not in nested or c.sp<nested[key].sp):
                    nested[key] = fork(c)
                    nested[key].memory.vector_floor = None

        run(z,lambda c:(c.pc,c.sp)==entry,visit)
        m.vector_floor = None
        resumed = Q.live(z)
        if resumed[1]!=live[1]:
            # A real lag handler can commit the just-published shadow before
            # resuming the exact STA bus instruction. The other tags stay exact.
            insn = bytes(m[z.pc-3:z.pc+3])
            assert kind=='lag_FF' and insn in source_windows,(kind,entry,insn.hex(),live[1],resumed[1])
            window,shadow = source_windows[insn]
            assert resumed[1][window]==N.get(m,shadow)==z.a
            assert resumed[1][:window]+resumed[1][window+1:]==live[1][:window]+live[1][window+1:]
            resumed = (resumed[0],live[1],*resumed[2:])
            if record:
                counts[f'pending_{shadow}_commit'] += 1
        assert hits==int(kind=='lag_FF') and resumed==live,(kind,entry)
        assert N.get(m,'NmiSkipped')==(skipped+int(kind=='lag_FF'))&255
        assert not any(0x200<=address<0x304 or address==0x4014 for address,_ in m.writes)

    def pair(z,kind,role=None):
        a,b = fork(z,old),fork(z)
        vector(a,kind,False)
        vector(b,kind,True)
        assert I.memory(a.memory)==I.memory(b.memory) and a.processorCycles==b.processorCycles
        assert a.memory.writes==b.memory.writes and a.memory.ram_writes==b.memory.ram_writes
        counts[role or kind] += 1
        return b

    scenarios = (
        ('before_window',853,41,False,None),
        ('third_birth',855,41,False,None),
        ('third_last_offscreen',862,41,False,None),
        ('full_pool',855,41,True,None),
        ('state_header_reject',855,41,False,(0x1fe1,40)),
        ('foreign_native',855,0,False,None),
    )
    cases = {}
    for name,right,owner,full,poison in scenarios:
        m = I.setup(seed,right,0xf0,owner=owner,seen=3,full=full)
        c = start(m,idle)
        entries,cuts,return_after_scan = {},set(),[]
        active = False

        def watch(z):
            nonlocal active
            tag,pc = Q.tags(z),z.pc
            if tag==254 and pc in (loop,core):
                entries[pc] = z.sp
            if (tag,pc)==(129,I.WRAPPER_RETURN):
                active = True
            if (tag,pc)==(128,0xa260):
                active = False
            if (tag,pc)==(212,0xb3dd) and poison:
                at,val = poison
                z.memory.ram[2][at] = val
            seam = active and (0x15a<=pc<0x17b or tag==254 and 0x80c2<=pc<0x80c9)
            key = tag,pc,z.sp,z.p&4
            if key in cuts or not (seam or any(tag==t and lo<=pc<hi for t,lo,hi in ranges)):
                return
            cuts.add(key)
            minima[0] = min(minima[0],z.sp)
            return_after_scan.append(pair(z,'lag_FF'))
            if not z.p&4:
                return_after_scan.append(pair(z,'IRQ'))

        run(c,stop,watch)
        assert entries=={loop:250,core:248} and cuts,(name,entries)
        expected_birth = name in ('third_birth','third_last_offscreen')
        assert (m.ram[2][0x30c]==7)==expected_birth,(name,I.camera_right(m),m.ram[2][0x30c])
        assert any(tag==212 and pc==0xb3dd for tag,pc,*_ in cuts)==(owner==41)
        for resumed in return_after_scan:
            def restore_poison(z):
                if (Q.tags(z),z.pc)==(212,0xb3dd) and poison:
                    at,val = poison
                    z.memory.ram[2][at] = val
            run(resumed,stop,restore_poison)
            assert Q.final(resumed)==Q.final(c),name
        cases[name] = dict(cuts=len(cuts),full_resumptions=len(return_after_scan))

    for cut in nested.values():
        pair(cut,'IRQ','nested_IRQ')
    assert counts['lag_FF'] and counts['IRQ'] and counts['nested_IRQ'] and minima[1]>0x7a
    return dict(cases=cases,cuts=dict(counts),min_foreground_SP=minima[0],min_handler_SP=minima[1],
                actual_FF_PC=lag,GameLoop_SP=250,GameCore_SP=248)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    path = out/'proof.json'
    proof = json.loads(path.read_text())
    assert proof['passed'] and not (out/'irq.json').exists()
    for source,h in proof['bindings'].items():
        assert M.sha(Path(source).read_bytes())==h,source
    _,before,_ = I.Strict.bound_image()
    after = install(before,proof['patches'])
    assert M.sha(before)==proof['parent_SHA256'] and M.sha(after)==proof['expected_memory_only_SHA256']
    sequence = lifecycle(before,after)
    print(json.dumps(dict(native_injury_sequence=sequence)),flush=True)
    result = vectors(before,after)
    result.update(passed=True,ROM_written=False,parent_SHA256=M.sha(before),memory_image_SHA256=M.sha(after),
                  native_injury_sequence=sequence,bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in
                  (Path(__file__),Path(Q.__file__),path,R/'src/reset.s')})
    (out/'irq.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
