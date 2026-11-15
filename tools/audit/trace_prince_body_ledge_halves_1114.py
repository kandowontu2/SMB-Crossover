"""Actual first-three Up ledge callers and native point returns, no seeds."""
from hashlib import sha256
import json
from unittest.mock import patch
import check_prince_body_world_1114 as Game
import current_prince_body_research_input_1114 as Current

C,P,N=Game.C,Game.P,Game.N


def run(current):
    raw,info=C.proposal(current.reference1daca);m,opening=Game.cold(raw)
    text=Game.Factory.controller(raw,mode='earned')
    old="          switch('third-park',65)";assert text.count(old)==1
    text=text.replace(old,"          final=s;finish(true,'Actual first-three ledge trace');return",1)
    for caller in(0xa484,0xa490):
        assert bytes(m.ram[3][caller-0xa000:caller-0xa000+3])==bytes.fromhex('20e2bd')
    base=N.NesMPU;world=[];points=[];rows=[];seen=set();commits=0
    def returning(cpu):
        sp=cpu.sp;ret=((m[0x100+((sp+1)&255)]|m[0x100+((sp+2)&255)]<<8)+1)&65535
        return ret,(sp+2)&255,m.rawtags[(ret-0x8000)//8192]if ret>=0x8000 else None
    class CPU(base):
        def step(self):
            nonlocal commits
            if self.memory is m:
                s=m.ram[2];tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
                key=self.pc,self.sp,tag
                if points and key==points[-1][0]:
                    _,point,row=points.pop();point.update(tile=self.a,carry=self.p&1);row['points'].append(point)
                if world and key==world[-1][0]:
                    _,row=world.pop();row.update(material=self.a,carry=self.p&1,Row=s[0x7c],CurrentRow=s[0x83],
                        surface=int.from_bytes(s[0x7f:0x81],'little'))
                    signature=tuple(row[k]for k in('pipe','caller','x','raw','Y','material'))
                    if signature not in seen:
                        seen.add(signature);rows.append(row)
                        assert len(rows)<=96,'Bounded ledge summary'
                if self.pc==0xb37c and tag==3:commits+=1
                if self.pc==0xbde5 and tag==3 and s[0x616]==28:
                    x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
                    ret=returning(self)
                    if 390<=x<=768 and ret[0]-3 in(0xa484,0xa490):
                        row=dict(commit=commits,pipe=1 if x<560 else 2 if x<680 else 3,
                            caller=ret[0]-3,x=x,sx=int.from_bytes(s[0x60f:0x611],'little'),sy=s[0x611],
                            raw=int.from_bytes(s[0x78:0x7a],'little'),Y=self.y,pose=s[0x617],mode=s[0x618],
                            points=[])
                        world.append((ret,row))
                if self.pc==0xb310 and tag==3 and world:
                    point=dict(x=int.from_bytes(m.ram[3][0x1369:0x136b],'little'),y=int.from_bytes(m.ram[3][0x136b:0x136d],'little'))
                    points.append((returning(self),point,world[-1][1]))
            return super().step()
    with patch.object(N,'NesMPU',CPU),patch.object(P,'controller',lambda image:text):proof=P.route(m,raw,1800)
    assert proof['passed']and proof['terminal']['x']>=720 and not world and not points,proof
    proof.pop('events',None)
    return dict(composition=info,public_input=current.metadata(),opening=opening,proof=proof,
        ledge_returns=rows,caller_bytes_exact=True,pending_world=len(world),pending_points=len(points),
        scope='Genuine ordinary first-three CPU/Main route; no native cadence claim',
        gameplay_seeds=0,outputs=0,Mesen=False)


if __name__=='__main__':
    q=run(Current.load(Game.Factory.ROM));q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(q,separators=(',',':')),flush=True)
