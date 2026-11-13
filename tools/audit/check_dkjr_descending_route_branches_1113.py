"""Ordinary-pad suffixes from one genuine pinned full-controller prefix."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from unittest.mock import patch

import check_dkjr_descending_platform_1113 as D

T,Q,P,H,N,W,L=D.T,D.Q,D.P,D.H,D.N,D.W,D.L
LAST=None


def view(m):
    actors=[]
    for i in range(6):
        if N.get(m,'Enemy_Flag',i)and N.get(m,'Enemy_ID',i)==37:
            actors.append(dict(slot=i,left=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
                top=N.get(m,'Enemy_Y_Position',i),speed=N.get(m,'Enemy_Y_Speed',i),
                force=N.get(m,'Enemy_Y_MoveForce',i),passenger=N.get(m,'PlatformCollisionFlag',i)))
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        y=N.get(m,'Player_Y_Position'),source_x=m.ram[2][0x213],source_y=m.ram[2][0x210],
        source=m.ram[2][0x6b],native_state=N.get(m,'Player_State'),
        box=list(m[0x658:0x65c]),saved_pad=N.get(m,'SavedJoypadBits'),actors=actors)


def prefix():
    global LAST
    Q.T=T
    parent=T.load_parent()
    candidate,_=T.transform(parent)
    _,seed=H.cold(parent,parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    m=Q.mounted(seed,candidate);text=T.controller(candidate,full=True)
    text=P.once(text,'local function drive()\n',
        "local function drive()\n if updates>=1000 then finish(true,'genuine-lower-prefix');return end\n")
    with redirect_stdout(io.StringIO()):prefix=P.B.route(m,candidate,1300,controller_text=text)
    assert prefix['passed']and prefix['receipt']['reason']=='genuine-lower-prefix'
    LAST=(candidate,L.clone(m))
    return candidate,m,dict(controller_SHA256=sha256(text.encode()).hexdigest(),
        logical_updates=prefix['logical_updates'],state=view(m))


def main():
    candidate,m,proof=prefix()
    rows=[]
    for policy in('right','neutral4-right-A8','right-A8','right-A16'):
        q=L.clone(m);writes=[];trace=[];Base=type(q);CPU=N.NesMPU
        class Watched(Base):
            def __setitem__(self,at,value):
                c=getattr(self,'route_cpu',None)
                delta=((value-self[at]+128)&255)-128 if isinstance(at,int)and at in(0x75,0xc213)else 0
                if c is not None and isinstance(at,int)and(at==0x75 or at==0xc213 and self.rawtags[2]==2)and abs(delta)>=4:
                    if len(writes)<160:writes.append(dict(age=self.route_age,PC=c.pc,maps=list(self.rawtags),
                        address=at,before=self[at],after=value,native_y=N.get(self,'Player_Y_Position'),
                        source_y=self.ram[2][0x210],source_state=self.ram[2][0x6b],R=list(self[3:11])))
                return super().__setitem__(at,value)
        q.__class__=Watched
        class TracedCPU(CPU):
            def step(self):
                self.memory.route_cpu=self
                return CPU.step(self)
        with patch.object(N,'NesMPU',TracedCPU):
            for age in range(180):
                q.route_age=age+1
                if view(q)['source']==5:break
                if policy=='right':pad=1
                elif policy=='neutral4-right-A8':pad=0 if age<4 else 129 if age<12 else 1
                else:pad=129 if age<(8 if policy=='right-A8'else 16)else 1
                Q.frame(q,pad);q.route_cpu=None
                if age<24 or age%8==0:
                    v=view(q);actor=next((a for a in v.pop('actors')if a['left']==480),None)
                    trace.append(dict(age=age+1,pad=pad,actor480=actor,**v))
                if view(q)['x']>=530 and view(q)['y']==176:break
        rows.append(dict(policy=policy,updates=age+1,final=view(q),trace=trace,actual_X_writers=writes))
    print('DKJR_DESCENDING_LOWER_FORKS '+json.dumps(dict(candidate_SHA256=T.PIN,
        prefix_controller_SHA256=proof['controller_SHA256'],prefix_updates=proof['logical_updates'],
        prefix=view(m),branches=rows,script_RAM_writes=False,outputs_written=0,
        scope='Genuine Main1000 prefix and ordinary controller-pad clone suffixes. Not an unbroken full-stage or Mesen pass.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
