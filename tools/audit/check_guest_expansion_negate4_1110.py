"""Source-link exact short-period negate shift four and qualify the real mixer."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import re
import subprocess
import tempfile

import check_guest_expansion_sweep_1110_v1 as Sweep
import check_guest_expansion_sweep_vectors_1110_v1 as V
from check_mini_audio_mixer_irq_1108_v2 import lag_path
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_native_audio_dirty_clear_irq_1110 import resume_matches
from check_native_ground_token_index_1110 import exact_state


M,N,R = Sweep.M,Sweep.N,Sweep.R
BASE = R/'build/mini-margin-trial-1110/candidate.nes'
PIN = '863e1e3c536c3e6b8027e212a0a430356805886609fc2c264263d3cdb163fc9f'
PROFILE_ROM = R/'build/mini-movement-popup-rng-native-1110/candidate.nes'
PROFILE = R/'build/mini-f518-nmi-1508-1110/capture/timing.json'
PROFILE_PIN = 'f5183f7ada374443222dc0b30a0777a8218aac154c04f84855d140245370daaa'
SOURCE = R/'tools/reference/guest_expansion_negate4_1110.s'
FUNDING = R/'build/mini-audio-1108-v1/mixer-irq.json'
SPANS = (('SWEEP_FOOTER',0xac0c,0xac28),('SWEEP_TARGET',0xac67,0xacc8))
FIRST,LAST = Sweep.FIRST,Sweep.LAST
FLUSH,CLOCK,TARGET = Sweep.FLUSH,Sweep.CLOCK,Sweep.TARGET
FAST = 0xac0c


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def off(pc):
    return 16+29*8192+(pc&8191)


def linked(raw,out):
    parent = M.bundle(raw)
    assert [M.address(parent,n) for n in ('GuestExpansionFlush','GuestExpansionSweepClock',
                                         'GuestExpansionSweepTarget')]==[FLUSH,CLOCK,TARGET]
    assert M.location(parent,'GuestExpansionSweepTarget')==off(TARGET)
    proof = read(FUNDING)
    row, = [row for row in proof['patches'] if row['bank']==29 and row['pc']==FLUSH]
    assert proof['passed'] and row['recovered_unused_tail']==28
    assert row['offset']==off(FLUSH) and row['byte_end']==CLOCK
    assert raw[off(FLUSH):off(CLOCK)]==bytes.fromhex(row['replacement'])
    assert raw[off(FAST):off(CLOCK)]==b'\xea'*28

    original = Sweep.SOURCE.read_text().split('.proc GuestExpansionSweepTarget\n',1)[1].split('.endproc',1)[0]
    names = set(re.findall(r'\bGuestSweep\w+\b',original))
    definitions = ''.join(f'{n}=${M.address(parent,n):04x}\n' for n in sorted(names))
    with tempfile.TemporaryDirectory(prefix='sweep-',dir=out) as folder:
        work = Path(folder)
        old,_ = M.assemble(work/'old',definitions+original,TARGET,0xacc8-TARGET)
        assert old==raw[off(TARGET):off(0xacc8)]
        cfg,obj,binary = (work/f'new.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY { '+''.join(f'{n}:start=${lo:04x},size={hi-lo},file=%O;'
                        for n,lo,hi in SPANS)+'}\nSEGMENTS { '+
                       ''.join(f'{n}:load={n},type=ro;' for n,_,_ in SPANS)+'}\n')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        result = binary.read_bytes()
    patches,at = [],0
    for name,lo,hi in SPANS:
        size = hi-lo
        patches.append(dict(role=name,physical_PRG=29,CPU_half_open=[lo,hi],file_offset=off(lo),
                            old_hex=raw[off(lo):off(lo)+size].hex(),new_hex=result[at:at+size].hex()))
        at += size
    assert len(result)==at
    return install(raw,patches),patches


def source_callers(raw):
    prg = raw[16:16+128*8192]
    bank = prg[29*8192:30*8192]
    rows = []
    for i in range(len(bank)-2):
        dest = int.from_bytes(bank[i+1:i+3],'little')
        if bank[i] in (0x20,0x4c,0x6c) and any(lo<=dest<hi for _,lo,hi in SPANS):
            rows.append([0xa000+i,bank[i],dest])
    assert rows==[[0xab3a,0x20,TARGET],[0xac36,0x20,TARGET],[0xaca7,0x4c,0xacbd]],rows
    for pc in (FAST,CLOCK,TARGET):
        literal = bytes.fromhex(f'a9{pc&255:02x}8d6c01a9{pc>>8:02x}8d6d01a99d')
        assert literal not in prg
    assert bank[0xb21:0xb24]==bytes.fromhex('2028ac')
    assert (R/'src/guest_audio.s').read_text().count('jsr GuestExpansionFlush')==1
    assert Sweep.SOURCE.read_text().count('jsr GuestExpansionSweepTarget')==2
    ops = {0x0d,0x2d,0x4d,0x6d,0x8c,0x8d,0x8e,0x99,0x9d,0xac,0xad,0xae,0xb9,0xbc,
           0xbd,0xbe,0xcc,0xcd,0xce,0xec,0xed,0xee,0x0e,0x2e,0x4e,0x6e}
    users = [(i//8192,0xa000+i%8192,prg[i],prg[i+1]+0x7200) for i in range(len(prg)-2)
             if prg[i] in ops and prg[i+1:i+3] in (b'\xf9\x72',b'\xfa\x72')]
    assert len(users)==15 and all(bank==29 and CLOCK<=pc<0xacc8 for bank,pc,*_ in users)
    return dict(linked_ingress=rows,delta_users=users,consumers=['Clock reads carry and Delta',
                'Flush reads carry and publishes its original output image'])


def profile_scope(raw):
    earlier = PROFILE_ROM.read_bytes()
    trace = read(PROFILE)
    assert M.sha(earlier)==trace['ROM_sha256']==PROFILE_PIN
    assert earlier[off(0xa000):off(0xa000)+8192]==raw[off(0xa000):off(0xa000)+8192]
    nmi = trace['nmi_sample']
    counts = nmi['cycles']
    assert nmi['frame']==1508 and nmi['duration']==4818
    assert [counts[f'29:{pc:04x}'] for pc in (0xab21,0xac36,0xab3a,0xac67,0xac75,
                                               0xac84,0xac8a,0xacaa,0xac3b)]==[12,6,6,8,8,48,16,4,4]
    target = sum(v for key,v in counts.items() if key.startswith('29:') and TARGET<=int(key[3:],16)<0xacc8)
    assert target==308
    return dict(earlier_profile_ROM_SHA256=PROFILE_PIN,exact_equal_bank29=True,frame=1508,
                elapsed_NMI=4818,targets=2,clock_commits=1,period_high=0,shift=4,negate=True,
                old_target_cycles=target,successor_target_cycles=146,projected_saving=162)


def direct_mixer(before,after):
    images = [M.bundle(raw) for raw in (before,after)]
    machines = [Sweep.Mixer(image) for image in images]
    addr = lambda n:M.address(images[0],n)
    stats = Counter()

    def execute(m,ctl,div,reload,period,mask,dirty,p):
        mem = m.mem
        m.hw.clear()
        for name in ('GuestExpansionApu','GuestExpansionLast','GuestFxApu','GuestFxDirty'):
            at = addr(name)
            mem[at:at+8] = bytes((i*(p|1)+ctl)&255 for i in range(8)) if name!='GuestFxDirty' else bytes(8)
        mem[addr('GuestMixMask')],mem[addr('GuestMixChanged')] = mask,p&3
        mem[FIRST:LAST] = bytes((period&255,period>>8,0xa1,0x65,ctl,div,reload,0xfd))
        at = addr('GuestFxDirty')
        mem[at+1:at+4] = bytes((dirty&1,dirty&2,dirty&4))
        c = N.NesMPU(memory=m,pc=FLUSH)
        c.a,c.x,c.y,c.p,c.sp = p,21,71,0x20|(p&0xcf),224
        c.stPushWord(0x5aff)
        targets,fast = 0,0
        for _ in range(800):
            if c.pc==0x5b00:
                break
            targets += c.pc==TARGET
            fast += c.pc==0xac12
            c.step()
        else:
            raise AssertionError(('Flush bound',hex(c.pc),c.sp))
        return (registers(c),bytes(mem[0x7282:LAST]),tuple(m.hw)),c.processorCycles,targets,fast

    def compare(ctl,div,reload,period,mask,dirty,p):
        a,b = [execute(m,ctl,div,reload,period,mask,dirty,p) for m in machines]
        assert a[0]==b[0] and a[2]==b[2] and a[3]==0,(ctl,div,reload,period,mask,dirty,p,a,b)
        assert b[3]<=b[2] and (b[2]==0)==(mask&1==0)
        stats[b[3],a[1]-b[1]] += 1
        return a[1]-b[1]

    for ctl,div,reload,period in product(range(12,256,16),(0,1,7),(0,1),range(8,256)):
        compare(ctl,div,reload,period,1|(ctl&2),0,period)
    for ctl,div,period,dirty in product(range(256),(0,1,255),
            (0,7,8,15,16,127,128,136,255,256,1023,2047,2048,65535),(0,7)):
        compare(ctl,div,ctl&1,period,ctl&3,dirty,ctl)
    for p in range(256):
        assert compare(0xbc,0,0,0x80,3,0,p)==162
    return dict(cases=sum(stats.values()),savings=[[fast,cycles,n] for (fast,cycles),n in sorted(stats.items())],
                sampled_shape_cycle_saving=162)


def lifecycle(before,after):
    warmed = [M.seed(M.bundle(raw),41) for raw in (before,after)]

    def step(pair,fields):
        for m in pair:
            m.writes.clear()
            N.put(m,**fields)
        a,b = [M.direct(m,'AudioUpdate') for m in pair]
        assert a[1]==b[1],fields
        exact_state(*pair)
        return a[0]-b[0]

    for t in range(160):
        step(warmed,dict(AreaMusicQueue=int(t==0),FrameCounter=t))
    results = []
    for owner in range(42):
        pair = [slim_fork(m) for m in warmed]
        saves = []
        for t in range(32):
            fields = dict(SelectedCharacter=owner if t<16 else 41,
                          AreaMusicQueue=1 if t in (0,16) else 4 if t==10 else 0,
                          EventMusicQueue=64 if t in (13,24) else 0,
                          Square1SoundQueue=32 if t%5==2 else 0,Square2SoundQueue=1 if t%7==3 else 0,
                          NoiseSoundQueue=1 if t%8==3 else 0,GamePauseStatus=int(t in (14,15)),FrameCounter=t)
            saves.append(step(pair,fields))
        results.append(dict(owner=owner,saving_range=[min(saves),max(saves)],sum_saved=sum(saves)))
    return dict(exact_AudioUpdate=160+42*32,owner_round_trips=42,results=results)


def native_nmi(image,owner,flag,shape,cuts=None):
    m = M.seed(image,owner)
    N.put(m,NmiDisable=flag,AreaMusicQueue=1,Square1SoundQueue=32,Square2SoundQueue=1,
          NoiseSoundQueue=1,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
    lag,normal = lag_path(m)
    c = V.start(m)
    visits = Counter()
    minimum = c.sp

    def watch(z):
        nonlocal minimum
        pc = z.pc
        minimum = min(minimum,z.sp)
        if pc in (lag,normal):
            visits[pc] += 1
        if not 0xa000<=pc<0xc000 or m.rawtags[1]!=157:
            return
        if pc==FLUSH:
            visits['flush'] += 1
            if shape:
                ctl,div,reload,period = shape
                assert N.get(m,'GuestMixMask')&1
                N.put(m,GuestSweepControl=ctl,GuestSweepDivider=div,GuestSweepReload=reload)
                m[FIRST:FIRST+2] = bytes((period&255,period>>8))
                at = M.address(image,'GuestFxDirty')
                m[at+1:at+4] = bytes(3)
        if pc in (0xab21,0xab3a,0xac36):
            visits[pc] += 1
        if cuts is not None and (CLOCK<=pc<0xacc8 or FAST<=pc<CLOCK):
            key = pc,z.sp,z.p&4,N.get(m,'GuestSweepTicks')
            if not z.p&4 and key not in cuts:
                cuts[key] = V.clone(z),tuple(m.writes)

    run(c,lambda z:(z.pc,z.sp)==(0x5b00,214),watch)
    assert visits[lag]==int(flag==255) and visits[normal]==int(flag==0)
    assert registers(c,0xef)==(0xa7,23,61,0x24,214)
    return c,visits,minimum


def vectors(before,after):
    images = [M.bundle(raw) for raw in (before,after)]
    profiles = (
        ('natural',41,None),('both_shift4',41,(0x8c,0,0,0x80)),
        ('sample_shift4',41,(0xbc,0,0,0x80)),('final_only_shift4',41,(0xbc,7,1,0xff)),
        ('high_shift4',41,(0xbc,0,0,0x700)),('under8',41,(0x8c,0,0,7)),
        ('fallback_positive',41,(0x84,0,0,0x80)),('fallback_negative',41,(0x8b,0,0,0x80)),
        ('native_legacy',0,None),('native_samus',2,None),('native_rygar',7,None),('native_smb2',25,None),
    )
    previous = N.Bus
    N.Bus = V.Guard
    counts, min_sp, samples = Counter(), [255,255], []
    try:
        for flag,(case,owner,shape) in product((0,255),profiles):
            cuts = {}
            a,old,lo = native_nmi(images[0],owner,flag,shape)
            b,new,hi = native_nmi(images[1],owner,flag,shape,cuts)
            assert old==new,(case,flag,old,new)
            V.same_end(a,b)
            exact_state(a.memory,b.memory)
            save = a.processorCycles-b.processorCycles
            if case=='sample_shift4':
                assert save==162 and new[0xab21]==2 and new[0xab3a]==new[0xac36]==1
            min_sp[0] = min(min_sp[0],lo,hi)
            for cut,prior in cuts.values():
                min_sp[1] = min(min_sp[1],V.interrupt(cut))
                resume_matches(cut,prior,b)
                counts[flag] += 1
            samples.append(dict(case=case,owner=owner,NmiDisable=flag,cycles_saved=save,
                                native_mixer_calls=new['flush'],IRQ_cuts=len(cuts)))
    finally:
        N.Bus = previous
    assert min(min_sp)>0x7a and min(counts.values())>50
    return dict(actual_NMI_cases=len(samples),nested_IRQ=dict(counts),minimum_SP=min_sp,samples=samples)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    out.mkdir(exist_ok=True)
    dest = out/'proof.json'
    assert not dest.exists()
    before = BASE.read_bytes()
    assert M.sha(before)==PIN
    after,patches = linked(before,out)
    callers = source_callers(before)
    peak = profile_scope(before)
    direct = direct_mixer(before,after)
    print('Exact complete mixer and 162-cycle sample-shaped case passed.',flush=True)
    owners = lifecycle(before,after)
    print('Exact original AudioUpdate owner handoffs and SFX passed.',flush=True)
    isr = vectors(before,after)
    refs = (Path(__file__),SOURCE,BASE,PROFILE_ROM,PROFILE,FUNDING,Sweep.SOURCE,
            R/'src/reset.s',R/'src/guest_audio.s',Path(V.__file__))
    proof = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),
                 patches=patches,source_callers=callers,native_profile_projection=peak,
                 direct_mixer=direct,lifecycle=owners,vectors=isr,
                 bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in refs})
    dest.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(dest,proof['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
