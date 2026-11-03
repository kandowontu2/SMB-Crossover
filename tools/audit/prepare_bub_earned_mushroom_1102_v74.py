"""Controller-only real first block/mushroom qualification on the private candidate."""
import json
from pathlib import Path
import compose_bub_tail_gateways_1102_v66 as G
from prepare_selected_native_packet_v1 import R,sha,prepare
O=R/'build/bub-upgrades-root-earned-1102-v74'

def main():
    O.mkdir(exist_ok=True);_,b,_,q=G.bundles();source=R/'build/bub-upgrades-root-candidate-1102-v72/bub-full11/controller.lua';text=source.read_text()
    assert text.count('local function full_tick(finish)')==1;text=text.replace('local function full_tick(finish)','local function full_tick_base(finish)')
    prefix='L=L or{}\n'+''.join(f'L["{name}"]={G.G.G.Q.address(b,name)}\n' for name in ['PlayerStatus','GuestPowerupActive','GuestPowerupAge','PowerUpType'])
    wrapper='''
local upgrade_phase,upgrade_age,upgrade_last='approach',0,-1
local upgrade_rows,upgrade_mature,upgrade_immature={},false,false
local function upgrade_item()
 for i=0,5 do
  if ram(L.Enemy_Flag+i)>0 and ram(L.Enemy_ID+i)==46 then
   return {slot=i,x=full_x(i),y=ram(L.Enemy_Y_Position+i),state=ram(L.Enemy_State+i)}
  end
 end
end
local function full_tick(finish)
 local q=BUB_OBSERVER.summary();local x,y=full_x(),r('Player_Y_Position');local engine=r('GameEngineSubroutine')
 assert(r('NumberofLives')==2 and engine~=11,'Earned mushroom no death')
 if upgrade_phase=='approach' and x<310 then return full_tick_base(finish)end
 if upgrade_phase=='approach'then upgrade_phase='align';upgrade_age=0;full_pad={}end
 local item=upgrade_item();local flags=full_state((Q.launch.bob==1 and 0x42 or 0x2e)+2)
 if item then
  if item.state<128 then upgrade_immature=true;assert(flags&1==0,'Immature mushroom cannot upgrade source')else upgrade_mature=true end
 end
 if q.completed_Main~=upgrade_last then
  upgrade_last=q.completed_Main;upgrade_age=upgrade_age+1
  if #upgrade_rows<96 and (upgrade_age%8==0 or item)then upgrade_rows[#upgrade_rows+1]={Main=q.completed_Main,phase=upgrade_phase,x=x,y=y,item=item,flags=flags,engine=engine,status=r('PlayerStatus')}end
 end
 assert(upgrade_age<600,'Bounded earned first mushroom phase '..upgrade_phase)
 if engine==9 then full_pad={};return end
 if flags&1~=0 and r('GuestPowerupActive')==0 and engine==8 then
  assert(r('PlayerStatus')==1 and upgrade_immature and upgrade_mature,'Actual emerged/mature mushroom and completed native transformation')
  local obs=BUB_OBSERVER.finish();assert(obs.passed and obs.failures==0)
  local f=assert(io.open(OUTPUT..'earned-mushroom.json','w'))
  f:write(BUB_OBSERVER.json({passed=true,controller_only=true,ROM_sha256=BUB_NATIVE_OBSERVER_CONFIG.ROM_sha256,identity=Q.launch.bob,source_flags=flags,native_status=r('PlayerStatus'),observed_immature=upgrade_immature,observed_mature=upgrade_mature,lives=r('NumberofLives'),rows=upgrade_rows,observer=obs,full_stage=false})..'\\n');f:close()
  shot('earned-first-mushroom-complete');finish();return
 end
 if item then upgrade_phase='collect' end
 if upgrade_phase=='align'then
  full_pad={right=x<329,left=x>332}
  if x>=329 and x<=332 and r('Player_State')==0 and full_state(0x301)&128==0 then upgrade_phase='bump';upgrade_age=0;full_pad={}end
 elseif upgrade_phase=='bump'then
  full_pad={a=upgrade_age<25}
  if upgrade_age>70 and r('Player_State')==0 then upgrade_phase='align';upgrade_age=0 end
 elseif upgrade_phase=='collect'then
  if item then full_pad={right=x<item.x-3,left=x>item.x+3}else full_pad={}end
 end
end
'''
    marker="local log=assert(io.open(OUTPUT..'observations.csv','w'))";assert text.count(marker)==1;text=prefix+text.replace(marker,wrapper+'\n'+marker)
    rom=R/'build/bub-upgrades-root-candidate-1102-v72/bub-original-upgrades.nes';prepare(O/'bub-mushroom',rom,text,[Path(__file__),source,G.O/'proposal.json'],expected=q['expected_memory_only_ROM_SHA256'],timeout=180,allow_interactive=True,scope='Cold actual menu and naturally spawned enemy combat to first native powerup block. Original inputs align329..332 under first mushroom, hit block, observe immature and mature item without early source upgrade, follow natural mushroom and require native60update animation complete/source01/status1/no life loss/passive hardware. No emulated writes or earned flower/fullstage claim.')
if __name__=='__main__':main()
