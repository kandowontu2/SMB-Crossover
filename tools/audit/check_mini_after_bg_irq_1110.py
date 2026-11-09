"""Rebind actual post-terrain IRQ, normal NMI, and FF-lag continuations."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_after_bg_1110 as P
import check_mini_lift_admission_async_1108_v1 as Q
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_native_relative_offscreen_irq_1110 import StackGuard


M,N,R = P.M,P.N,P.R
OPERANDS = (0x162,0x16a,0x16c,0x16d,0x179)


def vectors(before,after):
    old,new = P.L.bundles(before,after)
    saved = N.Bus
    N.Bus = StackGuard
    try:
        generic = N.fresh(new)
        mini = P.L.fixture(new,4,False,False)
        authenticated = {owner:P.cold_owner(new,owner,alt) for owner,alt in ((10,0x40),(34,1))}
    finally:
        N.Bus = saved
    lag,regular = Q.lag_pcs(mini)
    idle,loop,core = [M.address(new,n) for n in ('IdleLoop','GameLoop','GameCoreRoutine')]
    assert bytes(mini[0xe339:0xe33c])==bytes((0x20,idle&255,idle>>8))
    assert bytes(mini[idle+9:idle+12])==bytes((0x20,loop&255,loop>>8))
    backup = M.address(new,'RdsSmcBackup')
    assert backup==0x7278
    counts,deepest,sites = Counter(),{},set()
    minima = [255,255]

    def vector(cpu,kind,record):
        bus = cpu.memory
        at = cpu.pc,cpu.sp
        tags = tuple(bus.rawtags)
        caller = registers(cpu,0xef),live_stack(cpu),bytes(bus[0x15a:0x17b])
        operand_values = tuple(bus[a] for a in OPERANDS)
        skipped = N.get(bus,'NmiSkipped')
        bus.vector_floor,bus.written_stack = 0x100+cpu.sp,set()
        if kind=='IRQ':
            assert not cpu.p&4
            cpu.irq()
            assert (Q.tags(cpu),cpu.pc)==(254,0x8000)
        else:
            assert N.get(bus,'NmiDisable')==(255 if kind=='lag_FF' else 0)
            cpu.nmi()
        hits = Counter()

        def watch(z):
            minima[1] = min(minima[1],z.sp)
            if z.pc in (lag,regular):
                hits[z.pc] += 1
            if record and kind!='IRQ' and not z.p&4:
                key = kind,N.get(bus,'SelectedCharacter')
                if key not in deepest or z.sp<deepest[key].sp:
                    deepest[key] = fork(z)
                    deepest[key].memory.vector_floor = None

        run(cpu,lambda z:(z.pc,z.sp)==at,watch)
        bus.vector_floor = None
        assert caller==(registers(cpu,0xef),live_stack(cpu),bytes(bus[0x15a:0x17b])),(kind,at)
        actual = tuple(bus.rawtags)
        if actual!=tags:
            assert actual[:1]+actual[2:]==tags[:1]+tags[2:]
            assert kind!='IRQ' and bytes(bus[at[0]-3:at[0]+3])==bytes.fromhex('8d45018d1551')
            assert tags[1]!=actual[1]==cpu.a==N.get(bus,'CurrentBank')
            if record:
                counts['pending_A_map_completion'] += 1
        assert hits[lag]==int(kind=='lag_FF') and hits[regular]==int(kind=='normal_NMI'),(kind,at,hits)
        assert N.get(bus,'NmiSkipped')==(skipped+int(kind=='lag_FF'))&255
        published = [(addr,value) for addr,value in bus.writes if backup<=addr<backup+len(OPERANDS)]
        if published:
            assert published==list(enumerate(operand_values,backup)),(kind,at,published,operand_values)
            if record:
                counts['exact_RdsSmcBackup_publication'] += 1

    def inject(c,kind):
        pair = fork(c),fork(c,old)
        if kind=='normal_NMI':
            for z in pair:
                N.put(z.memory,NmiDisable=0)
                z.memory.writes.clear()
        for index,z in enumerate(pair):
            vector(z,kind,index==0)
        a,b = [z.memory for z in pair]
        assert P.memory(a)==P.memory(b) and a.writes==b.writes and a.ram_writes==b.ram_writes,(kind,c.pc)
        assert pair[0].processorCycles==pair[1].processorCycles
        counts[kind] += 1
        return pair[0]

    def exercise(c,stop,whole=False,full=False):
        seen,resume,entries = set(),[],{}
        active = False
        bridge = 0xe5cc
        def visit(z):
            nonlocal active
            tag,pc = Q.tags(z),z.pc
            if tag==254 and pc in (loop,core):
                entries[pc] = z.sp
            if (tag,pc)==(129,P.CALL):
                active = True
            if (tag,pc)==(129,P.RETURN):
                active = False
            native = tag==194 and (P.ENTRY<=pc<0xb48a or P.HELPER<=pc<0xb4a4)
            transport = 0x15a<=pc<0x17b or tag==255 and bridge<=pc<0xe5f8
            if not active or not (native or full and transport):
                return
            key = tag,pc,z.sp,z.p&4,tuple(z.memory.rawtags)
            if key in seen or not full and pc!=P.ENTRY:
                return
            seen.add(key)
            sites.add((tag,pc))
            minima[0] = min(minima[0],z.sp)
            resume.append(inject(z,'lag_FF'))
            if not z.p&4:
                resume.append(inject(z,'IRQ'))
            if full:
                normal = inject(z,'normal_NMI')
                run(normal,stop)
                counts['normal_NMI_resumed'] += 1

        run(c,stop,visit)
        owner = N.get(c.memory,'SelectedCharacter')
        assert seen and any(tag==194 and pc==P.ENTRY for tag,pc,*_ in seen)==(owner!=3),owner
        if whole:
            assert entries=={loop:250,core:248},entries
        expected = Q.final(c),bytes(c.memory[:11])
        for z in resume:
            run(z,stop)
            assert (Q.final(z),bytes(z.memory[:11]))==expected,hex(c.pc)
        counts['IRQ_or_FF_resumed'] += len(resume)

    for version in (0,1):
        bus = slim_fork(mini)
        N.put(bus,CrossoverBehaviorVersion=version,NmiDisable=255,AreaMusicQueue=1,
              VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
        c = N.NesMPU(memory=bus,pc=idle)
        c.sp,c.p = 255,0x31 if version==0 else 0x35
        c.stPushWord(0xe33b)
        exercise(c,lambda z:(z.pc,z.sp)==(idle+12,252),whole=True,full=True)
    for owner in range(42):
        seed = authenticated.get(owner,mini if owner==41 else generic)
        bus = slim_fork(seed)
        N.put(bus,SelectedCharacter=owner,NmiDisable=255,OperMode=1,OperMode_Task=3,
              GameEngineSubroutine=8,DisableScreenFlag=0,Mirror_PPUMASK=30,
              VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
        c = P.cpu_at(bus,0x93,3,151,0x61)
        exercise(c,P.stop,full=owner in (0,3,9,10,34))

    for cut in deepest.values():
        inject(cut,'IRQ')
        counts['nested_IRQ'] += 1
    assert minima[1]>0x7a and (194,P.HELPER) in sites and (-1,0x15d) in sites
    assert all(counts[k] for k in ('normal_NMI','lag_FF','IRQ','nested_IRQ','pending_A_map_completion'))
    return dict(cuts=dict(counts),reached_sites=len(sites),raw_owners=42,min_foreground_SP=minima[0],
                min_handler_SP=minima[1],actual_FF_PC=lag,actual_normal_NMI_PC=regular)


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
    result.update(passed=True,parent_SHA256=P.PIN,ROM_written=False,expected_memory_only_SHA256=M.sha(after),
                  bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in
                            (Path(__file__),Path(Q.__file__),path,R/'src/reset.s',
                             R/'src/rogue_dawn_audio_scheduler_hooks_v5.s')})
    (out/'irq.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
