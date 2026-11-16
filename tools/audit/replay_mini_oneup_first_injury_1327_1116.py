"""Same retained-lift L inputs up to first real native1→0 tier writer."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_retained_lifts_1327_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='712f91248acb98a446f6565fd69886300bf27a4e2d2ad8bd3fff79a8a58a122e'


@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    c=deepcopy(Previous.bindings(raw));b=Current.bindings(raw)['bundle']
    for name in('ObjectOffset','InjuryTimer','Enemy_X_Speed','Enemy_MovingDir'):c['ram'][name]=W.address(b,name)
    pc,at=W.address(b,'ForceInjury'),W.location(b,'ForceInjury');bank=(at-16)//8192
    c['hooks']['ForceInjury']=dict(pc=pc,offset=at-16,work=False,bytes=list(raw[at:at+8]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))
    at=Current.CODE_AT+0xc82;c['hooks']['MiniInjury']=dict(pc=0xac82,offset=3*8192+0xc82,work=True,bytes=list(raw[at:at+4]));assert raw[at:at+4]==bytes.fromhex('a9001860')
    _,body=Previous.controller(raw).split('\n',1)
    helper="""local function injuryActors()
 local t={};for i=0,5 do local e=actor(i);e.box=box('EnemyBoundingBoxCoord',i);e.vx=r('Enemy_X_Speed',i);e.direction=r('Enemy_MovingDir',i);t[#t+1]=e end;return t
end
hook('ForceInjury',function()if M.scope_passed and r('PlayerStatus')==1 and not route.injury then
 local c=emu.getState();route.injury={PC=c['cpu.pc'],SP=c['cpu.sp'],P=c['cpu.ps'],state=state(),ObjectOffset=r('ObjectOffset'),actors=injuryActors(),player_box=box('BoundingBox_UL_Corner'),buttons=buttons}
 returning(function(t)route.injury.returned={PC=t.pc,SP=t.sp,state=state(),timer=r('InjuryTimer')}end)
end end)
hook('MiniInjury',function()if route.injury and not route.injury_leaf then
 local c=emu.getState();route.injury_leaf={PC=c['cpu.pc'],SP=c['cpu.sp'],A=c['cpu.a'],P=c['cpu.ps']}
 returning(function(t)local z=emu.getState();route.injury_leaf.returned={PC=t.pc,SP=t.sp,A=z['cpu.a'],P=z['cpu.ps'],C=z['cpu.ps']&1}end)
end end)
emu.addMemoryCallback(guard(function(_,v)
 if M.scope_passed and r('PlayerStatus')==1 and v==0 and not route.first_tier_loss then
  local c=emu.getState();route.first_tier_loss={PC=c['cpu.pc'],SP=c['cpu.sp'],P=c['cpu.ps'],before=state(),after_power=v,ObjectOffset=r('ObjectOffset'),actors=injuryActors(),player_box=box('BoundingBox_UL_Corner'),buttons=buttons}
 end
end),emu.callbackType.write,C.ram.PlayerStatus)
"""
    body=Previous.Previous.once(body,"hook('GameLoop',function()",helper+"hook('GameLoop',function()")
    body=Previous.Previous.once(body,"local function drive()\n if not menuDone then return end;identity()","local function drive()\n if not menuDone then return end;if route.first_tier_loss then finish(false,'Same-controls first actual tier-loss diagnostic');return end;identity()")
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text);return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw).encode()),parent_L_factory_SHA256=BASE_SHA,
        scope='Same controls until first native power1→0; mapped actual ForceInjury/private A0CLC leaf and exact writer/actor/physical boxes, diagnostic only')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
