"""Check the paired parser's relocated call and blank-row interrupts in GameLoop."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_parser_paired_shadow_1110 as S
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork


M, N, Q, D, R = S.M,S.N,S.Q,S.D,S.R
P, IRQ, Async = S.P,M.IRQ,S.Async
ENTRY = (130,0xa2e4)


def cpu(seed,column):
    c = Q.Edge.prepare(seed,Q.read_scene(S.PROFILE),False)
    N.put(c.memory,AreaParserTaskNum=4,BlockBufferColumnPos=column,
          VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
    run(c,lambda z:D.bank_pc(z)==ENTRY)
    assert c.memory[0x139]==255 and 0x100+c.sp>=0x17b
    return c


def paired(before,after):
    images = [P.bundle(raw) for raw in (before,after)]
    seeds = M.cold_seeds(before,after)
    lag,regular = M.lag_pcs(seeds[41][1])
    counts,sites,deepest = Counter(),set(),{}
    minimum = [255,255]

    def execute(c,kind,observe=None,protect=True):
        m = c.memory
        m.__class__ = Async.ShadowGuard
        m.pending_dispatch,m.pending_backup = frozenset(),frozenset()
        m.scratch_reads,m.writer_sites = set(),[]
        m.active_x,m.active_y,m.site = c.x,c.y,D.bank_pc(c)
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()

        def inspect(z):
            m.active_x,m.active_y,m.site = z.x,z.y,D.bank_pc(z)
            minimum[1] = min(minimum[1],z.sp)
            if observe:
                observe(z)

        m.guarded = protect
        try:
            return IRQ.interrupt(c,kind,lag,regular,inspect)
        finally:
            m.guarded = False

    def native_cut(c,side,owner,column,kind,record=True):
        args = (side,owner,column,kind,tuple(c.memory.rawtags))
        a,b = fork(c),fork(c,images[1-side])

        def observe(z):
            if kind=='FF' and not z.p&4 and (args not in deepest or z.sp<deepest[args].sp):
                deepest[args] = fork(z)
                deepest[args].memory.guarded = False
                deepest[args].memory.vector_floor = None

        costs = execute(a,kind,observe if record else None),execute(b,kind)
        assert costs[0]==costs[1] and IRQ.hardware(a)==IRQ.hardware(b),(side,owner,column,kind,c.pc)
        assert S.Triple.H.state(a.memory)==S.Triple.H.state(b.memory)
        counts[kind if record else 'nested_IRQ'] += 1

    def tracked(c):
        tag,pc = D.bank_pc(c)
        return (tag==130 and (0xa2e4<=pc<0xa314 or 0xbfee<=pc<0xc000)
                or tag==154 and pc==0xa012)

    for side,owner,column in product((0,1),seeds,(0,31)):
        c = cpu(seeds[owner][side],column)
        seen = set()

        def watch(z):
            key = (*D.bank_pc(z),z.sp)
            if key in seen or not tracked(z):
                return
            seen.add(key)
            sites.add((side,*key[:2]))
            minimum[0] = min(minimum[0],z.sp)
            assert z.memory[0x139]==255
            native_cut(z,side,owner,column,'FF')
            if not z.p&4:
                native_cut(z,side,owner,column,'IRQ')

        run(c,Q.at_end,watch)
        assert seen

    for (side,owner,column,_,_),c in deepest.items():
        native_cut(c,side,owner,column,'IRQ',False)

    def state(c):
        return (registers(c,0xef),live_stack(c),S.Triple.H.state(c.memory))

    # Paired resume uses the real common ingress. Normal NMI runs after the
    # actual end-of-GameLoop publication, with the resulting VRAM pending.
    for owner,column,kind in product(seeds,(0,31),('FF','IRQ','normal')):
        pair = [cpu(seed,column) for seed in seeds[owner]]
        if kind=='normal':
            for c in pair:
                run(c,Q.at_end)
            assert state(pair[0])==state(pair[1])
        costs = [execute(c,kind,protect=kind!='normal') for c in pair]
        assert costs[0]==costs[1] and IRQ.hardware(pair[0])==IRQ.hardware(pair[1])
        if kind!='normal':
            for c in pair:
                run(c,Q.at_end)
        assert state(pair[0])==state(pair[1]),(owner,column,kind)
        counts[f'resume_{kind}'] += 1
    assert all(counts[key] for key in ('FF','IRQ','nested_IRQ','resume_normal'))
    assert min(minimum)>0x7a
    return dict(cuts=dict(counts),reached_sites=sorted(sites),minimum_SP=minimum,
                actual_lag_PC=lag,actual_normal_NMI_PC=regular)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    proof,dest = out/'proof.json',out/'ingress-irq.json'
    assert out.is_relative_to(R/'build') and not dest.exists()
    q = json.loads(proof.read_text())
    before = S.BASE.read_bytes()
    assert q['passed'] and q['parent_SHA256']==P.sha(before)==S.PIN
    for name,digest in q['bindings'].items():
        assert P.sha(Path(name).read_bytes())==digest,name
    after = install(before,q['patches'])
    assert P.sha(after)==q['expected_memory_only_SHA256']
    result = paired(before,after)
    refs = (Path(__file__),Path(S.__file__),Path(Async.__file__),proof,R/'src/reset.s')
    result.update(passed=True,ROM_written=False,parent_SHA256=S.PIN,expected_memory_only_SHA256=P.sha(after),
                  bindings={str(path.resolve()):P.sha(path.read_bytes()) for path in refs})
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(result['expected_memory_only_SHA256'],result['cuts'],flush=True)


if __name__=='__main__':
    main()
