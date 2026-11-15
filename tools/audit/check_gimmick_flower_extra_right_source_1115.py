"""One observed native extra-Right consumption, genuine source prefix/write trace."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import sys
from unittest.mock import patch
import replay_gimmick_flower_trajectory_current_1115 as Parent
import check_gimmick_flower_board_current_1115 as Source

R,ROM,W,N,PIN=Parent.R,Parent.ROM,Parent.W,Parent.N,Parent.PIN
Frozen,IDENTITIES,normalize,bindings=Parent.Frozen,Parent.IDENTITIES,Parent.normalize,Parent.bindings


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    text=Parent.controller(raw,key)
    assert sha256(text.encode()).hexdigest()=='ff47b6e21d5275af199b38f61d0975c8b581c3e5d2d5841e804d1958662c893b'
    old="  phase='left-chase';age=0;mark(c,'actual-star-launched')"
    new="  if not flower.diagnostic_extra_Right then flower.diagnostic_extra_Right=true;return{right=true,a=true}end\n"+old
    text=Parent.once(text,old,new);Frozen.LuaRuntime().compile(text)
    return text


def metadata(raw,key='mr_gimmick'):
    q=Parent.metadata(raw,key);q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        scope='Source diagnostic only: one extra ordinary Right+A consumption matching actual native26639; genuine prefix and all behavior gates retained. No native/game/physics/helper change')
    return q


if __name__=='__main__':
    raw=ROM.read_bytes();base=N.NesMPU;frame=Source.Runner.Frames.frame
    trace=[];ticks=0;armed=None;bundle=None
    b=dict(W.Symbols.bundle(),raw=raw)
    addresses={name:W.address(b,name)for name in('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_X_Speed','Player_Y_Speed','Player_State','PlayerStatus','SavedJoypadBits','GmRam0091','GmRam00AE','GmRam00B8','GmRam009A','GmRam00A4','GmRam00CC','GmRam00C2','GmRam00D7')}
    def snapshot(m):
        q={name:m[at]for name,at in addresses.items()}
        q['x']=q['Player_X_Position']+256*q['Player_PageLoc'];q['tick']=ticks
        q['scratch']=[m[i]for i in range(8)];return q
    class Trace(base):
        def step(cpu):
            global armed
            m=cpu.memory;px=m[addresses['Player_X_Position']];page=m[addresses['Player_PageLoc']]
            possible=page==4 and 196<=px<=224 and m[addresses['GmRam0091']]==1
            if armed is None and possible:armed=ticks
            watching=armed is not None and ticks<=armed+5
            if not watching:return super().step()
            before=snapshot(m);pc=cpu.pc;tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
            instruction=[m[(pc+i)&65535]for i in range(3)];sp=cpu.sp
            q=super().step();after=snapshot(m)
            if before['x']!=after['x']:
                row=dict(PC=pc,tag=tag,instruction=instruction,SP=sp,before=before,after=after)
                trace.append(row)
                if len(trace)>32:trace.pop(16)
            return q
    def clock(m,*args,**kwargs):
        global ticks
        if kwargs.get('whole_pass'):ticks+=1
        return frame(m,*args,**kwargs)
    def forbid(*args,**kwargs):raise RuntimeError('Extra-Right source diagnostic attempted files/Mesen')
    facade=sys.modules[__name__]
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Runner.Native,'run',forbid),patch.object(Source,'Factory',facade),patch.object(Source.Runner,'Factory',facade),patch.object(Source.Runner,'cold',Source.cold),patch.object(N,'NesMPU',Trace),patch.object(Source.Runner.Frames,'frame',clock):
        q=Source.Runner.run(raw,'mr_gimmick',2500)
    r=q['receipt'];f=r.get('natural_flower',{});t=f.get('trajectory_diagnostic',{})
    result=dict(gameplay_passed=q['passed'],receipt_SHA256=q['source_receipt_SHA256'],controller_SHA256=q['metadata']['controller_SHA256'],reason=r.get('reason'),
        Main=r.get('Main_returned'),seconds=q['seconds'],armed_Main=armed,writes=trace,returns=t.get('returns',[])[:18],terminal=r.get('terminal'),outputs=0,Mesen_run=False,gameplay_seeds=0)
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
