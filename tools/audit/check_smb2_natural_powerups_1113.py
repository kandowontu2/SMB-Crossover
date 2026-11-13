"""Current SMB2/Doki ordinary-controller native item audit; zero artifacts."""
from collections import Counter,defaultdict
from hashlib import sha256
import argparse
import json
import time
from unittest.mock import patch

import check_smb2_flag_handoff_1113 as Flag
import check_bub_current_budget_1113 as Frames

W=Flag.W
N=W.N
PIN=Flag.PIN


def state(m):
    names=('S2Health','S2MaxHealth','S2Vegetables','S2Size','PlayerStatus',
        'Player_State','S2Air','S2VX','S2VY','S2Held','S2Fresh','NumberofLives')
    s={name:N.get(m,name)for name in names}
    s.update(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        y=N.get(m,'Player_Y_Position'))
    return s


def item(m,i):
    return dict(slot=i,flag=N.get(m,'Enemy_Flag',i),id=N.get(m,'Enemy_ID',i),
        kind=N.get(m,'PowerUpType',i),state=N.get(m,'Enemy_State',i),
        x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
        y=N.get(m,'Enemy_Y_Position',i))


def first_birth(raw,variant=4,limit=900,*,injured=False,collect=False):
    """Real menu/constructor then ordinary controller inputs; no scene seeds."""
    assert sha256(raw).hexdigest()==PIN
    m=Flag.cold(raw,variant);opening=state(m);phase='approach';hold=0
    heads=[];prepares=[];recent=[];tick=0;counts=Counter();birth=None
    pending=None;pickups=[];injuries=[];last_health=opening['S2Health']
    watched={name:(W.address(m.bundle,name),((W.location(m.bundle,name)-16)//8192)|128)
        for name in('NativeRarePlayerHeadCollisionCore','S2MainPrepare','S2MainPickup')}
    def observe(memory,c):
        nonlocal pending
        if pending and(c.pc,c.sp)==(pending['return_pc'],pending['return_sp']):
            q=pending;q['after']=state(memory)
            q.update(erased=N.get(memory,'Enemy_Flag',q['actor']['slot'])==0,
                sound=N.get(memory,'Square2SoundQueue'),popup=N.get(memory,'FloateyNum_Control',q['actor']['slot']))
            pickups.append(q);pending=None
        if c.pc<0x8000:return
        key=(c.pc,memory.rawtags[(c.pc-0x8000)//8192])
        for name,point in watched.items():
            if key!=point:continue
            counts[name]+=1
            if name=='NativeRarePlayerHeadCollisionCore':
                heads.append(dict(tick=tick,a=c.a,s=state(memory)))
                assert len(heads)<=30,'Finite ordinary head attempts'
            elif name=='S2MainPrepare':prepares.append(dict(tick=tick,actor=item(memory,c.x),s=state(memory)))
            elif name=='S2MainPickup':
                sp=c.sp;lo=memory[0x100+((sp+1)&255)];hi=memory[0x100+((sp+2)&255)]
                pending=dict(tick=tick,actor=item(memory,c.x),before=state(memory),
                    return_pc=(lo+256*hi+1)&65535,return_sp=(sp+2)&255)
    for tick in range(1,limit+1):
        s=state(m);pad=0
        if phase=='approach':
            pad=1
            # Ordinary enemy approach uses the already qualified full-route
            # distance/hold. No HP/injury or projectile state is written.
            if hold:
                hold-=1;pad|=128
            elif not injured and not s['S2Air']and not s['S2Held']&128:
                for i in range(6):
                    a=item(m,i)
                    if a['flag']==1 and a['id']<21 and a['state']<32 and 0<a['x']-s['x']<48:
                        hold=23;pad|=128;break
            if s['x']>=326:phase='settle'
        elif phase=='settle':
            vx=s['S2VX'];vx=vx-256 if vx&128 else vx
            if s['x']>329:pad=2
            elif s['x']<328:pad=1
            elif vx>0:pad=2
            elif vx<0:pad=1
            if not s['S2Air']and 328<=s['x']<=329 and vx==0 and not s['S2Held']&128:
                phase='head';hold=23;pad=128
        elif phase=='head':
            if hold:hold-=1;pad=128
            elif not s['S2Air']and not s['S2Held']&128:hold=23;pad=128
        elif phase=='mushroom-collect':
            pad=1 if s['x']<395 else 2 if s['x']>397 else 0
        m.controller_pad=pad;Frames.frame(m,observe=observe)
        now=state(m)
        if now['S2Health']<last_health:injuries.append(dict(tick=tick,before=last_health,after=now))
        last_health=now['S2Health']
        if tick%60==0:recent.append(dict(tick=tick,phase=phase,pad=pad,s=state(m)))
        for i in range(6):
            a=item(m,i)
            if birth is None and a['flag']==1 and a['id']==46:
                birth=dict(item=a,s=state(m))
                if collect:
                    assert injured and a['kind']==0,'Collect mode currently qualifies injured natural Mushroom only'
                    phase='mushroom-collect'
                    break
        if birth is not None and(not collect or pickups):
                if collect:
                    q=pickups[-1]
                    assert q['actor']['state']>=128 and q['actor']['kind']==0
                    assert q['before']['S2Health']==15 and q['before']['S2MaxHealth']==0
                    assert q['after']['S2Health']==47 and q['after']['S2MaxHealth']==1
                    assert q['erased']and q['sound']==32 and q['popup']==6
                return dict(passed=True,scope='real authored first-question preparation/birth'+('/physical mature collector'if collect else' only'),
                    ROM_SHA256=PIN,variant=variant,opening=opening,iterations=tick,
                    birth=birth,heads=heads,prepares=prepares,pickups=pickups,injuries=injuries,
                    native_counts=dict(counts),recent=recent[-6:],state_or_actor_seeds=0,
                    outputs=0,Mesen_run=False,natural_collection_proven=bool(pickups))
        assert N.get(m,'NumberofLives')==2 and N.get(m,'S2Health')>0
    return dict(passed=False,reason='ordinary first-head route bound',variant=variant,
        terminal=state(m),heads=heads,prepares=prepares,recent=recent[-6:],outputs=0)


def run_controller(raw,variant=4,mode='injured-mushroom',limit=1500):
    """Run the exact readonly native Lua decisions on real Main/NMI/controller."""
    import replay_smb2_natural_powerups_1113 as Replay
    began=time.perf_counter();m=Flag.cold(raw,variant)
    text=Replay.controller(raw,variant,mode);lua=Replay.Root.Base.LuaRuntime(unpack_returned_tuples=True)
    callbacks=defaultdict(list);events={};context=dict(cpu=None,exit=None,receipt=None)
    emu=lua.table();emu.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2,nesPpuDebug=3))
    emu.eventType=lua.table_from(dict(inputPolled=0,endFrame=1));emu.callbackType=lua.table_from(dict(exec=0))
    def read(at,kind=0):
        if kind==1:return m.ram[at//8192][at%8192]
        if kind==2:return raw[16+at]
        if kind==3:return m.vram[at&0x3fff]
        return m[at]
    def mapped(at):
        if at<0x8000:return None
        tag=m.rawtags[(at-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(at&8191)))
    def get_state():
        c=context['cpu'];s={f'cpu.{k}':getattr(c,k)if c else 0 for k in('pc','sp','a','x','y','p')}
        s['cpu.ps']=s['cpu.p'];return lua.table_from(s)
    def set_input(pad,port):
        assert port==0
        m.controller_pad=sum(bit for name,bit in(('right',1),('left',2),('down',4),('up',8),
            ('start',16),('select',32),('b',64),('a',128))if pad[name])
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):context['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
    def memory(fn,kind,lo,hi=None):
        for at in range(lo,lo+1 if hi is None else hi+1):callbacks[at].append(fn)
    emu.read,emu.convertAddress,emu.getState,emu.setInput=read,mapped,get_state,set_input
    emu.addMemoryCallback=memory;emu.addEventCallback=lambda fn,kind:events.setdefault(kind,fn)
    emu.stop=lambda code:context.update(exit=code)
    lua.globals().emu=emu;lua.globals().print=emit;lua.globals().CPU_CONTROLLER_OPENING=True
    lua.execute(text)
    native=N.NesMPU
    class Observed(native):
        def step(self):
            context['cpu']=self
            for fn in tuple(callbacks.get(self.pc,())):fn()
            return native.step(self)
    with patch.object(N,'NesMPU',Observed):
        for tick in range(limit):
            events[0]();Frames.frame(m)
            c=context['cpu']
            assert(c.pc,c.sp)==(W.address(m.bundle,'IdleLoop')+12,252)
            for fn in tuple(callbacks.get(c.pc,())):fn()
            events[1]()
            if context['exit']is not None:break
    return dict(passed=context['exit']==0,ROM_SHA256=PIN,variant=variant,mode=mode,
        controller_SHA256=sha256(text.encode()).hexdigest(),seconds=round(time.perf_counter()-began,2),
        logical_Main_NMI_iterations=tick+1,terminal=state(m),receipt=context['receipt'],
        natural_scene_unmodified=True,state_or_actor_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',type=int,choices=range(8),default=4)
    p.add_argument('--limit',type=int,default=900);p.add_argument('--injured',action='store_true');p.add_argument('--collect',action='store_true')
    p.add_argument('--controller',action='store_true');p.add_argument('--mode',choices=('injured-mushroom','healthy-flower-birth'),default='injured-mushroom');args=p.parse_args()
    q=run_controller(Flag.ROM.read_bytes(),args.variant,args.mode,args.limit)if args.controller else first_birth(Flag.ROM.read_bytes(),args.variant,args.limit,injured=args.injured,collect=args.collect)
    print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Ordinary first-question route must reach actual item birth'
