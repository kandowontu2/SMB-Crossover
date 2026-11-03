"""Identify the naturally released item's actual slot/type and native clocks."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
import check_bub_head_projection_1102_v56 as H
O=R/'build/bub-head-item-diagnostic-1103-v84'
PIN='cc7b9bddfd39c62fadb5c1afc34bc82361432eab5a8a8e5b5a18bde184813a4e'

def main():
    O.mkdir(exist_ok=True)
    source=R/'build/bub-head-earned-alignment-1103-v83/bub-mushroom/controller.lua'
    _,bundle,_,_,_,_=H.bundle()
    text='L=L or{}\nL["TimerControl"]='+str(H.address(bundle,'TimerControl'))+'\n'+source.read_text();needle='local upgrade_attempts=0';assert text.count(needle)==1
    text=text.replace(needle,needle+'\nlocal diagnostic_mature_shot=false')
    before="  local _,b0=full_solid(324,144);";assert text.count(before)==1
    text=text.replace(before,"""  if item and item.state>=128 and not diagnostic_mature_shot then
   diagnostic_mature_shot=true;shot('first-mature-block-item')
  end
  local f=assert(io.open(OUTPUT..'item-current.json','w'))
  f:write(BUB_OBSERVER.json({diagnostic_only=true,Main=q.completed_Main,phase=upgrade_phase,x=x,y=y,item=item,flags=flags,engine=engine,status=r('PlayerStatus'),native_type=item and ram(L.PowerUpType+item.slot)or -1,native_timer=r('TimerControl'),item_speed=item and ram(L.Enemy_X_Speed+item.slot)or -1,native_powerup_active=r('GuestPowerupActive'),native_powerup_age=r('GuestPowerupAge')})..'\\n');f:close()
"""+before)
    before="assert(upgrade_age<600,'Bounded earned first mushroom phase '..upgrade_phase)";assert text.count(before)==1
    text=text.replace(before,"assert(upgrade_age<160,'Bounded diagnostic earned first mushroom phase '..upgrade_phase)")
    rom=R/'build/bub-head-root-candidate-1103-v81/bub-source-head.nes'
    prepare(O/'bub-item',rom,text,[Path(__file__),source],expected=PIN,timeout=90,allow_interactive=True,scope='Unqualified private diagnostic on samecc7b after real head bump. Record actual EnemySlot-indexed PowerUpType, PlayerStatus, TimerControl and item Y/X/speed in one overwritten JSON, one boundedCSV and atmostone additionalPNG. No earned pickup/nightly claim and no emulated writes. Existing bounded source/hardware/no-death assertions remain.')

if __name__=='__main__':main()
