"""Separate standing-head controls; retain the generic-policy negative."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import replay_battletoads_stock_6a3_1116 as Previous

Current,R,ROM,PIN,W,N=Previous.Current,Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N
TEMPLATE=R/'tools/playthroughs/battletoads_food_align_6a3_1116.lua'
BASE_SHA='ee5228be6664320d54663d54c4a00b24b4ab3b48885e83fb5b0ede33faa4a83c'
BODY_SHA='224e13326b90b0b988e5e8aeff64c926edf0fb634d5c00c53f8d4655bc63941e'

@lru_cache(maxsize=4)
def bindings(raw,key='rash',kind='mushroom'):
    assert Current.digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    assert Current.digest(Previous.TEMPLATE.read_bytes())==BODY_SHA
    q=deepcopy(Previous.bindings(raw,key,kind));b=Current.bundle(raw)
    for n in('BlockBufferColli_Head','NativeRarePlayerHeadCollisionCore'):
        pc,at=W.address(b,n),W.location(b,n);bank=(at-16)//8192
        q['hooks'][n]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank,
            bank_SHA256=Current.digest(raw[16+bank*8192:16+(bank+1)*8192]))
    for n in('R2','R3','R4','R5','R6','R7'):q['ram'][n]=W.address(b,n)
    return q

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=4)
def controller(raw,key='rash',kind='mushroom'):
    text=Previous.controller(raw,key,kind);prefix='local C='+Previous.Text.lua(Previous.bindings(raw,key,kind))+'\n'
    assert text.startswith(prefix);text='local C='+Previous.Text.lua(bindings(raw,key,kind))+'\n'+text[len(prefix):]
    marker=" if food.phase=='mushroom'then buttons=travel(c);return end"
    text=once(text,marker,TEMPLATE.read_text())
    marker="local age=0"
    probes="""hook('BlockBufferColli_Head',function()
 if not food.headAt or food.phase~='mushroom-head'then return end
 local q={before=state(),pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],Y=emu.getState()['cpu.y']}
 returning(function(t)
  q.after=state();q.A=emu.getState()['cpu.a'];q.P=emu.getState()['cpu.ps'];q.return_pc=t.pc;q.return_sp=t.sp
  q.R={r('R2'),r('R3'),r('R4'),r('R5'),r('R6'),r('R7')}
  food.head_queries=food.head_queries or{};if#food.head_queries<16 then food.head_queries[#food.head_queries+1]=q end
 end)
end)
hook('NativeRarePlayerHeadCollisionCore',function()
 food.actual_head=food.actual_head or{}
 if#food.actual_head<8 then food.actual_head[#food.actual_head+1]={state=state(),A=emu.getState()['cpu.a'],pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}end
end)
"""
    text=once(text,marker,probes+marker)
    text=once(text,"if mainReturns>4000 or frame>14000 then", "if mainReturns>2600 or frame>10000 then")
    Previous.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text

def metadata(raw,key='rash',kind='mushroom'):
    q=Previous.metadata(raw,key,kind);q.update(controller_SHA256=Current.digest(controller(raw,key,kind).encode()),
        aligned_factory_SHA256=Current.digest(Path(__file__).read_bytes()),aligned_controls_SHA256=Current.digest(TEMPLATE.read_bytes()),
        retained_generic_policy_negative='0d2d470821f31120a2486419d126d5153b1549b5e6075c45938ee2d84165c1db')
    return q

def family(kind='mushroom'):
    from types import SimpleNamespace
    return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,key,kind),metadata=lambda raw,key:metadata(raw,key,kind))
