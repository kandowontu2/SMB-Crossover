"""Passive current four-pipe query contexts; no candidate code/flag overlay."""
from collections import Counter
from hashlib import sha256
import json
from unittest.mock import patch
import check_prince_pit_foot_context_1114 as Pit

F,P,N=Pit.F,Pit.P,Pit.N


def run(raw):
    text=Pit.controller(raw)
    old="switch('first-gap-approach',1)"
    assert text.count(old)==1
    text=text.replace(old,"final=s;finish(true,'Passive original four-pipe climb query checkpoint')",1)
    model,opening=Pit.Base.cold(raw);native=N.NesMPU
    buffer=P.W.address(model.bundle,'Block_Buffer_1');attrs=P.W.address(model.bundle,'MTileAttribute')
    counts=Counter();maps=Counter();conflicts=[];seen=set()
    def solid(m,x,y):
        if not(0<=x<65536 and 32<=y<240):return False
        tile=m[buffer+((x//256)&1)*208+((y-32)//16)*16+((x&255)//16)]
        return bool(m[attrs+tile]&1)
    class Trace(native):
        def step(self):
            m=self.memory
            if self.pc in(0xbde5,0xb310)and m.rawtags[1]==3:
                maps[str((self.pc,*m.rawtags))]+=1
            if self.pc in(0xbe92,0xbece,0xbef8)and m.rawtags[1]==3 and self.p&1:
                s=m.ram[2];same=s[0x7c]==s[0x83]
                qx=int.from_bytes(m.ram[3][0x1369:0x136b],'little')
                qy=int.from_bytes(m.ram[3][0x136b:0x136d],'little')
                actor=int.from_bytes(s[0x60f:0x611],'little')-8;cell=qx&0xfff0
                overlap=max(cell,actor)<min(cell+16,actor+16)
                climbing=s[0x618]in(2,6)or s[0x616]==10
                counts[str((s[0x616],s[0x618],same,overlap,self.pc==0xbe92))]+=1
                reject=same and not overlap and(self.pc==0xbe92 or solid(m,qx,(qy&0xfff0)-1))
                if reject and climbing:
                    row=dict(pc=self.pc,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                        sx=actor+8,y=N.get(m,'Player_Y_Position'),action=s[0x616],mode=s[0x618],pose=s[0x617],
                        foot=int.from_bytes(s[0x84:0x86],'little'),query=[qx,qy],row=s[0x7c],current_row=s[0x83])
                    key=tuple(row[k]for k in('pc','x','action','mode','pose'))
                    if key not in seen:
                        seen.add(key);conflicts.append(row)
                        if len(conflicts)>24:conflicts.pop(12)
            return super().step()
    with patch.object(P,'controller',lambda image:text),patch.object(N,'NesMPU',Trace):q=P.route(model,raw,2300)
    return dict(ROM_SHA256=F.PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),opening=opening,
        passed=q['passed'],updates=q['logical_updates'],reason=q['reason'],terminal=q['terminal'],
        solid_query_context_counts=dict(counts),potential_hang_climb_filter_conflicts=len(seen),
        actual_query_PRG_RAM_map_counts=dict(maps),
        conflict_examples=conflicts,passive_policy_observer_only=True,
        source_overlay=False,gameplay_state_seeds=0,outputs=0,Mesen=False)


if __name__=='__main__':print(json.dumps(run(F.ROM.read_bytes()),separators=(',',':')),flush=True)
