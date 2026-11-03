"""Prepare, never run, earned Mini mushroom on exact ca90 with passive power observations."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_power_contract_1103_v51 as P
import prepare_mini_mario_native_smoke_1103_v25 as B
from prepare_selected_native_packet_v1 import prepare,sha
from observe_chip_committed_write import lua
R,O=P.R,P.O
def main():
 prior=R/'build/mini-mario-end-fixed-packets-1103-v49/full49';ready=json.loads((prior/'ready.json').read_text());rom=Path(ready['ROM']);assert ready['ROM_sha256']==P.PIN==sha(rom)
 contract=json.loads((O/'power-contract-v51.json').read_text());assert contract['passed']
 text=(prior/'controller.lua').read_text();G=B.labels(B.GLOBALS);names=['PlayerStatus','GuestPowerupActive','GuestPowerupAge','GuestPowerupOld','GuestPowerupTarget','GuestPowerupDisplay','Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','PowerUpType','TimerControl','FrameCounter']
 anchor='local function result(ok,why)';assert text.count(anchor)==1
 prefix='for k,v in pairs('+lua({n:G[n]for n in names})+')do L[k]=v end\nC.max_frames=9000\nlocal power={phase="approach",age=0,heads={},samples={},immature=false,mature=false,powered_samples=0}\n'
 text=text.replace(anchor,prefix+anchor)
 text=text.replace('native_end_handoff=end_native,','earned_power=power,native_end_handoff=end_native,')
 anchor=" if lastEpoch then check(((s.epoch-lastEpoch)&255)==1,"
 assert text.count(anchor)==1;text=text.replace(anchor," if power.reset_epoch then lastEpoch=nil;power.reset_epoch=false end\n"+anchor)
 a=" check(ram(0xc254)==1 and ram(0xc255)==6 and ram(0xc256)==1 and ram(0xc257)==7,'Original small6x7 integer bounds')"
 b=" local top=(ram(0xc244)>0 and ram(0xc243)==0)and -7 or 1\n check(ram(0xc254)==1 and ram(0xc255)==6 and ram(0xc256)==(top&255)and ram(0xc257)==7,'Original current small6x7/powered6x15/crouched6x7 bounds')"
 assert text.count(a)==1;text=text.replace(a,b)
 a="((p.y+25)&255)";assert text.count(a)==1;text=text.replace(a,'((p.y+24+top)&255)')
 text=text.replace("shot('mini-active-1-2');result(true)","shot('mini-earned-mushroom');result(true)")
 text=text.replace("print('PASS Mini actual nonshortcut1-1')","print('PASS Mini earned mushroom and source powered body')")
 host=json.loads((P.HOST/'mini-host-v48.json').read_text());kernel=(P.HOST/'mini-host-v48.bin').read_bytes();pc=host['labels']['MiniHostHead']
 hook=dict(pc=pc,physical=3*8192+pc-0xa000,memory='nesWorkRam',bytes=list(kernel[pc-0xa000:pc-0xa000+4]))
 extra='''
-- Reuse qualified initial enemy avoidance, then perform one source-proven
-- Right+B runjump at304 toward first Q336..351/queryrow144. No state writes.
local first_route=route_tick
local function power_item()
 for i=0,5 do
  if read(L.Enemy_Flag+i)>0 and read(L.Enemy_ID+i)==46 then
   return{slot=i,x=read(L.Enemy_X_Position+i)+256*read(L.Enemy_PageLoc+i),y=read(L.Enemy_Y_Position+i),state=read(L.Enemy_State+i),kind=read(L.PowerUpType+i)}
  end
 end
end
local function power_snapshot(reason)
 if #power.samples>=96 then return end
 power.samples[#power.samples+1]={reason=reason,frame=frame,source=updates,x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),engine=r('GameEngineSubroutine'),status=r('PlayerStatus'),active=r('GuestPowerupActive'),age=r('GuestPowerupAge'),old=r('GuestPowerupOld'),target=r('GuestPowerupTarget'),display=r('GuestPowerupDisplay'),tier=ram(0xc244),top=ram(0xc256),pose=ram(0xc310),item=power_item()}
end
route_tick=function(s)
 if power.phase=='approach'and s.x/16<280 then return first_route(s)end
 if power.phase=='approach'then power.phase='runup';power.age=0;power_snapshot('runup')end
 power.age=power.age+1;check(power.age<700,'Bounded earned power phase '..power.phase)
 local item=power_item()
 if item then
  if item.state<128 then power.immature=true;check(r('PlayerStatus')==0,'No power from immature mushroom')else power.mature=true end
  if not power.spawn then power.spawn={frame=frame,source=updates,item=item};power_snapshot('first-real-spawn')end
  if power.phase~='collect'then power.phase='collect';power.age=0 end
 end
 if r('PlayerStatus')==1 and r('GuestPowerupActive')==0 then
  check(power.immature and power.mature and #power.heads>0,'Earned head/emergence/mature lifecycle observed')
  check(ram(0xc244)==1 and ram(0xc256)==249 and s.pose>=39,'Actual powered source form and6x15 standing body')
  power.powered_samples=power.powered_samples+1;route_pad={}
  if power.powered_samples>=10 then
   power.completed=true;power.script_mushroom_wait_frames=30;power.original_transition_timing_qualified=false
   power_snapshot('earned-powered-body-complete');transition('finish')
  end
  return
 end
 if power.phase=='runup'then
  route_pad={right=true,b=true}
  if s.x>=304*16 and s.contacts&1~=0 and s.class==2 and s.held&128==0 then
   power.phase='bump';power.age=0;route_pad.a=true;power.takeoff={frame=frame,source=updates,x16=s.x,y16=s.y};power_snapshot('fresh-original-jump')
  end
 elseif power.phase=='bump'then
  route_pad={right=true,b=true,a=power.age<40}
  check(power.age<100,'First source runjump must produce native item')
 elseif power.phase=='collect'then
  if item then
   local x=s.x/16;route_pad={right=x<item.x+1,left=x>item.x+7}
  else route_pad={}end
 else route_pad={}end
end
route_endframe=function()
 check(r('NumberofLives')==startLives,'Earned power retains actual lives')
 check(r('GameEngineSubroutine')~=11,'No death in earned power route')
end
C.hooks.MiniHostHead=HEAD_HOOK
emu.addMemoryCallback(guard(function()
 if not active()or not valid(C.hooks.MiniHostHead)or ram(0xc25c)==0 then return end
 if word(0xc25d)//16==21 and #power.heads<8 then
  power.heads[#power.heads+1]={frame=frame,source=updates,x=word(0xc25d),y=word(0xc25f),tile=ram(0xc261),address=word(0xc262)}
 end
end),emu.callbackType.exec,C.hooks.MiniHostHead.pc)
local power_signature=nil
emu.addEventCallback(guard(function()
 if r('SelectedCharacter')~=41 or r('OperMode')~=1 or phase~='fullstage'then return end
 local sig=table.concat({r('GameEngineSubroutine'),r('PlayerStatus'),r('GuestPowerupActive'),r('GuestPowerupTarget')},':')
 if sig~=power_signature then power_signature=sig;power_snapshot('native-power-change')end
 if r('GameEngineSubroutine')==9 or r('GuestPowerupActive')~=0 then
  power.reset_epoch=true;route_pad={}
  if not power.freeze_start then power.freeze_start=frame end
  power.maximum_native_age=math.max(power.maximum_native_age or 0,r('GuestPowerupAge'))
  check(frame-power.freeze_start<1200,'Bounded native power freeze')
 elseif power.freeze_start and not power.freeze_end then power.freeze_end=frame;power_snapshot('native-freeze-complete')end
end),emu.eventType.endFrame)
'''.replace('HEAD_HOOK',lua(hook))
 text+='\n'+extra
 sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
 from lupa.lua54 import LuaRuntime
 assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
 refs=[Path(p)for p in ready['bindings']]+[Path(__file__),O/'power-contract-v51.json',O/'power-inputs-v51.zip',P.HOST/'mini-host-v48.json']
 prepare(O/'earned-mushroom',rom,text,refs,expected=P.PIN,timeout=180,allow_interactive=True,scope='Exactca90 no ROM/source/RAM writes. Reuses actual full49 cold Mini menu and initial enemy controls, then one sourceCPU-proven304runjump atfirstQ336..351/query144 and natural mushroom chase. Require real pendingHead row10, actual immature/mature item and no earlyupgrade, completed native status1/freeze and10source powered6x15/pose samples; existing sourceOAM/CHR/opaqueRGB guards retained, bbox expected actual originaltier. Record native transition ages/held poses vs original30scriptwait, no source timing fidelity or flower/projectile claim. TwoPNG/9000physicalframe cap; only root runs Mesen.')
if __name__=='__main__':main()
