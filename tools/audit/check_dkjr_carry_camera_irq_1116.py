"""Reached carry/camera IRQ and busy-NMI continuations, stdout-only fixtures."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import check_dkjr_carry_camera_components_1116 as K
import check_dkjr_retire_lease_1113 as ISR

C,N,Route=K.C,K.N,K.Route
L=K.Cold.H.L
H=lambda value:sha256(value).hexdigest()


def tag(c):
    return c.memory.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1


def clone(m,c):
    return L.clone(m,c)


def run(m,c,stop,observe=None):
    for _ in range(200000):
        if (c.pc,c.sp)==stop:return
        if observe:observe(m,c)
        assert m[c.pc],('ISR fixture BRK',tag(c),hex(c.pc),c.sp)
        N.NesMPU.step(c)
    raise AssertionError(('ISR fixture bound',hex(c.pc),c.sp))


def full(m,c):
    return ((c.pc,c.a,c.x,c.y,c.p&0xef,c.sp),tuple(m.rawtags),
        tuple(bytes(x) for x in m.ram),bytes(m[:0x100]),bytes(m[0x15a:0x17b]),
        bytes(m[0x200:0x800]),bytes(m[0x5c00:0x8000]),bytes(m.vram),
        tuple(m.chr_latches),m.ppu_addr,m.toggle,m.buffer,m.ppuctrl)


def gameplay(m,c):
    fields=('SelectedCharacter','GameEngineSubroutine','NumberofLives','Player_X_Position',
        'Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_Y_Speed')
    return ((c.pc,c.a,c.x,c.y,c.p&0xef,c.sp),tuple(m.rawtags),
        bytes(m.ram[2]),bytes(m.ram[3]),bytes(m[0x15a:0x17b]),bytes(m[0x200:0x304]),
        tuple(N.get(m,name) for name in fields),
        tuple(bytes(m[N.address(m.bundle,name):N.address(m.bundle,name)+6]) for name in
            ('Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position',
             'Enemy_Y_HighPos','Enemy_Y_Speed','PlatformCollisionFlag')),
        bytes(m.vram),tuple(m.chr_latches))


def start(seed,case):
    m=K.prepare(seed,**{k:v for k,v in case.items() if k in
        ('camera','delta','ready','state','distance')})
    N.put(m,NmiDisable=255)
    for name,value in case.get('fields',{}).items():N.put(m,**{name:value})
    for name,value in case.get('actor',{}).items():m[N.address(m.bundle,name)+2]=value
    slot=case.get('slot',2);entry=case.get('entry','PositionPlayerOnVPlat')
    if entry=='private':
        m.raw_page(1,3);m.raw_page(2,2);N.put(m,CurrentBank=3,CurrentBankC=2)
        c=N.NesMPU(memory=m,pc=0xb6a5);c.a,c.x,c.y,c.p,c.sp=83,slot,91,case.get('P',0x31),224
        c.stPushWord(0x5aff)
    else:
        pc=N.address(m.bundle,entry)
        m[0x16a]=case.get('A',83);m[0x16c],m[0x16d]=pc&255,pc>>8
        c=N.NesMPU(memory=m,pc=N.address(m.bundle,'FarCallCommon'))
        c.a=((N.location(m.bundle,entry)-16)//8192)|128
        c.x,c.y,c.p,c.sp=slot,91,case.get('P',0x31),224;c.stPushWord(0x5aff)
    return m,c


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent',type=Path,required=True)
    args=ap.parse_args()
    parent=args.parent.read_bytes();candidate,composition=C.proposal(parent)
    _,seed=Route.cold(candidate)
    _,_,_,_,_,_,linked=C.Plan.measured(C.reference(parent))
    emitted={row['pc'] for row in linked['instructions']}
    cases=[dict(name='ground-zero',delta=0),dict(name='ground-positive',delta=1),
        dict(name='ground-negative',delta=-8),dict(name='ground-plus8',delta=8),
        dict(name='ground-wrap',camera=0,delta=1),dict(name='cache-not-ready',ready=0),
        dict(name='large-positive',delta=9),dict(name='large-negative',delta=-9),
        dict(name='large-high',delta=300),dict(name='safe-jump',state=3),
        dict(name='safe-fall',state=4,distance=23),dict(name='fatal-fall',state=4,distance=24),
        dict(name='pending-fall',state=4,distance=0),dict(name='I1',P=0x35),dict(name='D1-V1',P=0x79)]
    for name,change in (
        ('bad-slot',dict(slot=6)),('bad-engine',dict(fields={'GameEngineSubroutine':11})),
        ('bad-timer',dict(fields={'TimerControl':1})),('bad-phase',dict(state=5)),
        ('empty-actor',dict(actor={'Enemy_Flag':0})),('low-ID',dict(actor={'Enemy_ID':35})),
        ('high-ID',dict(actor={'Enemy_ID':45})),('actor-high',dict(actor={'Enemy_Y_HighPos':2})),
        ('player-high',dict(fields={'Player_Y_HighPos':2})),
        ('Y-overflow',dict(fields={'Player_Y_Position':224})),
        ('large-wrong-top',dict(actor={'Enemy_Y_Position':207})),
        ('small-wrong-top',dict(actor={'Enemy_ID':43,'Enemy_Y_Position':79})),
        ('small-vanilla-second',dict(actor={'Enemy_ID':43,'Enemy_Y_Position':80})),
        ('small-source-second',dict(actor={'Enemy_ID':43,'Enemy_Y_Position':80,'Enemy_State':208},
            fields={'AreaPointer':0x62,'WorldNumber':1})),
        ('small-otherworld',dict(actor={'Enemy_ID':43,'Enemy_Y_Position':80},fields={'AreaPointer':0x62,'WorldNumber':2})),
        ('air-left-reject',dict(state=4,fields={'Player_X_Position':80,'Player_PageLoc':3})),
        ('air-right-reject',dict(state=4,fields={'Player_X_Position':56,'Player_PageLoc':4})),
    ):
        cases.append(dict(name=name,entry='private',**change))
    seen=set();reached=set();counts=Counter();minimum=255;foreground_min=255
    contexts=[]
    print('DKJR_CAMERA_IRQ_PHASE collect-and-resume',flush=True)
    for case in cases:
        origin=case['name'];m,c=start(seed,case);cuts=[];steps=0;active=False;entry_return=None
        def observe(memory,cpu):
            nonlocal steps,active,entry_return,foreground_min
            foreground_min=min(foreground_min,cpu.sp)
            if (tag(cpu),cpu.pc)==(3,0xb6a5):
                active=True
                entry_return=((memory[0x100+((cpu.sp+1)&255)]+256*memory[0x100+((cpu.sp+2)&255)]+1)&65535,
                              (cpu.sp+2)&255)
            if entry_return==(cpu.pc,cpu.sp):active=False
            own=tag(cpu)==3 and (0xb6a5<=cpu.pc<0xb77b or active and
                (0xb24c<=cpu.pc<0xb2ab or 0xbad2<=cpu.pc<0xbb36))
            if own or active and 0x15a<=cpu.pc<0x17b:
                if cpu.pc in emitted and tag(cpu)==3:reached.add(cpu.pc)
                key=(tag(cpu),cpu.pc,cpu.sp,cpu.p&0xcf)
                if key not in seen:
                    seen.add(key);cuts.append((steps,key))
            steps+=1
        run(m,c,(0x5b00,224),observe)
        expected=gameplay(m,c)
        for step,key in cuts:
            base,cpu=start(seed,case)
            for _ in range(step):N.NesMPU.step(cpu)
            assert (tag(cpu),cpu.pc,cpu.sp,cpu.p&0xcf)==key
            for kind in ('IRQ','lagNMI'):
                if kind=='IRQ' and cpu.p&4:
                    q,z=clone(base,cpu);before=full(q,z);cycle=z.processorCycles;z.irq()
                    assert full(q,z)==before and z.processorCycles==cycle
                    counts['masked_IRQ']+=1;continue
                outputs=[]
                for backing in (candidate,parent):
                    q,z=clone(base,cpu)
                    q.bundle=dict(q.bundle,raw=backing)
                    for window,page in enumerate(q.rawtags):
                        if page&128:q.raw_page(window,page)
                    live=bytes(q[0x101+z.sp:0x200])
                    before_SMC=bytes(q[0x15a:0x17b])
                    low,pending=ISR.inject_checked(z,kind)
                    minimum=min(minimum,low);counts['pending_map_commit']+=int(pending)
                    assert bytes(q[0x101+z.sp:0x200])==live
                    assert bytes(q[0x15a:0x17b])==before_SMC
                    outputs.append((q,z))
                assert full(*outputs[0])==full(*outputs[1]),('Matched unchanged actual ISR',origin,key,kind)
                for q,z in outputs:
                    q.bundle=dict(q.bundle,raw=candidate)
                    for window,page in enumerate(q.rawtags):
                        if page&128:q.raw_page(window,page)
                    run(q,z,(0x5b00,224))
                assert full(*outputs[0])==full(*outputs[1]),('Matched public continuation',origin,key,kind)
                assert gameplay(*outputs[0])==expected,('No-extra-ISR gameplay/SMC/maps',origin,key,kind)
                counts[kind]+=1
        contexts.append(dict(name=origin,new_cuts=len(cuts),foreground_steps=steps))
        print('DKJR_CAMERA_IRQ_PROGRESS '+json.dumps(dict(context=origin,cuts=len(seen),vectors=dict(counts)),separators=(',',':')),flush=True)
    assert emitted<=reached,('Unreached new instructions',sorted(emitted-reached))
    report=dict(passed=True,composition=composition,new_instructions=len(emitted),reached=len(reached),
        reached_cut_shapes=len(seen),vectors=dict(counts),minimum_foreground_SP=foreground_min,minimum_ISR_SP=minimum,
        actual_ISRs_compared_with_unchanged_parent=True,SMC33_and_live_stack_exact=True,
        complete_public_continuation_gameplay_exact=True,contexts=contexts,
        scope='Declared actual public/platform and defensive private source fixtures; no native/full-host-Main claim',
        source_route_and_vertical_negatives_retained=True,output_files=0,native_claim=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_CAMERA_IRQ '+encoded,flush=True)
    print('DKJR_CAMERA_IRQ_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
