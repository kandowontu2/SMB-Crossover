"""Preserve the deadline negative; observe genuine cooldown progress fairly."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import R,prepare,sha
from prepare_excitebike_dispatch_1101_v1 import O


def main():
    old=O/'heat-native';q=json.loads((old/'capture/result.json').read_text());h=json.loads((old/'capture/heat.json').read_text())
    assert not q['passed']and q['reason']=='Stationary terrain or recovery bound'and h['heat_seen']and not h['resumed_motion']
    text=(old/'controller.lua').read_text()
    marker='local heatEvents,lastHeatState={},nil'
    assert text.count(marker)==1;text=text.replace(marker,marker+'\nlocal lastMeaningfulRecovery=nil')
    marker=" local b={right=true,b=true};local x,y=wx(),r('Player_Y_Position');local epoch=r('FrameCounter')"
    assert text.count(marker)==1
    text=text.replace(marker,marker+"\n if heatSeen then return {right=true}end -- Genuine turbo release; no new jump/lean during cooling qualification.")
    marker=" local key=string.format('%d/%d/%d',cached.heat,cached.recovery,p(0xc03c))"
    assert text.count(marker)==1
    addition='''
 if phase=='play'and(cached.heat~=0 or cached.recovery~=0 or cached.crash~=0)then
  local progress=string.format('%d/%d/%d/%d/%d/%d/%d/%d',cached.heat,cached.recovery,cached.crash,p(0xc03c),p(0xc036),p(0xc374),p(0xc0b8),p(0xc390))
  if progress~=lastMeaningfulRecovery then lastMeaningfulRecovery=progress;lastProgress=age end
 end
'''
    text=text.replace(marker,addition+marker)
    rom=O/'current4.nes';pin='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'
    prepare(O/'heat-native2',rom,text,
            [Path(__file__),old/'controller.lua',old/'capture/result.json',old/'capture/heat.json',O/'current4-composition.json',O/'heat-CPU.json'],
            expected=pin,timeout=180,allow_interactive=True,
            scope='Same exact native5-passing ROM. Preserve actual heat-native negative caused by360frame deadline before original11epoch timer expired. Same controller until realoverheat, then releaseB and hold genuineRight; exempt stationary time only while heat/recovery/crash state, timers3C/36, gate374, laneB8 or recovery390 actually progress. Counter20/frameclock alone never extends deadline. Require realheat32→recovery5→0→speed>=608 and>=16px motion, same lives; global9500frames retained. No emulated writes/helpers/fullstage claim.')


if __name__=='__main__':main()
