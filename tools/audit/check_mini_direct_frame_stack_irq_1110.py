"""Check the exact native Mini direct frame under actual interrupt vectors."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_direct_frame_stack_1110 as P
import check_mini_lift_admission_async_1108_v1 as Q
import check_mini_sweep_center_irq_1110 as Sweep
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_native_relative_offscreen_irq_1110 import StackGuard


A,L,M,N,R = P.A,P.L,P.M,P.N,P.R


def vectors(before,after):
    bundles = L.bundles(before,after)
    old,new = bundles
    original_bus = N.Bus
    N.Bus = StackGuard
    try:
        seeds = [L.fixture(b,4,False,False) for b in bundles]
    finally:
        N.Bus = original_bus
    lag,normal = Q.lag_pcs(seeds[1])
    idle,loop,core = [M.address(new,n) for n in ('IdleLoop','GameLoop','GameCoreRoutine')]
    assert bytes(seeds[1][0xe339:0xe33c])==bytes((0x20,idle&255,idle>>8))
    assert bytes(seeds[1][idle+9:idle+12])==bytes((0x20,loop&255,loop>>8))
    stop = lambda c:(c.pc,c.sp)==(idle+12,252)
    deepest,counts,sites = {},Counter(),set()
    minima = [255,255]

    def interrupt(cpu,kind,record):
        m = cpu.memory
        entry = cpu.pc,cpu.sp
        maps = tuple(m.rawtags)
        snap = registers(cpu,0xef),live_stack(cpu),bytes(m[0x15a:0x17b])
        skipped = N.get(m,'NmiSkipped')
        m.vector_floor,m.written_stack = 0x100+cpu.sp,set()
        if kind=='IRQ':
            assert not cpu.p&4
            cpu.irq()
            assert (Q.tags(cpu),cpu.pc)==(254,0x8000)
        else:
            assert N.get(m,'NmiDisable')==(255 if kind=='lag_FF' else 0)
            cpu.nmi()
        hits = Counter()

        def watch(z):
            minima[1] = min(minima[1],z.sp)
            assert not (Q.tags(z)==212 and P.ENTRY<=z.pc<P.END)
            if z.pc in (lag,normal):
                hits[z.pc] += 1
            if record and kind!='IRQ' and not z.p&4:
                key = kind,Q.tags(z),z.pc
                if key not in deepest or z.sp<deepest[key].sp:
                    deepest[key] = fork(z)
                    deepest[key].memory.vector_floor = None

        run(cpu,lambda z:(z.pc,z.sp)==entry,watch)
        m.vector_floor = None
        assert snap==(registers(cpu,0xef),live_stack(cpu),bytes(m[0x15a:0x17b])),(kind,entry)
        actual = tuple(m.rawtags)
        if actual!=maps:
            assert kind!='IRQ'
            opcode = bytes(m[cpu.pc-3:cpu.pc+3])
            windows = {bytes.fromhex('8d45018d1551'):(1,'CurrentBank'),
                       bytes.fromhex('8da17d8d1651'):(2,'CurrentBankC')}
            assert opcode in windows,(kind,entry,opcode.hex(),maps,actual)
            window,name = windows[opcode]
            assert maps[window]!=actual[window]==cpu.a==N.get(m,name)
            assert maps[:window]+maps[window+1:]==actual[:window]+actual[window+1:]
            if record:
                counts[f'pending_{name}_bus_commit'] += 1
        assert hits[lag]==int(kind=='lag_FF') and hits[normal]==int(kind=='normal_NMI')
        assert N.get(m,'NmiSkipped')==(skipped+int(kind=='lag_FF'))&255

    def paired(z,kind,nested=False):
        a,b = fork(z),fork(z,old)
        if kind=='normal_NMI':
            for c in (a,b):
                N.put(c.memory,NmiDisable=0)
                c.memory.writes.clear()
        for c,record in ((a,True),(b,False)):
            interrupt(c,kind,record)
        m,n = a.memory,b.memory
        assert P.Q.memory(m)==P.Q.memory(n) and m.writes==n.writes and m.ram_writes==n.ram_writes,(kind,z.pc)
        assert a.processorCycles==b.processorCycles
        counts['nested_IRQ' if nested else kind] += 1
        return a

    def start(seed,p):
        m = slim_fork(seed)
        Sweep.setup(m,695,154,13,3665,8192,1,0)
        N.put(m,AreaMusicQueue=1,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
        c = N.NesMPU(memory=m,pc=idle)
        c.sp,c.p = 255,p
        c.stPushWord(0xe33b)
        return c

    cases = {}
    for mode,flags in (('warm',0x31),('warm_I1',0x35),('ready1',0x31),
                       ('state_owner_fault',0x31),('code_marker_fault',0x31)):
        a,b = [start(seed,flags) for seed in seeds]
        seen,resume,normal_resume,entries = set(),[],[],{}
        ingress = 0

        def perturb(c):
            m = c.memory
            if mode=='ready1':
                m.ram[2][0x300] = 1
            elif mode=='state_owner_fault':
                m.ram[2][0x1fe1] = 40
            elif mode=='code_marker_fault':
                m.ram[3][0x1fe0] = 0xa6

        def old_visit(c):
            if (Q.tags(c),c.pc)==(212,P.ENTRY):
                perturb(c)

        def visit(c):
            nonlocal ingress
            tag,pc = Q.tags(c),c.pc
            if tag==254 and pc in (loop,core):
                entries[pc] = c.sp
            if (tag,pc)==(212,P.ENTRY):
                ingress += 1
                perturb(c)
            mapped = c.memory.rawtags[1]==212
            transport = 0x15a<=pc<0x17b or tag==254 and 0x80c2<=pc<0x80c9
            if not (tag==212 and P.ENTRY<=pc<P.END or mapped and transport):
                return
            key = tag,pc,c.sp,c.p&4,tuple(c.memory.rawtags)
            if key in seen:
                return
            seen.add(key)
            sites.add((tag,pc))
            minima[0] = min(minima[0],c.sp)
            resume.append(paired(c,'lag_FF'))
            if not c.p&4:
                resume.append(paired(c,'IRQ'))
            normal_resume.append(paired(c,'normal_NMI'))

        run(a,stop,old_visit)
        run(b,stop,visit)
        assert entries=={loop:250,core:248} and ingress and seen,(mode,entries,ingress)
        A.P.compare_memory(a.memory,b.memory)
        assert P.Q.memory(a.memory)==P.Q.memory(b.memory) and Q.registers(a)==Q.registers(b)
        for c in resume:
            run(c,stop,old_visit)
            assert Q.final(c)==Q.final(b) and bytes(c.memory[:11])==bytes(b.memory[:11]),mode
        for c in normal_resume:
            run(c,stop,old_visit)
        cases[mode] = dict(sites=len(seen),normal_resumes=len(normal_resume),lag_or_irq_resumes=len(resume),
                           whole_GameLoop_saved=a.processorCycles-b.processorCycles)

    for c in deepest.values():
        paired(c,'IRQ',nested=True)
    assert all(counts[k] for k in ('IRQ','normal_NMI','lag_FF','nested_IRQ','pending_CurrentBankC_bus_commit'))
    assert minima[1]>0x7a and (212,P.ENTRY) in sites
    return dict(cuts=dict(counts),cases=cases,min_foreground_SP=minima[0],min_handler_SP=minima[1],
                actual_FF_PC=lag,actual_normal_NMI_PC=normal)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',required=True,type=Path)
    out = cli.parse_args().output.resolve()
    path = out/'proof.json'
    assert not (out/'irq.json').exists()
    proof = json.loads(path.read_text())
    before = P.BASE.read_bytes()
    assert proof['passed'] and M.sha(before)==P.PIN==proof['parent_SHA256']
    for source,digest in proof['bindings'].items():
        assert M.sha(Path(source).read_bytes())==digest,source
    after = install(before,proof['patches'])
    assert M.sha(after)==proof['expected_memory_only_SHA256']
    result = vectors(before,after)
    result.update(passed=True,parent_SHA256=P.PIN,expected_memory_only_SHA256=M.sha(after),ROM_written=False,
                  bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in
                            (Path(__file__),Path(Q.__file__),path,R/'src/reset.s',R/'src/mmc5.s')})
    (out/'irq.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
