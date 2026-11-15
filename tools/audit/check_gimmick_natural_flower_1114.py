"""Zero-output source execution of the ordinary Gimmick Flower route."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch
import replay_gimmick_natural_flower_1114 as F

N,W,Frames=F.N,F.W,F.Runner.Frames


def state(m):
    r=lambda name,i=0:N.get(m,name,i)
    word=lambda lo,hi:r(lo)+256*r(hi)
    return dict(x=word('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),
        vx=r('GmRam00CC'),vy=r('GmRam00C2'),ground=r('GmRam036E'),
        star=r('GmRam0091'),flags=r('GmRam00D7'),
        sx=word('GmRam00AF','GmRam00B9')/16,sy=word('GmRam009B','GmRam00A5')/16,
        svx=r('GmRam00CD'),svy=r('GmRam00C3'),face=r('GmRam030A'),
        hp=r('GmRam0346'),cap=r('GmRam002B'),inventory=r('GmRam0036'),
        next=r('GmNextSpecial'),held=r('GmRam0039'),lives=r('NumberofLives'),
        score=F.Previous.digit_value(m))


def mature_seed(raw):
    """Retain one genuine compiled-control prefix in RAM; no state restoration file."""
    old=Frames.frame;captured={};ticks=0
    class Captured(Exception):pass
    def frame(m,*args,**kw):
        nonlocal ticks
        q=old(m,*args,**kw)
        if kw.get('whole_pass'):
            ticks+=1
            for i in range(6):
                if (N.get(m,'Enemy_Flag',i),N.get(m,'Enemy_ID',i),N.get(m,'PowerUpType',i))==(1,46,1)and N.get(m,'Enemy_State',i)>=128:
                    assert N.get(m,'GmRam0346')==N.get(m,'GmRam002B')==3
                    assert N.get(m,'GmRam0039')==0 and N.get(m,'GmNextSpecial')==1
                    assert F.Previous.digit_value(m)>=1100
                    captured.update(memory=N.fork(m),Main=ticks,slot=i,state=state(m),
                        actor=dict(x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
                            y=N.get(m,'Enemy_Y_Position',i),state=N.get(m,'Enemy_State',i)))
                    raise Captured()
        return q
    with patch.object(Frames,'frame',frame):
        try:F.run(raw)
        except Captured:pass
    assert captured,'Genuine mature Flower prefix did not reach capture'
    print('MATURE '+json.dumps({k:v for k,v in captured.items()if k!='memory'},separators=(',',':')),flush=True)
    return captured


class Branch:
    """Only ordinary pads mutate this genuine-prefix clone; hooks only observe."""
    def __init__(self,seed):
        self.m=N.fork(seed);self.t=0;self.rides=[];self.pickups=[];self.trace=[]
        self.config=F.bindings(seed.bundle['raw']);self.pending=None
    def step(self,pad):
        owner=self;base=N.NesMPU
        entry=self.config['hooks']['GmRideStar'];exit=self.config['hooks']['GmRideStarReturn']
        pickup=self.config['hooks']['GmPickup']
        def match(cpu,h):
            return cpu.pc==h['pc']and(cpu.pc<0x8000 or owner.m.rawtags[(cpu.pc-0x8000)//8192]==(h.get('bank',0)|128))
        class Observe(base):
            def step(cpu):
                if match(cpu,entry):owner.pending=state(owner.m)
                elif match(cpu,exit)and owner.pending:
                    before=owner.pending;after=state(owner.m);owner.pending=None
                    if before['ground']<128 and before['vy']<128 and before['flags']&64 and after['ground']==128 and after['vy']==0:
                        owner.rides.append(dict(t=owner.t,before=before,after=after))
                if match(cpu,pickup):owner.pickups.append(dict(t=owner.t,a=cpu.a,state=state(owner.m)))
                return super().step()
        self.m.controller_pad=pad
        with patch.object(N,'NesMPU',Observe):Frames.frame(self.m,whole_pass=True)
        self.t+=1
        q=state(self.m)
        if self.t%4==0:self.trace.append(dict(t=self.t,pad=pad,**q))
        return q


def explore(raw):
    capture=mature_seed(raw);seed=capture['memory'];rows=[]
    for direction in(0,1,2):
        b=Branch(seed)
        for t in range(65):
            q=b.step((128 if t<35 else 0)|direction)
        rows.append(dict(kind='direct',direction=direction,end=q,min_y=min(x['y']for x in b.trace),pickups=b.pickups,trace=b.trace))
    return dict(ROM_SHA256=sha256(raw).hexdigest(),capture={k:v for k,v in capture.items()if k!='memory'},branches=rows,outputs=0,Mesen=False)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--explore',action='store_true');args=ap.parse_args()
    raw=F.ROM.read_bytes()
    def forbid(*a,**k):raise RuntimeError('Gimmick Flower source attempted file or Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(F.Runner.Native,'run',forbid):q=explore(raw)if args.explore else F.run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not args.explore:assert q['passed'],'Ordinary Gimmick Flower route remains unqualified'
