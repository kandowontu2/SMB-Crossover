"""Natural Sunny mushroom/flower/fireball route on the delivered nightly."""
import re
from pathlib import Path
import audit_current_menu_indicators_1102_v1 as A
from check_tmnt_render_oa import address
from prepare_selected_native_packet_v1 import R,prepare,sha
from observe_chip_committed_write import lua
O=R/'build/sunny-upgrades-current-1102-v1'
ROM=R/'build/sunny-growth-prelude-1102-v9/candidate.nes'

def main():
    O.mkdir(exist_ok=True);source=R/'build/sunny-growth-native-1102-v9/native/controller.lua';text=source.read_text()
    deps=[R/'tools/playthroughs'/n for n in ['sunny_upgrades_11_v4.lua','sunny_11_v3.lua','sunny_11_v1.lua','mario_luigi_scrooge_policy.lua','mario_luigi_scrooge_nav.lua']]
    text,n=re.subn(r'local POLICY="[^\n]+"',lambda m:'local POLICY='+lua(deps[0].as_posix()),text,count=1);assert n==1
    b=A.bundle();names=set(re.findall(r"c\.r\('([^']+)'",'\n'.join(p.read_text()for p in deps)))|{'Fireball_State','Square1SoundQueue'}
    extension='\nfor n,a in pairs('+lua({n:address(b,n)for n in names})+')do CURRENT_KIRBY_META_EARNED.ram[n]=a end\n'
    first,rest=text.split('\n',1);text=first+extension+rest
    anchor='local function finish(passed,why)';assert text.count(anchor)==1
    text=text.replace(anchor,'local mushroomSeen,flowerSeen,fireFrames,fireCues=false,false,0,0\n'+anchor)
    anchor=' if done then return end;done=true;inputFile:close()';assert text.count(anchor)==1
    text=text.replace(anchor," if passed then assert(mushroomSeen and flowerSeen and fireFrames>0 and fireCues>0,'Natural mushroom/flower and native fireball/SFX required')end\n"+anchor)
    anchor="player_status=r('PlayerStatus'),NMI=nmis";assert text.count(anchor)==1
    text=text.replace(anchor,"player_status=r('PlayerStatus'),mushroom_seen=mushroomSeen,flower_seen=flowerSeen,fireball_frames=fireFrames,fireball_cues=fireCues,NMI=nmis")
    anchor=' updates=updates+1;maxX=math.max(maxX,world())';assert text.count(anchor)==1
    text=text.replace(anchor,anchor+"\n if r('PlayerStatus')>=1 then mushroomSeen=true end\n if r('PlayerStatus')==2 then flowerSeen=true end\n if r('Fireball_State')~=0 or r('Fireball_State',1)~=0 then fireFrames=fireFrames+1 end\n if r('Square1SoundQueue')&32~=0 then fireCues=fireCues+1 end")
    prepare(O/'native',ROM,text,[Path(__file__),source,*deps],expected=sha(ROM),timeout=240,scope='Actual Sunny23 Hard controller-only natural mushroom plus genuine later flower, native fireballs and their SFX request, full1-1 into1-2 required. No powerup/health/position seeding. All existing deadline/DMA/CHR/IRQ/stack guards retained.',allow_interactive=True)
if __name__=='__main__':main()
