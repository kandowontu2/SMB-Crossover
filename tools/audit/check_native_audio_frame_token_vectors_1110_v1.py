"""Qualify actual normal and lag vectors and linked song-range ownership."""

from collections import Counter
import json
from pathlib import Path

import check_native_audio_frame_token_1110_v1 as T
import check_guest_expansion_sweep_vectors_1110_v1 as V
from check_mini_audio_mixer_irq_1108_v2 import lag_path, sound_writes
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork

F,M,N,R,OUT = T.F,T.M,T.N,T.R,T.OUT


def stream_extents(bundle):
    raw = bundle['raw']
    tables,_,_ = F.matrices(bundle)
    ml,mh = [M.location(bundle,'XgMacro'+s) for s in ('Lo','Hi')]
    macros = [F.offset(38,raw[ml+i]|raw[mh+i]<<8) for i in range(mh-ml)]
    roots = {(F.offset(bank,lo|hi<<8),index>=49)
             for table in tables for index,(bank,lo,hi) in enumerate(table)}
    extents = []
    target = F.offset(57,0xb74c),F.offset(57,0xbbb8)
    for start,mask in sorted(roots):
        if mask:
            data = F.stream(raw,start)
            for _ in range(300000):
                op,size = next(data)
                if op in (254,255):
                    break
                assert 1<=op<=129,(start,op)
                if op>=128:
                    lo,size = next(data)
                    hi,size = next(data)
                    for _ in range((lo|hi<<8).bit_count()+(op&1)):
                        _,size = next(data)
            else:
                raise AssertionError(('Original mask terminal bound',start))
        else:
            frames,size,*_ = F.project_stream(raw,start,macros)
            if start==target[0]:
                assert len(frames)==3264
        extents.append((start,start+size))
    overlap = [q for q in extents if q[0]<target[1] and q[1]>target[0]]
    assert len(extents)==66 and overlap==[target],overlap
    return dict(unique_roots=len(extents),ground_file_half_open=target,
                only_intersecting_root=overlap,extents=extents)


