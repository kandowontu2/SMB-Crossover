"""Actual Main/NMI continuation of explicit directed current pickup fixtures.

This derivative does not call row33 repeatedly at a frozen epoch. The mature
actor is synthetic and declared; all subsequent updates run real Main/NMI.
No natural earned-pickup, emulator, cadence or complete-powerup claim.
"""
import argparse
from collections import Counter, deque
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import audit_current_roster_powerups_1110 as C
import check_ff_white_mushroom_current_1110 as W
import check_ff_head_lifetime_irq_1110 as L

N=C.N


def frame(m,observe=None):
    idle=W.address(m.bundle,'IdleLoop')
    W.clear_logs(m);N.consume(m)
    c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
    L.finish(m,c,(idle+12,252),observe=observe)
    assert not m.blocked


def directed(seed,kind,epochs):
    m=L.clone(seed);slot=5
    N.put(m,NmiDisable=255,ObjectOffset=slot)
    for name,value in (('Enemy_Flag',1),('Enemy_ID',46),('Enemy_State',128),('PowerUpType',kind),
        ('Enemy_X_Position',N.get(m,'Player_X_Position')),('Enemy_PageLoc',N.get(m,'Player_PageLoc')),
        ('Enemy_Y_Position',N.get(m,'Player_Y_Position')),('Enemy_Y_HighPos',1)):
        m[W.address(m.bundle,name)+slot]=value
    N.invoke(m,'NrPrepare',a=kind,x=slot,y=0)
    m[W.address(m.bundle,'Enemy_State')+slot]=128
    before=C.state(m);calls=Counter();path=deque(maxlen=36);Base=N.NesMPU
    tracked={}
    for name in ('HandlePowerUpCollision','NrPickup','HuPickup','HuPowerup','NrNativePowerupDispatch',
        'GuestBeginPowerup','GuestPowerupUpdate','MarioSourceBeginFreeze','MarioSourcePowerupCollision'):
        if name in m.bundle['syms']:
            tracked[(((W.location(m.bundle,name)-16)//8192)|128,W.address(m.bundle,name))]=name
    class TracedMPU(Base):
        def step(self):
            if self.pc>=0x8000:
                tag=self.memory.rawtags[(self.pc-0x8000)//8192]
                name=tracked.get((tag,self.pc))
                if name:
                    calls[name]+=1
                    path.append(dict(name=name,tag=tag,PC=self.pc,frame=N.get(m,'FrameCounter'),
                        age=N.get(m,'GuestPowerupAge'),A=self.a,X=self.x,Y=self.y,P=self.p))
            return super().step()
    with patch.object(N,'NesMPU',TracedMPU):
        returned=N.invoke(m,'HandlePowerUpCollision',a=kind,x=slot,y=0)
        collected=C.state(m);rows=[]
        for epoch in range(epochs):
            m.controller_pad=0
            frame(m)
            row=dict(epoch=epoch,frame=N.get(m,'FrameCounter'),**C.state(m))
            if epoch<4 or epoch>=epochs-2 or row['GuestPowerupAge']>=58 or not row['GuestPowerupActive']:
                rows.append(row)
            if not row['GuestPowerupActive'] and epoch>=2:break
    return dict(kind=kind,before=before,collected=collected,returned=returned,
        real_Main_NMI_updates=epoch+1,states=rows,calls=dict(calls),last_callback_path=list(path),
        hosted_recovered=not N.get(m,'GuestPowerupActive'),actor_erased=not collected['actor_flag'],
        scope='Explicit synthetic mature prepared pickup followed by distinct actual Main/NMI updates; not a natural pickup')


def natural(seed,epochs):
    m=L.clone(seed);trace=deque(maxlen=32);events=[];jump=None;prelean=None;pickup=None;phase='approach'
    def now(epoch):
        return dict(epoch=epoch,frame=N.get(m,'FrameCounter'),
            x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
            state=N.get(m,'Player_State'),status=N.get(m,'PlayerStatus'),engine=N.get(m,'GameEngineSubroutine'),
            active=N.get(m,'GuestPowerupActive'),age=N.get(m,'GuestPowerupAge'),timer=N.get(m,'TimerControl'),
            lives=N.get(m,'NumberofLives'),source_speed=m.ram[2][0x90]+256*m.ram[2][0x94],
            source_angle=m.ram[2][0xac],source_air=m.ram[2][0xb0],source_crash=m.ram[2][0x98],
            actors=[dict(slot=i,flag=N.get(m,'Enemy_Flag',i),id=N.get(m,'Enemy_ID',i),
                state=N.get(m,'Enemy_State',i),kind=N.get(m,'PowerUpType',i),
                x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
                y=N.get(m,'Enemy_Y_Position',i)) for i in range(6) if N.get(m,'Enemy_Flag',i)])
    calls=Counter();pending=None
    targets={(((W.location(m.bundle,n)-16)//8192)|128,W.address(m.bundle,n)):n for n in
        ('HandlePowerUpCollision','GuestBeginPowerup','GuestPowerupUpdate','HuPowerup')}
    def observe(_memory,c):
        nonlocal pending
        if pending and (c.pc,c.sp)==pending:
            events.append(dict(event='natural_native_collection_return',state=now(epoch),
                sound=N.get(m,'Square2SoundQueue'),floaty=N.get(m,'FloateyNum_Control',5),
                actor_erased=N.get(m,'Enemy_Flag',5)==0,carry=bool(c.p&1)))
            pending=None
        if c.pc<0x8000:return
        name=targets.get((m.rawtags[(c.pc-0x8000)//8192],c.pc))
        if name:
            calls[name]+=1
            if name=='HandlePowerUpCollision':
                events.append(dict(event='natural_native_collection_entry',state=now(epoch),A=c.a,X=c.x,Y=c.y))
                pending=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1,c.sp+2)
    for epoch in range(epochs):
        q=now(epoch)
        assert q['lives']==2,('natural life lost',q,list(trace))
        if q['active']:
            if pickup is None:pickup=q;events.append(dict(event='natural_freeze',state=q))
            pad=0
            if epoch-pickup['epoch']>=90:
                return dict(passed=False,events=events,final=q,calls=dict(calls),
                    reason='naturally earned hosted powerup still active after90 actual Main/NMI updates')
        elif pickup:
            pad=1
            if q['x']>=pickup['x']+16:
                events.append(dict(event='recovered_move',state=q));return dict(passed=True,events=events,calls=dict(calls))
        elif phase=='approach':
            pad=65
            if q['x']>=400:phase='recover';pad=0
        elif phase=='recover':
            pad=0
            if not q['source_speed'] and not q['source_crash']:phase='return';pad=66
        elif phase=='return':
            pad=66
            if q['x']<=365:phase='prelean';prelean=epoch;pad=74
        elif phase=='prelean':
            pad=74
            if epoch-prelean>=4:phase='jump';jump=epoch;pad=202
        elif phase=='jump':
            pad=202 if epoch-jump<8 else 0
            if epoch-jump>=8:phase='wait'
        else:pad=0
        q['pad']=pad
        q['phase']=phase
        if epoch%32==0 or (prelean is not None and epoch-prelean<20):
            trace.append(q);print(json.dumps(dict(event='natural_route',state=q)),flush=True)
        m.controller_pad=pad;frame(m,observe)
    return dict(passed=False,events=events,final=now(epochs),trace=list(trace),
        reason='bounded ordinary-controller first-block route incomplete')


def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--epochs',type=int,default=85)
    p.add_argument('--kind',type=int,choices=range(4));p.add_argument('--natural',action='store_true');a=p.parse_args()
    raw=C.ROM.read_bytes();assert sha256(raw).hexdigest()==C.PIN
    b=W.Symbols.bundle();b['raw']=raw
    inventory=C.Starts.C.inventory(raw)
    row=next(r for r in inventory['rows'] if r['name']==a.name)
    opening,m=C.cold(b,row)
    if a.natural:
        q=natural(m,a.epochs)
        print(json.dumps(dict(name=a.name,natural=q,ROM_SHA256=C.PIN,source_CPU_only=True,
            Mesen_run=False,output_files=0,ROM_written=False)),flush=True)
        return
    results=[]
    for kind in (range(4) if a.kind is None else [a.kind]):
        q=directed(m,kind,a.epochs);results.append(q)
        print(json.dumps(dict(event='actual_continuation',name=a.name,result=q)),flush=True)
    print(json.dumps(dict(passed=True,audit_only=True,ROM_SHA256=C.PIN,name=a.name,opening=opening,
        cases=len(results),hosted_stuck=[q['kind'] for q in results if not q['hosted_recovered']],
        actor_not_admitted=[q['kind'] for q in results if not q['actor_erased']],
        output_files=0,ROM_written=False,Mesen_run=False,source_CPU_only=True)),flush=True)


if __name__=='__main__':main()
