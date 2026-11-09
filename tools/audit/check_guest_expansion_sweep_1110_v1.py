"""Prove the linked intermediate sweep admission and unchanged whole mixer."""

from collections import Counter
from itertools import product
import json
from pathlib import Path
import re

import measure_mini_audio_1108_v1 as M
from check_mini_funded_actor_1108_v3 import install, registers

R, N = M.ROOT, M.N
OUT = R/'build/guest-expansion-sweep-1110'
BASE = R/'build/mini-combined-camera-native-1110/candidate.nes'
PIN = '56c4135e3edd7421c207fd4cd623ad8f58cd263353342d0af54202cd790cbcbc'
TRACE_BASE = R/'build/mini-box-terrain-visible-1110/candidate.nes'
TRACE = R/'build/mini-final-peak-detail-1110/capture/instruction-sample.json'
SOURCE = R/'src/mmc5_sfx.s'
PROPOSAL = R/'tools/reference/guest_expansion_sweep_clock_1110_v1.s'
FLUSH, CLOCK, TARGET = 0xaab5, 0xac28, 0xac67
FIRST, LAST = 0x72f7, 0x72ff


def binding(raw):
    b = M.bundle(raw)
    assert [M.address(b,n) for n in ('GuestExpansionFlush','GuestExpansionSweepClock',
                                     'GuestExpansionSweepTarget')] == [FLUSH,CLOCK,TARGET]
    at = M.location(b,'GuestExpansionSweepClock')
    assert at == 16+29*8192+(CLOCK&8191)
    body = SOURCE.read_text().split('.proc GuestExpansionSweepClock\n',1)[1].split('.endproc',1)[0]
    names = sorted(set(re.findall(r'\bGuestSweep\w+\b',body)))
    names.append('GuestExpansionSweepTarget')
    prefix = ''.join(f'{n}=${M.address(b,n):04x}\n' for n in names)
    old,_ = M.assemble(OUT/'clock-original',prefix+'SweepClock:\n'+body,CLOCK,TARGET-CLOCK)
    assert len(old)==TARGET-CLOCK and raw[at:at+len(old)]==old
    next_source = PROPOSAL.read_text()+f'\n.res {TARGET-CLOCK}-(*-SweepClock),$ea\n'
    new,_ = M.assemble(OUT/'clock-successor',prefix+next_source,CLOCK,TARGET-CLOCK)
    assert len(new)==len(old) and new.endswith(b'\xea'*5)
    row = dict(file_offset=at,old_hex=old.hex(),new_hex=new.hex(),physical_PRG=29,
               CPU_half_open=[CLOCK,TARGET],role='Intermediate expansion sweep clock eligibility')
    return install(raw,[row]),row


def census(raw):
    prg = raw[16:16+128*8192]
    bank = prg[29*8192:30*8192]
    old_clock = bytes((0x20,CLOCK&255,CLOCK>>8))
    old_target = bytes((0x20,TARGET&255,TARGET>>8))
    assert bank.count(old_clock)==prg.count(old_clock)==1
    assert bank.index(old_clock)==0xab21-0xa000
    assert [i+0xa000 for i in range(len(bank)-2) if bank[i:i+3]==old_target]==[0xab3a,CLOCK]
    assert SOURCE.read_text().count('jsr GuestExpansionSweepClock')==1
    assert SOURCE.read_text().count('jsr GuestExpansionSweepTarget')==2
    # A same CPU-address JMP in physical92 stays in that physical bank.
    # No linked typed/far packet can dispatch the intermediate scratch leaf.
    for dst in (CLOCK,TARGET):
        literal = bytes.fromhex(f'a9{dst&255:02x}8d6c01a9{dst>>8:02x}8d6d01a99d')
        assert literal not in prg
    read_ops = {0x0d,0x2d,0x4d,0x6d,0x8c,0x8d,0x8e,0x99,0x9d,0xac,0xad,0xae,
                0xb9,0xbc,0xbd,0xbe,0xcc,0xcd,0xce,0xec,0xed,0xee,0x0e,0x2e,0x4e,0x6e}
    users = []
    for i in range(len(prg)-2):
        if prg[i] in read_ops and prg[i+1:i+3] in (b'\xf9\x72',b'\xfa\x72'):
            bank_no,rel = divmod(i,8192)
            pc = 0xa000+rel
            assert bank_no==29 and CLOCK<=pc<0xacc8,(bank_no,hex(pc))
            users.append([pc,prg[i],0x7200+prg[i+1]])
    assert len(users)==15
    return dict(clock_JSR=0xab21,clock_iterations=2,final_target_JSR=0xab3a,
                direct_Delta_users=users,ordered_completion='Final Target reinitializes both Delta bytes before deciding muting, and Flush normalizes X, Y, N, Z and C.')


class Mixer:
    def __init__(self,image):
        self.mem = bytearray(65536)
        at = 16+29*8192
        self.mem[0xa000:0xc000] = image['raw'][at:at+8192]
        self.lo = M.address(image,'GuestExpansionApu')
        self.hw = []

    def __getitem__(self,at):
        return self.mem[at]

    def __setitem__(self,at,v):
        if 0x5000<=at<=0x5015:
            self.hw.append((at,v))
        else:
            assert self.lo<=at<LAST or 0x100<=at<0x200,hex(at)
        self.mem[at]=v


