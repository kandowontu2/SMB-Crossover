"""Controls-only suffix forks from a genuine current first-item prefix."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from unittest.mock import patch

import check_dkjr_platform_contact_1113 as Q

P,H,N,W,L,T=Q.P,Q.H,Q.N,Q.W,Q.L,Q.T


def state(m):
    actor=next((i for i in range(6)if N.get(m,'Enemy_Flag',i)and
        N.get(m,'Enemy_ID',i)==37 and N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i)==336),None)
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        y=N.get(m,'Player_Y_Position'),source_y=m.ram[2][0x210],
        source=m.ram[2][0x6b],prior=m.ram[2][0x6c],fallStart=m.ram[2][0x76],
        fallLimit=m.ram[2][0x7b],source_input=list(m.ram[2][0x60:0x6b]),
        native_input=N.get(m,'SavedJoypadBits'),
        donor_pad=m.ram[2][0x15],donor_direction=m.ram[2][0x54],
        platform_top=N.get(m,'Enemy_Y_Position',actor)if actor is not None else None,
        passenger=N.get(m,'PlatformCollisionFlag',actor)if actor is not None else None)


def main():
    parent=T.load_parent()
    candidate,_=T.transform(parent)
    _,seed=H.cold(parent,parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    m=Q.mounted(seed,candidate);text=T.controller(candidate)
    text=P.once(text,' if game then\n'," if game then\n  if epoch>=490 then finish(true,'first-bridge-prefix');return end\n")
    with redirect_stdout(io.StringIO()):prefix=P.B.route(m,candidate,800,controller_text=text)
    assert prefix['passed']and prefix['receipt']['reason']=='first-bridge-prefix'
    rows=[];writes=[];probe=L.clone(m);Base=type(probe)
    class Watched(Base):
        def __setitem__(self,at,value):
            cpu=getattr(self,'contact_cpu',None)
            watch=isinstance(at,int)and(at==0x75 or at==0xc213 and self.rawtags[2]==2)
            if cpu and watch and self[at]!=value:
                writes.append(dict(age=self.contact_age,PC=cpu.pc,A=cpu.a,X=cpu.x,Y=cpu.y,
                    maps=list(self.rawtags),address=at,before=self[at],after=value,
                    native_y=N.get(self,'Player_Y_Position'),source_y=self.ram[2][0x210],
                    source_state=self.ram[2][0x6b],donor_pad=self.ram[2][0x15],direction=self.ram[2][0x54]))
            return super().__setitem__(at,value)
    probe.__class__=Watched;CPU=N.NesMPU
    class TracedCPU(CPU):
        def step(self):
            self.memory.contact_cpu=self
            return CPU.step(self)
    with patch.object(N,'NesMPU',TracedCPU):
        for age in range(40):
            probe.contact_age=age+1
            if state(probe)['source']==5:break
            Q.frame(probe,0)
    for policy in('neutral','center344','left4','left8'):
        q=L.clone(m);trace=[]
        for age in range(100):
            v=state(q)
            if v['source']==5:break
            pad=(1 if v['x']<343 else 2 if v['x']>345 else 0)if policy=='center344'else 2 if age<(4 if policy=='left4'else 8 if policy=='left8'else 0)else 0
            Q.frame(q,pad)
            if age<12 or age%8==0:trace.append(dict(age=age+1,pad=pad,**state(q)))
        rows.append(dict(policy=policy,updates=age,final=state(q),trace=trace))
    print('DKJR_FIRST_SUFFIX_BRANCHES '+json.dumps(dict(candidate_SHA256=T.PIN,
        prefix_controller_SHA256=sha256(text.encode()).hexdigest(),prefix_updates=prefix['logical_updates'],
        prefix_state=state(m),branches=rows,actual_neutral_X_writers=writes,
        source_or_ability_writes=False,outputs_written=0,
        scope='Genuine authored-item prefix then ordinary-pad in-memory forks. These are diagnostic suffixes, not an unbroken collection or native pass.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
