"""Keep Sunny's earned upgrades and land on the last stair before its pit."""
import re
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from observe_chip_committed_write import lua
from current_roster_recheck_routes import stair_controller
O=R/'build/sunny-upgrades-stairs-1102-v3'
ROM=R/'build/sunny-growth-prelude-1102-v9/candidate.nes'

def main():
    O.mkdir(exist_ok=True);source=R/'build/sunny-upgrades-current-1102-v2/native/controller.lua';text=source.read_text()
    prior=R/'tools/playthroughs/sunny_upgrades_11_v5.lua';policy=O/'policy.lua';policy.write_text(stair_controller(prior.read_text()))
    text,n=re.subn(r'local POLICY="[^\n]+"',lambda m:'local POLICY='+lua(policy.as_posix()),text,count=1);assert n==1
    # Two bounded end-of-frame samples, rather than a movie or frame forest.
    anchor="emu.addMemoryCallback(function(_,v)\n if entered and nmi and v&24~=0 then"
    assert text.count(anchor)==1
    images='''local flowerShot,fireShot=false,false
emu.addEventCallback(function()
 if entered and not done then
  local tag=nil
  if flowerSeen and not flowerShot then flowerShot=true;tag='flower-earned'
  elseif fireFrames>0 and not fireShot then fireShot=true;tag='native-fireball' end
  if tag then local p=assert(io.open(OUTPUT..tag..'.png','wb'));p:write(emu.takeScreenshot());p:close()end
 end
end,emu.eventType.endFrame)
'''
    text=text.replace(anchor,images+anchor)
    deps=[R/'tools/playthroughs'/n for n in ['sunny_upgrades_11_v5.lua','sunny_upgrades_11_v4.lua','sunny_11_v3.lua','sunny_11_v1.lua','mario_luigi_scrooge_policy.lua','mario_luigi_scrooge_nav.lua']]
    prepare(O/'native',ROM,text,[Path(__file__),source,policy,R/'tools/audit/current_roster_recheck_routes.py',*deps],expected=sha(ROM),timeout=240,scope='Same natural Sunny mushroom/flower/fireball/SFX requirements; controller settles on final stair before its32px pit. Full1-1/lives and hardware guards unchanged. Two end-frame ability PNGs plus endpoint, max3images.',allow_interactive=True)
if __name__=='__main__':main()
