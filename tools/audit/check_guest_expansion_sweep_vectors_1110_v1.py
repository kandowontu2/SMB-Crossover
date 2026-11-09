"""Check true normal and lag NMI plus mapper IRQ inside the changed audio leaf."""

from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_guest_expansion_sweep_1110_v1 as S
from check_mini_audio_mixer_irq_1108_v2 import lag_path, sound_writes
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork

M,N,R,OUT = S.M,S.N,S.R,S.OUT


class Guard(N.Bus):
    irq_only = False

    def __getitem__(self,at):
        if self.irq_only and isinstance(at,int):
            assert not S.FIRST<=at<S.LAST,('IRQ observes sweep scratch',hex(at))
        return super().__getitem__(at)

    def __setitem__(self,at,v):
        if self.irq_only and isinstance(at,int):
            assert not S.FIRST<=at<S.LAST,('IRQ changes sweep scratch',hex(at))
        super().__setitem__(at,v)


def clone(c):
    m = slim_fork(c.memory)
    z = N.NesMPU(memory=m,pc=c.pc)
    z.a,z.x,z.y,z.p,z.sp = registers(c)
    return z


def start(m):
    m.writes.clear()
    c = N.NesMPU(memory=m,pc=0x5b00)
    c.a,c.x,c.y,c.p,c.sp = 0xa7,23,61,0x24,214
    c.nmi()
    return c


def interrupt(c):
    before = (registers(c,0xef),live_stack(c),tuple(c.memory.rawtags),bytes(c.memory[:256]),
              bytes(c.memory[0x15a:0x17b]),bytes(c.memory[S.FIRST:S.LAST]),tuple(map(bytes,c.memory.ram)))
    ret = c.pc,c.sp
    m = c.memory
    m.irq_only = True
    c.irq()
    assert c.pc==0x8000 and m.rawtags[0]==254
    lowest = c.sp

    def see(z):
        nonlocal lowest
        lowest = min(lowest,z.sp)

    run(c,lambda z:(z.pc,z.sp)==ret,see)
    m.irq_only = False
    assert before == (registers(c,0xef),live_stack(c),tuple(m.rawtags),bytes(m[:256]),
                      bytes(m[0x15a:0x17b]),bytes(m[S.FIRST:S.LAST]),tuple(map(bytes,m.ram)))
    assert not sound_writes(m) and any(at==0x2005 for at,_ in m.writes)
    return lowest


def prepare(b,flag):
    m = M.seed(b,41)
    N.put(m,AreaMusicQueue=1,NmiDisable=flag,Square1SoundQueue=32)
    return m


def same_end(a,b):
    assert registers(a,0xef)==registers(b,0xef) and a.pc==b.pc and live_stack(a)==live_stack(b)
    M.compare_state(a.memory,b.memory)


def finish(c):
    run(c,lambda z:(z.pc,z.sp)==(0x5b00,214))


def qualification(images):
    before,after = images
    original_bus = N.Bus
    N.Bus = Guard
    counts, minimum, cycles = Counter(),255,{}
    try:
        for nmi_flag in (0,255):
            lag,regular = lag_path(prepare(after,nmi_flag))
            profiles = {
                'natural':None, 'disabled':(0x73,0,0,0x320), 'zero_shift':(0x90,0,0,0x320),
                'shift3_real_divider':(0x93,0,0,0x320), 'reload_nonzero':(0x93,1,1,0x320),
                'both_eligible':(0x8b,0,0,0x320), 'overflow_mute':(0x83,0,0,0x7ff),
                'under8_mute':(0x83,0,0,7),
            }
            for lane,args in profiles.items():
                samples, cuts = [], {}
                for b in (before,after):
                    c = start(prepare(b,nmi_flag))
                    seen, entry = Counter(),0
                    while (c.pc,c.sp)!=(0x5b00,214):
                        m = c.memory
                        pc = c.pc
                        tag = m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
                        if pc in (lag,regular):
                            seen[pc] += 1
                        if tag==157 and pc==S.FLUSH:
                            entry += 1
                            assert N.get(m,'GuestMixMask')&1
                            if args is not None:
                                ctl,div,reload,period = args
                                N.put(m,GuestSweepControl=ctl,GuestSweepDivider=div,GuestSweepReload=reload)
                                m[S.FIRST:S.FIRST+2] = bytes([period&255,period>>8])
                                at = M.address(b,'GuestFxDirty')
                                m[at+1:at+4] = bytes(3)
                        if b is after and tag==157 and S.CLOCK<=pc<0xacc5:
                            key = pc,c.sp,c.p&4,N.get(m,'GuestSweepTicks')
                            if not c.p&4 and key not in cuts:
                                cuts[key] = (clone(c),tuple(sound_writes(m)))
                        assert m[pc],(lane,hex(pc),c.sp)
                        assert c.processorCycles<60000
                        c.step()
                    assert seen[lag]==int(nmi_flag==255) and seen[regular]==int(nmi_flag==0)
                    assert entry==1,(lane,nmi_flag,entry)
                    samples.append(c)
                old,new = samples
                same_end(old,new)
                cycles[f'{nmi_flag}_{lane}'] = old.processorCycles-new.processorCycles
                assert cuts,(nmi_flag,lane)
                for cut,prior_writes in cuts.values():
                    minimum = min(minimum,interrupt(cut))
                    finish(cut)
                    assert registers(cut,0xef)==registers(new,0xef) and cut.pc==new.pc
                    assert list(prior_writes)+sound_writes(cut.memory)==sound_writes(new.memory)
                    assert bytes(cut.memory[0x6000:0x8000])==bytes(new.memory[0x6000:0x8000])
                    assert cut.memory.rawtags==new.memory.rawtags and cut.memory.ram==new.memory.ram
                    assert bytes(cut.memory[:256])+bytes(cut.memory[0x15a:0x17b])==(
                        bytes(new.memory[:256])+bytes(new.memory[0x15a:0x17b]))
                    counts[nmi_flag] += 1
    finally:
        N.Bus = original_bus
    assert all(counts[k] for k in (0,255)) and minimum>0x7a
    return dict(normal_nested_IRQ=counts[0],lag_nested_IRQ=counts[255],minimum_SP=minimum,
                cycles_saved_per_normal_or_FF_NMI_fixture=cycles,
                IRQ_scratch_guard=[S.FIRST,S.LAST],
                scope='The native NMI and audio driver reach real Flush. One genuine world cue per mode, plus explicit sweep-branch inputs staged at real Flush entry. Actual nested IRQ completes before every resumed audio continuation. No native video timing claim.')


def main():
    p = OUT/'proof.json'
    proof = json.loads(p.read_text())
    raw = S.BASE.read_bytes()
    assert M.sha(raw)==S.PIN==proof['parent_SHA256']
    after = install(raw,proof['patches'])
    assert M.sha(after)==proof['expected_memory_only_SHA256']
    q = qualification([M.bundle(raw),M.bundle(after)])
    q.update(passed=True,base_ROM_SHA256=S.PIN,expected_memory_only_SHA256=M.sha(after),
             bindings={f.relative_to(R).as_posix():M.sha(f.read_bytes())
                       for f in (p,Path(__file__),R/'src/reset.s')})
    (OUT/'vectors.json').write_text(json.dumps(q,indent=2)+'\n')
    print(q,flush=True)


if __name__=='__main__':
    main()
