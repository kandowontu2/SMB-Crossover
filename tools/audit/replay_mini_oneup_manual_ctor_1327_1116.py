"""Same existing-support inputs; observe the actual shared manual constructor."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_vertical_1327_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='e2fa9d1cd035583e5bf185fea1b48b668916134ec8b5cf51d3b6f064b57a7eda'


@lru_cache(maxsize=1)
def bindings(raw):
    c=deepcopy(Previous.bindings(raw));at=16+64*8192+(0xb378&8191)
    assert raw[at:at+4]==bytes.fromhex('a5a4c901'),'Actual shared manual constructor entry'
    c['hooks']['ManualPlatform']=dict(pc=0xb378,offset=at-16,work=False,bytes=list(raw[at:at+8]),bank_SHA256=H(raw[16+64*8192:16+65*8192]));return c


@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw).split('\n',1)
    observer="""hook('ManualPlatform',function()
 if not M.scope_passed or not item.summon_request or item.manual_birth then return end
 local z=emu.getState();local q={PC=z['cpu.pc'],SP=z['cpu.sp'],A=z['cpu.a'],X=z['cpu.x'],Y=z['cpu.y'],state=state(),stage=tostring(r('WorldNumber')+1)..'-'..tostring(r('LevelNumber')+1),area=r('AreaNumber')}
 item.manual_calls=item.manual_calls or{};assert(#item.manual_calls<8);item.manual_calls[#item.manual_calls+1]=q
 assert(q.X==65 and q.Y==244,'Actual existing vertical marker/signed offset')
 returning(function(t)
  local a=emu.getState();q.returned={PC=t.pc,SP=t.sp,A=a['cpu.a'],X=a['cpu.x'],P=a['cpu.ps']};assert(a['cpu.a']==a['cpu.x'])
  if a['cpu.x']>=1 and a['cpu.x']<=6 then
   local i=a['cpu.x']-1;local e=actor(i)
   assert(e.flag==1 and e.id==37 and e.state==65 and r('Enemy_BoundBoxCtrl',i)==5,'Actual native manual vertical actor published')
   assert(e.x==math.max(0,q.state.x-12)and e.y==q.state.y+32,'Actual native position at constructor return')
   local row={PC=q.PC,SP=q.SP,returned=q.returned,constructor='ManualPlatform',state=q.state,stage=q.stage,area=q.area,slot=i,initial_left=e.x,initial_center=e.x+16,initial_top=e.y,width=32,bbox_control=5,manual_vertical=true,actor=e}
   route.births[#route.births+1]=row;item.manual_birth=row
  else assert(a['cpu.x']==128,'Existing pool retry policy')end
 end)
end)
"""
    marker="hook('GameLoop',function()";assert body.count(marker)==1;body=body.replace(marker,observer+marker,1)
    text='local C='+Text.lua(bindings(raw))+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw).encode()),parent_vertical_factory_SHA256=BASE_SHA,
        manual_constructor_bank64_SHA256=bindings(raw)['hooks']['ManualPlatform']['bank_SHA256'],
        scope='Same directed existing UpSelect/raised-support inputs, actual mapped PRG64B378 constructor-return/actor positions/carry; genuine matureL/wholeC1/INC/cue64/+25 current source returns')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
