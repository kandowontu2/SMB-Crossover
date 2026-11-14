"""Bounded actual-current Prince query/return trace, normal controls only.

Primitive calls are observed, not injected. Cold/menu and the full approach
execute in the existing CPU model. No ROM, actor, coordinate or ability seed.
"""
from collections import Counter
from hashlib import sha256
import argparse,json,re
from unittest.mock import patch

import check_prince_pipe_usability_1114 as Base

F,P,N=Base.Factory,Base.P,Base.P.N


def trace(raw,*,target=1,pad=8):
    F.authenticate(raw)
    points=[];world=[];pending=[];counts=Counter();native=N.NesMPU
    lo,hi=(390,448)if target==1 else(560,608)
    def snap(m):
        s=m.ram[2]
        word=lambda at:int.from_bytes(s[at:at+2],'little')
        return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),sx=word(0x60f),sy=s[0x611],
            action=s[0x616],pose=s[0x617],mode=s[0x618],foot=word(0x84),
            raw_query=word(0x78),cell=word(0x7d),surface=word(0x7f),
            index=s[0x4b1],row=s[0x7c],current_row=s[0x83],sword=s[0x6ee],
            pad=s[0x40a],wall_timer=N.get(m,'SideCollisionTimer'))
    def retain(rows,q):
        # Keep first16 plus last32 distinct records; every call contributes
        # to aggregate counts even when the detailed ring is full.
        if rows and rows[-1]==q:return
        rows.append(q)
        if len(rows)>48:rows.pop(16)
    class Trace(native):
        def step(self):
            m=self.memory;pc=self.pc
            if pending and(pc,self.sp)==pending[-1]['return']:
                p=pending.pop();out=snap(m)
                if p['kind']=='point':
                    q=dict(p['state'],query=p['query'],raw=self.a,carry=self.p&1)
                    counts['point_calls']+=1
                    if self.p&1:counts['solid_point_calls']+=1
                    retain(points,q)
                else:
                    q=dict(p['state'],material=self.a,out_cell=out['cell'],out_row=out['row'],out_surface=out['surface'])
                    counts[f'material_{self.a}']+=1;retain(world,q)
            # BDE2 is an LDY prefix that falls through BDE5 with the same
            # stack frame. Observe BDE5 once, including either public entry.
            if pc in(0xb310,0xbde5)and m.rawtags[(pc-0x8000)//8192]==3:
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
                if lo<=x<=hi and m.ram[2][0xab]==0xa7:
                    kind='point'if pc==0xb310 else'world'
                    ret=((m[0x100+((self.sp+1)&255)]|m[0x100+((self.sp+2)&255)]<<8)+1)&65535
                    q=dict(kind=kind,state=snap(m),**{'return':(ret,(self.sp+2)&255)})
                    if kind=='point':q['query']=[int.from_bytes(m.ram[3][0x1369:0x136b],'little'),int.from_bytes(m.ram[3][0x136b:0x136d],'little')]
                    pending.append(q)
            return super().step()
    with patch.object(N,'NesMPU',Trace):
        q,_=Base.run(raw,target=target,pad=pad,approach='contact')
    observation=q['observation'];observation.pop('samples',None)
    return dict(passed=q['passed'],reason=q['reason'],phase=q['phase'],
        ROM_SHA256=F.PIN,Lua_SHA256=q['metadata']['Lua_SHA256'],
        receipt_SHA256=q['receipt_SHA256'],terminal=q['terminal'],observation=observation,
        primitive_calls_observed_only=True,query_counts=dict(counts),points=points,world=world,
        gameplay_state_seeds=0,outputs=0,Mesen=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=int,choices=(1,2),default=1)
    p.add_argument('--pad',type=int,choices=(8,9,136),default=8);a=p.parse_args()
    q=trace(F.ROM.read_bytes(),target=a.target,pad=a.pad)
    print(json.dumps(q,separators=(',',':')),flush=True)
