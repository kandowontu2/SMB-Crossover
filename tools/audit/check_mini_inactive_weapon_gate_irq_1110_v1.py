"""Qualify actual vectors at the local Mini weapon router and the native join."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
import check_mini_inactive_weapon_gate_1110_v1 as Gate
import check_mini_lift_admission_async_1108_v1 as Q
from check_mini_shared_offscreen_irq_1110_v1 import STOP, cpu_at, lag_pcs
from check_native_relative_offscreen_irq_1110 import StackGuard


P, N, Match = Gate.P, Gate.N, Gate.Match


def fork(c, bundle=None):
    m = slim_fork(c.memory)
    if bundle is not None:
        m.bundle = bundle
        for window,tag in enumerate(m.rawtags):
            if tag >= 128:
                m.raw_page(window,tag)
    clone = N.NesMPU(memory=m,pc=c.pc)
    clone.a,clone.x,clone.y,clone.p,clone.sp = registers(c)
    return clone


def at_cut(c):
    return Q.tags(c)==128 and (Gate.START <= c.pc < Gate.END or c.pc==Gate.AIR)


def vectors(before, after):
    old,new = [P.bundle(q) for q in (before,after)]
    saved_bus = N.Bus
    N.Bus = StackGuard
    try:
        mini = [Match.cold(b,41)[0] for b in (old,new)]
        mario = [Match.cold(b,0)[0] for b in (old,new)]
    finally:
        N.Bus = saved_bus
    scene = json.loads(Match.WITNESS.read_text())['scene']
    lag,regular = lag_pcs(mini[1])
    counts, sites, nested = Counter(),set(),{}
    minimum = [255,255]

    def inject(c, kind, observe=None):
        snapshot = Q.live(c)
        stop = c.pc,c.sp
        m = c.memory
        skipped = N.get(m,'NmiSkipped')
        m.vector_floor,m.written_stack = 0x100+c.sp,set()
        if kind=='lag_FF':
            assert N.get(m,'NmiDisable')==255
            c.nmi()
        else:
            assert not c.p&4
            c.irq()
            assert (c.pc,Q.tags(c)) == (0x8000,254)
        lag_hits = 0

        def watch(q):
            nonlocal lag_hits
            lag_hits += int(q.pc==lag)
            assert q.pc!=regular and not at_cut(q)
            minimum[1] = min(minimum[1],q.sp)
            if observe is not None:
                observe(q)

        run(c,lambda z:(z.pc,z.sp)==stop,watch)
        m.vector_floor = None
        assert Q.live(c)==snapshot
        assert lag_hits==int(kind=='lag_FF')
        assert N.get(m,'NmiSkipped')==(skipped+int(kind=='lag_FF'))&255

    def check(c, kind, *, nested_IRQ=False):
        effects = []
        for side in (0,1):
            z = fork(c,old if side else None)
            m = z.memory

            def retain(q):
                if side or kind!='lag_FF' or q.p&4:
                    return
                owner = N.get(q.memory,'SelectedCharacter')
                if owner not in nested or q.sp<nested[owner].sp:
                    nested[owner] = fork(q)
                    nested[owner].memory.vector_floor = None

            inject(z,kind,retain)
            effects.append((Gate.semantic(z),m.writes[:],z.processorCycles))
        assert effects[0]==effects[1], (kind,c.pc)
        counts['nested_IRQ' if nested_IRQ else kind] += 1

    def explore(c, stop, role):
        visited = set()

        def visit(z):
            if not at_cut(z) or (z.pc,z.sp,z.p&4) in visited:
                return
            visited.add((z.pc,z.sp,z.p&4))
            sites.add(z.pc)
            minimum[0] = min(minimum[0],z.sp)
            check(z,'lag_FF')
            if not z.p&4:
                check(z,'IRQ')

        run(c,stop,visit)
        assert visited
        counts[role] += 1

    # Confirm each raw dispatch class at the changed router. Stop at the
    # existing downstream map for synthetic foreign owners.
    for owner in range(42):
        m = slim_fork(mario[1])
        N.put(m, SelectedCharacter=owner, GuestAudioCharacter=owner, NmiDisable=255,
              PlayerStatus=2)
        c = Gate.root_cpu(m,Gate.START)
        explore(c,lambda z:z.pc in (0x15a,Gate.END),'router_entries')

    # Real linked GameLoop, owner cold data, three Goombas and three lifts.
    # Both the direct no-shot path and retained active route execute.
    for power in (0,2):
        m = Match.arena(slim_fork(mini[1]),scene,True)
        N.put(m,PlayerStatus=power)
        Match.controls(m,0)
        c = cpu_at(m,P.address(new,'GameLoop'),252,0x21,x=0,y=0)
        explore(c,lambda z:(z.pc,z.sp)==(STOP,252),'GameLoop_entries')

    # The omitted farcall packet is only live inside the transport. Interrupt
    # the old and new executions at matching logical cuts and resume the full
    # update, comparing all application/PPU state and ordered hardware I/O.
    resumes = []
    for pc, kind in product((Gate.START,Gate.AIR),('lag_FF','IRQ')):
        pair = []
        for seed in mini:
            m = Match.arena(slim_fork(seed),scene,True)
            m.writes.clear()
            m.ram_writes.clear()
            m.ppu_log.clear()
            Match.controls(m,0)
            c = cpu_at(m,P.address(m.bundle,'GameLoop'),252,0x21,x=0,y=0)
            used = False

            def visit(z):
                nonlocal used
                if not used and z.pc==pc and Q.tags(z)==128:
                    inject(z,kind)
                    used = True

            run(c,lambda z:(z.pc,z.sp)==(STOP,252),visit)
            assert used,(pc,kind)
            pair.append((Gate.semantic(c),bytes(m[0x15a:0x17b])))
        assert pair[0]==pair[1],(pc,kind)
        resumes.append(dict(PC=pc,kind=kind,full_GameLoop=True,final_SMC_exact=True))

    for c in nested.values():
        check(c,'IRQ',nested_IRQ=True)
    assert set(nested)==set(range(42)) and min(minimum)>0x7a
    return dict(cuts=dict(counts), actual_FF_PC=lag, forbidden_regular_PC=regular,
                minimum_SP=minimum, changed_sites=sorted(sites), paired_resumes=resumes)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    path = args.output/'proof.json'
    q = json.loads(path.read_text())
    assert q['passed']
    raw = Match.ROM.read_bytes()
    after = install(raw,q['patches'])
    assert P.sha(raw)==q['parent_SHA256'] and P.sha(after)==q['expected_memory_only_SHA256']
    for name,h in q['bindings'].items():
        assert P.sha(Path(name).read_bytes())==h,name
    result = vectors(raw,after)
    result.update(passed=True,ROM_written=False,parent_SHA256=P.sha(raw),
                  expected_memory_only_SHA256=P.sha(after),
                  bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),path,Path(Gate.__file__),
                             Match.ROM,Gate.R/'src/reset.s')})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['cuts'],result['minimum_SP'],result['paired_resumes'],flush=True)


if __name__ == '__main__':
    main()