class Guard(N.Bus):
    irq_only = False
    audio_private = ((0xde,0xec),(0x730c,0x7382),(0x7400,0x7c00))

    def __getitem__(self,at):
        if self.irq_only and isinstance(at,int):
            assert not any(lo<=at<hi for lo,hi in self.audio_private),hex(at)
            if 0x8000<=at<=0xffff:
                physical = self.rawtags[(at-0x8000)//8192]&127
                assert physical not in (38,57),('IRQ audio reader',physical,hex(at))
        return super().__getitem__(at)

    def __setitem__(self,at,value):
        if self.irq_only and isinstance(at,int):
            assert not any(lo<=at<hi for lo,hi in self.audio_private),hex(at)
        return super().__setitem__(at,value)


def mapped(c):
    return c.memory.rawtags[(c.pc-0x8000)//8192]&127 if c.pc>=0x8000 else -1


def full_nmi(seed,flag,ranges,labels,cuts,case):
    m = slim_fork(seed)
    m.packed_map_sites = []
    N.put(m,NmiDisable=flag,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
    lag,regular = lag_path(m)
    c = V.start(m)
    visits = Counter()
    minimum = c.sp

    def see(z):
        nonlocal minimum
        minimum = min(minimum,z.sp)
        pc = z.pc
        if pc in (lag,regular):
            visits[pc] += 1
        if mapped(z)!=38:
            return
        if pc==labels['GroundLoopFrame'] and cuts is not None:
            visits['packed'] += 1
        if pc in (0xc949,0xcaea) and z.a in (0xa6,0xb9):
            assert bytes(m[pc:pc+3])==b'\x8d\x15\x51'
            m.packed_map_sites.append(len(m.writes))
        if cuts is not None and any(lo<=pc<hi for lo,hi in ranges):
            k = case,pc,z.p&4
            if k not in cuts or z.sp<cuts[k][0].sp:
                cuts[k] = (V.clone(z),tuple(m.writes))

    run(c,lambda z:(z.pc,z.sp)==(0x5b00,214),see)
    assert visits[lag]==int(flag==255) and visits[regular]==int(flag==0)
    assert registers(c,0xef)==(0xa7,23,61,0x24,214)
    return c,visits['packed'],minimum


def native_vectors(images,proof):
    labels = proof['labels']
    ranges = [(labels['ReadSongPointer'],labels['EndCode']),(0xcb03,0xcbc5)]
    ranges.extend(tuple(q['CPU_half_open']) for q in proof['patches'] if
                  q['physical_PRG']==38 and q['CPU_half_open'][0]!=0xc000)
    counts,minima,perf = Counter(),[255,255],{0:[],255:[]}
    irq_latches = Counter()
    cuts_by_flag = {0:{},255:{}}
    warm = [M.seed(b,41) for b in images]
    # Both NMI entry branches read live state built by genuine AudioUpdate.
    for tick in range(129+3264+5):
        if tick in (0,1,8,80,127,128) or 129<=tick<161 or tick in (400,802,1350,2400,3391,3392,3393,3394):
            modes = [('ground',0,0)]
            if tick in (129,157,3392):
                modes += [('hurry',0,64),('other_event',0,4),('cave',4,0)]
            for case,area,event in modes:
                staged = [slim_fork(m) for m in warm]
                for m in staged:
                    N.put(m,AreaMusicQueue=area or int(tick==0),EventMusicQueue=event,
                          FrameCounter=tick&255,Square1SoundQueue=32 if tick%3==0 else 0)
                for flag,cuts in cuts_by_flag.items():
                    before,_,_ = full_nmi(staged[0],flag,ranges,labels,None,case)
                    after,packed,low = full_nmi(staged[1],flag,ranges,labels,cuts,case)
                    T.external_state(before.memory,after.memory,bool(packed))
                    minima[0] = min(minima[0],low)
                    counts[f'paired_{flag}'] += 1
                    if packed:
                        perf[flag].append(before.processorCycles-after.processorCycles)
                    # Retain the complete uninterrupted candidate end per cut.
                    for key,val in tuple(cuts.items()):
                        if len(val)==2:
                            cuts[key] = (*val,after)
        T.frame_pair(warm,dict(AreaMusicQueue=int(tick==0),FrameCounter=tick&255))

    for flag,cuts in cuts_by_flag.items():
        for (case,pc,mask),(c,prior,ref) in cuts.items():
            if mask:
                counts[f'masked_{flag}'] += 1
                continue
            minima[1] = min(minima[1],V.interrupt(c))
            irq_writes = tuple(c.memory.writes)
            c.memory.writes.clear()
            V.finish(c)
            m,q = c.memory,ref.memory
            assert registers(c,0xef)==registers(ref,0xef) and live_stack(c)==live_stack(ref),(flag,case,pc)
            assert prior+tuple(m.writes)==tuple(q.writes),(flag,case,pc)
            flat = lambda bus,lo,hi:bytes(list.__getitem__(bus,slice(lo,hi)))
            for lo,hi in ((0,0x100),(0x15a,0x17b),(0x200,0x8000)):
                lhs,rhs = flat(m,lo,hi),flat(q,lo,hi)
                if lhs==rhs:
                    continue
                diff = [(at,a,b) for at,(a,b) in enumerate(zip(lhs,rhs),lo) if a!=b]
                # The extra hardware IRQ updates its physical scroll and
                # IRQ-control ports. The flat CPU model also mirrors those
                # I/O stores into its backing list. Every RAM byte is exact.
                irq_ports = {at for at,_ in irq_writes if at in (0x2000,0x2005,0x2006,0x5128,0x5203,0x5204)}
                assert all(at in irq_ports for at,a,b in diff),(flag,case,hex(pc),diff[:12])
                irq_latches.update(at for at,a,b in diff)
            assert m.rawtags==q.rawtags and m.ram==q.ram and m.chr_latches==q.chr_latches
            counts[f'nested_IRQ_{flag}'] += 1
    assert min(counts['nested_IRQ_0'],counts['nested_IRQ_255'])>25 and min(minima)>0x7a
    return dict(vector_cases=counts,normal_and_lag_minimum_SP=minima,
                additional_IRQ_physical_latch_differences={hex(at):n for at,n in irq_latches.items()},
                packed_NMI_cycle_savings={flag:dict(min=min(p),max=max(p),mean=sum(p)/len(p),samples=len(p))
                                          for flag,p in perf.items()})


def qualify(before,after,proof):
    images = [M.bundle(raw) for raw in (before,after)]
    b = images[0]
    at = lambda name:M.address(b,name)
    assert Guard.audio_private==((at('XgAudioPtr'),at('XgLzSavedY')+1),
                                (at('XgMusicApu'),at('XgAudioStackBank')+32),
                                (at('XgLzHistory'),at('XgLzHistory')+2048))
    old_bus = N.Bus
    N.Bus = Guard
    try:
        result = native_vectors(images,proof)
    finally:
        N.Bus = old_bus
    return result|{'linked_track_extent_census':stream_extents(images[0])}


def main():
    path = OUT/'runtime-proof.json'
    proof = json.loads(path.read_text())
    for file,digest in proof['bindings'].items():
        assert M.sha((R/file).read_bytes())==digest,file
    before = F.BASE.read_bytes()
    assert M.sha(before)==F.PIN==proof['parent_SHA256']
    after = install(before,proof['patches'])
    assert M.sha(after)==proof['expected_memory_only_SHA256']
    result = qualify(before,after,proof)
    q = result|dict(passed=True,parent_SHA256=F.PIN,expected_memory_only_SHA256=M.sha(after),
                    bindings={f.relative_to(R).as_posix():M.sha(f.read_bytes())
                              for f in (path,Path(__file__),R/'src/reset.s',R/'src/expanded_audio.s',
                                        R/'src/expanded_music.inc')})
    (OUT/'vectors.json').write_text(json.dumps(q,indent=2)+'\n')
    print({key:val for key,val in result.items() if key!='linked_track_extent_census'},flush=True)


if __name__=='__main__':
    main()
