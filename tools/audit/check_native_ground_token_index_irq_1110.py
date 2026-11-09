"""Verify actual normal and lag NMI, including IRQ within each token lane."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import check_native_audio_frame_token_vectors_1110_v1 as Native
import check_native_ground_token_index_1110 as T
from check_mini_funded_actor_1108_v3 import install, live_stack, registers


M,N,R = T.M,T.N,T.R


class Guard(Native.Guard):
    audio_private = Native.Guard.audio_private+((0x0101,0x0106),(0x7282,0x72ba))


def samples(raw,tokens):
    at = lambda p:T.F.offset(57,p)
    left = [raw[at(0xbac0)+4*i:at(0xbac0)+4*i+4] for i in range(22)]
    right = [raw[at(0xbb18)+3*i:at(0xbb18)+3*i+3] for i in range(44)]
    chosen = {}
    for i,token in enumerate(tokens):
        group = next(g for g,row in enumerate(left) if token<row[0])
        start_group = next(g for g,row in enumerate(left) if token&0xfc<row[0])
        row = right[raw[at(0xba2b)+token]//3]
        lane = (0 if token<8 else 1 if token<53 else 2,group-start_group if token>=53 else 0,
                left[group][1]!=255,*(value!=255 for value in row))
        chosen.setdefault(lane,(129+i,token))
    assert {x[0] for x in chosen}=={0,1,2}
    assert {x[1] for x in chosen if x[0]==2}=={0,1,2}
    assert any(not lane[-2] and lane[-1] for lane in chosen)  # True high-only write.
    assert any(lane[-2] and lane[-1] for lane in chosen)
    return dict(chosen.values())


def vectors(before,after,labels):
    images = [M.bundle(im) for im in (before,after)]
    tokens,_,_ = T.records(before)
    chosen = samples(before,tokens)
    bounds = (labels['GroundLoopFrame'],labels['VolumeForToken'])
    counts = Counter()
    performance = defaultdict(list)
    minimum = [255,255]
    previous = N.Bus
    N.Bus = Guard
    try:
        for owner in (7,41):
            warm = [M.seed(b,owner) for b in images]
            trace_labels = {'GroundLoopFrame':labels['GroundLoopFrame']}
            for tick in range(max(chosen)+1):
                fields = dict(AreaMusicQueue=int(tick==0),FrameCounter=tick&255,
                              Square1SoundQueue=32 if tick in (180,409,1260) else 0,
                              Square2SoundQueue=1 if tick in (250,653) else 0,NoiseSoundQueue=0)
                if tick in chosen or tick in (0,128):
                    for m in warm:
                        N.put(m,**fields)
                    for flag in (0,255):
                        cuts = {}
                        a,_,_ = Native.full_nmi(warm[0],flag,[bounds],trace_labels,None,tick)
                        b,packed,lo = Native.full_nmi(warm[1],flag,[bounds],trace_labels,cuts,tick)
                        assert packed==int(tick in chosen),(owner,flag,tick,packed)
                        T.exact_state(a.memory,b.memory)
                        assert registers(a,0xef)==registers(b,0xef) and live_stack(a)==live_stack(b)
                        delta = a.processorCycles-b.processorCycles
                        assert (delta>0 if packed else delta==0),(owner,flag,tick,delta)
                        counts['actual_NMI',owner,flag] += 1
                        if packed:
                            performance[owner,flag].append(delta)
                        minimum[0] = min(minimum[0],lo)
                        for (_,pc,masked),(cut,prior) in cuts.items():
                            if masked:
                                counts['I1_cut',owner,flag] += 1
                                continue
                            minimum[1] = min(minimum[1],Native.V.interrupt(cut))
                            irq = tuple(cut.memory.writes)
                            cut.memory.writes.clear()
                            Native.V.finish(cut)
                            m,q = cut.memory,b.memory
                            assert registers(cut,0xef)==registers(b,0xef) and live_stack(cut)==live_stack(b)
                            assert prior+tuple(m.writes)==tuple(q.writes),(owner,flag,tick,hex(pc))
                            irq_ports = {at for at,_ in irq if at in (0x2000,0x2005,0x2006,0x5128,0x5203,0x5204)}
                            for lo,hi in ((0,0x17b),(0x200,0x8000)):
                                a0,b0 = [list.__getitem__(bus,slice(lo,hi)) for bus in (m,q)]
                                assert all(x==y or at in irq_ports
                                           for at,(x,y) in enumerate(zip(a0,b0,strict=True),lo)),(owner,flag,tick,hex(pc))
                            assert m.rawtags==q.rawtags and m.ram==q.ram and m.chr_latches==q.chr_latches
                            counts['nested_IRQ',owner,flag] += 1
                for m in warm:
                    N.put(m,**fields)
                    M.direct(m,'AudioUpdate')
            for flag in (0,255):
                assert counts['nested_IRQ',owner,flag]>25
    finally:
        N.Bus = previous
    assert min(minimum)>0x7a
    return dict(cuts=[[name,owner,flag,n] for (name,owner,flag),n in sorted(counts.items())],
                normal_and_lag_minimum_SP=minimum,tokens_and_native_ticks=sorted(chosen.items()),
                savings=[dict(owner=owner,flag=flag,min=min(p),max=max(p),cases=len(p))
                         for (owner,flag),p in sorted(performance.items())])


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert not (out/'irq.json').exists()
    path = out/'proof.json'
    proof = json.loads(path.read_text())
    before = T.BASE.read_bytes()
    assert proof['passed'] and M.sha(before)==T.PIN==proof['parent_SHA256']
    for file,digest in proof['bindings'].items():
        assert M.sha((R/file).read_bytes())==digest,file
    after = install(before,proof['patches'])
    assert M.sha(after)==proof['expected_memory_only_SHA256']
    result = vectors(before,after,proof['labels'])
    q = result|dict(passed=True,ROM_written=False,parent_SHA256=T.PIN,
                    expected_memory_only_SHA256=M.sha(after),
                    bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes())
                              for p in (Path(__file__),Path(Native.__file__),path,R/'src/reset.s')})
    (out/'irq.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