def direct_cases(images):
    machines = [Mixer(b) for b in images]
    masks = Counter()
    addr = lambda n:M.address(images[0],n)

    def execute(m,ctl,div,reload,period,mask,dirty,phase):
        m.hw.clear()
        mem = m.mem
        mem[addr('GuestMixMask')] = mask
        mem[addr('GuestMixChanged')] = phase&3
        for name in ('GuestExpansionApu','GuestExpansionLast','GuestFxApu','GuestFxDirty'):
            at = addr(name)
            mem[at:at+8] = bytes((i*phase+ctl) & 255 for i in range(8)) if name!='GuestFxDirty' else bytes(8)
        mem[FIRST:LAST] = bytes((period&255,period>>8,0xa1,0x65,ctl,div,reload,0xfd))
        if dirty:
            at = addr('GuestFxDirty')
            mem[at+1:at+4] = bytes([dirty&1,dirty&2,dirty&4])
        c = N.NesMPU(memory=m,pc=FLUSH)
        c.a,c.x,c.y,c.p,c.sp = phase,21,71,0x20|(phase&0xcf),224
        c.stPushWord(0x5aff)
        targets = 0
        for _ in range(800):
            if c.pc==0x5b00:
                break
            targets += c.pc==TARGET
            c.step()
        else:
            raise AssertionError(('Flush bound',hex(c.pc),c.sp))
        assert c.sp==224
        return (registers(c),bytes(mem[m.lo:LAST]),tuple(m.hw)),c.processorCycles,targets

    def compare(ctl,div,reload,period,mask,dirty,phase):
        a,b = [execute(m,ctl,div,reload,period,mask,dirty,phase) for m in machines]
        assert a[0]==b[0],(ctl,div,reload,period,mask,dirty,phase,a,b)
        assert a[2]==(3 if mask&1 else 0) and b[2]<=a[2]
        if mask&1:
            assert b[2]>=1
        masks[a[2]-b[2],a[1]-b[1]] += 1
        return [a[1],b[1]]

    for ctl,div,reload,period in product(range(256),range(8),range(2),
                                        (0,7,8,255,256,1023,1536,2047,2048,65535)):
        compare(ctl,div,reload,period,1|(ctl&2),0,ctl)
    for dirty,mask,ctl,div,period in product(range(8),range(4),(0,7,8,0x87,0x8f,0x93,0xf7,0xff),
                                            (0,1,7,255),(0,0x7ff)):
        compare(ctl,div,1,period,mask,dirty,dirty*19+mask)
    representative = compare(0x93,0,0,0x320,3,0,0x12)
    return dict(cases=sum(masks.values()),minimum_saved=min(k[1] for k in masks),
                maximum_saved=max(k[1] for k in masks),peak_shape_cycle_pair=representative,
                grouped={str(skipped):dict(cases=sum(n for (k,d),n in masks.items() if k==skipped),
                                          cycle_range=[min(d for k,d in masks if k==skipped),
                                                       max(d for k,d in masks if k==skipped)])
                         for skipped in sorted({k for k,_ in masks})})


def audio_update(images):
    results = []
    for who in range(42):
        pair = [M.seed(b,who) for b in images]
        savings = []
        for t in range(28):
            for m in pair:
                m.writes.clear()
                N.put(m,AreaMusicQueue=(1 if t==0 else 2 if t==17 else 0),
                      EventMusicQueue=4 if t==22 else 0,Square1SoundQueue=32 if t in (4,10) else 0,
                      Square2SoundQueue=1 if t==15 else 0,NoiseSoundQueue=1 if t==19 else 0,
                      GamePauseStatus=int(t==24),FrameCounter=t)
            a,b = [M.direct(m,'AudioUpdate') for m in pair]
            assert a[1]==b[1],(who,t,a,b)
            M.compare_state(*pair)
            savings.append(a[0]-b[0])
        results.append(dict(raw=who,updates=len(savings),cycles_saved=[min(savings),max(savings)],
                            sum_saved=sum(savings)))
    return results


def peak_scope(raw):
    ref = TRACE_BASE.read_bytes()
    lo = 16+29*8192+(FLUSH&8191)
    assert raw[lo:lo+0x230]==ref[lo:lo+0x230]
    scene = json.loads(TRACE.read_text())
    irq = scene['interrupt_opcodes']
    target_cycles = sum(v for k,v in irq.items() if k.startswith('29:') and 0xac67<=int(k[3:],16)<=0xacc5)
    assert target_cycles==396 and irq['29:ac28']==12 and irq['29:ac3b']==4 and irq['29:ac55']==4
    return dict(source='Bound prior native X1511 trace, relevant audio bytes match exact current ROM',
                x=scene['scene']['x'],frame=scene['scene']['frame'],target_calls=3,
                target_cycles=target_cycles,clock_commits=1,clock_nonzero_divider=1,shift=3)


def main():
    raw = BASE.read_bytes()
    assert M.sha(raw)==PIN
    OUT.mkdir(exist_ok=True)
    after,patch = binding(raw)
    images = [M.bundle(b) for b in (raw,after)]
    proof = dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),
                 source_CPU_only=True,ROM_written=False,patches=[patch],
                 source_callers=census(raw),peak_shape=peak_scope(raw))
    proof['mixer'] = direct_cases(images)
    print('Direct mixer',proof['mixer'],flush=True)
    proof['actual_AudioUpdate'] = audio_update(images)
    paths = (Path(__file__),SOURCE,PROPOSAL,TRACE,R/'src/guest_audio.s',Path(M.__file__))
    proof['bindings'] = {p.relative_to(R).as_posix():M.sha(p.read_bytes()) for p in paths}
    (OUT/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(proof['expected_memory_only_SHA256'],len(proof['actual_AudioUpdate'])*28,'AudioUpdate calls',
          min(r['cycles_saved'][0] for r in proof['actual_AudioUpdate']),
          max(r['cycles_saved'][1] for r in proof['actual_AudioUpdate']),flush=True)


if __name__=='__main__':
    main()
