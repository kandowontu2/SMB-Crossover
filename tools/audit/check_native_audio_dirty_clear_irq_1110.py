"""Check true native NMI and nested mapper IRQ in the changed mixer leaf."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_guest_expansion_sweep_vectors_1110_v1 as V
import check_native_audio_dirty_clear_1110 as D
from check_mini_audio_mixer_irq_1108_v2 import lag_path
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork


M,N,R = D.M,D.N,D.R
SMB2_PHYSICAL,SMB2_MAPPED = 82,0xde6b


class Guard(N.Bus):
    irq_only = False

    def __getitem__(self,at):
        if self.irq_only and isinstance(at,int):
            assert not 0x72aa<=at<0x72ca,('IRQ reads audio dirty state',hex(at))
            if at>=0x8000 and self.rawtags[(at-0x8000)//8192]==157:
                assert not D.ENTRY<=at<D.END,('IRQ observes native audio leaf',hex(at))
        return super().__getitem__(at)

    def __setitem__(self,at,v):
        if self.irq_only and isinstance(at,int):
            assert not 0x72aa<=at<0x72ca,('IRQ writes audio dirty state',hex(at))
        super().__setitem__(at,v)


def native_nmi(seed,flag,staging=None,cuts=None):
    m = slim_fork(seed)
    N.put(m,NmiDisable=flag,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
    lag,regular = lag_path(m)
    c = V.start(m)
    counts = Counter()
    minimum = c.sp

    def see(z):
        nonlocal minimum
        minimum = min(minimum,z.sp)
        pc = z.pc
        if pc in (lag,regular):
            counts[pc] += 1
        kind = D.trace_kind(pc,m)
        if pc==SMB2_MAPPED and m.rawtags[2]==(128|SMB2_PHYSICAL):
            assert not kind
            kind = 'smb2_pause'
        if kind:
            counts[kind] += 1
        if D.ENTRY<=pc<D.END and m.rawtags[1]==157:
            if pc==D.ENTRY:
                counts['leaf'] += 1
                if staging is not None:
                    change,dirty = staging
                    current = bytes(m[0x7282:0x7292])
                    m[0x72ca:0x72da] = bytes(v^255 if change>>i&1 else v for i,v in enumerate(current))
                    m[0x72aa:0x72ba] = bytes(255 if dirty>>i&1 else 0 for i in range(16))
            if cuts is not None:
                k = pc,z.p&4
                if k not in cuts or z.sp<cuts[k][0].sp:
                    cuts[k] = V.clone(z),tuple(m.writes)

    run(c,lambda z:(z.pc,z.sp)==(0x5b00,214),see)
    assert counts[lag]==int(flag==255) and counts[regular]==int(flag==0)
    assert registers(c,0xef)==(0xa7,23,61,0x24,214)
    assert counts['leaf']==sum(counts[k] for k in D.CALLS.values()),counts
    return c,counts,minimum


def resume_matches(c,prior,ref):
    irq = tuple(c.memory.writes)
    c.memory.writes.clear()
    V.finish(c)
    m,q = c.memory,ref.memory
    assert registers(c,0xef)==registers(ref,0xef) and live_stack(c)==live_stack(ref)
    assert prior+tuple(m.writes)==tuple(q.writes)
    irq_ports = {at for at,_ in irq if at in (0x2000,0x2005,0x2006,0x5128,0x5203,0x5204)}
    for lo,hi in ((0,0x17b),(0x200,0x8000)):
        a,b = [list.__getitem__(bus,slice(lo,hi)) for bus in (m,q)]
        assert all(x==y or at in irq_ports for at,(x,y) in enumerate(zip(a,b,strict=True),lo))
    assert m.rawtags==q.rawtags and m.ram==q.ram and m.chr_latches==q.chr_latches


def vectors(before,after):
    images = [M.bundle(raw) for raw in (before,after)]
    counts = Counter()
    perf = Counter()
    minima = [255,255]
    cuts_for = {}
    previous = N.Bus
    N.Bus = Guard
    try:
        for owner in (2,7,25,41):
            for flag in (0,255):
                warm = [D.seed(b,owner) for b in images]
                if owner in (2,25):
                    for m in warm:
                        # Real audio gate uses $5FFF bit zero as Main busy.
                        assert M.address(m.bundle,'FamilyMainCommit')==0x5fff
                        N.put(m,FamilyMainCommit=0)
                for tick in range(26):
                    for m in warm:
                        N.put(m,**D.fields(tick))
                    a,old,lo = native_nmi(warm[0],flag)
                    b,new,_ = native_nmi(warm[1],flag)
                    assert old==new
                    D.Token.exact_state(a.memory,b.memory)
                    minima[0] = min(minima[0],lo)
                    counts['native_NMI',owner,flag] += 1
                    for kind in D.CALLS.values():
                        if not new[kind]:
                            continue
                        counts[kind,owner,flag] += 1
                        # The authentic caller reached the real leaf first.
                        # Explicit leaf inputs cover both skip conditions,
                        # both timer-write conditions and maximum dirty load.
                        key = kind,flag
                        if key not in cuts_for:
                            cuts_for[key] = tick,owner,warm
                    delta = a.processorCycles-b.processorCycles
                    assert 0<=delta<=52 and (new['leaf'] or delta==0)
                    perf[delta] += 1
                    warm = [a.memory,b.memory]

        print('actual NMI ingresses',sorted((k,v) for k,v in counts.items() if k[0]!='native_NMI'),flush=True)
        assert set(cuts_for)=={(k,flag) for k in D.CALLS.values() for flag in (0,255)},cuts_for.keys()
        staging = ((0,0),(0xffff,0),(0,0xffff),(0x5555,0xaaaa))
        for (kind,flag),(tick,owner,warm) in cuts_for.items():
            # Use deepest reached stack for every physical instruction and
            # each mask state. Keep the uninterrupted reference per cut.
            profile = {}
            for state in staging:
                cuts = {}
                a,old,_ = native_nmi(warm[0],flag,state)
                b,new,lo = native_nmi(warm[1],flag,state,cuts)
                assert old==new and new[kind]==1 and cuts
                D.Token.exact_state(a.memory,b.memory)
                minima[0] = min(minima[0],lo)
                for pc_mask,(cut,prior) in cuts.items():
                    if pc_mask not in profile or cut.sp<profile[pc_mask][0].sp:
                        profile[pc_mask] = cut,prior,b
            for (_,masked),(c,prior,ref) in profile.items():
                if masked:
                    counts['masked_cut_'+kind,owner,flag] += 1
                    continue
                minima[1] = min(minima[1],V.interrupt(c))
                resume_matches(c,prior,ref)
                counts['nested_IRQ_'+kind,owner,flag] += 1
    finally:
        N.Bus = previous
    assert all(0x7a<low<255 for low in minima)
    return dict(counts=[[*k,v] for k,v in sorted(counts.items())],min_SP_NMI_and_nested_IRQ=minima,
                actual_NMI_cycle_savings=perf,IRQ_dirty_RAM_half_open=[0x72aa,0x72ca],
                scope='Exact paired normal and FF NMI and mapper IRQ between real mixer instructions. Every IRQ is bus-guarded against reading or writing the dirty arrays or entering the leaf; no audio hardware write may occur inside it.')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    assert not (out/'irq.json').exists()
    path = out/'proof.json'
    proof = json.loads(path.read_text())
    before = D.BASE.read_bytes()
    assert proof['passed'] and M.sha(before)==D.PIN==proof['parent_SHA256']
    for name,sha in proof['bindings'].items():
        assert M.sha((R/name).read_bytes())==sha,name
    after = install(before,proof['patches'])
    assert M.sha(after)==proof['expected_memory_only_SHA256']
    assert D.code(before,SMB2_PHYSICAL,SMB2_MAPPED,15)==bytes.fromhex('a92d8d6c01a9a98d6d01a99d205a01')
    result = vectors(before,after)
    receipt = result|dict(passed=True,ROM_written=False,parent_SHA256=D.PIN,
                          expected_memory_only_SHA256=M.sha(after),
                          bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes())
                                    for p in (path,Path(__file__),Path(V.__file__),R/'src/reset.s')})
    (out/'irq.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
