"""Same F/dash inputs up to first tier loss; readonly causal snapshots."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_celeste_flower_00bb_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='84f7b18bf4d97d18d8f47bf024d8e3ef2f2757ca15f8c1b10ced88ca6a11b1b6'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    c=deepcopy(Previous.bindings(raw));b=Current.bundle(raw)
    for name in('ObjectOffset','InjuryTimer','CmInjuryStatus'):c['ram'][name]=W.address(b,name)
    for name in('CmInjuryStart','ForceInjury'):
        pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
        c['hooks'][name]=dict(pc=pc,bank=bank,offset=at-16,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    _,body=Previous.controller(raw).split('\n',1)
    observer="""local function nearby()
 local a={};for i=0,5 do local e=actor(i);e.box=box('EnemyBoundingBoxCoord',i);a[#a+1]=e end;return a
end
hook('ForceInjury',function()if stock.flower_scope_passed and r('CmTier')==2 then dash.force_injury={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp'],state=state(),ObjectOffset=r('ObjectOffset'),buttons=buttons,actors=nearby()}end end)
hook('CmInjuryStart',function()if stock.flower_scope_passed and r('CmTier')==2 then
 local q={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp'],state=state(),ObjectOffset=r('ObjectOffset'),buttons=buttons,actors=nearby()};dash.injury_entry=q
 returning(function(t)q.returned={PC=t.pc,SP=t.sp,state=state(),injury_timer=r('InjuryTimer')}end)
end end)
emu.addMemoryCallback(guard(function(_,v)
 if stock.flower_scope_passed and r('CmTier')==2 and v<2 and not dash.first_tier_loss then
  local cpu=emu.getState();dash.first_tier_loss={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],P=cpu['cpu.ps'],before=state(),after_tier=v,ObjectOffset=r('ObjectOffset'),buttons=buttons,actors=nearby(),player_box=box('BoundingBox_UL_Corner')}
 end
end),emu.callbackType.write,C.ram.CmTier)
"""
    marker='local function drive()';assert body.count(marker)==1;body=body.replace(marker,observer+marker,1)
    marker=' local c=context();buttons=flowerPolicy(c)'
    replacement=""" if dash.first_tier_loss then dash.after_loss=state();finish(false,'Same-controls first earned tier-loss diagnostic');return end
 local c=context()
 if stock.flower_scope_passed and c.x>=1280 and c.x<1900 and(not dash.last_probe_x or math.abs(c.x-dash.last_probe_x)>=24)then
  dash.safe_samples=dash.safe_samples or{};if#dash.safe_samples<12 then
   local safe=true;local cells={};for dx=0,112,16 do local f,h=c.block(c.x+dx,208),c.block(c.x+dx,176);if f==0 or f==35 or h~=0 then safe=false end;cells[#cells+1]={x=c.x+dx,floor=f,head=h}end
   dash.safe_samples[#dash.safe_samples+1]={state=state(),grounded=c.grounded,terrain_safe=safe,enemy=c.enemy(),cells=cells};dash.last_probe_x=c.x
  end
 end
 buttons=flowerPolicy(c)"""
    assert body.count(marker)==1;body=body.replace(marker,replacement,1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw);q.update(controller_SHA256=digest(controller(raw).encode()),probe_factory_SHA256=digest(Path(__file__).read_bytes()),
        controls_identical_until_first_loss=True,scope='Same F/dash inputs; first real tier writer/injury and <=12 floor/enemy snapshots, diagnostic only')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
