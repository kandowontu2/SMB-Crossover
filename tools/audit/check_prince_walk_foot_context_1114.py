"""Genuine normal Right/Left walk query contexts on current421, no overlay."""
from collections import Counter
from hashlib import sha256
import json
from unittest.mock import patch
import check_prince_pipe_usability_1114 as Base

F,P,N=Base.Factory,Base.P,Base.P.N


def controller(raw):
    text=F.controller(raw,target=1,approach='prefix')
    anchor='local function tick()\n'
    assert text.count(anchor)==1
    body=r'''
local walk={marks={}}
late.footWalk=walk
local function footWalk(s)
 if progress=='settle-start'and commits-changedAt>=4 then switch('foot-right',1)
 elseif progress=='foot-right'and s.x>=176 then walk.right=s;switch('foot-left',2)
 elseif progress=='foot-left'and s.facing==0 and s.x<=48 then
  walk.left=s;final=s;finish(true,'Bounded genuine right and left walking feet contexts')
 end
end
'''
    text=text.replace(anchor,body+anchor,1)
    anchor='  local enemy=enemyNear(s.x)\n'
    assert text.count(anchor)==1
    text=text.replace(anchor,"  do footWalk(s);return end\n"+anchor,1)
    F.LuaRuntime().compile(text)
    return text


def run(raw):
    text=controller(raw);model,opening=Base.cold(raw)
    native=N.NesMPU;records=[];counts=Counter();seen=set()
    class Trace(native):
        def step(self):
            if self.pc==0xbde5 and self.memory.rawtags[1]==3:
                m=self.memory;s=m.ram[2];sx=int.from_bytes(s[0x60f:0x611],'little')
                rq=int.from_bytes(s[0x78:0x7a],'little')
                row=dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                    sx=sx,raw_query=rq,facing=s[0x615],alternate=s[0x4fe],
                    action=s[0x616],pose=s[0x617],mode=s[0x618],index=self.y,
                    source_phase=s[0xa6]&3,foot=int.from_bytes(s[0x84:0x86],'little'),
                    native_y=N.get(m,'Player_Y_Position'),native_state=N.get(m,'Player_State'))
                key=(row['facing'],row['alternate'],sx-rq)
                counts[str(key)]+=1
                if row['facing']==0 and row['alternate']==0 and sx-rq==31:
                    k=(row['x']&31,row['action'],row['pose'],self.y)
                    if k not in seen:
                        seen.add(k);records.append(row)
                        if len(records)>32:records.pop(16)
            return super().step()
    with patch.object(P,'controller',lambda image:text),patch.object(N,'NesMPU',Trace):
        proof=P.route(model,raw,1200)
    return dict(ROM_SHA256=F.PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),
        opening=opening,passed=proof['passed'],terminal=proof['terminal'],
        reason=proof['reason'],logical_updates=proof['logical_updates'],
        facing_alternate_query_delta_counts=dict(counts),
        actual_nonalternate_left_feet_examples=records,
        source_overlay=False,gameplay_state_seeds=0,outputs=0,Mesen=False)


if __name__=='__main__':print(json.dumps(run(F.ROM.read_bytes()),separators=(',',':')),flush=True)
