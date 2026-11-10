"""Ordinary-controller current Thomas first-block diagnostic; stdout only."""
from collections import Counter,deque
from hashlib import sha256
import json

import audit_current_roster_powerups_1110 as C
import check_roster_powerup_continuation_1110 as Frames
import check_ff_mux_unused_tail_1110 as A5

W,N=C.W,C.N


def route(seed):
    m=C.L.clone(seed);trace=deque(maxlen=24);events=[];calls=Counter();pending=None
    jump=None;pickup=None;head_pending=[];heads=[];mature_pending=None;collect_slot=None
    handle=(((W.location(m.bundle,'HandlePowerUpCollision')-16)//8192)|128,W.address(m.bundle,'HandlePowerUpCollision'))
    tick=(((W.location(m.bundle,'GuestPowerupUpdate')-16)//8192)|128,W.address(m.bundle,'GuestPowerupUpdate'))
    mature=(((W.location(m.bundle,'NrPickupCollision')-16)//8192)|128,W.address(m.bundle,'NrPickupCollision'))
    diagnostic={(((W.location(m.bundle,n)-16)//8192)|128,W.address(m.bundle,n)):n
        for n in ('BlockBufferColli_Head','PlayerHeadCollision','SetupPowerUp') if n in m.bundle['syms']}
    def state():
        return dict(epoch=epoch,frame=N.get(m,'FrameCounter'),x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),engine=N.get(m,'GameEngineSubroutine'),lives=N.get(m,'NumberofLives'),
            status=N.get(m,'PlayerStatus'),active=N.get(m,'GuestPowerupActive'),age=N.get(m,'GuestPowerupAge'),
            timer=N.get(m,'TimerControl'),source_input=m.ram[2][0x68],source_action=m.ram[2][0x69])
    def actors():
        return [dict(slot=i,flag=N.get(m,'Enemy_Flag',i),id=N.get(m,'Enemy_ID',i),state=N.get(m,'Enemy_State',i),
            kind=N.get(m,'PowerUpType',i),x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
            y=N.get(m,'Enemy_Y_Position',i)) for i in range(6) if N.get(m,'Enemy_Flag',i)]
    def observe(mem,c):
        nonlocal pending,mature_pending,collect_slot
        if mature_pending and (c.pc,c.sp)==mature_pending['stop']:
            q=mature_pending;mature_pending=None
            events.append(dict(event='actual_near_mature_admission_return',before=q['before'],actor=q['actor'],
                state=state(),carry=bool(c.p&1),A=c.a,X=c.x,Y=c.y,P=c.p,
                following_opcode=m[c.pc],following_PC=c.pc))
        for p in head_pending[:]:
            if (c.pc,c.sp)==p['stop']:
                head_pending.remove(p);p.update(after=state(),A=c.a,P=c.p,R4=m[4],R5=m[5],
                    crouching=N.get(m,'CrouchingFlag'),group=m[0xeb])
                if len(heads)<40:heads.append(p)
        if pending and (c.pc,c.sp)==pending:
            events.append(dict(event='native_collection_return',state=state(),actors=actors(),
                slot=collect_slot,erased=not N.get(m,'Enemy_Flag',collect_slot),
                sound=N.get(m,'Square2SoundQueue'),floaty=N.get(m,'FloateyNum_Control',collect_slot),carry=bool(c.p&1)))
            pending=None
        if c.pc<0x8000:return
        point=(m.rawtags[(c.pc-0x8000)//8192],c.pc)
        if point==mature:
            calls['NrPickupCollision']+=1
            s=state();a=next((a for a in actors() if a['slot']==c.x),None)
            if a and a['id']==46 and a['state']&128 and a['y']>=170 and abs(a['x']-s['x'])<=18 and len(events)<8:
                mature_pending=dict(before=s,actor=a,
                    stop=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1,c.sp+2))
        name=diagnostic.get(point)
        if name:
            calls[name]+=1
            if name=='BlockBufferColli_Head' and jump is not None and epoch-jump<20:
                head_pending.append(dict(before=state(),entryY=c.y,
                    stop=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1,c.sp+2)))
        if point==tick:calls['GuestPowerupUpdate']+=1
        if point==handle:
            calls['HandlePowerUpCollision']+=1
            collect_slot=c.x
            events.append(dict(event='native_collection_entry',state=state(),actors=actors(),A=c.a,X=c.x,Y=c.y))
            pending=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1,c.sp+2)
    for epoch in range(700):
        s=state();assert N.get(m,'SelectedCharacter')==10
        assert s['lives']==2,('life lost',s,events,list(trace))
        if s['active']:
            if pickup is None:pickup=s;events.append(dict(event='earned_freeze',state=s))
            pad=0
            if epoch-pickup['epoch']>=90:
                return dict(passed=False,natural_earned=True,reason='stuck90actualMain',events=events,final=s,calls=dict(calls))
        elif pickup:
            pad=1
            if s['x']>=pickup['x']+16:return dict(passed=True,natural_earned=True,events=events,final=s,calls=dict(calls))
        elif jump is None and s['x']>=325:jump=epoch;pad=73
        elif jump is not None and epoch-jump<8:pad=73
        else:pad=65 if s['x']<400 else 0
        if epoch%32==0 or (jump is not None and epoch-jump<15):
            q=dict(**s,pad=pad,actors=actors());trace.append(q)
            print(json.dumps(dict(event='natural_Thomas_route',state=q)),flush=True)
        m.controller_pad=pad;Frames.frame(m,observe)
    return dict(passed=False,natural_earned=pickup is not None,reason='routebound',events=events,final=state(),trace=list(trace)[-4:],heads=heads[-3:],calls=dict(calls))


def main():
    # Downloads may advance after this fixed-parent diagnostic. Reconstruct
    # the exact frozena5 input from retainedc10; never silently repin C.PIN.
    raw=A5.proposal(W.ROM.read_bytes())[0];assert sha256(raw).hexdigest()==C.PIN
    b=W.Symbols.bundle();b['raw']=raw
    row=next(r for r in C.Starts.C.inventory(raw)['rows'] if r['name']=='THOMAS')
    opening,m=C.cold(b,row);result=route(m)
    print(json.dumps(dict(ROM_SHA256=C.PIN,source_CPU_only=True,Mesen_run=False,ROM_written=False,
        output_files=0,opening=opening,result=result)),flush=True)


if __name__=='__main__':main()
