"""Qualify in-loop empty popup rejection on exact f003."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
import check_mini_lift_admission_async_1108_v1 as Q
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at
from check_mini_visibility_dispatch_1110_v1 import memory
from check_native_relative_offscreen_irq_1110 import StackGuard
import profile_mini_busy_1108_v1 as P


N,R = P.N,P.R
BASE = R/'build/mini-helper-powered-injury-native-1110/candidate.nes'
PIN = 'f003b378b0e5bd862403eae71f267d8c33a3b06e9270548ae20b1d9f6b2f9979'
SOURCE = R/'tools/reference/native_floatey_gate_1110.s'
SPANS = (
    ('ACTOR_LOOP',0x83c7,0x83df,bytes.fromhex('a200860d2060a2206489e8e006d0f320f5a1208c8a8d6a01')),
    ('FLAGPOLE_PACKET',0x86a6,0x86b8,bytes.fromhex('8d6a01a9158d6c01a9b88d6d01a983205a01')),
)
CONTROL,TIMER,STOP = 0x10d,0x129,0x5b00


def offset(pc):
    return 16+126*8192+(pc&8191)


def build(raw, out):
    packet = SPANS[1][3][:-3]+bytes.fromhex('4c5a01')
    assert raw[offset(0x8998):offset(0x89aa)]==packet
    assert raw[offset(0x8964):offset(0x8969)]==bytes.fromhex('bd0d01f012')
    assert raw[offset(0x8969):offset(0x896d)]==bytes.fromhex('c90b9005')
    with tempfile.TemporaryDirectory(dir=out,prefix='link-') as name:
        cfg,obj,data = (Path(name)/f'floatey.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY {'+''.join(f'{label}:start=${lo:04x},size={hi-lo},file=%O;'
                        for label,lo,hi,_ in SPANS)+'}\nSEGMENTS {'+
                       ''.join(f'{label}:load={label},type=ro;' for label,*_ in SPANS)+'}',encoding='utf-8')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',data],check=True)
        code = data.read_bytes()
    patches,cursor = [],0
    for label,lo,hi,old in SPANS:
        size = hi-lo
        start = offset(lo)
        assert len(old)==size and raw[start:start+size]==old
        replacement = code[cursor:cursor+size]
        assert len(replacement)==size
        patches.append(dict(file_offset=start,old_hex=old.hex(),new_hex=replacement.hex(),
                            physical_PRG=126,CPU_half_open=[lo,hi],role=label))
        cursor += size
    assert cursor==len(code)
    return install(raw,patches),patches


def inputs(m, owner, pattern, age, *, clear_enemies=False):
    if clear_enemies:
        for slot in range(6):
            m[0x10+slot]=0
    N.put(m,SelectedCharacter=owner,TimerControl=0,AreaParserTaskNum=7,NmiDisable=255,
          CurrentBank=128,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,ObjectOffset=0)
    m.raw_page(0,254)
    m.raw_page(1,128)
    for slot,tag in enumerate(pattern):
        m[CONTROL+slot],m[TIMER+slot] = tag,age
    m.writes.clear()
    m.ppu_log.clear()
    m.ram_writes.clear()


def run_at(m, pc, *, stop=STOP, x=0, y=0, a=85, flags=0x21, visit=None):
    c = cpu_at(m,pc,248,flags,x=x,y=y)
    c.a = a
    run(c,lambda z:(z.pc,z.sp)==(stop,246 if stop!=STOP else 248),visit)
    return c


def paired(a,b, case):
    assert registers(a)==registers(b),case
    m,n = a.memory,b.memory
    assert memory(m)==memory(n),case
    # Return-address stack bytes move with the relocated JSRs. Only the
    # completed call stack is live, and all outward hardware writes match.
    writes = lambda bus:[(address,value) for address,value in bus.writes if not 0x17b<=address<0x200]
    assert writes(m)==writes(n) and m.ram_writes==n.ram_writes,case
    return a.processorCycles-b.processorCycles


def qualify(before,after):
    images = [P.bundle(raw) for raw in (before,after)]
    worlds = [[P.fixture(b,n,False,False) for b in images] for n in (0,3)]
    cases = Counter()
    patterns = ([0]*7,[0,1,0,0,0,0,0],[0,0,0,6,0,0,0],
                [0,0,0,0,0,0xff,0],[1,5,6,10,11,0xff,6],[0,0,0,0,0,0,11])
    for owner, crowd, pattern, age in product((0,2,4,6,7,25,32,41,51),range(2),patterns,(0,1,42,43,44,48,255)):
        active = sum(bool(value) for value in pattern[:6])
        buses = [slim_fork(m) for m in worlds[crowd]]
        before_lives = N.get(buses[0],'NumberofLives')
        for m in buses:
            inputs(m,owner,pattern,age,clear_enemies=not crowd)
        a,b = [run_at(m,0x83c7,stop=0x83df) for m in buses]
        saving = paired(a,b,(owner,crowd,pattern,age))
        assert saving==12*(6-active)-6,(owner,crowd,pattern,age,saving)
        assert buses[1][CONTROL+6]==pattern[6] and buses[1][TIMER+6]==age
        if age==43 and any(tag>=11 for tag in pattern[:6]):
            assert N.get(buses[1],'NumberofLives')==before_lives+sum(tag>=11 for tag in pattern[:6])
            assert N.get(buses[1],'Square2SoundQueue')==64
        cases['actor_loop',saving] += 1

    # The active ingress is unchanged, including 1-up, clamp, timeout and
    # current-player score/HUD writes. Compare the real flagpole award too.
    for owner,player,score,flags in product((0,2,4,7,25,32,41,51),range(2),range(5),(0x21,0x71)):
        outputs = []
        for seed in worlds[0]:
            m = slim_fork(seed)
            inputs(m,owner,[0]*7,0,clear_enemies=True)
            N.put(m,CurrentPlayer=player,FlagpoleScore=score,GameEngineSubroutine=4)
            digit,amount = m[0x864c+score],m[0x8647+score]
            m[0x131+digit] = amount
            outputs.append(run_at(m,0x86a6,stop=0x86b8,x=digit,y=score,a=amount,flags=flags))
        saving = paired(*outputs,('flagpole',owner,player,score,flags))
        assert saving==-6
        cases['flagpole_score',saving] += 1

    # Both ordinary and hit-triggered cases proceed to actual bank4 draw.
    # Score popup timers and positions are deliberately initialized inputs.
    for owner,pattern,age in product((0,7,41),patterns,(0,43,48)):
        outputs = []
        for seed in worlds[0]:
            m = slim_fork(seed)
            inputs(m,owner,pattern,age,clear_enemies=True)
            if owner!=41:
                N.put(m,PlayerStatus=0,PlayerSize=1)
            for slot in range(7):
                m[0x114+slot],m[0x11b+slot] = 64+slot*8,60+slot*8
            outputs.append(run_at(m,P.address(m.bundle,'GameCoreRoutine')))
        saving = paired(*outputs,('GameCore',owner,pattern,age))
        assert saving==12*(6-sum(bool(value) for value in pattern[:6]))-6
        cases['full_GameCore',saving] += 1
    return dict(cycle_savings={kind:dict(sorted((value,n) for (name,value),n in cases.items() if name==kind))
                for kind in ('actor_loop','flagpole_score','full_GameCore')})


def vectors(before,after):
    old,new = map(P.bundle,(before,after))
    original_bus = N.Bus
    N.Bus = StackGuard
    try:
        seed = P.fixture(new,0,False,False)
    finally:
        N.Bus = original_bus
    lag,normal = Q.lag_pcs(seed)
    counts,deepest = Counter(),None

    def inject(c,kind,record):
        nonlocal deepest
        m = c.memory
        snapshot = Q.live(c)
        stop = c.pc,c.sp
        skipped = N.get(m,'NmiSkipped')
        m.vector_floor,m.written_stack = 0x100+c.sp,set()
        if kind=='lag_FF':
            assert N.get(m,'NmiDisable')==255
            c.nmi()
        else:
            assert not c.p&4
            c.irq()
            assert (Q.tags(c),c.pc)==(254,0x8000)
        hits = 0

        def observe(z):
            nonlocal hits,deepest
            assert z.pc!=normal
            hits += z.pc==lag
            if record and kind=='lag_FF' and not z.p&4 and (deepest is None or z.sp<deepest.sp):
                deepest = fork(z)
                deepest.memory.vector_floor = None

        run(c,lambda z:(z.pc,z.sp)==stop,observe)
        m.vector_floor = None
        assert Q.live(c)==snapshot,(kind,stop)
        assert hits==int(kind=='lag_FF') and N.get(m,'NmiSkipped')==(skipped+hits)&255
        assert not any(0x200<=a<0x304 or a==0x4014 for a,_ in m.writes)

    def pair(z,kind):
        a,b = fork(z,old),fork(z)
        inject(a,kind,False)
        inject(b,kind,True)
        assert memory(a.memory)==memory(b.memory)
        assert a.processorCycles==b.processorCycles and a.memory.writes==b.memory.writes
        counts[kind] += 1
        return b

    for owner,case in product((0,41),(0,1,2)):
        m = slim_fork(seed)
        pattern = [1,0,11,0,0,6,0] if case else [0]*7
        inputs(m,owner,pattern,43,clear_enemies=True)
        visited,resumes = set(),[]
        stop = STOP if case!=2 else 0x86b8

        def watch(z):
            point = Q.tags(z),z.pc
            if point in visited or point[0]!=254 or not any(lo<=z.pc<hi for _,lo,hi,_ in SPANS):
                return
            visited.add(point)
            for kind in ('IRQ','lag_FF'):
                resumes.append((point,kind,pair(z,kind)))

        start = P.address(new,'GameCoreRoutine') if case!=2 else 0x86a6
        full = run_at(m,start,stop=stop,visit=watch)
        assert visited
        for point,kind,resumed in resumes:
            run(resumed,lambda z:(z.pc,z.sp)==(stop,full.sp))
            assert registers(full,0xef)==registers(resumed,0xef),(owner,case,point,kind)
            for lo,hi in ((CONTROL,TIMER+7),(0x200,0x304),(0x75b,0x760)):
                assert m[lo:hi]==resumed.memory[lo:hi],(owner,case,lo)
            assert tuple(m.rawtags)==tuple(resumed.memory.rawtags)
            counts['full_resumes'] += 1
    assert deepest is not None
    pair(deepest,'nested_IRQ')
    return dict(counts=counts,deepest_nested_SP=deepest.sp)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    out.mkdir(exist_ok=True)
    raw = BASE.read_bytes()
    assert P.sha(raw)==PIN
    after,patches = build(raw,out)
    foreground = qualify(raw,after)
    print(json.dumps(foreground),flush=True)
    irq = vectors(raw,after)
    inputs = (Path(__file__),SOURCE,BASE,R/'src/game.s',R/'src/screen_render.s')
    proof = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),
                 patches=patches,foreground=foreground,vectors=irq,
                 source_bindings={str(p.resolve().relative_to(R)):P.sha(p.read_bytes()) for p in inputs})
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(SHA256=P.sha(after),vectors=irq)),flush=True)


if __name__=='__main__':
    main()
