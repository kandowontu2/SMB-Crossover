"""Natural first mushroom then second flower collection, with no state writes."""
import argparse,json
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_getsu_earned_powerups_1110 as G
from check_tmnt_render_oa import address

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--rom',type=Path,required=True);p.add_argument('--proof',type=Path,required=True)
 p.add_argument('--mode',choices=('route','powerup'),default='powerup')
 a=p.parse_args();digest=sha(a.rom);proof=json.loads(a.proof.read_text());assert proof['passed'] and proof['expected_memory_only_SHA256']==digest
 source=(G.NATIVE/'controller.lua').read_text();assert source.count(G.D.PIN)==1;source=source.replace(G.D.PIN,digest)
 b=G.D.Current.Getsu.W.bundle(a.rom.read_bytes())
 at=source.index('\n-- Real frontend')
 source=source[:at]+'\n'+'\n'.join(f'C.ram.{n}={address(b,n)}' for n in ('PlayerStatus','GuestPowerupActive','GuestPowerupAge','PowerUpType'))+source[at:]
 if a.mode=='powerup':
  source=source.replace('local frame, updates, draws =','local pickup={events={},items={}}\nlocal jumpAt=-200\nlocal frame, updates, draws =',1)
  source=source.replace('terminal=state(),max_x=lastX,','terminal=state(),pickup=pickup,max_x=lastX,',1)
  # Reuse the proven route between the two real powerup blocks.
  source=source.replace('local function choose()','local function routeChoose()',1)
  at=source.index('\nemu.addEventCallback(function() emu.setInput')
  source=source[:at]+'''
local function choose()
 local stage=r('PlayerStatus');local x=playerX()
 if stage>=2 then
  pickup.recovered_x=pickup.recovered_x or x
  input={right=true}
  if x>=pickup.recovered_x+16 then return finish(true,'Natural mushroom and flower transformations completed; movement resumed') end
  return
 end
 local block=stage==0 and 336 or 1248
 local item=nil
 for i=0,5 do
  local e=actor(i)
  if e.flag==1 and e.id==46 then item=e;break end
 end
 if item then
  pickup.items[tostring(stage)]={kind=r('PowerUpType',item.slot),item=item,player=state()}
  local gap=item.x-x
  if stage==1 then
   if not pickup.flower_launch then
    if x>item.x-54 then input={left=true,b=updates%16<4};return end
    if r('Player_State')==0 then pickup.flower_launch=updates end
   end
   input={right=true,b=updates%16<4,a=pickup.flower_launch~=nil and updates-pickup.flower_launch<23}
   return
  end
  if math.abs(gap)<20 and item.y<r('Player_Y_Position')-16 and r('Player_State')==0 and updates-jumpAt>45 then jumpAt=updates end
  input={right=gap>3,left=gap< -3,a=updates-jumpAt<23}
  return
 end
 if x<block-24 then return routeChoose() end
 if updates-jumpAt<23 then input={a=true};return end
 local gap=(block-6)-x
 if math.abs(gap)>2 then input={right=gap>0,left=gap<0};return end
 if r('Player_State')==0 and updates-jumpAt>45 then jumpAt=updates end
 input={a=updates-jumpAt<23}
end
emu.addMemoryCallback(function(_,value)
 if r('SelectedCharacter')==42 and started then
  pickup.events[#pickup.events+1]={player=state(),active=value,age=r('GuestPowerupAge'),status=r('PlayerStatus')}
 end
end,emu.callbackType.write,C.ram.GuestPowerupActive)
''' +source[at:]
 prepare(a.output,a.rom,source,{Path(__file__),a.proof,G.NATIVE/'controller.lua'},
         expected=digest,timeout=240,allow_interactive=True,rom_symbols=G.D.SYMBOLS,
         scope='Controller-only real item blocks and completed native transformations.' if a.mode=='powerup' else 'Unchanged full Getsu controller on powerup callback repair.')

if __name__=='__main__':main()
