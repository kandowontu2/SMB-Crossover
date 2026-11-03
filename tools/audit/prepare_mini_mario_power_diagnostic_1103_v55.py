"""Observe54's real item disappearance before changing controls or game code."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_power_contract_1103_v51 as P
import prepare_mini_mario_native_smoke_1103_v25 as B
from prepare_selected_native_packet_v1 import prepare,sha
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua
R,O=P.R,P.O
def main():
 prior=O/'earned-mushroom54';ready=json.loads((prior/'ready.json').read_text());rom=Path(ready['ROM']);assert sha(rom)==P.PIN
 negative=prior/'capture/result.json';q=json.loads(negative.read_text());assert not q['passed']and q['earned_power']['spawn']and q['earned_power']['immature']and q['earned_power']['mature']
 bundle=load(rom)
 # The passed native DBG is intentionally compact; bind legacy native
 # locations from the retained full native metadata, with CURRENT ROM bytes.
 full_debug=B.GLOBALS.with_suffix('.dbg')
 for line in full_debug.read_text().splitlines():
  if not line.startswith(('sym\t','seg\t')):continue
  z=dict(x.split('=',1)for x in line[4:].split(',')if '='in x)
  if line.startswith('seg\t'):bundle['segs'][z['id']]=z
  elif 'val'in z:bundle['syms'][z['name'].strip('"')]=z
 hooks={}
 for name in['HandlePowerUpCollision','NrPickup','HuPickup','MarioSourcePowerupCollision','GuestBeginPowerup','GuestPowerupUpdate','EraseEnemyObject','InventoryCollect']:
  at=location(bundle,name)-16;hooks[name]=dict(name=name,pc=address(bundle,name),physical=at,memory='nesPrgRom',bytes=list(bundle['raw'][at+16:at+20]))
 for row in[23,24,33]:
  pc=0xb08c+row*3;at=65*8192+pc-0xa000;name=f'CoService{row}'
  hooks[name]=dict(name=name,pc=pc,physical=at,memory='nesPrgRom',bytes=list(bundle['raw'][16+at:20+at]))
 text=(prior/'controller.lua').read_text();G=B.labels(B.GLOBALS);anchor='local function result(ok,why)';assert text.count(anchor)==1
 text=text.replace(anchor,'L.ObjectOffset='+str(G['ObjectOffset'])+'\npower.trajectory={};power.native_calls={};power.native_events={}\n'+anchor)
 extra='''
-- Same54inputs. These finite passive records distinguish real collection
-- from offscreen removal and retain the last genuine item state.
local diagnostic_route=route_tick
local diagnostic_last_source=-1
route_tick=function(s)
 local item=power_item()
 if power.spawn and updates~=diagnostic_last_source then
  diagnostic_last_source=updates
  if #power.trajectory<128 and(item==nil or updates%8==0)then
   power.trajectory[#power.trajectory+1]={frame=frame,source=updates,playerX=s.x/16,playerY=s.y/16,nativeY=r('Player_Y_Position'),held=s.held,phase=power.phase,item=item,flag5=read(L.Enemy_Flag+5),ID5=read(L.Enemy_ID+5),state5=read(L.Enemy_State+5),status=r('PlayerStatus')}
  end
  if item then power.last_actual_item={frame=frame,source=updates,item=item,playerX=s.x/16,playerY=s.y/16}
  elseif not power.item_lost then power.item_lost={frame=frame,source=updates,playerX=s.x/16,playerY=s.y/16,status=r('PlayerStatus'),flag5=read(L.Enemy_Flag+5),ID5=read(L.Enemy_ID+5),state5=read(L.Enemy_State+5)}end
  if power.item_lost and updates-power.item_lost.source>80 and r('PlayerStatus')==0 then
   check(false,'Real item disappeared without status gain; inspect native_calls/native_events/trajectory')
  end
 end
 return diagnostic_route(s)
end
local diagnostic_hooks=HOOKS
for name,h in pairs(diagnostic_hooks)do
 emu.addMemoryCallback(guard(function()
  if r('SelectedCharacter')~=41 or r('OperMode')~=1 or phase~='fullstage'or not power.spawn or not valid(h)then return end
  local cpu=emu.getState();local x=cpu['cpu.x']
  if name=='EraseEnemyObject'and x~=5 and r('ObjectOffset')~=5 then return end
  power.native_calls[name]=(power.native_calls[name]or 0)+1
  if #power.native_events<48 and(name~='CoService23'or power.native_calls[name]<3)then
   power.native_events[#power.native_events+1]={name=name,frame=frame,source=updates,A=cpu['cpu.a'],X=x,Y=cpu['cpu.y'],SP=cpu['cpu.sp'],object=r('ObjectOffset'),status=r('PlayerStatus'),active=r('GuestPowerupActive'),engine=r('GameEngineSubroutine'),flag5=read(L.Enemy_Flag+5),ID5=read(L.Enemy_ID+5),state5=read(L.Enemy_State+5),itemX=read(L.Enemy_X_Position+5)+256*read(L.Enemy_PageLoc+5),itemY=read(L.Enemy_Y_Position+5)}
  end
 end),emu.callbackType.exec,h.pc)
end
'''.replace('HOOKS',lua(hooks))
 text+='\n'+extra
 sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
 from lupa.lua54 import LuaRuntime
 assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
 receipt=O/'power-diagnostic-v55.json';receipt.write_text(json.dumps(dict(passed=True,observer_only=True,controller_inputs_unchanged=True,ROM_SHA256=P.PIN,hooks=hooks,retained_negative=negative.relative_to(R).as_posix(),scope='Only passive aggregate trajectory/native call entries; earlier native head release and immature/mature confirmed54. No chase input or game change, no collection acceptance before runtime.'),indent=2)+'\n')
 refs=[Path(p)for p in ready['bindings']]+[Path(__file__),negative,receipt,full_debug]
 prepare(O/'earned-mushroom55',rom,text,refs,expected=P.PIN,timeout=180,allow_interactive=True,scope='Read-only diagnostic on unchangedca90/exact54inputs.128item/player samples+48nativeentryevents, aggregatecounts. Distinguish Head release, mature item motion, collection callback/erase/GuestBeginPowerup vsdespawn. Stop80sourceupdates after realdisappearance withoutstatus. Existing hardware/bbox/name/CHR/sourceguards/twoPNG retained; no ROM/RAM writes or earnedpass claimed.')
if __name__=='__main__':main()
