"""Check real IRQ, normal NMI, and FF lag-NMI at the native contact boundary."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_native_contact_1110 as P
import check_mini_lift_admission_async_1108_v1 as Q
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_native_relative_offscreen_irq_1110 import StackGuard


L,M,N,R = P.L,P.M,P.N,P.R


def scene(bundle,owner,alt):
    m = N.fresh(bundle)
    N.put(m,SelectedCharacter=owner,FmAlts=alt,OperMode=1,FamilyMainCommit=1,
          DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,NumberofLives=2)
    N.invoke(m,'InitScreen')
    N.put(m,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,GamePauseStatus=0,
          DisableScreenFlag=0,Mirror_PPUMASK=30)
    if owner==39:
        assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(m.ram[3][0x1fe0:0x1ff0])
        assert m.ram[2][0x1fe0:0x1fe2]==bytes((167,39))
        assert m.ram[3][0x6f]==0x4c
    return m


def vectors(before,after):
    images = L.bundles(before,after)
    old,new = images
    bus_type = N.Bus
    N.Bus = StackGuard
    try:
        generic = [N.fresh(b) for b in images]
        mini = [L.fixture(b,0,False,False) for b in images]
        owned = {(raw,alt):[scene(b,raw,alt) for b in images] for raw,alt in ((25,0),(39,0),(39,16))}
    finally:
        N.Bus = bus_type
    lag,normal = Q.lag_pcs(mini[1])
    counts,deepest,sites = Counter(),{},set()
    minima = [255,255]

    def interrupt(c,kind,record):
        m = c.memory
        entry = c.pc,c.sp
        maps = tuple(m.rawtags)
        snap = registers(c,0xef),live_stack(c),bytes(m[0x15a:0x17b])
        skipped = N.get(m,'NmiSkipped')
        m.vector_floor,m.written_stack = 0x100+c.sp,set()
        if kind=='IRQ':
            assert not c.p&4
            c.irq()
            assert (Q.tags(c),c.pc)==(254,0x8000)
        else:
            assert N.get(m,'NmiDisable')==(255 if kind=='lag_FF' else 0)
            c.nmi()
        hits = Counter()

        def watch(z):
            minima[1] = min(minima[1],z.sp)
            if z.pc in (lag,normal):
                hits[z.pc] += 1
            # Keep the deepest actual context for each owner and mapping
            # shape. A full Bus clone per audio opcode would be wasteful.
            key = kind,N.get(m,'SelectedCharacter'),m.rawtags[1]==202,m.rawtags[2]==2
            if record and kind!='IRQ' and not z.p&4 and (key not in deepest or z.sp<deepest[key].sp):
                deepest[key] = fork(z)
                deepest[key].memory.vector_floor = None

        run(c,lambda z:(z.pc,z.sp)==entry,watch)
        m.vector_floor = None
        assert snap==(registers(c,0xef),live_stack(c),bytes(m[0x15a:0x17b])),(kind,entry)
        actual = tuple(m.rawtags)
        if actual!=maps:
            opcode = bytes(m[c.pc-3:c.pc+3])
            ports = {bytes.fromhex('8d45018d1551'):(1,'CurrentBank'),
                     bytes.fromhex('8da17d8d1651'):(2,'CurrentBankC')}
            assert kind!='IRQ' and opcode in ports,(kind,entry,opcode.hex(),maps,actual)
            window,name = ports[opcode]
            assert maps[window]!=actual[window]==c.a==N.get(m,name)
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
        assert P.Link.Q.memory(m)==P.Link.Q.memory(n) and m.writes==n.writes and m.ram_writes==n.ram_writes
        assert a.processorCycles==b.processorCycles
        counts['nested_IRQ' if nested else kind] += 1
        return a

    def cpu(seed,owner,version,flags,whole,poison):
        c = P.setup(seed,owner,6,8,version,flags,pc=P.ENEMY if whole else P.BRIDGE)
        m = c.memory
        N.put(m,NmiDisable=255,OperMode=1,OperMode_Task=3,Mirror_PPUMASK=30,
              DisableScreenFlag=0,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
        if poison:
            m.ram[poison][0x1fe1] ^= 1
        return c

    stop = lambda c:(c.pc,c.sp)==(0x5b00,236)
    cases = {}
    def exercise(name,seeds,owner,version,flags,*,whole=False,poison=None,every=False):
        a,b = [cpu(seed,owner,version,flags,whole,poison) for seed in seeds]
        old_hits = P.execute(a)
        seen,resume,normal_resume = set(),[],[]
        def visit(c):
            pc,tag = c.pc,Q.tags(c)
            gate = tag==202 and (0xbf00<=pc<0xbf34 or P.HELPER<=pc<0xb180)
            transport = c.memory.rawtags[1]==202 and 0x15a<=pc<0x17b
            if not (gate or transport) or not every and (tag,pc)!=(202,P.GATE):
                return
            key = tag,pc,c.sp,c.p&4
            if key in seen:
                return
            seen.add(key)
            sites.add((tag,pc))
            minima[0] = min(minima[0],c.sp)
            resume.append(paired(c,'lag_FF'))
            if not c.p&4:
                resume.append(paired(c,'IRQ'))
            if every:
                normal_resume.append(paired(c,'normal_NMI'))

        new_hits = Counter()
        def observe(c):
            if (Q.tags(c),c.pc) in ((202,P.HOT),(246,0xbb15),(193,0xb029),(3,0xa06f)):
                new_hits[Q.tags(c),c.pc] += 1
            visit(c)
        run(b,stop,observe)
        assert seen and P.compare(a,b,(old_hits,(new_hits,{})))==(owner==41)
        if owner==25:
            assert new_hits[246,0xbb15]==1
        if owner==39 and every:
            assert new_hits[193,0xb029]==1
            assert new_hits[3,0xa06f]==int(poison is None)
        for c in resume:
            run(c,stop)
            assert Q.final(c)==Q.final(b) and bytes(c.memory[:11])==bytes(b.memory[:11]),name
        for c in normal_resume:
            run(c,stop)
        cases[name] = dict(sites=len(seen),normal_resumes=len(normal_resume),lag_or_irq_resumes=len(resume),
                           cycles_saved=a.processorCycles-b.processorCycles)

    exercise('Mini_easy_native_enemy',mini,41,0,0x31,whole=True,every=True)
    exercise('Mini_hard_native_enemy',mini,41,1,0x35,whole=True,every=True)
    exercise('Kirby',generic,13,1,0x31,every=True)
    exercise('SMB2_body',owned[25,0],25,1,0x31,every=True)
    for alt in (0,16):
        for poison in (None,2,3):
            exercise(f'BubBob_{alt}_{poison}',owned[39,alt],39,1,0x31,poison=poison,every=True)
    for owner in sorted(set(range(42))-{13,25,39,41}):
        exercise(f'owner_{owner}',generic,owner,1,0x31)
    for c in deepest.values():
        paired(c,'IRQ',nested=True)
    assert all(counts[k] for k in ('IRQ','lag_FF','normal_NMI','nested_IRQ'))
    assert minima[1]>0x7a and (202,P.HOT) in sites
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
