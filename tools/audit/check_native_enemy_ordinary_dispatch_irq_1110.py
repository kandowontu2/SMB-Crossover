"""Check real interrupts through the ordinary enemy dispatch's scratch lifetime."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_native_enemy_ordinary_dispatch_1110 as Q
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import lag_pcs


N, P, D, R = Q.N,Q.P,Q.D,Q.R


def hardware(c):
    m = c.memory
    # IRQ/NMI push the currently different incoming A/Y on their own stack.
    # The live caller stack and reserved instruction bytes are checked below.
    writes = tuple((a,v) for a,v in m.writes if not 0x100<=a<0x200 or 0x15a<=a<0x17b)
    return (writes,tuple(m.ram_writes),tuple(m.ppu_log),tuple(m.rawtags),
            tuple(m.chr_latches),bytes(m.vram),m.ppu_addr,m.ppuctrl)


def interrupt(c, kind, lag, normal, observe=None):
    m = c.memory
    target = c.pc,c.sp
    pending = m.pending_dispatch
    snapshot = (registers(c,0xef),live_stack(c),tuple(m.rawtags),bytes(m[D.SMC]),Q.raw_zp(c)[7:11])
    skipped = N.get(m,'NmiSkipped')
    m.vector_floor,m.written_stack = 0x100+c.sp,set()
    if kind=='IRQ':
        assert not c.p&4
        c.irq()
        assert D.bank_pc(c)==(254,0x8000)
    else:
        assert N.get(m,'NmiDisable')==(255 if kind=='FF' else 0)
        c.nmi()
    hits = Counter()

    def visit(q):
        m.dispatch_site = D.bank_pc(q)
        if q.pc in (lag,normal):
            hits[q.pc] += 1
        if observe:
            observe(q)

    start = c.processorCycles
    run(c,lambda q:(q.pc,q.sp)==target,visit)
    m.vector_floor = None
    m.pending_dispatch = pending
    actual = (registers(c,0xef),live_stack(c),tuple(m.rawtags),bytes(m[D.SMC]),Q.raw_zp(c)[7:11])
    assert actual[:2]+actual[3:] == snapshot[:2]+snapshot[3:], (kind,target,snapshot,actual)
    if actual[2]!=snapshot[2]:
        # NMI may legally commit a just-written mapper shadow before the
        # foreground STA to the physical port. The old and new bus traces
        # still have to match. Accept only the two actual store pairs.
        stores = {bytes.fromhex('8d45018d1551'):(1,'CurrentBank'),
                  bytes.fromhex('8da17d8d1651'):(2,'CurrentBankC')}
        opcodes = bytes(m[c.pc-3:c.pc+3])
        assert kind!='IRQ' and opcodes in stores, (kind,target,snapshot,actual)
        bank,name = stores[opcodes]
        expected = list(snapshot[2])
        expected[bank] = N.get(m,name)
        assert tuple(expected)==actual[2] and actual[2][bank]==c.a
    assert hits[lag]==int(kind=='FF') and hits[normal]==int(kind=='normal')
    assert N.get(m,'NmiSkipped')==(skipped+int(kind=='FF'))&255
    return c.processorCycles-start


def vectors(before,after):
    seeds = Q.cold([P.bundle(q) for q in (before,after)])
    lag,normal = lag_pcs(seeds[41][1])
    counts, deepest, sites = Counter(),{},set()
    minima = [255,255]
    native = Q.read_scene(Q.LATE)
    peak = Q.read_scene(Q.Edge.E.PEAK)

    def pair(c,d,kind,role,record=True):
        a,b = fork(c),fork(d)
        for z in (a,b):
            if kind=='normal':
                N.put(z.memory,NmiDisable=0)
            z.memory.writes.clear()
            z.memory.ram_writes.clear()
            z.memory.ppu_log.clear()

        def watcher(z):
            minima[1] = min(minima[1],z.sp)
            key = role,tuple(z.memory.rawtags)
            if record and kind!='IRQ' and not z.p&4 and (key not in deepest or z.sp<deepest[key][1].sp):
                # The old/optimized lag handler executes the same instruction
                # stream. Save an actual pair below after its equal-depth cut.
                candidates[key] = min(candidates.get(key,z.sp),z.sp)

        candidates = {}
        x = interrupt(a,kind,lag,normal)
        y = interrupt(b,kind,lag,normal,watcher)
        ha,hb = hardware(a),hardware(b)
        assert ha==hb and x==y,(kind,role,N.get(b.memory,'SelectedCharacter'),D.bank_pc(c),x,y,
                                [i for i,(u,v) in enumerate(zip(ha,hb,strict=True)) if u!=v],
                                [(u,v) for u,v in zip(ha[0],hb[0]) if u!=v][:8])
        counts[role,kind]+=1

        if candidates:
            a0,b0 = fork(c),fork(d)
            if kind=='normal':
                for z in (a0,b0):
                    N.put(z.memory,NmiDisable=0)
            for z in (a0,b0):
                z.nmi()
            for _ in range(20000):
                assert D.bank_pc(a0)==D.bank_pc(b0) and a0.sp==b0.sp
                key = role,tuple(b0.memory.rawtags)
                if candidates.get(key)==b0.sp and not b0.p&4:
                    deepest[key] = fork(a0),fork(b0)
                    del candidates[key]
                    if not candidates:
                        break
                a0.step()
                b0.step()
            assert not candidates, (role,candidates)
        return a,b

    resumes = []
    for owner,role,scene in (*((n,'ordinary',native) for n in Q.OWNERS),
                             (25,'carried',peak),(2,'frozen',peak),(41,'near_edges',peak)):
        frames = [Q.Edge.prepare(seed,scene,role=='carried') for seed in seeds[owner]]
        if role=='frozen':
            for c in frames:
                N.put(c.memory,AvStopwatch=4)
        if role=='near_edges':
            for c in frames:
                for slot,relative in enumerate((-13,248,255)):
                    x = scene['camera_left']+relative
                    Q.Edge.M.place(c.memory,'Enemy_X_Position',slot,x&255)
                    Q.Edge.M.place(c.memory,'Enemy_PageLoc',slot,x>>8)
        seen = set()
        checks = {}

        def visit(c,d):
            site = D.bank_pc(c)
            mark = site,c.sp,c.p&4,d.memory.pending_dispatch
            if mark in seen:
                return
            seen.add(mark)
            sites.add(site)
            minima[0] = min(minima[0],c.sp)
            pair(c,d,'FF',role)
            if not c.p&4:
                pair(c,d,'IRQ',role)
            if site==(128,Q.NORMAL):
                checks.setdefault('FF',(fork(c),fork(d)))
                checks.setdefault('normal',(fork(c),fork(d)))

        Q.through_frame(*frames,visit)
        assert seen and checks, (owner,role)
        for kind, (a,b) in checks.items():
            a,b = pair(a,b,kind,role)
            # Restart the matched ordinary prefix with its real live packet.
            for z in (a,b):
                z.memory.pending_dispatch = frozenset()
            Q.through_frame(a,b)
            resumes.append([owner,role,kind])

    for (role,_),(a,b) in list(deepest.items()):
        pair(a,b,'IRQ','nested_'+role,False)
    assert all(any(k==kind for _,k in counts) for kind in ('FF','IRQ','normal'))
    assert deepest and minima[1]>0x7a
    return dict(cuts=[[role,kind,count] for (role,kind),count in sorted(counts.items())],
                measured_sites=sorted(sites),minimum_SP=minima,paired_GameLoop_resumes=resumes,
                actual_lag_PC=lag,actual_normal_PC=normal)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    path = args.output/'proof.json'
    proof = json.loads(path.read_text())
    before = Q.BASE.read_bytes()
    assert proof['passed'] and proof['parent_SHA256']==P.sha(before)==Q.PIN
    for name,digest in proof['bindings'].items():
        assert P.sha(Path(name).read_bytes())==digest,name
    after = install(before,proof['patches'])
    assert P.sha(after)==proof['expected_memory_only_SHA256']
    report = vectors(before,after)
    inputs = (Path(__file__),path,R/'src/reset.s',R/'src/game.s',R/'src/smb2_roster_main_v2.s')
    report.update(passed=True,parent_SHA256=Q.PIN,expected_memory_only_SHA256=P.sha(after),
                  ROM_written=False,bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in inputs})
    (args.output/'irq.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['cuts'],report['minimum_SP'],flush=True)


if __name__ == '__main__':
    main()
