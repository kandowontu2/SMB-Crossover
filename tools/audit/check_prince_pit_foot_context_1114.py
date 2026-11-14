"""Current421 genuine authored first/second-pit donor feet-query returns.

Frozen tuned original traversal is only a means to reach the pits. It does
not supersede the independently reproduced intuitive pipe-input failures.
"""
from collections import Counter
from hashlib import sha256
import json
from unittest.mock import patch
import check_prince_pipe_usability_1114 as Base

F,P,N=Base.Factory,Base.P,Base.P.N


def controller(raw):
    q=F.authenticate(raw)
    assert sha256(F.FROZEN.read_bytes()).hexdigest()==F.FROZEN_SHA
    text=F.FROZEN.read_text()
    old="local cookie = 'a726021676a00802119275ac7f48cce7'"
    assert text.count(old)==1;text=text.replace(old,f"local cookie = '{q['cookie']}'")
    old="local variant = tonumber(os.getenv('SMB_TEST_VARIANT') or '0')"
    assert text.count(old)==1;text=text.replace(old,f"local variant = 3\nassert(rom=='{F.PIN}','Exact421 pit query diagnostic')")
    text=text.replace('emu.setInput({right=pad&1~=0,','emu.setInput({right=pad&1~=0,left=pad&2~=0,',1)
    text=text.replace('observe(0xd74b,2,','observe(0xd746,2,',1)
    for a,b in(('read(0xd74b)','read(0xd746)'),('read(0xd74c)','read(0xd747)'),('read(0xd74d)','read(0xd748)')):text=text.replace(a,b)
    F.LuaRuntime().compile(text)
    return text


def run(raw):
    text=controller(raw);m,opening=Base.cold(raw);native=N.NesMPU
    pending=[];records=[];counts=Counter();last=None
    def snapshot(m):
        s=m.ram[2]
        return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            sx=int.from_bytes(s[0x60f:0x611],'little'),raw_query=int.from_bytes(s[0x78:0x7a],'little'),
            facing=s[0x615],alternate=s[0x4fe],action=s[0x616],pose=s[0x617],mode=s[0x618],
            foot=int.from_bytes(s[0x84:0x86],'little'),phase=s[0xa6]&3,
            y=N.get(m,'Player_Y_Position'),native_state=N.get(m,'Player_State'))
    class Trace(native):
        def step(self):
            nonlocal last
            m=self.memory
            if pending and(self.pc,self.sp)==pending[-1]['return']:
                q=pending.pop()['state'];q.update(material=self.a,
                    cell=int.from_bytes(m.ram[2][0x7d:0x7f],'little'),
                    surface=int.from_bytes(m.ram[2][0x7f:0x81],'little'))
                counts[str((q['facing'],q['sx']-q['raw_query'],q['material']))]+=1
                key=(q['x'],q['sx']-q['raw_query'],q['material'],q['surface'])
                if key!=last:
                    records.append(q);last=key
                    if len(records)>48:records.pop(16)
            if self.pc==0xbde5 and m.rawtags[1]==3:
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
                if 1040<=x<=1152 or 1320<=x<=1440:
                    ret=((m[0x100+((self.sp+1)&255)]|m[0x100+((self.sp+2)&255)]<<8)+1)&65535
                    pending.append(dict(state=snapshot(m),**{'return':(ret,(self.sp+2)&255)}))
            return super().step()
    with patch.object(P,'controller',lambda image:text),patch.object(N,'NesMPU',Trace):q=P.route(m,raw,2600)
    return dict(ROM_SHA256=F.PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),
        passed=q['passed'],reason=q['reason'],terminal=q['terminal'],updates=q['logical_updates'],
        opening=opening,query_counts=dict(counts),genuine_query_returns=records,
        gameplay_state_seeds=0,source_overlay=False,outputs=0,Mesen=False)


if __name__=='__main__':print(json.dumps(run(F.ROM.read_bytes()),separators=(',',':')),flush=True)
