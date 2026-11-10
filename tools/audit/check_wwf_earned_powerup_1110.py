"""Actual ordinary-controller WWF first-item caller diagnostic; stdout only."""
import argparse
from collections import Counter,deque
from hashlib import sha256
import json

import check_thomas_powerup_progression_1110 as Images
import check_roster_powerup_continuation_1110 as Frames

C,W,N,L=Images.C,Images.W,Images.N,Images.L


def route(seed,return_arena=False,quiet=False):
    m=L.clone(seed);calls=Counter();trace=deque(maxlen=8);events=[];jump=None;birth=None;pickup=None;pending=None;collect_pending=None
    def done(**fields):return (fields,m) if return_arena else fields
    targets={(((W.location(m.bundle,n)-16)//8192)|128,W.address(m.bundle,n)):n for n in
        ('NrPickupCollision','HandlePowerUpCollision','HuPickup','HuMature','GuestBeginPowerup','GuestPowerupUpdate') if n in m.bundle['syms']}
    def state():
        return dict(epoch=epoch,frame=N.get(m,'FrameCounter'),x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),native_state=N.get(m,'Player_State'),status=N.get(m,'PlayerStatus'),
            engine=N.get(m,'GameEngineSubroutine'),lives=N.get(m,'NumberofLives'),
            active=N.get(m,'GuestPowerupActive'),age=N.get(m,'GuestPowerupAge'),timer=N.get(m,'TimerControl'))
    def actors():
        return [dict(slot=i,flag=N.get(m,'Enemy_Flag',i),id=N.get(m,'Enemy_ID',i),state=N.get(m,'Enemy_State',i),
            kind=N.get(m,'PowerUpType',i),x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
            y=N.get(m,'Enemy_Y_Position',i)) for i in range(6) if N.get(m,'Enemy_Flag',i)]
    def observe(mem,c):
        nonlocal pending,collect_pending
        if collect_pending and (c.pc,c.sp)==collect_pending['stop']:
            p=collect_pending;collect_pending=None;slot=p['slot']
            events.append(dict(event='native_collection_return',slot=slot,state=state(),
                erased=not N.get(m,'Enemy_Flag',slot),floaty=N.get(m,'FloateyNum_Control',slot),
                sound=N.get(m,'Square2SoundQueue'),carry=bool(c.p&1)))
        if pending and (c.pc,c.sp)==pending['stop']:
            p=pending;pending=None
            events.append(dict(event=p['name']+'_return',before=p['before'],actor=p.get('actor'),
                carry=bool(c.p&1),state=state(),A=c.a,X=c.x,Y=c.y))
        if c.pc<0x8000:return
        name=targets.get((m.rawtags[(c.pc-0x8000)//8192],c.pc))
        if not name:return
        calls[name]+=1
        if name=='HandlePowerUpCollision':
            events.append(dict(event='actual_native_collection_entry',state=state(),actors=actors()))
            collect_pending=dict(slot=c.x,stop=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1,c.sp+2))
        if name=='NrPickupCollision' and len(events)<12:
            a=next((v for v in actors() if v['slot']==c.x),None);s=state()
            if a and a['id']==46 and a['state']&128 and abs(a['x']-s['x'])<22 and abs(a['y']-s['y'])<35:
                pending=dict(name=name,before=s,actor=a,
                    stop=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1,c.sp+2))
    for epoch in range(1200):
        s=state();a=actors()
        assert s['lives']==2,('life lost',s,a,list(trace))
        item=next((v for v in a if v['id']==46),None)
        if item and birth is None:birth=dict(player=s,actor=item);events.append(dict(event='authored_item_birth',value=birth))
        if s['active']:
            pickup=pickup or s;pad=0
            if epoch-pickup['epoch']>=90:return done(passed=False,reason='natural_freeze_stuck',events=events,final=s,calls=dict(calls))
        elif pickup:
            pad=1
            if s['x']>=pickup['x']+16:return done(passed=True,events=events,final=s,calls=dict(calls))
        elif jump is not None and epoch-jump<18:pad=128
        else:
            near=any(v['id']==6 and not v['state']&32 and 0<v['x']-s['x']<=40 for v in a)
            if near:pad=64 if epoch%18<2 else 0
            elif jump is None and s['x']>=328:jump=epoch;pad=128
            else:pad=1 if s['x']<401 else 0
        if epoch%100==0 or (jump is not None and epoch-jump<8):
            q=dict(**s,pad=pad,actors=a);trace.append(q)
            if not quiet:print(json.dumps(dict(event='WWF_natural_route',state=q)),flush=True)
        m.controller_pad=pad;Frames.frame(m,observe)
        if birth and epoch-birth['player']['epoch']>550 and events:
            return done(passed=False,reason='authored_item_no_accepted_collection',birth=birth,
                events=events,final=state(),trace=list(trace),calls=dict(calls))
    return done(passed=False,reason='controller_bound',events=events,final=state(),trace=list(trace),calls=dict(calls))


def main():
    a=argparse.ArgumentParser();a.add_argument('--role',type=int,default=0,choices=range(6));args=a.parse_args()
    raw=Images.Ex.proposal(Images.Route.A5.proposal(W.ROM.read_bytes())[0])[0]
    assert sha256(raw).hexdigest()==Images.PIN
    b=W.Symbols.bundle();b['raw']=raw
    row=next(r for r in C.Starts.C.inventory(raw)['rows'] if r['slot']==28 and r['cycle']==args.role)
    opening,m=C.cold(b,row);q=route(m)
    print(json.dumps(dict(parent_ROM_SHA256=Images.PIN,name=row['name'],source_CPU_only=True,
        Mesen_run=False,ROM_written=False,output_files=0,genuine_cold=opening,result=q)),flush=True)


if __name__=='__main__':main()
